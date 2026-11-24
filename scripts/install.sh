#!/usr/bin/env bash
set -euo pipefail

# Cross-Agent Installer, Global Pinner & Health Check Script for scientific-research-skills
# Supports: Antigravity / Gemini CLI, Claude Code, Codex CLI, and Cursor.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROUTER_BLOCK_FILE="$REPO_ROOT/rules/GLOBAL_RESEARCH_ROUTER.md"
TARGET="antigravity"
MODE="install"
PIN_GLOBAL="false"

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--target antigravity|claude|codex|cursor|all] [--pin-global] [--check]

Options:
  --target, -t       Destination agent runtime (default: antigravity)
  --pin-global, -p   Pin the Default Scientific Research Router into global Always-On rules
                     (~/.gemini/config/rules/AGENTS.md, ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)
  --check, -c        Verify prerequisites (uv), installed plugins/skills, and global pin state
  --help, -h         Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target|-t)
      TARGET="${2:-}"
      shift 2
      ;;
    --pin-global|-p)
      PIN_GLOBAL="true"
      shift
      ;;
    --check|-c)
      MODE="check"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

upsert_router_block() {
  local label="$1"
  local rule_file="$2"
  local max_bytes="$3"

  mkdir -p "$(dirname "$rule_file")"
  python3 - "$label" "$rule_file" "$ROUTER_BLOCK_FILE" "$max_bytes" <<'PY'
import pathlib
import re
import sys

label, rule_path_s, block_path_s, max_bytes_s = sys.argv[1:5]
rule_path = pathlib.Path(rule_path_s)
block = pathlib.Path(block_path_s).read_text(encoding="utf-8").strip()
max_bytes = int(max_bytes_s)

existing = rule_path.read_text(encoding="utf-8") if rule_path.exists() else ""
pattern = re.compile(
    r"<!-- scientific-research-skills:start -->.*?<!-- scientific-research-skills:end -->",
    re.DOTALL,
)

if pattern.search(existing):
    updated = pattern.sub(lambda _m: block, existing)
else:
    sep = "\n\n---\n\n" if existing.strip() else ""
    updated = existing.rstrip() + sep + block + "\n"

encoded_len = len(updated.encode("utf-8"))
if max_bytes > 0 and encoded_len > max_bytes:
    print(
        f"[{label}] Skipped modifying {rule_path} ({encoded_len} B > {max_bytes} B cap; "
        "skills remain globally available via skills directory)."
    )
    raise SystemExit(0)

rule_path.write_text(updated, encoding="utf-8")
print(f"[{label}] Pinned global research router -> {rule_path} ({encoded_len} bytes)")
PY
}

if [[ "$MODE" == "check" ]]; then
  echo "=== Prerequisites ==="
  if command -v uv >/dev/null 2>&1; then
    echo "  [OK] uv: $(uv --version)"
  else
    echo "  [WARN] uv not found on PATH (install: curl -LsSf https://astral.sh/uv/install.sh | sh)"
  fi
  echo "=== Installed Locations ==="
  for d in \
    "$HOME/.gemini/config/plugins/scientific-ideation" \
    "$HOME/.gemini/config/plugins/research-literature" \
    "$HOME/.gemini/config/plugins/scientific-computing" \
    "$HOME/.gemini/config/plugins/scientific-writing" \
    "$HOME/.gemini/config/plugins/llm-review-triage" \
    "$HOME/.claude/skills/scientific-ideation" \
    "$HOME/.claude/skills/scholarly-graph-audit" \
    "$HOME/.claude/skills/scientific-computing" \
    "$HOME/.claude/skills/scientific-writing" \
    "$HOME/.claude/skills/llm-review-triage" \
    "$HOME/.codex/skills/scientific-ideation" \
    "$HOME/.codex/skills/scholarly-graph-audit" \
    "$HOME/.codex/skills/scientific-computing" \
    "$HOME/.codex/skills/scientific-writing" \
    "$HOME/.codex/skills/llm-review-triage" \
    "$HOME/.cursor/skills/scientific-ideation" \
    "$HOME/.cursor/skills/scholarly-graph-audit" \
    "$HOME/.cursor/skills/scientific-computing" \
    "$HOME/.cursor/skills/scientific-writing" \
    "$HOME/.cursor/skills/llm-review-triage"; do
    if [[ -d "$d" ]]; then
      echo "  [PRESENT] $d"
    fi
  done
  echo "=== Global Always-On Router Pin State ==="
  for rf in \
    "$HOME/.gemini/config/rules/AGENTS.md" \
    "$HOME/.claude/CLAUDE.md" \
    "$HOME/.codex/AGENTS.md"; do
    if [[ -f "$rf" ]] && grep -q "scientific-research-skills:start" "$rf"; then
      echo "  [PINNED] $rf"
    fi
  done
  exit 0
fi

install_antigravity() {
  local dest="$HOME/.gemini/config/plugins"
  mkdir -p "$dest"
  for p in scientific-ideation research-literature scientific-computing scientific-writing llm-review-triage; do
    rm -rf "$dest/$p"
    cp -R "$REPO_ROOT/plugins/$p" "$dest/$p"
    find "$dest/$p" -name "__pycache__" -type d -prune -exec rm -rf {} +
    echo "[antigravity] Synced plugin -> $dest/$p"
  done
  if [[ "$PIN_GLOBAL" == "true" ]]; then
    upsert_router_block "antigravity" "$HOME/.gemini/config/rules/AGENTS.md" 24000
  fi
}

install_flat_skills() {
  local label="$1"
  local dest="$2"
  mkdir -p "$dest"
  for skill_dir in \
    "$REPO_ROOT/plugins/scientific-ideation/skills/scientific-ideation" \
    "$REPO_ROOT/plugins/research-literature/skills/scholarly-graph-audit" \
    "$REPO_ROOT/plugins/research-literature/skills/literature-evidence-workflow" \
    "$REPO_ROOT/plugins/scientific-computing/skills/scientific-computing" \
    "$REPO_ROOT/plugins/scientific-writing/skills/scientific-writing" \
    "$REPO_ROOT/plugins/scientific-writing/skills/scientific-figures" \
    "$REPO_ROOT/plugins/llm-review-triage/skills/llm-review-triage"; do
    local sname
    sname="$(basename "$skill_dir")"
    rm -rf "$dest/$sname"
    cp -R "$skill_dir" "$dest/$sname"
    find "$dest/$sname" -name "__pycache__" -type d -prune -exec rm -rf {} +
    echo "[$label] Synced skill -> $dest/$sname"
  done
}

case "$TARGET" in
  antigravity)
    install_antigravity
    ;;
  claude)
    install_flat_skills "claude" "$HOME/.claude/skills"
    if [[ "$PIN_GLOBAL" == "true" ]]; then
      upsert_router_block "claude" "$HOME/.claude/CLAUDE.md" 0
    fi
    ;;
  codex)
    install_flat_skills "codex" "$HOME/.codex/skills"
    if [[ "$PIN_GLOBAL" == "true" ]]; then
      upsert_router_block "codex" "$HOME/.codex/AGENTS.md" 32768
    fi
    ;;
  cursor)
    install_flat_skills "cursor" "$HOME/.cursor/skills"
    ;;
  all)
    install_antigravity
    install_flat_skills "claude" "$HOME/.claude/skills"
    if [[ "$PIN_GLOBAL" == "true" ]]; then
      upsert_router_block "claude" "$HOME/.claude/CLAUDE.md" 0
    fi
    install_flat_skills "codex" "$HOME/.codex/skills"
    if [[ "$PIN_GLOBAL" == "true" ]]; then
      upsert_router_block "codex" "$HOME/.codex/AGENTS.md" 32768
    fi
    install_flat_skills "cursor" "$HOME/.cursor/skills"
    ;;
  *)
    echo "Unsupported target: $TARGET" >&2
    usage
    exit 1
    ;;
esac

echo "Done."
