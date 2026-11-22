#!/usr/bin/env bash
set -euo pipefail

# Cross-Agent Installer, Sync & Health Check Script for scientific-research-skills
# Supports: Antigravity / Gemini CLI, Claude Code, Codex CLI, and Cursor.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="antigravity"
MODE="install"

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--target antigravity|claude|codex|cursor|all] [--check]

Options:
  --target, -t   Destination agent runtime (default: antigravity)
  --check, -c    Verify prerequisites (uv, python3) and check installed skill directories
  --help, -h     Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target|-t)
      TARGET="${2:-}"
      shift 2
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

if [[ "$MODE" == "check" ]]; then
  echo "=== Prerequisites ==="
  if command -v uv >/dev/null 2>&1; then
    echo "  [OK] uv: $(uv --version)"
  else
    echo "  [WARN] uv not found on PATH (install: curl -LsSf https://astral.sh/uv/install.sh | sh)"
  fi
  echo "=== Installed Locations ==="
  for d in \
    "$HOME/.gemini/config/plugins/research-literature" \
    "$HOME/.gemini/config/plugins/scientific-writing" \
    "$HOME/.claude/skills/scholarly-graph-audit" \
    "$HOME/.codex/skills/scholarly-graph-audit" \
    "$HOME/.cursor/skills/scholarly-graph-audit"; do
    if [[ -d "$d" ]]; then
      echo "  [PRESENT] $d"
    fi
  done
  exit 0
fi

install_antigravity() {
  local dest="$HOME/.gemini/config/plugins"
  mkdir -p "$dest"
  for p in research-literature scientific-writing; do
    rm -rf "$dest/$p"
    cp -R "$REPO_ROOT/plugins/$p" "$dest/$p"
    echo "[antigravity] Synced plugin -> $dest/$p"
  done
}

install_flat_skills() {
  local label="$1"
  local dest="$2"
  mkdir -p "$dest"
  for skill_dir in \
    "$REPO_ROOT/plugins/research-literature/skills/scholarly-graph-audit" \
    "$REPO_ROOT/plugins/research-literature/skills/literature-evidence-workflow" \
    "$REPO_ROOT/plugins/scientific-writing/skills/scientific-writing" \
    "$REPO_ROOT/plugins/scientific-writing/skills/scientific-figures"; do
    local sname
    sname="$(basename "$skill_dir")"
    rm -rf "$dest/$sname"
    cp -R "$skill_dir" "$dest/$sname"
    echo "[$label] Synced skill -> $dest/$sname"
  done
}

case "$TARGET" in
  antigravity)
    install_antigravity
    ;;
  claude)
    install_flat_skills "claude" "$HOME/.claude/skills"
    ;;
  codex)
    install_flat_skills "codex" "$HOME/.codex/skills"
    ;;
  cursor)
    install_flat_skills "cursor" "$HOME/.cursor/skills"
    ;;
  all)
    install_antigravity
    install_flat_skills "claude" "$HOME/.claude/skills"
    install_flat_skills "codex" "$HOME/.codex/skills"
    install_flat_skills "cursor" "$HOME/.cursor/skills"
    ;;
  *)
    echo "Unsupported target: $TARGET" >&2
    usage
    exit 1
    ;;
esac

echo "Done."
