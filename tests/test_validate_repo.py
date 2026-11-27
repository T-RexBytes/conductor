"""Tests for scripts/validate_repo.py: the real repo passes, and each rule catches its violation."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import validate_repo  # noqa: E402

PLUGIN = Path("plugins/allot")
SKILL = PLUGIN / "skills/run/SKILL.md"
AGENTS = PLUGIN / "agents"
TIERS = PLUGIN / "skills/run/reference/tiers.json"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    dest = tmp_path / "repo"
    shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    return dest


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def errors_for(root: Path) -> str:
    return "\n".join(validate_repo.validate(root))


def test_real_repo_passes() -> None:
    assert validate_repo.validate(REPO) == []


def test_main_exit_codes(repo: Path) -> None:
    assert validate_repo.main(["--root", str(repo)]) == 0
    (repo / PLUGIN / "hooks").mkdir()
    assert validate_repo.main(["--root", str(repo)]) == 1


@pytest.mark.parametrize("forbidden", ["hooks", "monitors", "bin"])
def test_forbidden_dirs(repo: Path, forbidden: str) -> None:
    (repo / PLUGIN / forbidden).mkdir()
    assert "forbidden in the plugin" in errors_for(repo)


@pytest.mark.parametrize("forbidden", ["settings.json", ".mcp.json", ".lsp.json", "CLAUDE.md"])
def test_forbidden_files(repo: Path, forbidden: str) -> None:
    (repo / PLUGIN / forbidden).write_text("{}", encoding="utf-8")
    assert "forbidden in the plugin" in errors_for(repo)


def test_skill_must_disable_model_invocation(repo: Path) -> None:
    replace(repo / SKILL, "disable-model-invocation: true", "disable-model-invocation: false")
    assert "disable-model-invocation must be true" in errors_for(repo)


def test_skill_hooks_rejected(repo: Path) -> None:
    replace(repo / SKILL, "effort: high\n---", "effort: high\nhooks: {}\n---")
    assert "skill hooks persist" in errors_for(repo)


def test_skill_disallowed_tools_rejected(repo: Path) -> None:
    replace(repo / SKILL, "effort: high\n---", "effort: high\ndisallowed-tools: Bash\n---")
    assert "disallowed-tools would hide" in errors_for(repo)


def test_skill_unknown_key(repo: Path) -> None:
    replace(repo / SKILL, "effort: high\n---", "effort: high\nmodle: opus\n---")
    assert "undocumented frontmatter keys" in errors_for(repo)


def test_skill_rule_marker_required(repo: Path) -> None:
    replace(repo / SKILL, "**No probing.**", "**Probing.**")
    assert "hard rule marker missing" in errors_for(repo)


def test_skill_reference_must_exist(repo: Path) -> None:
    (repo / PLUGIN / "skills/run/reference/ROUTING.md").unlink()
    assert "referenced file does not exist: reference/ROUTING.md" in errors_for(repo)


def test_agent_internal_marker(repo: Path) -> None:
    replace(repo / AGENTS / "builder.md", "description: Internal to the allot plugin.", "description: Builds things.")
    assert "description must start with" in errors_for(repo)


def test_agent_must_deny_agent_tool(repo: Path) -> None:
    replace(repo / AGENTS / "worker.md", "disallowedTools: Agent", "disallowedTools: NotebookEdit")
    assert "disallowedTools must include Agent" in errors_for(repo)


def test_read_only_agents_cannot_write(repo: Path) -> None:
    replace(repo / AGENTS / "watcher.md", "disallowedTools: Write, Edit, NotebookEdit, Agent", "disallowedTools: Agent")
    assert "read-only agent must deny" in errors_for(repo)


@pytest.mark.parametrize("key", ["tools: Read", "permissionMode: auto", "mcpServers: []", "hooks: {}"])
def test_agent_banned_keys(repo: Path, key: str) -> None:
    replace(repo / AGENTS / "scout.md", "color: cyan", f"color: cyan\n{key}")
    assert "banned keys" in errors_for(repo)


def test_agent_invalid_effort(repo: Path) -> None:
    replace(repo / AGENTS / "scout.md", "effort: low", "effort: extreme")
    assert "effort must be one of" in errors_for(repo)


def test_tiers_must_match_agents(repo: Path) -> None:
    replace(repo / AGENTS / "builder.md", "effort: medium", "effort: high")
    assert "'allot:builder' effort" in errors_for(repo)


def test_tiers_bands_contiguous(repo: Path) -> None:
    data = json.loads((repo / TIERS).read_text(encoding="utf-8"))
    data["tiers"][1]["score_min"] = 4
    (repo / TIERS).write_text(json.dumps(data), encoding="utf-8")
    assert "contiguous" in errors_for(repo)


def test_tiers_escalation_order(repo: Path) -> None:
    data = json.loads((repo / TIERS).read_text(encoding="utf-8"))
    data["escalation_order"] = list(reversed(data["escalation_order"]))
    (repo / TIERS).write_text(json.dumps(data), encoding="utf-8")
    assert "escalation_order" in errors_for(repo)


def test_scout_must_be_read_only(repo: Path) -> None:
    data = json.loads((repo / TIERS).read_text(encoding="utf-8"))
    data["tiers"][0]["writes"] = True
    (repo / TIERS).write_text(json.dumps(data), encoding="utf-8")
    assert "scout tier must exist with writes: false" in errors_for(repo)


def test_marketplace_name_mismatch(repo: Path) -> None:
    path = repo / PLUGIN / ".claude-plugin/plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["name"] = "other"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert "name must equal the marketplace entry name" in errors_for(repo)


def test_plugin_manifest_hooks_rejected(repo: Path) -> None:
    path = repo / PLUGIN / ".claude-plugin/plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["hooks"] = {}
    path.write_text(json.dumps(data), encoding="utf-8")
    assert "must not declare hooks" in errors_for(repo)


def test_changelog_must_cover_version(repo: Path) -> None:
    path = repo / PLUGIN / ".claude-plugin/plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "9.9.9"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert "missing section '## [9.9.9]'" in errors_for(repo)


def test_bad_semver(repo: Path) -> None:
    path = repo / PLUGIN / ".claude-plugin/plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "v1"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert "version must be semver" in errors_for(repo)


def test_marketplace_source_traversal(repo: Path) -> None:
    path = repo / ".claude-plugin/marketplace.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["plugins"][0]["source"] = "./../elsewhere"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert "must not contain '..'" in errors_for(repo)
