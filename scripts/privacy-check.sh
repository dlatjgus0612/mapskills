#!/usr/bin/env bash
# Run before every commit. Fails if personal paths, emails, hostnames or secrets appear in tracked files.
set -uo pipefail
cd "$(dirname "$0")/.."
files=$(git ls-files 2>/dev/null || find . -type f -not -path './.git/*')
pat='/Users/[A-Za-z]|/home/[a-z]+/|C:\\Users\\|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|AKIA[0-9A-Z]{16}|sk_live_|sk-ant-|ghp_[A-Za-z0-9]{20,}|gho_|xox[bp]-|-----BEGIN [A-Z ]*PRIVATE KEY|eyJ[A-Za-z0-9_-]{20,}\.'
extra="${MAPSKILLS_PRIVATE_WORDS:-}"   # e.g. export MAPSKILLS_PRIVATE_WORDS='myname|myserver'
[[ -n "$extra" ]] && pat="$pat|$extra"
hits=$(echo "$files" | grep -v '^scripts/privacy-check.sh$' | xargs grep -nIE "$pat" 2>/dev/null | grep -vE 'noreply@|example\.(com|org)' || true)
if [[ -n "$hits" ]]; then echo "$hits"; echo "privacy-check: FAILED"; exit 1; fi
echo "privacy-check: ok"
