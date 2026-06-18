# Source Baseline Policy

This document defines the expected repository hygiene for `deck2pptx`. It is enforced by `scripts/check_source_hygiene.ps1`, which runs automatically as part of the release verification pipeline (`scripts/verify_release.ps1`).

## Tracked Source Files

The following paths are considered core source code and must be tracked in version control:

- `deck2pptx/` — Core library source
- `tests/` — Test suite
- `docs/` — Documentation
- `scripts/` — Operational scripts and verification tools
- `LICENSE`
- `README.md`
- `README_AI.md`
- `pyproject.toml`
- `.gitignore`

## Generated Artifacts (Git-Ignored)

These paths represent generated outputs, cached data, or local environments. They are listed in `.gitignore` and will not fail hygiene checks:

- `.venv/`, `.venv-release/` — Python virtual environments
- `__pycache__/`, `deck2pptx/__pycache__/`, `tests/__pycache__/`
- `.pytest_cache/`
- `deck2pptx.egg-info/`, `dist/`, `build/`
- `outputs/` — Generated PPTX and PDF files

## Operational / Reference Data (Git-Ignored)

These directories contain working inputs, sample files, prompts, or legacy reference material. They are allowed to exist untracked but are distinct from core source:

- `Inputs/` — Working input files for manual testing
- `examples/` — Local sample inputs and assets
- `_sample/` — Archived sample data
- `dual-model-operation-kit/` — Meta-operational reference

## Hygiene Rules

The script `scripts/check_source_hygiene.ps1` categorizes every file in the repository:

1. If the repository is completely clean (all files committed), verification **passes**.
2. If the repository contains **only** expected untracked source files or operational folders, verification will warn but **pass**, marking the repository as "Commit-ready".
3. If the repository contains **unexpected** untracked files or modified artifacts not categorized above, verification will **fail** the release gate.
