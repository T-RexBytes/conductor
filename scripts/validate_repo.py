#!/usr/bin/env python3
"""Static checks for the Conductor repository.

Enforces the manifest, frontmatter, routing and non-interference rules in
docs/BUILD-SPEC.md section 10.2. Standard library plus PyYAML; no network access.

Usage:
    python scripts/validate_repo.py [--root PATH]

Exit code 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

PLUGIN_NAME = "conductor"
INTERNAL_MARKER = "Internal to the conductor plugin"

# Documented Claude Code skill frontmatter keys (code.claude.com/docs/en/skills).
SKILL_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools", "disallowed-tools",
    "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
    "metadata", "license", "compatibility",
}
# Frontmatter keys supported for plugin agents (code.claude.com/docs/en/plugins/components).
AGENT_KEYS = {
    "name", "description", "model", "effort", "maxTurns", "tools", "disallowedTools",
    "skills", "memory", "background", "omitClaudeMd", "isolation", "color", "experimental",
}
# Keys Conductor agents must never use (ignored for plugin agents, or break non-interference).
AGENT_BANNED_KEYS = {"tools", "permissionMode", "hooks", "mcpServers", "initialPrompt"}

EFFORT_LEVELS = {"low", "medium", "high", "xhigh", "max"}
ALLOWED_MODELS = {"haiku", "sonnet", "opus"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
READ_ONLY_DENY = {"Write", "Edit", "NotebookEdit", "Agent"}
EXPECTED_AGENTS = {"scout", "worker", "builder", "builder-plus", "architect", "watcher"}

# Paths that would give the plugin session-wide side effects (BUILD-SPEC N2, N3).
FORBIDDEN_PLUGIN_PATHS = [
    "hooks", "settings.json", "monitors", ".mcp.json", ".lsp.json", "bin", "CLAUDE.md",
]

SKILL_RULE_MARKERS = ["**No probing.**", "**Leave the user's setup alone.**"]
SKILL_MAX_LINES = 500
DESCRIPTION_MAX_CHARS = 1536
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_REF = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([\w./-]+\.(?:md|json))")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")


def load_json(path: Path, rep: Report) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.error(str(path), "file not found")
        return None
    except json.JSONDecodeError as exc:
        rep.error(str(path), f"invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        rep.error(str(path), "top level must be an object")
        return None
    return data


def split_frontmatter(path: Path, rep: Report) -> tuple[dict[str, Any], str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        rep.error(str(path), "missing YAML frontmatter (file must start with ---)")
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        rep.error(str(path), "unterminated YAML frontmatter")
        return None
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as exc:
        rep.error(str(path), f"invalid YAML frontmatter: {exc}")
        return None
    if not isinstance(meta, dict):
        rep.error(str(path), "frontmatter must be a mapping")
        return None
    return meta, text[end + 5:]


def tool_list(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {part.strip() for part in value.split(",") if part.strip()}
    if isinstance(value, list):
        return {str(part).strip() for part in value}
    return set()


def check_manifests(root: Path, rep: Report) -> tuple[Path | None, dict[str, Any] | None]:
    market = load_json(root / ".claude-plugin" / "marketplace.json", rep)
    if market is None:
        return None, None
    where = ".claude-plugin/marketplace.json"
    for key in ("name", "owner", "plugins"):
        if key not in market:
            rep.error(where, f"missing required field '{key}'")
    plugins = market.get("plugins") or []
    entry = next((p for p in plugins if isinstance(p, dict) and p.get("name") == PLUGIN_NAME), None)
    if entry is None:
        rep.error(where, f"no plugin entry named '{PLUGIN_NAME}'")
        return None, None
    source = entry.get("source")
    if not isinstance(source, str) or not source.startswith("./"):
        rep.error(where, "plugin source must be a relative path starting with ./")
        return None, None
    if ".." in Path(source).parts:
        rep.error(where, "plugin source must not contain '..'")
        return None, None
    plugin_dir = (root / source).resolve()
    if not plugin_dir.is_dir():
        rep.error(where, f"plugin source does not exist: {source}")
        return None, None

    manifest = load_json(plugin_dir / ".claude-plugin" / "plugin.json", rep)
    if manifest is None:
        return plugin_dir, None
    mwhere = "plugin.json"
    if manifest.get("name") != entry.get("name"):
        rep.error(mwhere, "name must equal the marketplace entry name")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        rep.error(mwhere, "version must be semver (X.Y.Z)")
    if "hooks" in manifest:
        rep.error(mwhere, "plugin must not declare hooks (non-interference N2)")
    for key in ("settings", "mcpServers", "lspServers", "monitors"):
        if key in manifest:
            rep.error(mwhere, f"plugin must not declare '{key}' (non-interference N3)")
    if isinstance(version, str):
        changelog = root / "CHANGELOG.md"
        if not changelog.exists() or f"## [{version}]" not in changelog.read_text(encoding="utf-8"):
            rep.error("CHANGELOG.md", f"missing section '## [{version}]'")
    return plugin_dir, manifest


def check_forbidden_paths(plugin_dir: Path, rep: Report) -> None:
    for rel in FORBIDDEN_PLUGIN_PATHS:
        if (plugin_dir / rel).exists():
            rep.error(f"plugins/{PLUGIN_NAME}/{rel}", "forbidden in the plugin (non-interference)")


def check_skill(plugin_dir: Path, rep: Report) -> None:
    skill = plugin_dir / "skills" / "conductor" / "SKILL.md"
    where = f"plugins/{PLUGIN_NAME}/skills/conductor/SKILL.md"
    if not skill.exists():
        rep.error(where, "file not found")
        return
    parsed = split_frontmatter(skill, rep)
    if parsed is None:
        return
    meta, body = parsed
    unknown = set(meta) - SKILL_KEYS
    if unknown:
        rep.error(where, f"undocumented frontmatter keys: {sorted(unknown)}")
    if meta.get("disable-model-invocation") is not True:
        rep.error(where, "disable-model-invocation must be true (non-interference N1)")
    if "hooks" in meta:
        rep.error(where, "skill hooks persist for the session; not allowed (N2)")
    if "disallowed-tools" in meta:
        rep.error(where, "disallowed-tools would hide the user's tools (N5)")
    if meta.get("model") not in ALLOWED_MODELS:
        rep.error(where, f"model must be one of {sorted(ALLOWED_MODELS)}")
    if meta.get("effort") not in EFFORT_LEVELS:
        rep.error(where, f"effort must be one of {sorted(EFFORT_LEVELS)}")
    description = str(meta.get("description", "")) + str(meta.get("when_to_use", ""))
    if not description.strip():
        rep.error(where, "description is required")
    if len(description) > DESCRIPTION_MAX_CHARS:
        rep.error(where, f"description + when_to_use exceeds {DESCRIPTION_MAX_CHARS} chars")
    lines = skill.read_text(encoding="utf-8").count("\n") + 1
    if lines > SKILL_MAX_LINES:
        rep.error(where, f"{lines} lines; keep SKILL.md under {SKILL_MAX_LINES}")
    for marker in SKILL_RULE_MARKERS:
        if marker not in body:
            rep.error(where, f"hard rule marker missing: {marker}")
    for ref in sorted(set(SKILL_REF.findall(body))):
        if not (skill.parent / ref).is_file():
            rep.error(where, f"referenced file does not exist: {ref}")


def check_agents(plugin_dir: Path, rep: Report) -> dict[str, dict[str, Any]]:
    agents_dir = plugin_dir / "agents"
    found: dict[str, dict[str, Any]] = {}
    if not agents_dir.is_dir():
        rep.error(f"plugins/{PLUGIN_NAME}/agents", "directory not found")
        return found
    for path in sorted(agents_dir.rglob("*.md")):
        where = f"plugins/{PLUGIN_NAME}/agents/{path.relative_to(agents_dir)}"
        parsed = split_frontmatter(path, rep)
        if parsed is None:
            continue
        meta, body = parsed
        name = meta.get("name")
        if name != path.stem:
            rep.error(where, f"name '{name}' must match the file name '{path.stem}'")
        unknown = set(meta) - AGENT_KEYS - AGENT_BANNED_KEYS
        if unknown:
            rep.error(where, f"undocumented frontmatter keys: {sorted(unknown)}")
        banned = set(meta) & AGENT_BANNED_KEYS
        if banned:
            rep.error(where, f"banned keys: {sorted(banned)}")
        if not str(meta.get("description", "")).startswith(INTERNAL_MARKER):
            rep.error(where, f"description must start with '{INTERNAL_MARKER}' (N4)")
        if meta.get("model") not in ALLOWED_MODELS:
            rep.error(where, f"model must be one of {sorted(ALLOWED_MODELS)}")
        if meta.get("effort") not in EFFORT_LEVELS:
            rep.error(where, f"effort must be one of {sorted(EFFORT_LEVELS)}")
        max_turns = meta.get("maxTurns")
        if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns < 1:
            rep.error(where, "maxTurns must be a positive integer")
        if "color" in meta and meta["color"] not in COLORS:
            rep.error(where, f"color must be one of {sorted(COLORS)}")
        denied = tool_list(meta.get("disallowedTools"))
        if "Agent" not in denied:
            rep.error(where, "disallowedTools must include Agent (N10)")
        if name in {"scout", "watcher"} and not READ_ONLY_DENY <= denied:
            rep.error(where, f"read-only agent must deny {sorted(READ_ONLY_DENY)}")
        marker = "CONDUCTOR-VERDICT" if name == "watcher" else "CONDUCTOR-REPORT"
        if marker not in body:
            rep.error(where, f"body must define the {marker} output contract")
        if isinstance(name, str):
            found[name] = meta
    missing = EXPECTED_AGENTS - set(found)
    if missing:
        rep.error(f"plugins/{PLUGIN_NAME}/agents", f"missing agents: {sorted(missing)}")
    return found


def check_tiers(plugin_dir: Path, agents: dict[str, dict[str, Any]], rep: Report) -> None:
    path = plugin_dir / "skills" / "conductor" / "reference" / "tiers.json"
    where = "tiers.json"
    data = load_json(path, rep)
    if data is None:
        return
    tiers = data.get("tiers")
    if not isinstance(tiers, list) or not tiers:
        rep.error(where, "'tiers' must be a non-empty list")
        return
    lo, hi = data.get("score_range", [0, 12])
    expected_min = lo
    ids: list[str] = []
    for tier in sorted(tiers, key=lambda t: t.get("score_min", -1)):
        tid = tier.get("id")
        ids.append(tid)
        if tier.get("score_min") != expected_min:
            rep.error(where, f"tier '{tid}' score bands must be contiguous (expected min {expected_min})")
        if tier.get("score_max", -1) < tier.get("score_min", 0):
            rep.error(where, f"tier '{tid}' has score_max below score_min")
        expected_min = tier.get("score_max", expected_min) + 1
        check_role_matches_agent(tier, agents, where, rep)
        if tier.get("effort") not in EFFORT_LEVELS:
            rep.error(where, f"tier '{tid}' effort invalid")
        if not isinstance(tier.get("cost_index"), (int, float)) or tier["cost_index"] <= 0:
            rep.error(where, f"tier '{tid}' cost_index must be positive")
    if expected_min - 1 != hi:
        rep.error(where, f"score bands must end at {hi}")
    if len(ids) != len(set(ids)):
        rep.error(where, "tier ids must be unique")
    order = data.get("escalation_order")
    if order != ids:
        rep.error(where, f"escalation_order must list every tier once, cheapest first: {ids}")
    scout = next((t for t in tiers if t.get("id") == "scout"), None)
    if scout is None or scout.get("writes") is not False:
        rep.error(where, "scout tier must exist with writes: false")
    watcher = data.get("watcher")
    if not isinstance(watcher, dict):
        rep.error(where, "'watcher' entry missing")
    else:
        check_role_matches_agent(watcher, agents, where, rep)
    profiles = data.get("profiles", {})
    if set(profiles) != {"budget", "balanced", "quality"}:
        rep.error(where, "profiles must be exactly budget, balanced, quality")
    if not isinstance(data.get("max_escalations_per_task"), int):
        rep.error(where, "max_escalations_per_task must be an integer")
    default_parallel = data.get("default_parallel")
    max_parallel = data.get("max_parallel")
    if not (isinstance(default_parallel, int) and isinstance(max_parallel, int)
            and 1 <= default_parallel <= max_parallel <= 20):
        rep.error(where, "need 1 <= default_parallel <= max_parallel <= 20")


def check_role_matches_agent(role: dict[str, Any], agents: dict[str, dict[str, Any]],
                             where: str, rep: Report) -> None:
    ref = str(role.get("agent", ""))
    prefix = f"{PLUGIN_NAME}:"
    if not ref.startswith(prefix):
        rep.error(where, f"agent '{ref}' must be namespaced '{prefix}<name>'")
        return
    name = ref[len(prefix):]
    meta = agents.get(name)
    if meta is None:
        rep.error(where, f"agent file for '{ref}' not found")
        return
    for key in ("model", "effort"):
        if role.get(key) != meta.get(key):
            rep.error(where, f"'{ref}' {key} '{role.get(key)}' != agent frontmatter '{meta.get(key)}'")


def validate(root: Path) -> list[str]:
    rep = Report()
    plugin_dir, _ = check_manifests(root, rep)
    if plugin_dir is not None:
        check_forbidden_paths(plugin_dir, rep)
        check_skill(plugin_dir, rep)
        agents = check_agents(plugin_dir, rep)
        check_tiers(plugin_dir, agents, rep)
    if not (root / "CLAUDE.md").exists():
        rep.error("CLAUDE.md", "repository root CLAUDE.md is required")
    return rep.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    errors = validate(args.root.resolve())
    if errors:
        print(f"validate_repo: {len(errors)} problem(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("validate_repo: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
