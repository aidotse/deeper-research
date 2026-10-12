#!/usr/bin/env bash
# The simulation runner and its blind scratch copy (docs/audits.md, "Roles").
#
#   runner.sh build                     rebuild the copy from the repo's working tree. Run it after restoring a
#                                       checkpoint, before every launch. The copy has no .audits/, docs/roadmap.md,
#                                       docs/audits.md or tests/, and a one-commit git history of its own.
#   runner.sh run <prompt> <out.json> [<session-id>]
#                                       launch a headless Claude Code session in the copy, with the prompt file on
#                                       stdin and the fixed tool allowlist below; its JSON result goes to <out.json>.
#                                       With a session id, resume that session instead, e.g. with a halt's decision.
#                                       Limits (docs/audits.md, "Limits"): LIMIT_TIME (default 3h, for timeout) and
#                                       LIMIT_TURNS (default 300, the runner's own turns), set in the environment.
#   runner.sh collect <topic>           after a run: list every file the runner wrote or deleted in the copy, then
#                                       copy the topic's files back into the repo (survey, output, bib, graphs).
#                                       A change outside them is a finding; it is listed, never copied back.
set -euo pipefail
REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SCRATCH="${SCRATCH:-/tmp/deeper-research-sim}"
LIMIT_TIME="${LIMIT_TIME:-3h}"
LIMIT_TURNS="${LIMIT_TURNS:-300}"

# What a pass's main session and its agents need, and nothing else. A call outside it is denied, and
# shows in the runner's report as a tool failure.
ALLOWED="Agent,ToolSearch,Read,Write,Edit,Grep,Glob,WebSearch,WebFetch,mcp__asta__*"
ALLOWED+=",Bash(python3:*),Bash(uv run:*),Bash(mdformat:*)"
ALLOWED+=",Bash(ls:*),Bash(wc:*),Bash(head:*),Bash(tail:*),Bash(grep:*),Bash(jq:*)"

case "${1:-}" in
build)
  rm -rf "$SCRATCH"
  mkdir -p "$SCRATCH"
  rsync -a \
    --exclude .git --exclude .audits --exclude tests \
    --exclude docs/roadmap.md --exclude docs/audits.md \
    --exclude .venv --exclude .serena --exclude __pycache__ \
    --exclude .claude/worktrees --exclude .claude/settings.local.json \
    "$REPO"/ "$SCRATCH"/
  cd "$SCRATCH"
  git init -q
  git add -A
  git -c user.name=runner -c user.email=runner@localhost commit -qm "scratch copy for a simulation runner"
  echo "scratch copy at $SCRATCH: $(git log --oneline | head -1)"
  ;;
run)
  PROMPT="$(realpath "${2:?usage: runner.sh run <prompt> <out.json> [<session-id>]}")"
  OUT="$(realpath -m "${3:?usage: runner.sh run <prompt> <out.json> [<session-id>]}")"
  RESUME=()
  if [ -n "${4:-}" ]; then RESUME=(--resume "$4"); fi
  [ -d "$SCRATCH/.git" ] || { echo "no scratch copy at $SCRATCH: run build first" >&2; exit 1; }
  mkdir -p "$(dirname "$OUT")"
  cd "$SCRATCH"
  # --allowedTools takes several values, so the prompt goes on stdin, never as an argument after it
  CODE=0
  timeout "$LIMIT_TIME" claude -p --output-format json --max-turns "$LIMIT_TURNS" "${RESUME[@]}" \
    --allowedTools "$ALLOWED" < "$PROMPT" > "$OUT" || CODE=$?
  if [ "$CODE" = 124 ]; then
    echo "LIMIT: wall-clock time ($LIMIT_TIME) reached; the run was stopped. Its session's transcript is the record."
    exit 2
  fi
  python3 - "$OUT" <<'EOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except ValueError:
    sys.exit(f"no JSON result in {sys.argv[1]}")
keys = ("session_id", "subtype", "is_error", "num_turns", "duration_ms", "total_cost_usd")
print(" ".join(f"{k}={d.get(k)}" for k in keys))
if d.get("api_error"):
    print(f"API ERROR: {d.get('api_error')} ({d.get('api_error_status')}): {d.get('result')}")
    print("Not a finding: the run did not get to work. Rerun the same iteration once the error clears.")
if d.get("subtype") == "error_max_turns":
    print("LIMIT: the runner's turns reached their limit; the run was stopped.")
EOF
  ;;
collect)
  TOPIC="${2:?usage: runner.sh collect <topic>}"
  cd "$SCRATCH"
  # every file written since the build, ignored files included; deletions show in git status
  # .serena/ and __pycache__/ are written by the user-level Serena server and by Python, not by the runner
  CHANGED="$(find . \( -path ./.git -o -path ./.serena -o -name __pycache__ \) -prune -o -type f -newer .git/HEAD -print |
    sed 's#^\./##' | sort)"
  echo "written in the copy since the build:"
  echo "${CHANGED:-none}" | sed 's/^/  /'
  echo "deleted:"
  git status --short | grep '^ D' | sed 's/^/  /' || echo "  none"
  echo "outside the topic's files:"
  echo "$CHANGED" | grep -vE "^((surveys|outputs)/$TOPIC\.md|bib/$TOPIC\.bib|graphs/$TOPIC/.*|runner-report\.md)$" |
    grep . | sed 's/^/  /' || echo "  none"
  for f in "surveys/$TOPIC.md" "outputs/$TOPIC.md" "bib/$TOPIC.bib"; do
    if [ -e "$f" ]; then cp "$f" "$REPO/$f"; fi
  done
  if [ -d "graphs/$TOPIC" ]; then
    mkdir -p "$REPO/graphs/$TOPIC"
    rsync -a --delete "graphs/$TOPIC/" "$REPO/graphs/$TOPIC/"
  fi
  echo "copied the topic's files back to $REPO"
  ;;
*)
  sed -n '2,15p' "$0"
  exit 1
  ;;
esac
