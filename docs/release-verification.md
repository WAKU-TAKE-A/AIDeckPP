# Release Verification Workflow

The `deck2pptx` project provides a release-quality verification baseline. This ensures that the codebase can be installed cleanly and behaves as expected in production environments, particularly regarding output generation and visual export.

## Verification Pipeline

To run the complete release verification pipeline, execute the provided script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_release.ps1
```

This script now acts as a **strict release gate**. It will fail immediately with a non-zero exit code if any of the following stages encounter an error or unexpected output:

1. **Test Suite Execution**: Runs the `pytest` suite ensuring all unit and feature tests pass.
2. **Quality Gate Verification**: Invokes all `deck2pptx` AI authoring commands (`explain-spec`, `inspect`, `validate`) and builds sample PPTX files.
3. **Negative Validation Verification**: Verifies that structured multi-errors are correctly emitted for broken decks, failing the gate if the command succeeds unexpectedly.
4. **Visual Export Check**: If `LibreOffice` (`soffice`) is installed (via PATH or standard `Program Files` location), the pipeline exports the generated PPTX files to PDF. It asserts that the output PDFs are created, non-empty, and LibreOffice exits successfully.
5. **Clean Environment Package Test**: Creates a temporary virtual environment (`.venv-release`), installs the package in editable mode, and executes CLI smoke commands.
6. **Git Hygiene Check**: Evaluates the repository against the defined source baseline policy. It categorizes files into source, generated artifacts, and operational reference data, failing the gate if any unexpected or dirty artifacts pollute the workspace. See [Source Baseline](source-baseline.md) for specifics.

## Visual Export Notes (LibreOffice)

Level 3 verification (Visual Export) requires LibreOffice. 

If LibreOffice is not installed, the test pipeline will gracefully skip the visual export verification. The console output will explicitly note that the step was skipped. 

### Installing LibreOffice

If you are running Windows and have Chocolatey installed, you can quickly install LibreOffice to enable Level 3 validation:

```powershell
# Run in an elevated (Administrator) command prompt / PowerShell
choco install libreoffice-fresh -y
```

Once installed, ensure `soffice` is available in your PATH. The verification script and pytest markers will automatically detect it and run the visual export checks.
