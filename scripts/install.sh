#!/usr/bin/env bash
set -euo pipefail

# Cross-Agent Installer & Sync Script for scientific-research-skills
# Supports: Antigravity / Gemini CLI, Claude Code, Codex CLI, and Cursor.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="antigravity"

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--target antigravity|claude|codex|cursor|all]

Targets:
  antigravity  Install/sync bundled plugins into ~/.gemini/config/plugins/ (default)
  claude       Install skills into ~/.claude/skills/
  codex        Install skills into ~/.codex/skills/
  cursor       Install skills into ~/.cursor/skills/
  all          Install across all detected agent directories above
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target|-t)
      TARGET="${2:-}"
      shift 2
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
