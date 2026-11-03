#!/usr/bin/env bash
# mapskills installer: links this repo's skills into your coding agents' skill folders.
# Adds symlinks only. Never overwrites or edits existing skills, CLAUDE.md or AGENTS.md.
#   ./install.sh                         Claude Code + Codex (and every agent sharing ~/.agents/skills)
#   ./install.sh --agents claude-code,codex,cursor,gemini-cli
#   ./install.sh --list                  show detected agents
#   ./install.sh --remove                remove the links this installer made
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MS=(python3 "$ROOT/skills/map/scripts/mapskills.py")
case "${1:-}" in
  --list)   "${MS[@]}" agents; exit 0 ;;
  --remove) "${MS[@]}" self-install --remove; exit 0 ;;
  --agents) "${MS[@]}" config agents "${2:?usage: --agents a,b,c}" >/dev/null ;;
esac
"${MS[@]}" self-install
echo
echo "Done. Start a new agent session, then try:  /map   /map-rcm <task>   /map-set   /map-check   /map-rule"
echo "Usage counting is on and stays in ~/.mapskills. Turn off: ${MS[*]} config usage off"
