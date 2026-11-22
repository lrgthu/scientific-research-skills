#!/usr/bin/env python3
r"""Unpacks candidate papers into a structured local full-text/LaTeX corpus for Elicit-style extraction.

Provenance Priority Hierarchy:
1. arXiv `.tar.gz` LaTeX source -> flattens `\input{}` / `\include{}` into `fulltext.tex` + extracts `tables.tex`
2. Open-Access PDF or local `.pdf` -> extracts page-anchored `[Page N]` text via `pypdf` into `fulltext.txt`
3. Abstract-only fallback -> writes `abstract_only.txt` stamped `PROVENANCE_TIER: abstract_only`
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27.0",
#   "pypdf>=4.2.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import gzip
import io
import json
import logging
from pathlib import Path
import re
import tarfile
import time
from typing import Any
import urllib.parse

import dotenv
import httpx
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("unpack_corpus")

dotenv.load_dotenv(Path.home() / ".env")

ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}|[a-z\-]+/\d{7})(?:v\d+)?$", re.IGNORECASE)
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
TABLE_RE = re.compile(r"(\\begin\{table\*?\}.*?\\end\{table\*?\})", re.DOTALL)


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", text.strip()).strip("_")
    return s[:64] or "paper"


def strip_tex_comments(tex: str) -> str:
    out_lines = []
    for ln in tex.splitlines():
        out_lines.append(re.sub(r"(?<!\\)%.*$", "", ln))
    return "\n".join(out_lines)


def flatten_tex_tree(root_tex: Path, base_dir: Path, visited: set[Path] | None = None) -> str:
    if visited is None:
        visited = set()
    resolved = root_tex.resolve()
    if resolved in visited or not resolved.exists():
        return ""
    visited.add(resolved)
    content = strip_tex_comments(resolved.read_text(encoding="utf-8", errors="ignore"))

    def _repl(match: re.Match[str]) -> str:
        rel_target = match.group(1).strip()
        candidates = [
            (resolved.parent / rel_target),
            (resolved.parent / f"{rel_target}.tex"),
            (base_dir / rel_target),
            (base_dir / f"{rel_target}.tex"),
        ]
        for cand in candidates:
            if cand.exists() and cand.is_file():
                sub = flatten_tex_tree(cand, base_dir, visited)
                return f"\n% --- BEGIN INCLUDED FILE: {rel_target} ---\n{sub}\n% --- END INCLUDED FILE: {rel_target} ---\n"
        return match.group(0)

    return INPUT_RE.sub(_repl, content)


def unpack_arxiv_source(client: httpx.Client, arxiv_id: str, paper_dir: Path) -> dict[str, Any] | None:
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    try:
        resp = client.get(url)
        if resp.status_code != 200 or not resp.content:
            return None
    except httpx.HTTPError as exc:
        logger.warning("arXiv e-print download failed for %s: %s", arxiv_id, exc)
        return None

    raw_dir = paper_dir / "raw_tex"
    raw_dir.mkdir(parents=True, exist_ok=True)
    tex_files: list[Path] = []

    try:
        with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:*") as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                rel = Path(m.name)
                if rel.is_absolute() or ".." in rel.parts:
                    continue
                if rel.suffix.lower() in {".tex", ".bib", ".bbl", ".sty"}:
                    dest = (raw_dir / rel).resolve()
                    if not str(dest).startswith(str(raw_dir.resolve())):
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    fobj = tf.extractfile(m)
                    if fobj:
                        dest.write_bytes(fobj.read())
                        if dest.suffix.lower() == ".tex":
                            tex_files.append(dest)
    except tarfile.TarError:
        try:
            decompressed = gzip.decompress(resp.content)
            main_p = raw_dir / "main.tex"
            main_p.write_bytes(decompressed)
            tex_files.append(main_p)
        except OSError:
            return None

    if not tex_files:
        return None

    # Identify root .tex containing \documentclass or largest file
    root_candidates = [
        p for p in tex_files if "\\documentclass" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    root_tex = (
        max(root_candidates, key=lambda p: p.stat().st_size)
        if root_candidates
        else max(tex_files, key=lambda p: p.stat().st_size)
    )

    flattened = flatten_tex_tree(root_tex, raw_dir)
    # Append any remaining orphan .tex files not pulled via \input
    for extra in sorted(tex_files):
        if extra.resolve() != root_tex.resolve() and extra.stem not in flattened:
            extra_txt = strip_tex_comments(extra.read_text(encoding="utf-8", errors="ignore"))
            flattened += f"\n\n% --- SUPPLEMENTARY TEX FILE: {extra.name} ---\n{extra_txt}"

    full_tex_path = paper_dir / "fulltext.tex"
    full_tex_path.write_text(flattened, encoding="utf-8")

    tables = TABLE_RE.findall(flattened)
    tables_path = paper_dir / "tables.tex"
    if tables:
        tables_path.write_text("\n\n% ==========================================\n\n".join(tables), encoding="utf-8")

    return {
        "provenance_tier": "latex_source",
        "primary_text_path": str(full_tex_path),
        "tables_path": str(tables_path) if tables else None,
        "table_count": len(tables),
        "char_count": len(flattened),
    }


def extract_pdf_bytes_to_text(pdf_bytes: bytes, paper_dir: Path) -> dict[str, Any] | None:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_out: list[str] = []
        for idx, page in enumerate(reader.pages, start=1):
            txt = (page.extract_text() or "").strip()
            if txt:
                pages_out.append(f"=== [Page {idx}] ===\n{txt}")
        if not pages_out:
            return None
        joined = "\n\n".join(pages_out)
        out_path = paper_dir / "fulltext.txt"
        out_path.write_text(joined, encoding="utf-8")
        return {
            "provenance_tier": "oa_pdf_fulltext",
            "primary_text_path": str(out_path),
            "tables_path": None,
            "page_count": len(reader.pages),
            "char_count": len(joined),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDF parsing failed: %s", exc)
        return None


def resolve_lightweight_item(client: httpx.Client, spec: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(spec, dict):
        return spec
    s = spec.strip()
    local_p = Path(s).expanduser()
    if local_p.exists() and local_p.suffix.lower() == ".pdf":
        return {"title": local_p.stem, "local_pdf": str(local_p.resolve()), "canonical_id": f"local:{local_p.stem}"}

    m_ax = ARXIV_RE.match(s)
    extracted_ax = (
        m_ax.group(1)
        if m_ax
        else (
            s.split("/abs/")[-1].split("/pdf/")[-1].replace(".pdf", "").split("v")[0].strip("/")
            if "arxiv.org/" in s
            else None
        )
    )

    # Query OpenAlex for DOI / arXiv DataCite DOI / title so full metadata is populated
    doi_clean = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", "", s, flags=re.IGNORECASE)
    if extracted_ax:
        url = f"https://api.openalex.org/works/https://doi.org/10.48550/arXiv.{extracted_ax}"
    elif doi_clean.startswith("10."):
        url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi_clean, safe='/')}"
    else:
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(s)}&per-page=1"

    try:
        r = client.get(url)
        if r.status_code == 200:
            data = r.json()
            w = data["results"][0] if "results" in data and data["results"] else (data if "id" in data else None)
            if w:
                oa_url = (w.get("open_access") or {}).get("oa_url")
                raw_doi = (w.get("doi") or "").replace("https://doi.org/", "")
                arxiv_id = extracted_ax
                if raw_doi.lower().startswith("10.48550/arxiv."):
                    arxiv_id = arxiv_id or re.sub(r"^10\.48550/arxiv\.", "", raw_doi, flags=re.IGNORECASE)
                    raw_doi = ""
                venue = ""
                for loc in [w.get("primary_location")] + (w.get("locations") or []):
                    if not loc:
                        continue
                    lp = loc.get("landing_page_url") or ""
                    if "arxiv.org/abs/" in lp and not arxiv_id:
                        arxiv_id = lp.split("arxiv.org/abs/")[-1].split("v")[0].strip("/")
                    disp = ((loc.get("source") or {}).get("display_name") or "").strip()
                    if disp and "arxiv" not in disp.lower() and not venue:
                        venue = disp
                authors = [
                    ((a.get("author") or {}).get("display_name") or "").strip()
                    for a in (w.get("authorships") or [])
                    if (a.get("author") or {}).get("display_name")
                ]
                inv = w.get("abstract_inverted_index") or {}
                pos = {p: word for word, plist in inv.items() for p in plist}
                abstract = " ".join(pos[i] for i in sorted(pos)) if pos else None
                return {
                    "title": w.get("title") or (f"arXiv:{arxiv_id}" if arxiv_id else s),
                    "authors": authors,
                    "year": w.get("publication_year"),
                    "venue": venue or ("arXiv" if arxiv_id else None),
                    "doi": raw_doi or None,
                    "arxiv_id": arxiv_id,
                    "oa_pdf_url": oa_url or (f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None),
                    "abstract": abstract,
                    "canonical_id": f"doi:{raw_doi}" if raw_doi else (f"arxiv:{arxiv_id}" if arxiv_id else f"oa:{w['id'].split('/')[-1]}"),
                }
    except httpx.HTTPError:
        pass

    if extracted_ax:
        return {
            "title": f"arXiv:{extracted_ax}",
            "arxiv_id": extracted_ax,
            "oa_pdf_url": f"https://arxiv.org/pdf/{extracted_ax}.pdf",
            "canonical_id": f"arxiv:{extracted_ax}",
        }
    return {"title": s, "canonical_id": slugify(s)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Unpack candidate papers into a local full-text/LaTeX corpus.")
    parser.add_argument("--papers", nargs="*", default=[], help="Paper IDs (arXiv, DOI, title) or local .pdf paths")
    parser.add_argument("--from-json", help="Path to JSON from scholarly_graph.py (lineage or resolve)")
    parser.add_argument("--roles", nargs="*", default=["seed", "ancestor", "frontier", "semantic_sibling"], help="Roles to include when reading --from-json")
    parser.add_argument("--max-papers", type=int, default=25, help="Max papers to unpack (default: 25)")
    parser.add_argument("--out-dir", required=True, help="Output corpus directory")
    args = parser.parse_args()

    out_root = Path(args.out_dir).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    candidates: list[str | dict[str, Any]] = list(args.papers)
    if args.from_json:
        jdata = json.loads(Path(args.from_json).expanduser().read_text(encoding="utf-8"))
        if "nodes" in jdata:
            allowed = set(args.roles)
            candidates.extend([n for n in jdata["nodes"] if n.get("role") in allowed])
        elif "results" in jdata:
            candidates.extend([r["resolved"] for r in jdata["results"] if r.get("resolved")])

    candidates = candidates[: args.max_papers]
    client = httpx.Client(
        timeout=40.0,
        follow_redirects=True,
        headers={"User-Agent": "ResearchLiteratureCorpusUnpacker/1.0"},
    )

    manifest_items: list[dict[str, Any]] = []
    for idx, item in enumerate(candidates, start=1):
        meta = resolve_lightweight_item(client, item)
        cid = meta.get("canonical_id") or f"paper_{idx}"
        folder = out_root / f"{idx:02d}_{slugify(cid)}"
        folder.mkdir(parents=True, exist_ok=True)

        extraction_info: dict[str, Any] | None = None
        # 1. Try local PDF if given
        if meta.get("local_pdf"):
            pdf_bytes = Path(meta["local_pdf"]).read_bytes()
            extraction_info = extract_pdf_bytes_to_text(pdf_bytes, folder)

        # 2. Prefer arXiv LaTeX source
        if not extraction_info and meta.get("arxiv_id"):
            time.sleep(1.0)
            extraction_info = unpack_arxiv_source(client, meta["arxiv_id"], folder)

        # 3. Try Open-Access PDF
        if not extraction_info and meta.get("oa_pdf_url"):
            try:
                time.sleep(0.5)
                resp = client.get(meta["oa_pdf_url"])
                if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                    (folder / "paper.pdf").write_bytes(resp.content)
                    extraction_info = extract_pdf_bytes_to_text(resp.content, folder)
            except httpx.HTTPError:
                pass

        # 4. Fallback to abstract-only with explicit provenance warning
        if not extraction_info:
            abs_path = folder / "abstract_only.txt"
            abs_txt = (
                "PROVENANCE_TIER: abstract_only\n"
                "WARNING: Full text was not openly accessible. Do NOT guess experimental hyperparameters or ablation numbers not stated below.\n\n"
                f"Title: {meta.get('title')}\n"
                f"Year: {meta.get('year')}\n"
                f"Abstract:\n{meta.get('abstract') or 'No abstract available.'}\n"
            )
            abs_path.write_text(abs_txt, encoding="utf-8")
            extraction_info = {
                "provenance_tier": "abstract_only",
                "primary_text_path": str(abs_path),
                "tables_path": None,
                "char_count": len(abs_txt),
            }

        entry = {
            "index": idx,
            "canonical_id": cid,
            "title": meta.get("title"),
            "authors": meta.get("authors", []),
            "year": meta.get("year"),
            "venue": meta.get("venue"),
            "doi": meta.get("doi"),
            "arxiv_id": meta.get("arxiv_id"),
            "folder": str(folder),
            **extraction_info,
        }
        (folder / "metadata.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
        manifest_items.append(entry)
        logger.info(
            "[%d/%d] %s -> %s (%d chars)",
            idx,
            len(candidates),
            meta.get("title", cid)[:55],
            entry["provenance_tier"],
            entry["char_count"],
        )

    manifest = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "corpus_dir": str(out_root),
        "paper_count": len(manifest_items),
        "tier_counts": {
            tier: sum(1 for x in manifest_items if x["provenance_tier"] == tier)
            for tier in ("latex_source", "oa_pdf_fulltext", "abstract_only")
        },
        "papers": manifest_items,
    }
    manifest_path = out_root / "corpus_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Wrote corpus manifest -> %s", manifest_path)


if __name__ == "__main__":
    main()
