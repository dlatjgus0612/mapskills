#!/usr/bin/env bash
# mapskills installer: links this repo's skills into Claude Code and Codex.
# Adds symlinks only. Never overwrites or edits existing skills, CLAUDE.md or AGENTS.md.
#   ./install.sh            install
#   ./install.sh --remove   remove the links this script made
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")
SKILLS=(map map-set map-check ui-effects-glossary)

for t in "${TARGETS[@]}"; do
  for s in "${SKILLS[@]}"; do
    dst="$t/$s"; src="$ROOT/skills/$s"
    if [[ "${1:-}" == "--remove" ]]; then
      if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then rm "$dst"; echo "removed $dst"; fi
      continue
    fi
    if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then continue; fi
    if [[ -e "$dst" || -L "$dst" ]]; then echo "skip  $dst (already exists, left untouched)"; continue; fi
    mkdir -p "$t"; ln -s "$src" "$dst"; echo "link  $dst"
  done
done
[[ "${1:-}" == "--remove" ]] && exit 0
mkdir -p "$HOME/.mapskills"
echo
echo "Done. Start a new Claude Code / Codex session, then try:  /map   /map rcm <task>   /map-set   /map-check"
echo "Usage counting is on and stays in ~/.mapskills. Turn off: python3 $ROOT/skills/map/scripts/mapskills.py config usage off"
