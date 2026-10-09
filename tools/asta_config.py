#!/usr/bin/env python3
"""Report whether Claude Code's Asta MCP server is configured with an API key, without printing the key.

Usage: python3 tools/asta_config.py [--quiet]

`claude mcp add ... --header "x-api-key: $ASTA_API_KEY"` expands the variable when the server is added, so the key
lives in the stored MCP config, not in the environment of later sessions. This reads that config, in Claude Code's
order of precedence: local scope (~/.claude.json, under this project), project scope (.mcp.json), user scope
(~/.claude.json). It prints the scope found and whether an `x-api-key` header is set, and exits 1 if there is no Asta
server or no key. --quiet prints only a warning, and nothing when all is well (for the session-start hook).

Nothing is sent anywhere; the key is never printed.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def find():
    home = load(Path.home() / ".claude.json")
    scopes = [
        ("local", home.get("projects", {}).get(str(ROOT), {}).get("mcpServers", {})),
        ("project", load(ROOT / ".mcp.json").get("mcpServers", {})),
        ("user", home.get("mcpServers", {})),
    ]
    for scope, servers in scopes:
        if "asta" in servers:
            return scope, servers["asta"]
    return None, None


def main(argv):
    quiet = "--quiet" in argv
    scope, server = find()
    if server is None:
        print("WARNING: no Asta MCP server is configured; see docs/external_services.md, \"Configuration\"")
        return 1
    key = next((v for k, v in (server.get("headers") or {}).items() if k.lower() == "x-api-key"), "")
    # An unexpanded "$ASTA_API_KEY" or "${ASTA_API_KEY}" left in a project .mcp.json is expanded by Claude Code
    # from the environment at startup.
    if key.lstrip("${").startswith("ASTA_API_KEY"):
        import os
        key = os.environ.get("ASTA_API_KEY", "")
    if not key.strip():
        print(f"WARNING: the Asta MCP server ({scope} scope) has no x-api-key header; anonymous rate limits apply, "
              "and a pass halts at preflight (H1)")
        return 1
    if not quiet:
        print(f"Asta: configured ({scope} scope, {server.get('url')}), x-api-key set")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
