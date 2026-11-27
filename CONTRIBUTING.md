# Contributing to Allot

Thanks for helping. Allot is used to make decisions about other people's money and code, so the
bar for changes is evidence, not opinion. Please read this page before opening a pull request.

## Ground rules

- Read [docs/BUILD-SPEC.md](docs/BUILD-SPEC.md) and [CLAUDE.md](CLAUDE.md). The invariants in
  CLAUDE.md are not negotiable in a PR; changing one needs an issue and maintainer agreement first.
- One logical change per PR. Small PRs get reviewed faster.
- Be kind. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Development setup

```bash
git clone https://github.com/T-RexBytes/conductor.git
cd conductor
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py
python -m pytest -q
```

Try the plugin from your clone without installing it:

```bash
claude --plugin-dir ./plugins/allot
```

Then run `/allot:run --plan-only <some task>` in a scratch project.

## Kinds of change

| Change | What the PR needs |
|---|---|
| Docs, typos, templates wording | CI green |
| Validator or tests | CI green; a test for each new rule |
| Prompt changes (SKILL.md, agents, reference files) | CI green; the behavioral evals they affect (BUILD-SPEC 11.2) run and reported in the PR |
| Routing (tiers, models, effort, bands, floors, watcher policy) | Everything above, plus benchmark results before and after (see below) |
| New flag or feature | An issue agreed first; spec update in the same PR |
| New frontmatter key | A link to the Claude Code docs that defines it; validator allowlist updated |

## Routing changes need benchmark evidence

1. Run the suite on `main`: `python benchmarks/run_benchmark.py --out before.jsonl`
2. Apply your change and run it again: `--out after.jsonl`
3. Paste both summary tables in the PR.

A routing change is accepted only if the pass rate does not drop and total cost does not rise.
Running benchmarks needs an Anthropic API key and costs money; maintainers can run it for you on
request.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`,
`test:`, `ci:`, `refactor:`, `chore:`. Routing changes use `feat(routing):` or `fix(routing):`.

## Pull request checklist

The PR template repeats this list.

- [ ] `python scripts/validate_repo.py` passes
- [ ] `python -m pytest -q` passes
- [ ] Docs updated (spec, README, CHANGELOG under "Unreleased")
- [ ] Behavioral evals run if prompts changed
- [ ] Benchmark before/after attached if routing changed
- [ ] No hooks, settings, MCP/LSP servers, monitors or `bin/` added to the plugin

## Releases (maintainers)

1. Move "Unreleased" entries in `CHANGELOG.md` under the new version.
2. Bump `version` in `plugins/allot/.claude-plugin/plugin.json`.
3. Run behavioral evals E1–E10 and the benchmark suite; record results in the release PR.
4. Merge, tag `vX.Y.Z`, publish a GitHub release with the changelog section.

## Reporting bugs and proposing features

Use the issue templates. Security problems go to [SECURITY.md](SECURITY.md), not public issues.
