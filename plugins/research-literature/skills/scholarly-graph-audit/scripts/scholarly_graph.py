#!/usr/bin/env python3
r"""Open-stack scholarly graph, citation stance/retraction audit, and .bib verifier.

Combines Semantic Scholar (Academic Graph + SPECTER2 Recommendations + Citation
Contexts/Intents), OpenAlex (Works Graph + Retraction flags + OA locations),
Crossref (Retraction Watch `update-to` notices + publisher metadata), and arXiv
(API + direct `.tar.gz` LaTeX `\cite{}` sentence extraction) with local SQLite
HTTP caching and automatic multi-provider fallback.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import logging
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import tarfile
import time
from typing import Any
import urllib.parse
import xml.etree.ElementTree as ET

import dotenv
import httpx

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("scholarly_graph")

# Load ~/.env silently (never log or print secret values)
dotenv.load_dotenv(Path.home() / ".env")
dotenv.load_dotenv(Path.cwd() / ".env")

CACHE_DIR = Path.home() / ".cache" / "research-literature"
CACHE_DB_PATH = CACHE_DIR / "http_cache.sqlite3"
ARXIV_SRC_CACHE = CACHE_DIR / "arxiv_src"
DEFAULT_TTL_SECS = 7 * 24 * 3600

S2_GRAPH_BASE = "https://api.semanticscholar.org/graph/v1"
S2_REC_BASE = "https://api.semanticscholar.org/recommendations/v1"
OPENALEX_BASE = "https://api.openalex.org"
CROSSREF_BASE = "https://api.crossref.org"
ARXIV_API_URL = "https://export.arxiv.org/api/query"

S2_PAPER_FIELDS = (
    "paperId,externalIds,url,title,abstract,venue,publicationVenue,year,"
    "citationCount,influentialCitationCount,isOpenAccess,openAccessPdf,"
    "fieldsOfStudy,authors,tldr,publicationTypes"
)

PREPRINT_VENUES = {
    "arxiv",
    "arxiv.org",
    "corr",
    "biorxiv",
    "medrxiv",
    "chemrxiv",
    "ssrn",
    "research square",
    "preprints",
    "hal",
}

CONTRAST_PATTERNS = [
    r"\bhowever\b",
    r"\bunlike\b",
    r"\bcontrary to\b",
    r"\bin contrast\b",
    r"\bfails? to\b",
    r"\blimitation",
    r"\bdrawback",
    r"\bsuffer[s]? from\b",
    r"\bunderperform",
    r"\boutperform[s]? [a-z0-9\s,\[\]\\cite]*",
    r"\bdegrad",
    r"\binstabilit",
    r"\bcannot\b",
    r"\boverfit",
    r"\bquestion[s]?\b",
    r"\brefut",
    r"\bdisagrees?\b",
    r"\bbreak[s]? down\b",
    r"\bexpensive\b",
    r"\bbottleneck\b",
]
ADOPTION_PATTERNS = [
    r"\bfollowing\b",
    r"\bwe adopt\b",
    r"\bwe use\b",
    r"\bbuild[s]? (?:upon|on)\b",
    r"\bbased on\b",
    r"\bextend[s]?\b",
    r"\binspired by\b",
    r"\badapted from\b",
    r"\busing the .* of\b",
]
SUPPORT_PATTERNS = [
    r"\bconsistent with\b",
    r"\bconfirm[s]?\b",
    r"\bcorroborat",
    r"\bin agreement with\b",
    r"\bdemonstrated by\b",
    r"\bas shown in\b",
    r"\bvalidat",
    r"\bsupport[s]?\b",
]


class CachedHttpClient:
    """Polite HTTP client with SQLite response caching and backoff."""

    def __init__(self, use_cache: bool = True, ttl_secs: int = DEFAULT_TTL_SECS) -> None:
        self.use_cache = use_cache
        self.ttl_secs = ttl_secs
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(CACHE_DB_PATH))
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS http_cache (
                cache_key TEXT PRIMARY KEY,
                status_code INTEGER NOT NULL,
                body TEXT NOT NULL,
                fetched_at REAL NOT NULL
            )
            """
        )
        self.conn.commit()
        self._last_req_ts: dict[str, float] = defaultdict(float)
        self.s2_throttled = False

        mailto = os.environ.get("CROSSREF_MAILTO") or os.environ.get("USER_EMAIL") or ""
        ua = "ResearchLiteratureSkill/1.0 (Antigravity"
        if mailto:
            ua += f"; mailto:{mailto}"
        ua += ")"
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": ua},
        )

    def _make_key(self, method: str, url: str, params: dict[str, Any] | None, json_body: Any) -> str:
        raw = json.dumps(
            {
                "m": method.upper(),
                "u": url,
                "p": params or {},
                "b": json_body,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _pace(self, host: str, min_interval: float) -> None:
        elapsed = time.time() - self._last_req_ts[host]
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_req_ts[host] = time.time()

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
        min_interval: float = 0.2,
        max_retries: int = 3,
    ) -> dict[str, Any] | list[Any] | None:
        cache_key = self._make_key(method, url, params, json_body)
        now = time.time()
        if self.use_cache:
            row = self.conn.execute(
                "SELECT status_code, body, fetched_at FROM http_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
            if row and (now - row[2]) < self.ttl_secs:
                if row[0] == 404:
                    return None
                return json.loads(row[1])

        host = urllib.parse.urlparse(url).netloc
        if "semanticscholar.org" in host and self.s2_throttled:
            return None

        req_headers = dict(headers or {})
        if "semanticscholar.org" in host:
            s2_key = os.environ.get("S2_API_KEY") or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
            if s2_key:
                req_headers["x-api-key"] = s2_key
                min_interval = max(min_interval, 1.05)
            else:
                min_interval = max(min_interval, 0.45)
        elif "openalex.org" in host:
            oa_key = os.environ.get("OPENALEX_API_KEY")
            if oa_key:
                params = dict(params or {})
                params["api_key"] = oa_key

        for attempt in range(max_retries):
            self._pace(host, min_interval)
            try:
                resp = self.client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=req_headers,
                )
            except httpx.HTTPError as exc:
                logger.warning("HTTP transport error on %s (attempt %d): %s", host, attempt + 1, exc)
                time.sleep(1.5 * (attempt + 1))
                continue

            if resp.status_code == 200:
                text = resp.text
                if self.use_cache:
                    self.conn.execute(
                        "INSERT OR REPLACE INTO http_cache VALUES (?, ?, ?, ?)",
                        (cache_key, 200, text, time.time()),
                    )
                    self.conn.commit()
                return resp.json()

            if resp.status_code == 404:
                if self.use_cache:
                    self.conn.execute(
                        "INSERT OR REPLACE INTO http_cache VALUES (?, ?, ?, ?)",
                        (cache_key, 404, "{}", time.time()),
                    )
                    self.conn.commit()
                return None

            if resp.status_code in (429, 500, 502, 503, 504):
                retry_after = float(resp.headers.get("Retry-After", 2.0 * (attempt + 1)))
                wait_s = min(retry_after, 6.0)
                if "semanticscholar.org" in host and resp.status_code == 429 and attempt >= 1:
                    logger.warning(
                        "Semantic Scholar anonymous pool returned 429; activating OpenAlex + Crossref fallback for remaining uncached queries."
                    )
                    self.s2_throttled = True
                    return None
                time.sleep(wait_s)
                continue

            logger.debug("Non-200 status %d from %s: %s", resp.status_code, url, resp.text[:200])
            return None

        return None

    def request_bytes(self, url: str, min_interval: float = 1.0) -> bytes | None:
        host = urllib.parse.urlparse(url).netloc
        self._pace(host, min_interval)
        try:
            resp = self.client.get(url)
            if resp.status_code == 200:
                return resp.content
        except httpx.HTTPError as exc:
            logger.warning("Download failed from %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Identifier Normalization & Record Merging
# ---------------------------------------------------------------------------

ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}|[a-z\-]+/\d{7})(?:v\d+)?$", re.IGNORECASE)
DOI_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)?(10\.\d{4,9}/[-._;()/:A-Z0-9]+)$", re.IGNORECASE)
OPENALEX_RE = re.compile(r"^(?:https?://openalex\.org/)?(W\d+)$", re.IGNORECASE)


def classify_identifier(raw: str) -> tuple[str, str]:
    s = raw.strip()
    m_arxiv = ARXIV_RE.match(s)
    if m_arxiv:
        return ("arxiv", m_arxiv.group(1))
    if "arxiv.org/abs/" in s or "arxiv.org/pdf/" in s:
        tail = s.split("/abs/")[-1].split("/pdf/")[-1].replace(".pdf", "")
        m2 = ARXIV_RE.match(tail)
        if m2:
            return ("arxiv", m2.group(1))
    m_doi = DOI_RE.match(s)
    if m_doi:
        doi = m_doi.group(1)
        if doi.lower().startswith("10.48550/arxiv."):
            return ("arxiv", doi.split("10.48550/arXiv.")[-1].split("10.48550/arxiv.")[-1])
        return ("doi", doi)
    m_oa = OPENALEX_RE.match(s)
    if m_oa:
        return ("openalex", m_oa.group(1).upper())
    if re.fullmatch(r"[0-9a-f]{40}", s.lower()):
        return ("s2", s.lower())
    if s.upper().startswith("PMID:"):
        return ("pmid", s.split(":", 1)[1].strip())
    return ("query", s)


def is_preprint_venue(venue: str | None) -> bool:
    if not venue:
        return True
    v = venue.strip().lower()
    if not v:
        return True
    return any(p in v for p in PREPRINT_VENUES)


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def title_similarity(t1: str, t2: str) -> float:
    w1 = set(normalize_title(t1).split())
    w2 = set(normalize_title(t2).split())
    if not w1 or not w2:
        return 0.0
    inter = len(w1 & w2)
    union = len(w1 | w2)
    return inter / union if union else 0.0


def canonical_key(paper: dict[str, Any]) -> str:
    if paper.get("doi") and not str(paper["doi"]).lower().startswith("10.48550/arxiv."):
        return f"doi:{paper['doi'].lower()}"
    if paper.get("arxiv_id"):
        return f"arxiv:{paper['arxiv_id'].lower()}"
    if paper.get("openalex_id"):
        return f"oa:{paper['openalex_id'].upper()}"
    if paper.get("s2_id"):
        return f"s2:{paper['s2_id']}"
    return f"title:{normalize_title(paper.get('title', ''))[:80]}"


def from_s2_paper(data: dict[str, Any]) -> dict[str, Any]:
    ext = data.get("externalIds") or {}
    doi = ext.get("DOI")
    arxiv_id = ext.get("ArXiv")
    pub_venue = (data.get("publicationVenue") or {}).get("name") or data.get("venue") or ""
    oa_pdf = (data.get("openAccessPdf") or {}).get("url")
    if not oa_pdf and arxiv_id:
        oa_pdf = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    tldr = (data.get("tldr") or {}).get("text")
    authors = [a.get("name", "") for a in (data.get("authors") or []) if a.get("name")]
    return {
        "title": (data.get("title") or "").strip(),
        "authors": authors,
        "year": data.get("year"),
        "venue": pub_venue,
        "is_published_venue": not is_preprint_venue(pub_venue),
        "doi": doi,
        "arxiv_id": arxiv_id,
        "s2_id": data.get("paperId"),
        "openalex_id": None,
        "pmid": ext.get("PubMed"),
        "citation_count": data.get("citationCount") or 0,
        "influential_citation_count": data.get("influentialCitationCount") or 0,
        "is_retracted": False,
        "tldr": tldr,
        "abstract": data.get("abstract"),
        "oa_pdf_url": oa_pdf,
        "url": data.get("url") or (f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None)),
    }


def reconstruct_openalex_abstract(inv_idx: dict[str, list[int]] | None) -> str | None:
    if not inv_idx:
        return None
    pos_map: dict[int, str] = {}
    for word, positions in inv_idx.items():
        for p in positions:
            pos_map[p] = word
    if not pos_map:
        return None
    return " ".join(pos_map[i] for i in sorted(pos_map))


def from_openalex_work(work: dict[str, Any]) -> dict[str, Any]:
    oa_id = (work.get("id") or "").split("/")[-1] or None
    raw_doi = work.get("doi") or ""
    doi = raw_doi.replace("https://doi.org/", "").strip() or None
    arxiv_id = None
    if doi and doi.lower().startswith("10.48550/arxiv."):
        arxiv_id = re.sub(r"^10\.48550/arxiv\.", "", doi, flags=re.IGNORECASE)
        doi = None

    # Check locations for published venue AND arXiv ID
    best_venue = ""
    for loc in [work.get("primary_location")] + (work.get("locations") or []):
        if not loc:
            continue
        src = loc.get("source") or {}
        disp = (src.get("display_name") or "").strip()
        landing = loc.get("landing_page_url") or ""
        if "arxiv.org/abs/" in landing and not arxiv_id:
            cand = landing.split("arxiv.org/abs/")[-1].split("v")[0].strip("/")
            if ARXIV_RE.match(cand):
                arxiv_id = cand
        if disp and not is_preprint_venue(disp) and not best_venue:
            best_venue = disp
    if not best_venue:
        src = ((work.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        best_venue = src

    ids = work.get("ids") or {}
    pmid_url = ids.get("pmid") or ""
    pmid = pmid_url.split("/")[-1] if pmid_url else None

    authors = [
        ((a.get("author") or {}).get("display_name") or "").strip()
        for a in (work.get("authorships") or [])
        if (a.get("author") or {}).get("display_name")
    ]
    oa_url = (work.get("open_access") or {}).get("oa_url")
    if not oa_url and arxiv_id:
        oa_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    return {
        "title": (work.get("title") or work.get("display_name") or "").strip(),
        "authors": authors,
        "year": work.get("publication_year"),
        "venue": best_venue or ("arXiv" if arxiv_id else ""),
        "is_published_venue": bool(best_venue and not is_preprint_venue(best_venue)),
        "doi": doi,
        "arxiv_id": arxiv_id,
        "s2_id": None,
        "openalex_id": oa_id,
        "pmid": pmid,
        "citation_count": work.get("cited_by_count") or 0,
        "influential_citation_count": 0,
        "is_retracted": bool(work.get("is_retracted")),
        "tldr": None,
        "abstract": reconstruct_openalex_abstract(work.get("abstract_inverted_index")),
        "oa_pdf_url": oa_url,
        "referenced_works": [(r or "").split("/")[-1] for r in (work.get("referenced_works") or []) if r],
        "related_works": [(r or "").split("/")[-1] for r in (work.get("related_works") or []) if r],
        "url": f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else work.get("id")),
    }


def merge_paper_records(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for k in ("s2_id", "openalex_id", "doi", "arxiv_id", "pmid", "tldr", "abstract", "oa_pdf_url", "url"):
        if not merged.get(k) and extra.get(k):
            merged[k] = extra[k]
    if not merged.get("authors") and extra.get("authors"):
        merged["authors"] = extra["authors"]
    if extra.get("is_published_venue") and not merged.get("is_published_venue"):
        merged["venue"] = extra["venue"]
        merged["is_published_venue"] = True
        if extra.get("year"):
            merged["year"] = extra["year"]
    elif not merged.get("venue") and extra.get("venue"):
        merged["venue"] = extra["venue"]
    if not merged.get("year") and extra.get("year"):
        merged["year"] = extra["year"]
    merged["citation_count"] = max(merged.get("citation_count") or 0, extra.get("citation_count") or 0)
    merged["influential_citation_count"] = max(
        merged.get("influential_citation_count") or 0,
        extra.get("influential_citation_count") or 0,
    )
    merged["is_retracted"] = bool(merged.get("is_retracted") or extra.get("is_retracted"))
    for list_key in ("referenced_works", "related_works"):
        if extra.get(list_key) and not merged.get(list_key):
            merged[list_key] = extra[list_key]
    return merged


# ---------------------------------------------------------------------------
# Multi-Provider Resolution & Crossref Integrity Checks
# ---------------------------------------------------------------------------

def fetch_arxiv_metadata(http: CachedHttpClient, arxiv_id: str) -> dict[str, Any] | None:
    raw = http.request_bytes(f"{ARXIV_API_URL}?id_list={urllib.parse.quote(arxiv_id)}", min_interval=1.0)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        entry = root.find("atom:entry", ns)
        if entry is None:
            return None
        title_el = entry.find("atom:title", ns)
        title = re.sub(r"\s+", " ", (title_el.text if title_el is not None and title_el.text else "")).strip()
        if not title or title.lower() == "error":
            return None
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        year = int(published_el.text[:4]) if published_el is not None and published_el.text else None
        authors = [
            (a.find("atom:name", ns).text or "").strip()
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ]
        doi_el = entry.find("arxiv:doi", ns)
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None
        jref_el = entry.find("arxiv:journal_ref", ns)
        jref = jref_el.text.strip() if jref_el is not None and jref_el.text else ""
        return {
            "title": title,
            "authors": authors,
            "year": year,
            "venue": jref or "arXiv",
            "is_published_venue": bool(jref and not is_preprint_venue(jref)),
            "doi": doi,
            "arxiv_id": arxiv_id,
            "s2_id": None,
            "openalex_id": None,
            "pmid": None,
            "citation_count": 0,
            "influential_citation_count": 0,
            "is_retracted": False,
            "tldr": None,
            "abstract": re.sub(r"\s+", " ", summary_el.text).strip() if summary_el is not None and summary_el.text else None,
            "oa_pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        }
    except ET.ParseError:
        return None


def check_crossref_integrity(http: CachedHttpClient, doi: str) -> dict[str, Any]:
    """Queries Crossref REST API (including Retraction Watch integration) for a DOI."""
    encoded = urllib.parse.quote(doi, safe="")
    res = http.request_json("GET", f"{CROSSREF_BASE}/works/{encoded}", min_interval=0.15)
    if not res or not isinstance(res, dict) or "message" not in res:
        return {"found": False, "updates": [], "is_retracted": False, "has_correction": False}

    msg = res["message"]
    updates_raw = (msg.get("update-to") or []) + (msg.get("updated-by") or [])
    updates = []
    is_retracted = False
    has_correction = False
    for u in updates_raw:
        utype = (u.get("type") or "").lower()
        label = u.get("label") or utype
        source = u.get("source") or "publisher"
        udoi = u.get("DOI")
        if any(k in utype for k in ("retract", "withdrawal", "removed")):
            is_retracted = True
        elif any(k in utype for k in ("concern", "correction", "erratum", "corrigendum")):
            has_correction = True
        updates.append({"type": utype, "label": label, "source": source, "doi": udoi})

    titles = msg.get("title") or []
    container = (msg.get("container-title") or [""])[0]
    pub_date = (
        (msg.get("published-print") or msg.get("published-online") or msg.get("issued") or {})
        .get("date-parts", [[None]])[0][0]
    )
    authors = [
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in (msg.get("author") or [])
        if a.get("family") or a.get("given")
    ]
    return {
        "found": True,
        "doi": msg.get("DOI") or doi,
        "title": titles[0] if titles else "",
        "authors": authors,
        "venue": container,
        "year": pub_date,
        "type": msg.get("type"),
        "citation_count": msg.get("is-referenced-by-count") or 0,
        "is_retracted": is_retracted,
        "has_correction": has_correction,
        "updates": updates,
    }


def resolve_paper(http: CachedHttpClient, raw_input: str) -> dict[str, Any] | None:
    kind, val = classify_identifier(raw_input)
    record: dict[str, Any] | None = None

    # 1. Try Semantic Scholar lookup
    s2_lookup_id: str | None = None
    if kind == "arxiv":
        s2_lookup_id = f"ARXIV:{val}"
    elif kind == "doi":
        s2_lookup_id = f"DOI:{val}"
    elif kind == "s2":
        s2_lookup_id = val
    elif kind == "pmid":
        s2_lookup_id = f"PMID:{val}"

    if s2_lookup_id:
        s2_data = http.request_json(
            "GET",
            f"{S2_GRAPH_BASE}/paper/{urllib.parse.quote(s2_lookup_id, safe=':')}",
            params={"fields": S2_PAPER_FIELDS},
        )
        if isinstance(s2_data, dict) and s2_data.get("paperId"):
            record = from_s2_paper(s2_data)
    elif kind == "query":
        s2_search = http.request_json(
            "GET",
            f"{S2_GRAPH_BASE}/paper/search",
            params={"query": val, "limit": 5, "fields": S2_PAPER_FIELDS},
        )
        if isinstance(s2_search, dict) and s2_search.get("data"):
            best = max(
                s2_search["data"],
                key=lambda item: (
                    title_similarity(val, item.get("title") or ""),
                    math.log1p(item.get("citationCount") or 0) * 0.05,
                ),
            )
            if title_similarity(val, best.get("title") or "") >= 0.45 or len(val.split()) <= 5:
                record = from_s2_paper(best)

    # 2. Enrich / Resolve via OpenAlex
    oa_work: dict[str, Any] | None = None
    if kind == "openalex":
        oa_work = http.request_json("GET", f"{OPENALEX_BASE}/works/{val}")  # type: ignore[assignment]
    elif (record and record.get("doi")) or kind == "doi":
        doi_q = (record.get("doi") if record else None) or val
        oa_work = http.request_json(
            "GET",
            f"{OPENALEX_BASE}/works/https://doi.org/{urllib.parse.quote(doi_q, safe='/')}",
        )  # type: ignore[assignment]
    elif (record and record.get("arxiv_id")) or kind == "arxiv":
        ax = (record.get("arxiv_id") if record else None) or val
        oa_work = http.request_json(
            "GET",
            f"{OPENALEX_BASE}/works/https://doi.org/10.48550/arXiv.{ax}",
        )  # type: ignore[assignment]
        if not oa_work and record and record.get("title"):
            oa_search = http.request_json(
                "GET",
                f"{OPENALEX_BASE}/works",
                params={"search": record["title"], "per-page": 5},
            )
            if isinstance(oa_search, dict) and oa_search.get("results"):
                cand = oa_search["results"][0]
                if title_similarity(record["title"], cand.get("title") or "") >= 0.8:
                    oa_work = cand

    if not oa_work and (kind == "query" or record is not None):
        q_title = record["title"] if record and record.get("title") else val
        oa_search = http.request_json(
            "GET",
            f"{OPENALEX_BASE}/works",
            params={"search": q_title, "per-page": 5},
        )
        if isinstance(oa_search, dict) and oa_search.get("results"):
            best_oa = max(
                oa_search["results"],
                key=lambda w: (
                    title_similarity(q_title, w.get("title") or ""),
                    1 if not is_preprint_venue(((w.get("primary_location") or {}).get("source") or {}).get("display_name")) else 0,
                ),
            )
            if title_similarity(q_title, best_oa.get("title") or "") >= 0.55 or (kind == "query" and record is None):
                oa_work = best_oa

    if isinstance(oa_work, dict) and oa_work.get("id"):
        oa_rec = from_openalex_work(oa_work)
        record = merge_paper_records(record, oa_rec) if record else oa_rec
        # Check if OpenAlex also knows a separate published version of the same title!
        if record and not record.get("is_published_venue") and record.get("title"):
            oa_dup = http.request_json(
                "GET",
                f"{OPENALEX_BASE}/works",
                params={"search": record["title"], "per-page": 5},
            )
            if isinstance(oa_dup, dict):
                for item in oa_dup.get("results") or []:
                    cand_rec = from_openalex_work(item)
                    if (
                        cand_rec.get("is_published_venue")
                        and title_similarity(record["title"], cand_rec["title"]) >= 0.85
                    ):
                        record = merge_paper_records(record, cand_rec)
                        break

    # 3. Fallback to arXiv API if needed
    if kind == "arxiv" and record is None:
        record = fetch_arxiv_metadata(http, val)

    # 4. If we resolved via OpenAlex first and still lack S2 metadata (TLDR / s2_id), fetch S2 once
    if record and not record.get("s2_id") and not http.s2_throttled:
        probe = (
            f"DOI:{record['doi']}"
            if record.get("doi")
            else (f"ARXIV:{record['arxiv_id']}" if record.get("arxiv_id") else None)
        )
        if probe:
            s2_extra = http.request_json(
                "GET",
                f"{S2_GRAPH_BASE}/paper/{urllib.parse.quote(probe, safe=':')}",
                params={"fields": S2_PAPER_FIELDS},
            )
            if isinstance(s2_extra, dict) and s2_extra.get("paperId"):
                record = merge_paper_records(record, from_s2_paper(s2_extra))

    if record:
        record["canonical_id"] = canonical_key(record)
    return record


# ---------------------------------------------------------------------------
# Subcommand 2: Seed-Based Lineage Graph (ResearchRabbit + Litmaps Engine)
# ---------------------------------------------------------------------------

def batch_fetch_openalex(http: CachedHttpClient, oa_ids: list[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    clean = [i.split("/")[-1] for i in oa_ids if i]
    for idx in range(0, len(clean), 45):
        chunk = clean[idx : idx + 45]
        res = http.request_json(
            "GET",
            f"{OPENALEX_BASE}/works",
            params={"filter": f"openalex:{'|'.join(chunk)}", "per-page": len(chunk)},
        )
        if isinstance(res, dict):
            for w in res.get("results") or []:
                rec = from_openalex_work(w)
                if rec.get("openalex_id"):
                    out[rec["openalex_id"]] = rec
    return out


def build_lineage_graph(
    http: CachedHttpClient,
    seed_inputs: list[str],
    negative_inputs: list[str],
    max_per_group: int = 15,
) -> dict[str, Any]:
    seeds: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for raw in seed_inputs:
        rec = resolve_paper(http, raw)
        if rec and rec["canonical_id"] not in seen_keys:
            rec["role"] = "seed"
            seeds.append(rec)
            seen_keys.add(rec["canonical_id"])

    if not seeds:
        raise RuntimeError("Could not resolve any seed papers. Check the provided IDs or titles.")

    negatives: list[dict[str, Any]] = []
    for raw in negative_inputs:
        rec = resolve_paper(http, raw)
        if rec:
            negatives.append(rec)

    nodes_by_key: dict[str, dict[str, Any]] = {s["canonical_id"]: s for s in seeds}
    edges: list[dict[str, Any]] = []

    # 1. Co-citation Ancestors (Foundational Roots cited by seeds)
    oa_ref_counts: Counter[str] = Counter()
    oa_ref_sources: defaultdict[str, list[str]] = defaultdict(list)
    s2_ancestor_Pool: dict[str, dict[str, Any]] = {}
    s2_ref_sources: defaultdict[str, list[str]] = defaultdict(list)
    s2_ref_influential: Counter[str] = Counter()

    for seed in seeds:
        sk = seed["canonical_id"]
        for ref_oa in seed.get("referenced_works") or []:
            oa_ref_counts[ref_oa] += 1
            oa_ref_sources[ref_oa].append(sk)

        if seed.get("s2_id") and not http.s2_throttled:
            ref_resp = http.request_json(
                "GET",
                f"{S2_GRAPH_BASE}/paper/{seed['s2_id']}/references",
                params={
                    "fields": "isInfluential,intents,citedPaper.paperId,citedPaper.externalIds,citedPaper.title,citedPaper.year,citedPaper.venue,citedPaper.citationCount,citedPaper.influentialCitationCount,citedPaper.authors,citedPaper.openAccessPdf",
                    "limit": 150,
                },
            )
            if isinstance(ref_resp, dict):
                for item in ref_resp.get("data") or []:
                    cp = item.get("citedPaper") or {}
                    if not cp.get("paperId") or not cp.get("title"):
                        continue
                    rec = from_s2_paper(cp)
                    ck = canonical_key(rec)
                    if ck in seen_keys:
                        edges.append({"source": sk, "target": ck, "type": "cites", "influential": bool(item.get("isInfluential"))})
                        continue
                    s2_ancestor_Pool[ck] = merge_paper_records(s2_ancestor_Pool[ck], rec) if ck in s2_ancestor_Pool else rec
                    if sk not in s2_ref_sources[ck]:
                        s2_ref_sources[ck].append(sk)
                    if item.get("isInfluential"):
                        s2_ref_influential[ck] += 1

    # Fetch top OpenAlex co-cited candidates if needed
    top_oa_refs = [oa_id for oa_id, _ in oa_ref_counts.most_common(60)]
    oa_fetched = batch_fetch_openalex(http, top_oa_refs) if top_oa_refs else {}
    for oa_id, rec in oa_fetched.items():
        ck = canonical_key(rec)
        if ck in seen_keys:
            for src_sk in oa_ref_sources[oa_id]:
                edges.append({"source": src_sk, "target": ck, "type": "cites", "influential": False})
            continue
        s2_ancestor_Pool[ck] = merge_paper_records(s2_ancestor_Pool[ck], rec) if ck in s2_ancestor_Pool else rec
        for src_sk in oa_ref_sources[oa_id]:
            if src_sk not in s2_ref_sources[ck]:
                s2_ref_sources[ck].append(src_sk)

    scored_ancestors: list[tuple[float, str, dict[str, Any]]] = []
    for ck, rec in s2_ancestor_Pool.items():
        seed_cnt = len(s2_ref_sources[ck])
        inf_cnt = s2_ref_influential[ck]
        glob_cit = rec.get("citation_count") or 0
        # Specificity-weighted co-citation score
        score = (seed_cnt ** 2.2) * (1.0 + 0.45 * inf_cnt) / math.log(12.0 + glob_cit)
        rec["seed_overlap"] = seed_cnt
        rec["lineage_score"] = round(score, 4)
        scored_ancestors.append((score, ck, rec))

    scored_ancestors.sort(key=lambda x: (x[2]["seed_overlap"] >= 2, x[0]), reverse=True)
    ancestors: list[dict[str, Any]] = []
    for _, ck, rec in scored_ancestors[:max_per_group]:
        rec["canonical_id"] = ck
        rec["role"] = "ancestor"
        nodes_by_key[ck] = rec
        ancestors.append(rec)
        for src_sk in s2_ref_sources[ck]:
            edges.append(
                {
                    "source": src_sk,
                    "target": ck,
                    "type": "cites",
                    "influential": s2_ref_influential[ck] > 0,
                }
            )

    # 2. Active Frontier (Papers citing multiple seeds / influential descendants)
    frontier_pool: dict[str, dict[str, Any]] = {}
    frontier_targets: defaultdict[str, list[str]] = defaultdict(list)
    frontier_influential: Counter[str] = Counter()

    oa_seed_ids = [s["openalex_id"] for s in seeds if s.get("openalex_id")]
    if oa_seed_ids:
        # Recent + Highly-cited works citing any seed
        for sort_expr in ("cited_by_count:desc", "publication_date:desc"):
            cit_res = http.request_json(
                "GET",
                f"{OPENALEX_BASE}/works",
                params={
                    "filter": f"cites:{'|'.join(oa_seed_ids)}",
                    "sort": sort_expr,
                    "per-page": 60,
                },
            )
            if isinstance(cit_res, dict):
                for w in cit_res.get("results") or []:
                    rec = from_openalex_work(w)
                    ck = canonical_key(rec)
                    if ck in nodes_by_key:
                        continue
                    refs_set = set(rec.get("referenced_works") or [])
                    matched_seeds = [s["canonical_id"] for s in seeds if s.get("openalex_id") in refs_set]
                    if not matched_seeds and len(seeds) == 1:
                        matched_seeds = [seeds[0]["canonical_id"]]
                    if matched_seeds:
                        frontier_pool[ck] = merge_paper_records(frontier_pool[ck], rec) if ck in frontier_pool else rec
                        for msk in matched_seeds:
                            if msk not in frontier_targets[ck]:
                                frontier_targets[ck].append(msk)

    for seed in seeds:
        sk = seed["canonical_id"]
        if seed.get("s2_id") and not http.s2_throttled:
            cit_resp = http.request_json(
                "GET",
                f"{S2_GRAPH_BASE}/paper/{seed['s2_id']}/citations",
                params={
                    "fields": "isInfluential,intents,citingPaper.paperId,citingPaper.externalIds,citingPaper.title,citingPaper.year,citingPaper.venue,citingPaper.citationCount,citingPaper.influentialCitationCount,citingPaper.authors,citingPaper.openAccessPdf",
                    "limit": 80,
                },
            )
            if isinstance(cit_resp, dict):
                for item in cit_resp.get("data") or []:
                    cp = item.get("citingPaper") or {}
                    if not cp.get("paperId") or not cp.get("title"):
                        continue
                    rec = from_s2_paper(cp)
                    ck = canonical_key(rec)
                    if ck in seen_keys:
                        continue
                    frontier_pool[ck] = merge_paper_records(frontier_pool[ck], rec) if ck in frontier_pool else rec
                    if sk not in frontier_targets[ck]:
                        frontier_targets[ck].append(sk)
                    if item.get("isInfluential"):
                        frontier_influential[ck] += 1

    current_year = 2026
    scored_frontier: list[tuple[float, str, dict[str, Any]]] = []
    for ck, rec in frontier_pool.items():
        if ck in nodes_by_key:
            continue
        scnt = len(frontier_targets[ck])
        yr = rec.get("year") or 2020
        recency = 1.0 / (1.0 + max(0, current_year - yr) * 0.25)
        cit = rec.get("citation_count") or 0
        score = (scnt ** 2.0) * (1.0 + 0.5 * frontier_influential[ck]) * (0.6 * math.log1p(cit + 1) + 1.8 * recency)
        rec["seed_overlap"] = scnt
        rec["lineage_score"] = round(score, 4)
        scored_frontier.append((score, ck, rec))

    scored_frontier.sort(key=lambda x: (x[2]["seed_overlap"] >= 2, x[0]), reverse=True)
    frontier: list[dict[str, Any]] = []
    for _, ck, rec in scored_frontier[:max_per_group]:
        rec["canonical_id"] = ck
        rec["role"] = "frontier"
        nodes_by_key[ck] = rec
        frontier.append(rec)
        for tgt_sk in frontier_targets[ck]:
            edges.append(
                {
                    "source": ck,
                    "target": tgt_sk,
                    "type": "cites",
                    "influential": frontier_influential[ck] > 0,
                }
            )

    # 3. Semantic Siblings (SPECTER2 Positive/Negative Seed Recommendations + OpenAlex Related)
    siblings: list[dict[str, Any]] = []
    pos_s2 = [s["s2_id"] for s in seeds if s.get("s2_id")]
    neg_s2 = [n["s2_id"] for n in negatives if n.get("s2_id")]
    if pos_s2 and not http.s2_throttled:
        rec_body: dict[str, Any] = {"positivePaperIds": pos_s2}
        if neg_s2:
            rec_body["negativePaperIds"] = neg_s2
        rec_resp = http.request_json(
            "POST",
            f"{S2_REC_BASE}/papers/",
            params={"fields": S2_PAPER_FIELDS, "limit": max_per_group * 2},
            json_body=rec_body,
        )
        if isinstance(rec_resp, dict):
            for idx, item in enumerate(rec_resp.get("recommendedPapers") or []):
                rec = from_s2_paper(item)
                ck = canonical_key(rec)
                if ck in nodes_by_key:
                    continue
                rec["canonical_id"] = ck
                rec["role"] = "semantic_sibling"
                rec["seed_overlap"] = 0
                rec["lineage_score"] = round(1.0 / (1.0 + idx * 0.15), 4)
                nodes_by_key[ck] = rec
                siblings.append(rec)
                edges.append(
                    {
                        "source": seeds[0]["canonical_id"],
                        "target": ck,
                        "type": "specter2_similar",
                        "influential": False,
                    }
                )
                if len(siblings) >= max_per_group:
                    break

    if len(siblings) < max(4, max_per_group // 2):
        rel_counts: Counter[str] = Counter()
        for s in seeds:
            for rw in s.get("related_works") or []:
                rel_counts[rw] += 1
        rel_fetched = batch_fetch_openalex(http, [r for r, _ in rel_counts.most_common(20)])
        for oa_id, rec in rel_fetched.items():
            ck = canonical_key(rec)
            if ck in nodes_by_key:
                continue
            rec["canonical_id"] = ck
            rec["role"] = "semantic_sibling"
            rec["seed_overlap"] = rel_counts[oa_id]
            rec["lineage_score"] = round(0.5 * rel_counts[oa_id], 4)
            nodes_by_key[ck] = rec
            siblings.append(rec)
            edges.append({"source": seeds[0]["canonical_id"], "target": ck, "type": "specter2_similar", "influential": False})
            if len(siblings) >= max_per_group:
                break

    # 4. Recurring Key Authors across the Graph
    author_papers: defaultdict[str, list[str]] = defaultdict(list)
    for ck, node in nodes_by_key.items():
        # Strip transient referenced_works lists to keep output compact
        node.pop("referenced_works", None)
        node.pop("related_works", None)
        for a in (node.get("authors") or [])[:8]:
            author_papers[a].append(node.get("title") or ck)

    key_authors = [
        {"author": name, "paper_count_in_subgraph": len(titles), "sample_papers": titles[:4]}
        for name, titles in sorted(author_papers.items(), key=lambda kv: len(kv[1]), reverse=True)
        if len(titles) >= 2
    ][:15]

    # Deduplicate edges
    dedup_edges = list({(e["source"], e["target"], e["type"]): e for e in edges}.values())

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {
            "seed_count": len(seeds),
            "ancestor_count": len(ancestors),
            "frontier_count": len(frontier),
            "semantic_sibling_count": len(siblings),
            "total_nodes": len(nodes_by_key),
            "total_edges": len(dedup_edges),
            "s2_throttled_fallback_used": http.s2_throttled,
        },
        "seeds": seeds,
        "foundational_ancestors": ancestors,
        "active_frontier": frontier,
        "semantic_siblings": siblings,
        "key_authors": key_authors,
        "nodes": list(nodes_by_key.values()),
        "edges": dedup_edges,
    }


# ---------------------------------------------------------------------------
# Subcommand 3: Scite-Grade Smart Citation & Retraction Audit
# ---------------------------------------------------------------------------

def classify_context_cues(sentence: str) -> list[str]:
    low = sentence.lower()
    cues: list[str] = []
    if any(re.search(p, low) for p in CONTRAST_PATTERNS):
        cues.append("contrasting_or_limitation_cue")
    if any(re.search(p, low) for p in ADOPTION_PATTERNS):
        cues.append("method_adoption_or_extension_cue")
    if any(re.search(p, low) for p in SUPPORT_PATTERNS):
        cues.append("supporting_or_consistent_cue")
    if not cues:
        cues.append("mentioning_cue")
    return cues


def audit_paper_citations(http: CachedHttpClient, target_input: str, max_citing: int = 80) -> dict[str, Any]:
    target = resolve_paper(http, target_input)
    if not target:
        raise RuntimeError(f"Could not resolve target paper: {target_input}")

    crossref_status = (
        check_crossref_integrity(http, target["doi"])
        if target.get("doi")
        else {"found": False, "updates": [], "is_retracted": False, "has_correction": False}
    )

    is_retracted = bool(target.get("is_retracted") or crossref_status.get("is_retracted"))
    has_correction = bool(crossref_status.get("has_correction"))

    intent_counts: Counter[str] = Counter()
    cue_counts: Counter[str] = Counter()
    contextualized_citations: list[dict[str, Any]] = []
    influential_citers: list[dict[str, Any]] = []

    if target.get("s2_id") and not http.s2_throttled:
        resp = http.request_json(
            "GET",
            f"{S2_GRAPH_BASE}/paper/{target['s2_id']}/citations",
            params={
                "fields": "contexts,intents,isInfluential,citingPaper.paperId,citingPaper.externalIds,citingPaper.title,citingPaper.year,citingPaper.venue,citingPaper.citationCount,citingPaper.authors,citingPaper.openAccessPdf",
                "limit": min(max_citing, 200),
            },
        )
        if isinstance(resp, dict):
            for row in resp.get("data") or []:
                cp = row.get("citingPaper") or {}
                if not cp.get("title"):
                    continue
                rec = from_s2_paper(cp)
                contexts = [c.strip() for c in (row.get("contexts") or []) if c and c.strip()]
                intents = [i.lower() for i in (row.get("intents") or []) if i]
                is_inf = bool(row.get("isInfluential"))
                for it in intents:
                    intent_counts[it] += 1

                entry_cues: set[str] = set()
                annotated_contexts = []
                for ctx in contexts:
                    cues = classify_context_cues(ctx)
                    for c in cues:
                        cue_counts[c] += 1
                        entry_cues.add(c)
                    annotated_contexts.append({"text": ctx, "lexical_cues": cues})

                item_summary = {
                    "citing_title": rec["title"],
                    "citing_authors": rec["authors"][:5],
                    "year": rec["year"],
                    "venue": rec["venue"],
                    "doi": rec["doi"],
                    "arxiv_id": rec["arxiv_id"],
                    "citation_count": rec["citation_count"],
                    "is_influential": is_inf,
                    "s2_intents": intents,
                    "lexical_cues": sorted(entry_cues),
                    "contexts": annotated_contexts,
                }
                if contexts:
                    contextualized_citations.append(item_summary)
                if is_inf:
                    influential_citers.append(item_summary)

    # Fallback/Supplement: if S2 had 0 citing records and OpenAlex has citing works, list top OpenAlex citers
    # AND automatically sample top arXiv citers' LaTeX sources for verbatim \cite{} sentences!
    openalex_top_citers: list[dict[str, Any]] = []
    if not contextualized_citations and target.get("openalex_id"):
        oa_cit = http.request_json(
            "GET",
            f"{OPENALEX_BASE}/works",
            params={
                "filter": f"cites:{target['openalex_id']}",
                "sort": "cited_by_count:desc",
                "per-page": min(max_citing, 25),
            },
        )
        if isinstance(oa_cit, dict):
            for w in oa_cit.get("results") or []:
                r = from_openalex_work(w)
                openalex_top_citers.append(
                    {
                        "citing_title": r["title"],
                        "citing_authors": r["authors"][:5],
                        "year": r["year"],
                        "venue": r["venue"],
                        "doi": r["doi"],
                        "arxiv_id": r["arxiv_id"],
                        "citation_count": r["citation_count"],
                    }
                )

        # Extract verbatim LaTeX \cite{} sentences from up to 4 top arXiv citers when S2 contexts are unavailable
        first_surname = (
            target["authors"][0].split()[-1].lower()
            if target.get("authors")
            else ""
        )
        title_probe = " ".join(normalize_title(target.get("title") or "").split()[:3])
        sampled_tex = 0
        for citer in openalex_top_citers:
            c_ax = citer.get("arxiv_id")
            if not c_ax or sampled_tex >= 4:
                continue
            sampled_tex += 1
            try:
                tex_res = extract_tex_citations(http, c_ax, None, first_surname or title_probe)
                matched_sents = tex_res.get("contexts") or []
                if not matched_sents and title_probe and first_surname:
                    tex_res = extract_tex_citations(http, c_ax, None, title_probe)
                    matched_sents = tex_res.get("contexts") or []
                if matched_sents:
                    entry_cues_fb: set[str] = set()
                    ann_ctx_fb = []
                    for ms in matched_sents[:6]:
                        for c in ms["lexical_cues"]:
                            cue_counts[c] += 1
                            entry_cues_fb.add(c)
                        ann_ctx_fb.append(
                            {
                                "text": f"[{ms['section']}] {ms['sentence']}",
                                "lexical_cues": ms["lexical_cues"],
                            }
                        )
                    contextualized_citations.append(
                        {
                            "citing_title": citer["citing_title"],
                            "citing_authors": citer["citing_authors"],
                            "year": citer["year"],
                            "venue": citer["venue"],
                            "doi": citer["doi"],
                            "arxiv_id": c_ax,
                            "citation_count": citer["citation_count"],
                            "is_influential": True,
                            "s2_intents": ["arxiv_tex_source_extracted"],
                            "lexical_cues": sorted(entry_cues_fb),
                            "contexts": ann_ctx_fb,
                        }
                    )
            except Exception as exc:  # noqa: BLE001
                logger.debug("LaTeX citer fallback skipped for %s: %s", c_ax, exc)

    contrasting = [
        c for c in contextualized_citations if "contrasting_or_limitation_cue" in c["lexical_cues"]
    ]
    adopting = [
        c
        for c in contextualized_citations
        if "method_adoption_or_extension_cue" in c["lexical_cues"] or "methodology" in c["s2_intents"]
    ]
    supporting = [
        c
        for c in contextualized_citations
        if "supporting_or_consistent_cue" in c["lexical_cues"] or "result" in c["s2_intents"]
    ]

    target.pop("referenced_works", None)
    target.pop("related_works", None)

    return {
        "target_paper": target,
        "integrity_status": {
            "is_retracted": is_retracted,
            "has_correction_or_concern": has_correction,
            "published_venue_found": target.get("is_published_venue"),
            "crossref_updates": crossref_status.get("updates", []),
        },
        "citation_tally": {
            "global_citations": target.get("citation_count", 0),
            "influential_citations": target.get("influential_citation_count", 0),
            "sampled_with_verbatim_contexts": len(contextualized_citations),
            "s2_intent_counts": dict(intent_counts),
            "lexical_cue_counts": dict(cue_counts),
        },
        "contrasting_or_limitation_contexts": contrasting[:20],
        "method_adoption_contexts": adopting[:20],
        "supporting_or_result_contexts": supporting[:20],
        "influential_citers": influential_citers[:20],
        "openalex_top_citers_fallback": openalex_top_citers,
    }


# ---------------------------------------------------------------------------
# Subcommand 4: Direct arXiv LaTeX `\cite{}` Context Extractor
# ---------------------------------------------------------------------------

def safe_extract_tar_bytes(raw_bytes: bytes, dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    try:
        with tarfile.open(fileobj=io.BytesIO(raw_bytes), mode="r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                rel = Path(member.name)
                if rel.is_absolute() or ".." in rel.parts:
                    continue
                if rel.suffix.lower() in {".tex", ".bib", ".bbl"}:
                    out_path = (dest_dir / rel).resolve()
                    if not str(out_path).startswith(str(dest_dir.resolve())):
                        continue
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    fobj = tf.extractfile(member)
                    if fobj:
                        out_path.write_bytes(fobj.read())
                        extracted.append(out_path)
    except tarfile.TarError:
        # Single gzipped .tex file fallback
        import gzip

        try:
            content = gzip.decompress(raw_bytes)
            single = dest_dir / "main.tex"
            single.write_bytes(content)
            extracted.append(single)
        except OSError:
            pass
    return extracted


def parse_bib_and_bbl(src_dir: Path) -> dict[str, str]:
    bib_map: dict[str, str] = {}
    for bib_file in src_dir.rglob("*.bib"):
        txt = bib_file.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,([^@]*)", txt, flags=re.DOTALL):
            key, body = m.group(1).strip(), m.group(2)
            tm = re.search(r"title\s*=\s*[\{\"](.+?)[\}\"](?:\s*,|\s*\n)", body, flags=re.IGNORECASE | re.DOTALL)
            am = re.search(r"author\s*=\s*[\{\"](.+?)[\}\"](?:\s*,|\s*\n)", body, flags=re.IGNORECASE | re.DOTALL)
            ym = re.search(r"year\s*=\s*[\{\"]?(\d{4})[\}\"]?", body, flags=re.IGNORECASE)
            desc = " | ".join(
                re.sub(r"\s+", " ", p).strip("{}")
                for p in [
                    tm.group(1) if tm else "",
                    (am.group(1)[:60] + "...") if am and len(am.group(1)) > 60 else (am.group(1) if am else ""),
                    ym.group(1) if ym else "",
                ]
                if p
            )
            bib_map[key] = desc or key

    for bbl_file in src_dir.rglob("*.bbl"):
        txt = bbl_file.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", txt, flags=re.DOTALL):
            key = m.group(1).strip()
            if key not in bib_map:
                clean = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", m.group(2))
                clean = re.sub(r"\s+", " ", clean).strip()[:180]
                bib_map[key] = clean
    return bib_map


def extract_tex_citations(
    http: CachedHttpClient,
    arxiv_id: str | None,
    tex_dir_arg: str | None,
    filter_query: str | None = None,
) -> dict[str, Any]:
    if tex_dir_arg:
        src_dir = Path(tex_dir_arg).expanduser().resolve()
    elif arxiv_id:
        _, clean_ax = classify_identifier(arxiv_id)
        src_dir = ARXIV_SRC_CACHE / clean_ax.replace("/", "_")
        if not any(src_dir.rglob("*.tex")):
            raw = http.request_bytes(f"https://arxiv.org/e-print/{clean_ax}", min_interval=1.5)
            if not raw:
                raise RuntimeError(f"Failed to download arXiv source bundle for {clean_ax}")
            safe_extract_tar_bytes(raw, src_dir)
    else:
        raise ValueError("Provide either --arxiv or --tex-dir")

    bib_map = parse_bib_and_bbl(src_dir)
    cite_re = re.compile(r"\\(?:cite|citet|citep|citealp|citeauthor|autocite|parencite|textcite)\*?\[?[^\]]*\]?\{([^}]+)\}")
    sec_re = re.compile(r"\\(?:section|subsection|subsubsection)\*?\{([^}]+)\}")

    contexts: list[dict[str, Any]] = []
    q_low = filter_query.lower() if filter_query else None

    for tex_path in sorted(src_dir.rglob("*.tex")):
        raw_lines = tex_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        # Strip LaTeX comments while preserving escaped \%
        stripped_lines: list[str] = []
        current_sec = "Preamble / Main"
        line_sections: list[str] = []
        for ln in raw_lines:
            clean_ln = re.sub(r"(?<!\\)%.*$", "", ln)
            sm = sec_re.search(clean_ln)
            if sm:
                current_sec = sm.group(1).strip()
            stripped_lines.append(clean_ln)
            line_sections.append(current_sec)

        joined = "\n".join(stripped_lines)
        paragraphs = re.split(r"\n\s*\n", joined)
        curr_sec_tracker = "Introduction / Main"
        for para in paragraphs:
            sm = sec_re.search(para)
            if sm:
                curr_sec_tracker = sm.group(1).strip()
            if "\\cite" not in para and "cite{" not in para:
                continue
            # Split roughly into sentences while keeping LaTeX intact
            sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", re.sub(r"\s+", " ", para).strip())
            for sent in sentences:
                matches = list(cite_re.finditer(sent))
                if not matches:
                    continue
                keys: list[str] = []
                for m in matches:
                    keys.extend(k.strip() for k in m.group(1).split(",") if k.strip())
                resolved_refs = {k: bib_map.get(k, k) for k in keys}
                haystack = (sent + " " + " ".join(resolved_refs.values())).lower()
                if q_low and q_low not in haystack:
                    continue
                contexts.append(
                    {
                        "file": str(tex_path.relative_to(src_dir)),
                        "section": curr_sec_tracker,
                        "cite_keys": keys,
                        "resolved_references": resolved_refs,
                        "lexical_cues": classify_context_cues(sent),
                        "sentence": sent[:800],
                    }
                )

    return {
        "source_dir": str(src_dir),
        "bib_entries_parsed": len(bib_map),
        "matching_citation_sentences": len(contexts),
        "contexts": contexts[:150],
    }


# ---------------------------------------------------------------------------
# Subcommand 5: Zero-Hallucination Canonical `.bib` Verifier & Upgrader
# ---------------------------------------------------------------------------

def parse_bibtex_file(bib_text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    # Match @type{key, ...} with balanced brace awareness
    idx = 0
    n = len(bib_text)
    while idx < n:
        at_pos = bib_text.find("@", idx)
        if at_pos == -1:
            break
        m_head = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", bib_text[at_pos:])
        if not m_head:
            idx = at_pos + 1
            continue
        etype = m_head.group(1).lower()
        if etype in {"comment", "preamble", "string"}:
            idx = at_pos + m_head.end()
            continue
        key = m_head.group(2).strip()
        brace_depth = 1
        pos = at_pos + m_head.end()
        while pos < n and brace_depth > 0:
            if bib_text[pos] == "{":
                brace_depth += 1
            elif bib_text[pos] == "}":
                brace_depth -= 1
            pos += 1
        body = bib_text[at_pos + m_head.end() : pos - 1]
        raw_block = bib_text[at_pos:pos]
        fields: dict[str, str] = {}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)", body, flags=re.DOTALL):
            fname = fm.group(1).lower().strip()
            fval = re.sub(r"\s+", " ", fm.group(2).strip()).strip("{}\"")
            fields[fname] = fval
        entries.append({"entry_type": etype, "key": key, "fields": fields, "raw": raw_block})
        idx = pos
    return entries


def format_canonical_bibtex(key: str, rec: dict[str, Any]) -> str:
    authors = " and ".join(rec.get("authors") or ["Unknown"])
    title = rec.get("title") or "Untitled"
    year = str(rec.get("year") or "")
    venue = rec.get("venue") or ""
    if venue and venue == venue.lower():
        venue = venue.title().replace(" Of ", " of ").replace(" In ", " in ").replace(" On ", " on ").replace(" And ", " and ").replace(" For ", " for ")
    doi = rec.get("doi")
    arxiv_id = rec.get("arxiv_id")
    is_pub = bool(rec.get("is_published_venue"))

    venue_low = venue.lower()
    is_conf = any(
        c in venue_low
        for c in (
            "conference",
            "proceedings",
            "symposium",
            "workshop",
            "neural information processing systems",
            "learning representations",
            "empirical methods in natural language processing",
            "association for computational linguistics",
            "computer vision and pattern recognition",
            "neurips",
            "nips",
            "iclr",
            "icml",
            "cvpr",
            "iccv",
            "eccv",
            "acl",
            "emnlp",
            "naacl",
            "aaai",
            "ijcai",
            "kdd",
            "sigir",
            "chi",
            "usenix",
            "osdi",
            "sosp",
        )
    )

    if is_pub and is_conf:
        etype = "inproceedings"
        venue_field = f"  booktitle = {{{venue}}},"
    elif is_pub:
        etype = "article"
        venue_field = f"  journal = {{{venue}}},"
    else:
        etype = "misc"
        venue_field = f"  howpublished = {{arXiv preprint arXiv:{arxiv_id}}}," if arxiv_id else ""

    lines = [
        f"@{etype}{{{key},",
        f"  title = {{{title}}},",
        f"  author = {{{authors}}},",
    ]
    if venue_field:
        lines.append(venue_field)
    if year:
        lines.append(f"  year = {{{year}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    if arxiv_id:
        lines.append(f"  eprint = {{{arxiv_id}}},")
        lines.append("  archivePrefix = {arXiv},")
    if rec.get("url"):
        lines.append(f"  url = {{{rec['url']}}},")
    lines.append("}")
    return "\n".join(lines)


def verify_bibliography(
    http: CachedHttpClient,
    bib_path: str | None,
    raw_ids: list[str],
) -> dict[str, Any]:
    items_to_check: list[dict[str, Any]] = []
    if bib_path:
        text = Path(bib_path).expanduser().read_text(encoding="utf-8", errors="ignore")
        items_to_check.extend(parse_bibtex_file(text))

    for rid in raw_ids:
        safe_k = re.sub(r"[^a-zA-Z0-9_]+", "_", rid).strip("_")[:32] or "ref"
        items_to_check.append({"entry_type": "misc", "key": safe_k, "fields": {"note_query": rid}, "raw": ""})

    results: list[dict[str, Any]] = []
    verified_bib_blocks: list[str] = []
    counts: Counter[str] = Counter()

    for entry in items_to_check:
        key = entry["key"]
        f = entry["fields"]
        probe = (
            f.get("doi")
            or f.get("eprint")
            or f.get("arxivid")
            or f.get("note_query")
            or f.get("title")
            or ""
        )
        if not probe:
            counts["UNVERIFIED_HALLUCINATION_RISK"] += 1
            results.append({"key": key, "status": "UNVERIFIED_HALLUCINATION_RISK", "reason": "Empty DOI/eprint/title"})
            continue

        resolved = resolve_paper(http, probe)
        # If DOI/eprint failed or mismatched title, double-check by title
        if resolved and f.get("title"):
            sim = title_similarity(f["title"], resolved.get("title") or "")
            if sim < 0.60:
                by_title = resolve_paper(http, f["title"])
                if by_title and title_similarity(f["title"], by_title.get("title") or "") >= 0.75:
                    resolved = by_title
                elif sim < 0.45:
                    resolved = None
        elif not resolved and f.get("title"):
            by_title = resolve_paper(http, f["title"])
            if by_title and title_similarity(f["title"], by_title.get("title") or "") >= 0.75:
                resolved = by_title

        if not resolved:
            counts["UNVERIFIED_HALLUCINATION_RISK"] += 1
            results.append(
                {
                    "key": key,
                    "status": "UNVERIFIED_HALLUCINATION_RISK",
                    "input_title": f.get("title"),
                    "input_probe": probe,
                    "reason": "No matching scholarly work found across Semantic Scholar, OpenAlex, Crossref, or arXiv.",
                }
            )
            continue

        cr = check_crossref_integrity(http, resolved["doi"]) if resolved.get("doi") else {}
        is_ret = bool(resolved.get("is_retracted") or cr.get("is_retracted"))
        has_corr = bool(cr.get("has_correction"))

        orig_venue = f.get("booktitle") or f.get("journal") or ""
        orig_was_preprint = is_preprint_venue(orig_venue) or entry["entry_type"] == "misc"

        if is_ret:
            status = "RETRACTED_OR_WITHDRAWN"
        elif orig_was_preprint and resolved.get("is_published_venue") and f.get("title"):
            status = "UPGRADE_AVAILABLE_TO_PUBLISHED"
        elif f.get("year") and resolved.get("year") and abs(int(re.findall(r"\d{4}", f["year"])[0]) - int(resolved["year"])) > 1 and not orig_was_preprint:
            status = "METADATA_YEAR_MISMATCH"
        elif resolved.get("is_published_venue"):
            status = "VERIFIED_PUBLISHED"
        else:
            status = "VERIFIED_PREPRINT"

        counts[status] += 1
        # Generate smart key if user passed bare IDs
        out_key = key
        if "note_query" in f and resolved.get("authors") and resolved.get("year"):
            surname = re.sub(r"[^a-zA-Z]", "", resolved["authors"][0].split()[-1]).lower()
            first_word = (normalize_title(resolved.get("title") or "paper").split() or ["paper"])[0]
            out_key = f"{surname}{resolved['year']}{first_word}"

        canonical_bib = format_canonical_bibtex(out_key, resolved)
        if not is_ret:
            verified_bib_blocks.append(canonical_bib)

        resolved_clean = {k: v for k, v in resolved.items() if k not in ("referenced_works", "related_works", "abstract")}
        results.append(
            {
                "key": out_key,
                "status": status,
                "has_correction": has_corr,
                "crossref_updates": cr.get("updates", []),
                "resolved": resolved_clean,
                "canonical_bibtex": canonical_bib,
            }
        )

    return {
        "summary_counts": dict(counts),
        "total_checked": len(items_to_check),
        "entries": results,
        "verified_bibtex_bundle": "\n\n".join(verified_bib_blocks) + ("\n" if verified_bib_blocks else ""),
    }


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def write_or_print(payload: dict[str, Any], output_path: str | None) -> None:
    formatted = json.dumps(payload, indent=2, ensure_ascii=False)
    if output_path:
        out = Path(output_path).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(formatted + "\n", encoding="utf-8")
        logger.info("Wrote JSON output to %s", out)
    else:
        sys.stdout.write(formatted + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open-stack scholarly graph, citation stance/retraction audit, and .bib verifier."
    )
    parser.add_argument("--no-cache", action="store_true", help="Bypass local SQLite HTTP cache")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1. resolve
    p_res = sub.add_parser("resolve", help="Resolve DOI, arXiv ID, OpenAlex ID, S2 ID, or title query")
    p_res.add_argument("queries", nargs="+", help="One or more paper identifiers or titles")
    p_res.add_argument("--output", "-o", help="Output JSON file path")

    # 2. lineage
    p_lin = sub.add_parser(
        "lineage",
        help="Build ResearchRabbit/Litmaps-style lineage graph (co-cited roots, frontier, SPECTER2 siblings)",
    )
    p_lin.add_argument("--seeds", nargs="+", required=True, help="Seed paper IDs or titles")
    p_lin.add_argument("--negatives", nargs="*", default=[], help="Optional negative seed IDs for SPECTER2 filtering")
    p_lin.add_argument("--max-per-group", type=int, default=15, help="Max nodes per group (default: 15)")
    p_lin.add_argument("--output", "-o", required=True, help="Output graph JSON path")

    # 3. citation-audit
    p_aud = sub.add_parser(
        "citation-audit",
        help="Scite-style audit of in-text citing contexts, intents, influential citers, and retraction status",
    )
    p_aud.add_argument("paper", help="Target paper DOI, arXiv ID, S2 ID, or title")
    p_aud.add_argument("--max-citing", type=int, default=80, help="Max citing works to inspect (default: 80)")
    p_aud.add_argument("--output", "-o", help="Output audit JSON path")

    # 4. tex-context
    p_tex = sub.add_parser(
        "tex-context",
        help="Extract verbatim \\cite{} sentences and resolved bibliography keys directly from arXiv LaTeX source",
    )
    p_tex.add_argument("--arxiv", help="arXiv ID (downloads and caches .tar.gz source)")
    p_tex.add_argument("--tex-dir", help="Local unpacked LaTeX directory")
    p_tex.add_argument("--query", "-q", help="Optional keyword/author/citekey filter")
    p_tex.add_argument("--output", "-o", help="Output JSON path")

    # 5. bib-verify
    p_bib = sub.add_parser(
        "bib-verify",
        help="Verify .bib file or IDs against Crossref/OpenAlex/S2/arXiv, flag retractions/hallucinations, upgrade preprints",
    )
    p_bib.add_argument("--bib", help="Path to input .bib file")
    p_bib.add_argument("--ids", nargs="*", default=[], help="Additional DOIs / arXiv IDs / titles to verify and emit BibTeX")
    p_bib.add_argument("--output-bib", help="Write verified & upgraded canonical .bib file to this path")
    p_bib.add_argument("--report", "-o", help="Write verification JSON report to this path")

    args = parser.parse_args()
    http = CachedHttpClient(use_cache=not args.no_cache)

    if args.cmd == "resolve":
        resolved = []
        for q in args.queries:
            r = resolve_paper(http, q)
            if r:
                r.pop("referenced_works", None)
                r.pop("related_works", None)
            resolved.append({"input": q, "resolved": r})
        write_or_print({"results": resolved}, args.output)

    elif args.cmd == "lineage":
        # Support comma-separated OR space-separated --seeds
        flat_seeds = [s.strip() for item in args.seeds for s in (item.split(",") if "," in item and not item.startswith("http") and " " not in item else [item]) if s.strip()]
        flat_negs = [s.strip() for item in args.negatives for s in item.split(",") if s.strip()]
        graph = build_lineage_graph(http, flat_seeds, flat_negs, max_per_group=args.max_per_group)
        write_or_print(graph, args.output)

    elif args.cmd == "citation-audit":
        report = audit_paper_citations(http, args.paper, max_citing=args.max_citing)
        write_or_print(report, args.output)

    elif args.cmd == "tex-context":
        res = extract_tex_citations(http, args.arxiv, args.tex_dir, args.query)
        write_or_print(res, args.output)

    elif args.cmd == "bib-verify":
        if not args.bib and not args.ids:
            parser.error("Provide --bib <file.bib> and/or --ids <id1 ...>")
        rep = verify_bibliography(http, args.bib, args.ids)
        if args.output_bib:
            out_b = Path(args.output_bib).expanduser()
            out_b.parent.mkdir(parents=True, exist_ok=True)
            out_b.write_text(rep["verified_bibtex_bundle"], encoding="utf-8")
            logger.info("Wrote verified BibTeX to %s", out_b)
        write_or_print(rep, args.report)


if __name__ == "__main__":
    main()
