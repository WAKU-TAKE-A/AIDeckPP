# Release Verification Workflow

The `deck2pptx` project provides a release-quality verification pipeline via `scripts/verify_release.ps1`. This script acts as a **strict release gate** — it will fail immediately with a non-zero exit code if any stage encounters an error.

## Running the Pipeline

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_release.ps1
```

## Pipeline Stages

The pipeline executes the following stages in order:

### Stage 1: Test Suite

Runs `pytest` to ensure all unit and feature tests pass.

### Stage 2: Quality Gate Commands

Invokes all `deck2pptx` CLI commands used in the AI authoring loop:
- `explain-spec` (text and JSON)
- `inspect` (YAML and Markdown inputs)
- `validate` (YAML and Markdown inputs)
- `build` (YAML and Markdown to PPTX)

Sample input files are auto-generated in `outputs/` for this purpose.

### Stage 3: Negative Validation

Verifies that structured multi-errors are correctly emitted for intentionally broken decks (`tests/fixtures/multi_error.deck.yaml`). Fails the gate if the command succeeds unexpectedly.

### Stage 4: Visual Export (Optional — LibreOffice)

If `soffice` (LibreOffice) is found in PATH or at `C:\Program Files\LibreOffice\program\soffice.exe`:
- Exports generated PPTX files to PDF using headless mode.
- Asserts that output PDFs are created, non-empty, and LibreOffice exits successfully.

If LibreOffice is not installed, this stage is **skipped gracefully** with a console message.

To install LibreOffice on Windows with Chocolatey:
```powershell
choco install libreoffice-fresh -y
```

### Stage 5: Clean Environment Package Test

Creates a temporary virtual environment (`.venv-release`), installs the package in editable mode, and runs CLI smoke commands (`validate`, `build`). The temporary environment is cleaned up after the test.

### Stage 6: Git Hygiene

Runs `scripts/check_source_hygiene.ps1` to verify that no unexpected or dirty artifacts exist in the repository. See [source-baseline.md](source-baseline.md) for the file categorization rules.
