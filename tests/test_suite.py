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
VISUAL_LINT_SCRIPT = REPO_ROOT / "plugins/scientific-writing/skills/scientific-writing/scripts/lint_manuscript_visuals.py"
SCAFFOLD_SCRIPT = REPO_ROOT / "plugins/scientific-computing/skills/scientific-computing/scripts/scaffold_research_project.py"
PY_AUDIT_SCRIPT = REPO_ROOT / "plugins/scientific-computing/skills/scientific-computing/scripts/audit_scientific_python.py"
IDEA_LINT_SCRIPT = REPO_ROOT / "plugins/scientific-ideation/skills/scientific-ideation/scripts/lint_research_ideas.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sg = load_module("scholarly_graph", GRAPH_SCRIPT)
rcm = load_module("render_citation_map", MAP_SCRIPT)
cem = load_module("compile_evidence_matrix", MATRIX_SCRIPT)
lmv = load_module("lint_manuscript_visuals", VISUAL_LINT_SCRIPT)
srp = load_module("scaffold_research_project", SCAFFOLD_SCRIPT)
asp = load_module("audit_scientific_python", PY_AUDIT_SCRIPT)
lri = load_module("lint_research_ideas", IDEA_LINT_SCRIPT)


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
        for pdir in (
            REPO_ROOT / "plugins/scientific-ideation",
            REPO_ROOT / "plugins/research-literature",
            REPO_ROOT / "plugins/scientific-computing",
            REPO_ROOT / "plugins/scientific-writing",
        ):
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
        router = REPO_ROOT / "rules/GLOBAL_RESEARCH_ROUTER.md"
        self.assertTrue(router.is_file(), "Missing rules/GLOBAL_RESEARCH_ROUTER.md")
        router_txt = router.read_text(encoding="utf-8")
        self.assertIn("<!-- scientific-research-skills:start -->", router_txt)
        self.assertNotIn("/Users/", router_txt)
        self.assertLess(len(router_txt.encode("utf-8")), 4000)

        for f in (REPO_ROOT / "plugins").rglob("*"):
            if f.is_file() and f.suffix in {".md", ".py", ".json", ".svg"}:
                content = f.read_text(encoding="utf-8")
                self.assertNotIn("/Users/", content, f"Hardcoded /Users/ path leaked in {f}")

    def test_scientific_writing_mandates_automatic_figures_coinvocation(self) -> None:
        writing_skill = REPO_ROOT / "plugins/scientific-writing/skills/scientific-writing/SKILL.md"
        figures_target = (writing_skill.parent / "../scientific-figures/SKILL.md").resolve()
        self.assertTrue(figures_target.is_file(), f"Broken relative sibling path: {figures_target}")

        writing_txt = writing_skill.read_text(encoding="utf-8")
        self.assertIn("Mandatory Automatic Co-Invocation", writing_txt)
        self.assertIn("MUST immediately read [`../scientific-figures/SKILL.md`](../scientific-figures/SKILL.md)", writing_txt)

        writing_rules = (REPO_ROOT / "plugins/scientific-writing/rules/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("MUST** read **BOTH** `scientific-writing`", writing_rules)
        self.assertNotIn("pure prose tasks load `scientific-writing` only", writing_rules)


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


class TestProseVisualSymbiosisLinter(unittest.TestCase):
    def test_detects_orphans_out_of_order_pointer_topics_and_weak_captions(self) -> None:
        bad_tex = r"""
        Figure~\ref{fig:second} shows that loss decreases.
        Later we mention accuracy (Fig.~\ref{fig:first}) and a missing ref (Tab.~\ref{tab:ghost}).

        \begin{figure}[t]
          \caption{Relationship between width and validation loss.}
          \label{fig:first}
        \end{figure}

        \begin{figure}[t]
          \caption{Spectral gating preserves constant validation loss up to 128k tokens.}
          \label{fig:second}
        \end{figure}

        \begin{table}[t]
          \caption{Ablation across tokenization granularities.}
          \label{tab:orphan}
        \end{table}
        """
        rep = lmv.lint_tex_source(bad_tex)
        self.assertFalse(rep["clean"])
        self.assertEqual([o["label"] for o in rep["orphan_visuals"]], ["tab:orphan"])
        self.assertEqual([o["label"] for o in rep["out_of_order_callouts"]], ["fig:first"])
        self.assertEqual(rep["undefined_visual_refs"], ["tab:ghost"])
        self.assertEqual(len(rep["pointer_topic_sentences"]), 1)
        self.assertEqual([w["label"] for w in rep["weak_descriptive_figure_captions"]], ["fig:first"])

    def test_clean_manuscript_passes(self) -> None:
        good_tex = r"""
        Spectral gating preserved constant loss up to 128k tokens (Fig.~\ref{fig:scaling}),
        cutting decoding latency 3.1-fold over Flash-2 (Table~\ref{tab:latency}).

        \begin{figure}[t]
          \caption{\textbf{Spectral gating preserves constant loss up to 128k tokens.} Validation perplexity across context lengths ($n=5$ seeds, 95\% CI).}
          \label{fig:scaling}
        \end{figure}

        \begin{table}[t]
          \caption{Wall-clock decoding latency across sequence lengths.}
          \label{tab:latency}
        \end{table}
        """
        rep = lmv.lint_tex_source(good_tex)
        self.assertTrue(rep["clean"], msg=json.dumps(rep, indent=2))

    def test_abstract_abt_explicit_and_implicit_scaffolding_pass(self) -> None:
        explicit_abt_tex = r"""
        \begin{abstract}
        Long-context language models rely on key-value caches during autoregressive decoding.
        At 128k tokens, cache memory exceeds model weights, and uniform token eviction erases rare retrieval anchors.
        However, existing importance scorers recompute dense attention weights at quadratic cost.
        To preserve retrieval anchors in linear time, we introduce spectral anchor routing, reducing cache memory 4.2-fold with zero recall loss.
        \end{abstract}
        """
        rep_exp = lmv.lint_tex_source(explicit_abt_tex)
        self.assertTrue(rep_exp["clean"], msg=json.dumps(rep_exp, indent=2))
        self.assertTrue(rep_exp["abstract_narrative"]["present"])
        self.assertEqual(rep_exp["counts"]["abstract_narrative_warnings"], 0)

        # Removable-scaffolding ABT (no literal 'but'/'however', uses concrete bottleneck/failure verb)
        implicit_abt_tex = r"""
        \abstract{
          Mixture-of-experts transformers scale parameter capacity at constant per-token FLOPs.
          Under domain shift, top-k token routing collapses onto two dominant experts and degrades tail-class accuracy by 14\%.
          To restore balanced utilization without auxiliary loss tuning, we introduce sinkhorn Sink-Gate routing.
          Across six benchmarks, Sink-Gate recovers full dense accuracy at 1.9x higher throughput.
        }
        """
        rep_imp = lmv.lint_tex_source(implicit_abt_tex)
        self.assertTrue(rep_imp["clean"], msg=json.dumps(rep_imp, indent=2))
        self.assertEqual(rep_imp["counts"]["abstract_narrative_warnings"], 0)

    def test_abstract_aaa_dhy_and_premature_openers_flagged(self) -> None:
        aaa_tex = r"""
        \begin{abstract}
        Graph neural networks aggregate neighborhood representations across molecular topologies.
        Message passing layers compute permutation-equivariant node embeddings at each hop.
        Readout pooling combines node vectors into graph-level molecular descriptors.
        Benchmark evaluations report validation scores across twelve quantum chemistry properties.
        \end{abstract}
        """
        rep_aaa = lmv.lint_tex_source(aaa_tex)
        self.assertFalse(rep_aaa["clean"])
        codes_aaa = [w["code"] for w in rep_aaa["abstract_narrative"]["warnings"]]
        self.assertIn("NO_CONTRADICTION_AAA_ABSTRACT", codes_aaa)

        dhy_tex = r"""
        \begin{abstract}
        We measured expert activation entropy across sixteen sparse language models.
        Despite auxiliary load-balancing penalties, routing entropy drops during mid-training.
        However, increasing the balance coefficient degrades perplexity on code tokens.
        Yet freezing router logits early prevents specialization on reasoning benchmarks.
        \end{abstract}
        """
        rep_dhy = lmv.lint_tex_source(dhy_tex)
        self.assertFalse(rep_dhy["clean"])
        codes_dhy = [w["code"] for w in rep_dhy["abstract_narrative"]["warnings"]]
        self.assertIn("ZERO_CONTEXT_ACTION_OPENER", codes_dhy)
        self.assertIn("CONSECUTIVE_CONTRADICTION_ZIGZAG", codes_dhy)

        bare_s1_tex = r"""
        \begin{abstract}
        However, sparse attention kernels underutilize tensor cores at batch size one.
        To saturate memory bandwidth, we tile key-value blocks across warp groups.
        \end{abstract}
        """
        rep_bare = lmv.lint_tex_source(bare_s1_tex)
        self.assertFalse(rep_bare["clean"])
        codes_bare = [w["code"] for w in rep_bare["abstract_narrative"]["warnings"]]
        self.assertIn("PREMATURE_CONTRADICTION_OPENER", codes_bare)

        # --no-abstract-lint bypasses abstract warnings
        rep_suppressed = lmv.lint_tex_source(bare_s1_tex, check_abstract=False)
        self.assertTrue(rep_suppressed["clean"])
        self.assertEqual(rep_suppressed["counts"]["abstract_narrative_warnings"], 0)

    def test_assertion_evidence_visual_inventory_and_topic_captions(self) -> None:
        tex = r"""
        \section{Introduction}
        Standard eviction drops dormant keys, whereas spectral sketching preserves them (Fig.~\ref{fig:overview}).

        \begin{figure}[t]
          \caption{Overview of Spectral Anchor Routing comparing dense eviction and rank-16 sketching.}
          \label{fig:overview}
        \end{figure}

        \section{Experiments}
        Rank-16 sketches recover 99.1\% recall across distances (Fig.~\ref{fig:mech}a--b).
        Ablation sweeps are reported in Fig.~\ref{fig:ablation}.

        \begin{figure}[t]
          \caption{\textbf{Rapid singular-value decay enables compact key sketches.} (a) Dormant-head recall vs. distance. (b) Key spectrum decay. (c) Uncited warmup loss curve.}
          \label{fig:mech}
        \end{figure}

        \begin{figure}[t]
          \caption{Ablation study on routing temperature and sketch rank.}
          \label{fig:ablation}
        \end{figure}
        """
        rep = lmv.lint_tex_source(tex)
        self.assertFalse(rep["clean"])
        # Overview schematic is allowed; empirical topic-label 'Ablation study on...' is flagged!
        self.assertEqual([w["label"] for w in rep["weak_descriptive_figure_captions"]], ["fig:ablation"])
        inv_by_label = {item["label"]: item for item in rep["visual_inventory"]}
        self.assertEqual(inv_by_label["fig:overview"]["section"], "Introduction")
        self.assertEqual(inv_by_label["fig:mech"]["section"], "Experiments")
        self.assertEqual(inv_by_label["fig:mech"]["subpanels_declared"], ["a", "b", "c"])
        self.assertEqual(inv_by_label["fig:mech"]["subpanels_explicitly_cited"], ["a", "b"])
        self.assertEqual(inv_by_label["fig:mech"]["uncited_subpanels_hint"], ["c"])
        self.assertIn("Rank-16 sketches recover", inv_by_label["fig:mech"]["first_callout_sentence"])

    def test_cross_table_silent_drift_flagged_and_protocol_badges_allowed(self) -> None:
        tex = r"""
        \section{Results}
        Main benchmark scores appear in Table~\ref{tab:main}, supplementary breakdowns in Table~\ref{tab:supp_drift} and Table~\ref{tab:supp_p2},
        and single-cohort checks in Table~\ref{tab:cohort_x} and Table~\ref{tab:cohort_y}.

        \begin{table}[t]
          \caption{Cross-cohort outer-fold $R^2$ under full-rank inputs.}
          \label{tab:main}
          \begin{tabular}{lrr}
            \toprule
            Method & Bench-Alpha & Bench-Beta V4 \\
            \midrule
            Div. Norm. & \textbf{0.2106} & 0.2911 \\
            Spectral Gate & 0.2240 & 0.3055 \\
            \bottomrule
          \end{tabular}
        \end{table}

        \begin{table}[t]
          \caption{Supplementary multirow table with silent pooled-vs-macro drift on Bench-Alpha and valid 2-digit rounding on Bench-Beta V4.}
          \label{tab:supp_drift}
          \begin{tabular}{llrr}
            \toprule
            Cohort & Method & Test $R^2$ & Latency (ms) \\
            \midrule
            \multirow{2}{*}{Bench-Alpha} & Div. Norm. & 0.2071 & 12.4 \\
             & Spectral Gate & 0.2240 & 14.1 \\
            Bench-Beta V4 & Div. Norm. & 0.29 & 18.2 \\
            \bottomrule
          \end{tabular}
        \end{table}

        \begin{table}[t]
          \caption{Dimension-matched SVD ablation (Protocol P2: rank-96 native SVD).}
          \label{tab:supp_p2}
          \begin{tabular}{lrr}
            \toprule
            Method & Bench-Alpha & Bench-Beta V4 \\
            \midrule
            Div. Norm. & 0.1995 & 0.2724 \\
            \bottomrule
          \end{tabular}
        \end{table}

        \begin{table}[t]
          \caption{Accuracy on Cohort-X.}
          \label{tab:cohort_x}
          \begin{tabular}{lr}
            \toprule
            Method & Accuracy \\
            \midrule
            Spectral Gate & 84.2 \\
            \bottomrule
          \end{tabular}
        \end{table}

        \begin{table}[t]
          \caption{Accuracy on Cohort-Y.}
          \label{tab:cohort_y}
          \begin{tabular}{lr}
            \toprule
            Method & Accuracy \\
            \midrule
            Spectral Gate & 71.9 \\
            \bottomrule
          \end{tabular}
        \end{table}
        """
        rep = lmv.lint_tex_source(tex)
        self.assertFalse(rep["clean"])
        # Exactly 1 conflict: Bench-Alpha + Div. Norm. (0.2106 vs 0.2071); Protocol P2, 0.29 rounding, and Cohort-X/Y do NOT false-flag!
        self.assertEqual(len(rep["cross_table_conflicts"]), 1, msg=json.dumps(rep["cross_table_conflicts"], indent=2))
        conflict = rep["cross_table_conflicts"][0]
        self.assertEqual(conflict["table_a"], "tab:main")
        self.assertEqual(conflict["table_b"], "tab:supp_drift")
        self.assertAlmostEqual(conflict["abs_diff"], 0.0035, places=6)

    def test_abstract_body_stale_metric_flagged_and_derived_delta_allowed(self) -> None:
        tex = r"""
        \begin{abstract}
        Long-context retrieval models rely on cached keys.
        However, uniform eviction degrades multi-hop accuracy at 128k tokens.
        To preserve dormant cues, we introduce Spectral Gate, reaching 91.5\% accuracy (+3.2 percentage points over eviction) and 0.2189 mean $R^2$.
        \end{abstract}

        \section{Experiments}
        Spectral Gate improved accuracy over eviction across benchmarks (Table~\ref{tab:res}).

        \begin{table}[t]
          \caption{Retrieval accuracy and $R^2$ across models.}
          \label{tab:res}
          \begin{tabular}{lrr}
            \toprule
            Method & Retrieval Acc. & Test $R^2$ \\
            \midrule
            Eviction & 88.3 & 0.1950 \\
            Spectral Gate & 91.5 & 0.2106 \\
            \bottomrule
          \end{tabular}
        \end{table}
        """
        rep = lmv.lint_tex_source(tex)
        self.assertFalse(rep["clean"])
        # 91.5 matches directly, 3.2 matches 91.5 - 88.3, while stale 0.2189 is flagged!
        self.assertEqual([u["number"] for u in rep["abstract_unmatched_numbers"]], ["0.2189"])


class TestScientificComputingTools(unittest.TestCase):
    def test_scaffold_project_passes_strict_audit_and_rejects_bad_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proj_dir = Path(tmp) / "2026-spectral-solver"
            pkg_name = srp.derive_package_name(proj_dir.name)
            self.assertEqual(pkg_name, "proj_2026_spectral_solver")
            spec = srp.ScaffoldSpec(
                project_dir=proj_dir,
                dist_name="spectral-solver",
                pkg_name=pkg_name,
                author="Unit Test Lab",
                license_id="MIT",
                python_req=">=3.11",
            )
            written = srp.scaffold_project(spec)
            self.assertEqual(len(written), 18)
            self.assertTrue((proj_dir / "CITATION.cff").is_file())
            self.assertTrue((proj_dir / "data/raw/README.md").is_file())

            report = asp.audit_target(proj_dir)
            self.assertTrue(report["clean"], msg=json.dumps(report, indent=2))

            # Provenance writer must reject manuscript-numbered placeholder filenames
            prov_mod = load_module(
                "scaffolded_prov",
                proj_dir / "src" / pkg_name / "provenance.py",
            )
            with self.assertRaises(ValueError):
                prov_mod.write_provenance_json(
                    proj_dir / "results" / "fig_3a.json",
                    {"seed": 1},
                )

    def test_python_auditor_catches_google_style_and_numerical_hazards(self) -> None:
        bad_code = """
import os, sys
from math import exp
from .helpers import *

np.random.seed(42)

def run_sim(x: np.ndarray, p: float, a, b, c, d, e, f, cache=[]):
    assert p > 0
    if p < 0.0 or p > 1.0:
        raise ValueError("bad p")
    if not x:
        return None
    if p == 0.1:
        logger.info(f"hit {p}")
    fh = open("results/fig_2b.csv", "w")
    plt.savefig("results/plot.jpg")
    try:
        fh.write("x")
    except:
        pass
    try:
        fh.close()
    except Exception:
        pass
    return exp(p)
"""
        with tempfile.TemporaryDirectory() as tmp:
            bad_py = Path(tmp) / "bad_sim.py"
            bad_py.write_text(bad_code, encoding="utf-8")
            rep = asp.audit_target(bad_py)
            self.assertFalse(rep["clean"])
            rules = set(rep["counts"]["by_rule"].keys())
            expected_rules = {
                "missing_docstring",
                "multiple_imports_on_line",
                "symbol_import_instead_of_module",
                "relative_import",
                "wildcard_import",
                "unprotected_top_level_exec",
                "legacy_global_rng",
                "mutable_default_arg",
                "too_many_arguments",
                "assert_public_precondition",
                "nan_unsafe_range_check",
                "ambiguous_array_truthiness",
                "exact_float_equality",
                "fstring_in_logging",
                "unclosed_resource",
                "non_semantic_artifact_path",
                "jpeg_scientific_figure",
                "bare_except",
                "swallowed_broad_except",
            }
            self.assertTrue(
                expected_rules.issubset(rules),
                msg=f"Missing rules: {expected_rules - rules}",
            )

            # Inline # noqa suppression silences targeted lines cleanly
            suppressed_py = Path(tmp) / "suppressed.py"
            suppressed_py.write_text(
                '"""Clean module."""\n\nimport random\n\n\ndef sample() -> float:\n'
                '    """Samples with explicit noqa."""\n'
                "    return random.random()  # noqa: legacy_global_rng\n",
                encoding="utf-8",
            )
            rep_sup = asp.audit_target(suppressed_py)
            self.assertTrue(rep_sup["clean"], msg=json.dumps(rep_sup, indent=2))


class TestScientificIdeationTools(unittest.TestCase):
    def test_starter_template_passes_cleanly_and_ranks_pareto_front(self) -> None:
        rep = lri.audit_portfolio(lri._STARTER_TEMPLATE)
        self.assertTrue(rep["clean"], msg=json.dumps(rep, indent=2))
        self.assertEqual(rep["counts"]["pareto_optimal"], 2)
        md = lri.render_markdown_brief(lri._STARTER_TEMPLATE, rep)
        self.assertIn("Tier 1 (Optimal)", md)
        self.assertIn("Experimentum Crucis", md)

    def test_ideation_linter_flags_slop_pet_hypothesis_and_dominated_traps(self) -> None:
        flawed_portfolio = {
            "topic": "Test topic",
            "constraints": {"max_crucial_test_hours": 4.0},
            "candidates": [
                {
                    "id": "slop_1",
                    "title": "Semantic Resonance Pivot Constellation for Reasoning",
                    "archetype": "algorithmic_mechanism",
                    "c_abt": "Large language models use transformers and we add a new module and benchmark it.",
                    "attack_vector": "too short",
                    "competing_hypotheses": ["Only my pet hypothesis H1 works."],
                    "proposed_operator": "Compute quantum resonance thought lattice across layers.",
                    "compute_matched_baseline": "Greedy decoding baseline with matched tokens.",
                    "verified_prior_art": ["Some paper I vaguely remember from 2023"],
                    "crucial_experiment": {
                        "setup": "Full benchmark",
                        "metric": "Accuracy",
                        "kill_condition": "none",
                        "estimated_hours": 48.0,
                    },
                    "cloud_pivot_plan": "Analyze failure modes carefully and adjust.",
                    "scores": {
                        "knowledge_gain": 3.5,
                        "feasibility": 4.0,
                        "attack_clarity": 4.0,
                        "scoop_safety": 5.0,
                    },
                },
                {
                    "id": "slop_2",
                    "title": "Semantic Resonance Pivot Constellation for Better Reasoning",
                    "archetype": "algorithmic_mechanism",
                    "c_abt": "Models struggle on hard tasks, however our module fixes it.",
                    "attack_vector": "Valid twenty-plus character attack description here.",
                    "competing_hypotheses": ["H1: works", "H2: baseline works"],
                    "proposed_operator": "Compute quantum resonance thought lattice across transformer layers.",
                    "compute_matched_baseline": "Matched token budget self-consistency.",
                    "verified_prior_art": ["arXiv:2203.11171"],
                    "crucial_experiment": {
                        "setup": "100 GSM8K items",
                        "metric": "Exact match",
                        "kill_condition": "Kill if <2% gain over self-consistency at k=5.",
                        "estimated_hours": 1.0,
                    },
                    "cloud_pivot_plan": "Pivot to error taxonomy of self-consistency votes.",
                    "scores": {
                        "knowledge_gain": 8.0,
                        "feasibility": 8.5,
                        "attack_clarity": 8.0,
                        "scoop_safety": 7.5,
                    },
                },
            ],
        }
        rep = lri.audit_portfolio(flawed_portfolio)
        self.assertFalse(rep["clean"])
        codes = {iss["code"] for iss in rep["issues"]}
        expected = {
            "MISSING_ABT_CONTRADICTION",
            "SINGLE_PET_HYPOTHESIS",
            "VAGUE_OR_MISSING_SPEC",
            "UNGROUNDED_PRIOR_ART",
            "MISSING_KILL_CONDITION",
            "CRUCIAL_TEST_TOO_SLOW",
            "ANTHROPOMORPHIC_OR_BUZZWORD_SLOP",
            "HARD_LOW_GAIN_TRAP",
            "DUPLICATE_IDEA_PAIR",
        }
        self.assertTrue(expected.issubset(codes), msg=f"Missing codes: {expected - codes}")
        # slop_2 (8.5, 8.0) strictly dominates slop_1 (4.0, 3.5) -> tiers 1 and 2!
        by_id = {r["id"]: r for r in rep["ranked_candidates"]}
        self.assertEqual(by_id["slop_2"]["pareto_tier"], 1)
        self.assertEqual(by_id["slop_1"]["pareto_tier"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
