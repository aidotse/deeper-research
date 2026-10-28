"""Report whether Claude Code's Asta MCP server is configured with an API key, without printing the key.

Usage: uv run python -m deeper_research.asta_config [--quiet]

`claude mcp add ... --header "x-api-key: $ASTA_API_KEY"` expands the variable when the server is added, so the key
lives in the stored MCP config, not in the environment of later sessions. This reads that config, in Claude Code's
order of precedence: local scope (~/.claude.json, under this project), project scope (.mcp.json), user scope
(~/.claude.json). It prints the scope found and whether an `x-api-key` header is set, and exits 1 if there is no Asta
server or no key. --quiet prints only a warning, and nothing when all is well (for the session-start hook).

Nothing is sent anywhere; the key is never printed.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


# Parsed JSON is as loose as the file: Claude Code's config, or an empty object where it is missing or unreadable.
def load(path: Path) -> Any:  # noqa: ANN401
    """Return a JSON file's content, or an empty dict where the file is missing or not JSON."""
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def find() -> tuple[str, dict[str, Any]] | tuple[None, None]:
    """Return the scope and config of the Asta MCP server that takes precedence, or (None, None) if there is none."""
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


def main(argv: list[str]) -> int:
    """Report whether the Asta server is configured with a key: return 0 if it is, 1 if not."""
    quiet = "--quiet" in argv
    scope, server = find()
    if server is None:
        print('WARNING: no Asta MCP server is configured; see docs/external_services.md, "Configuration"')
        return 1
    key = next((v for k, v in (server.get("headers") or {}).items() if k.lower() == "x-api-key"), "")
    # An unexpanded "$ASTA_API_KEY" or "${ASTA_API_KEY}" left in a project .mcp.json is expanded by Claude Code
    # from the environment at startup.
    if key.lstrip("${").startswith("ASTA_API_KEY"):
        key = os.environ.get("ASTA_API_KEY", "")
    if not key.strip():
        print(
            f"WARNING: the Asta MCP server ({scope} scope) has no x-api-key header; anonymous rate limits apply, "
            "and a pass halts at preflight (H1)"
        )
        return 1
    if not quiet:
        print(f"Asta: configured ({scope} scope, {server.get('url')}), x-api-key set")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
