# Source Baseline Policy

This document defines the expected repository hygiene and source baseline for `deck2pptx`.

## Intended Source Files

The following paths are considered core source code or necessary operational files that should be tracked in version control:

- `deck2pptx/` (Core library source)
- `tests/` (Test suite)
- `docs/` (Documentation)
- `scripts/` (Operational scripts and verification tools)
- `LICENSE`
- `README.md`
- `README_AI.md`
- `pyproject.toml`
- `.gitignore`

## Generated Artifacts (Ignored)

The following paths represent generated outputs, cached data, or local environments. They should be ignored by Git and will not fail hygiene checks:

- `.venv/` and `.venv-release/` (Python virtual environments)
- `__pycache__/`, `deck2pptx/__pycache__/`, `tests/__pycache__/`
- `.pytest_cache/`
- `deck2pptx.egg-info/`, `dist/`, `build/`
- `outputs/` (Generated PPTX and PDF files)
- `examples/` (Local sample inputs and assets)

## Operational / Reference

These directories contain meta-operational data, such as prompts, checkpoints, or legacy files. They are allowed to exist in the tree (tracked or untracked) but are distinct from core application source:

- `_sample/`
- `dual-model-operation-kit/`

## Release Verification Hygiene

The script `scripts/check_source_hygiene.ps1` runs automatically during the release verification pipeline (`scripts/verify_release.ps1`).

**Rules:**
1. If the repository is completely clean (all files committed), verification passes.
2. If the repository contains **only** expected untracked source files or operational folders, verification will warn but **pass**, marking the repository as "Commit-ready".
3. If the repository contains **unexpected** untracked files or modified artifacts that are not categorized as valid source, verification will **fail** the release gate to prevent dirty releases.
