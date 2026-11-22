#!/usr/bin/env python3
r"""Offline deterministic regression test suite for scientific-research-skills.

Covers:
1. Plugin & Skill manifest validity (plugin.json, marketplace.json, SKILL.md YAML frontmatter, zero hardcoded user paths)
2. Arbitrary-depth nested-brace BibTeX parsing, LaTeX diacritic/Greek normalization, author-surname extraction, OpenReview ID parsing, & .tex citation cross-checking
3. Booktabs LaTeX evidence matrix compilation (`tabularx` wrapping, preserved `$...$` math & `\cite{}`, Unicode `Δ`/`±` conversion, Wilke Rule 4 right-aligned numeric headers)
4. Interactive HTML citation map compilation (standalone + inline modes, offline fallback styles, Copy BibTeX button)
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_SCRIPT = REPO_ROOT / "plugins/research-literature/skills/scholarly-graph-audit/scripts/scholarly_graph.py"
MAP_SCRIPT = REPO_ROOT / "plugins/research-literature/skills/scholarly-graph-audit/scripts/render_citation_map.py"
MATRIX_SCRIPT = REPO_ROOT / "plugins/research-literature/skills/literature-evidence-workflow/scripts/compile_evidence_matrix.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sg = load_module("scholarly_graph", GRAPH_SCRIPT)
rcm = load_module("render_citation_map", MAP_SCRIPT)
cem = load_module("compile_evidence_matrix", MATRIX_SCRIPT)


class TestPluginAndSkillManifests(unittest.TestCase):
    def test_plugin_manifests_and_skill_frontmatter(self) -> None:
        allowed_plugin_keys = {
            "name",
            "displayName",
            "version",
            "description",
            "logo",
            "suggestedPrompts",
            "author",
            "homepage",
            "repository",
            "disabled",
        }
        for pdir in (REPO_ROOT / "plugins/research-literature", REPO_ROOT / "plugins/scientific-writing"):
            manifest = json.loads((pdir / "plugin.json").read_text(encoding="utf-8"))
            self.assertTrue(set(manifest.keys()).issubset(allowed_plugin_keys))
            self.assertLessEqual(len(manifest.get("suggestedPrompts", [])), 3)
            logo_p = pdir / manifest["logo"]
            self.assertTrue(logo_p.exists(), f"Missing logo: {logo_p}")

        for skill_md in (REPO_ROOT / "plugins").rglob("SKILL.md"):
            txt = skill_md.read_text(encoding="utf-8")
            self.assertTrue(txt.startswith("---\n"), f"Missing YAML frontmatter in {skill_md}")
            self.assertIn("\nname:", f"\n{txt}")
            self.assertIn("\ndescription:", f"\n{txt}")

    def test_zero_hardcoded_personal_paths(self) -> None:
        for f in (REPO_ROOT / "plugins").rglob("*"):
            if f.is_file() and f.suffix in {".md", ".py", ".json", ".svg"}:
                content = f.read_text(encoding="utf-8")
                self.assertNotIn("/Users/", content, f"Hardcoded /Users/ path leaked in {f}")


class TestBibtexAndIdentifierEdgeCases(unittest.TestCase):
    def test_identifier_classification_including_openreview(self) -> None:
        self.assertEqual(sg.classify_identifier("arXiv:2305.18290v3"), ("arxiv", "2305.18290"))
        self.assertEqual(sg.classify_identifier("https://doi.org/10.48550/arXiv.2203.02155"), ("arxiv", "2203.02155"))
        self.assertEqual(sg.classify_identifier("https://openreview.net/forum?id=ljNZyrAlaa"), ("openreview", "ljNZyrAlaa"))
        self.assertEqual(sg.classify_identifier("10.1038/s41586-021-03819-2"), ("doi", "10.1038/s41586-021-03819-2"))

    def test_nested_brace_bibtex_and_diacritics(self) -> None:
        tricky_bib = r"""
@inproceedings{wu2024betadpo,
  title = {{{$\beta$-{DPO}}: {Direct Preference Optimization} with {Dynamic} {$\beta$}}},
  author = {M{\"u}ller, Karl and V{\"o}lske, Michael and Wu, Junkang},
  booktitle = {Advances in {Neural Information Processing Systems}},
  year = {2024}
}
"""
        parsed = sg.parse_bibtex_file(tricky_bib)
        self.assertEqual(len(parsed), 1)
        fields = parsed[0]["fields"]
        self.assertIn("Direct Preference Optimization", fields["title"])
        # Greek \beta-DPO matches Unicode β-DPO!
        sim = sg.title_similarity(fields["title"], "β-DPO: Direct Preference Optimization with Dynamic β")
        self.assertGreaterEqual(sim, 0.95)
        surnames = sg.extract_author_surnames(fields["author"])
        self.assertEqual(surnames, {"muller", "volske", "wu"})

    def test_tex_citation_scanner_ignores_comments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tex_p = Path(tmp) / "main.tex"
            tex_p.write_text(
                r"""
                We build on \citep{rafailov2023dpo, ouyang2022training} and \citet{jiang2026ddpo} vs. \cite{extra2024}.
                % \cite{commented_out_ghost_key}
                100\% improvement \citet[Sec.~2][p.~4]{schulz2025new}.
                """,
                encoding="utf-8",
            )
            keys = sg.scan_tex_cited_keys(str(tex_p))
            self.assertEqual(
                keys,
                {"rafailov2023dpo", "ouyang2022training", "jiang2026ddpo", "extra2024", "schulz2025new"},
            )


class TestMatrixAndCitationMapCompilers(unittest.TestCase):
    def test_booktabs_tabularx_math_and_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            in_json = Path(tmp) / "rows.json"
            in_json.write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "included": True,
                                "citation_label": r"Rafailov et al. \citep{rafailov2023dpo}",
                                "core_mechanism": "Closed-form mapping from optimal policy $\\pi^*$ to implicit reward without PPO rollouts in long-horizon settings",
                                "win_rate": "61.4 ± 1.2%",
                                "provenance_tier": "latex_source",
                                "provenance_anchor": "Table 1",
                                "verbatim_quote": "Outperforms PPO.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            out_dir = Path(tmp) / "out"
            subprocess.run(
                [
                    sys.executable,
                    str(MATRIX_SCRIPT),
                    str(in_json),
                    "--out-dir",
                    str(out_dir),
                    "--columns",
                    "citation_label:Study,core_mechanism:Core Mechanism,win_rate:Win Rate (Δ)",
                ],
                check=True,
                capture_output=True,
            )
            tex = (out_dir / "comparison_table.tex").read_text(encoding="utf-8")
            self.assertIn(r"\begin{tabularx}{\textwidth}", tex)
            self.assertIn(r">{\raggedright\arraybackslash}X", tex)
            self.assertIn(r"\multicolumn{1}{r}{Win Rate ($\Delta$)}", tex)
            self.assertIn(r"\citep{rafailov2023dpo}", tex)
            self.assertIn(r"$\pi^*$", tex)
            self.assertIn(r"61.4 $\pm$ 1.2\%", tex)
            self.assertNotIn("|", tex.split(r"\toprule")[1])

    def test_citation_map_offline_html_and_copy_bibtex(self) -> None:
        sample_graph = {
            "seeds": [{"canonical_id": "doi:10.1/seed"}],
            "nodes": [
                {
                    "canonical_id": "doi:10.1/seed",
                    "role": "seed",
                    "title": "Seed Paper",
                    "authors": ["Alice Zhang"],
                    "year": 2024,
                    "venue": "ICLR",
                    "is_published_venue": True,
                    "doi": "10.1/seed",
                    "citation_count": 120,
                }
            ],
            "edges": [],
        }
        html = rcm.render_html(sample_graph, mode="standalone", title="Test Map")
        self.assertIn("btnCopyBib", html)
        self.assertIn("Copy BibTeX", html)
        self.assertIn('[class*="bg-[var(--card)]"]', html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
