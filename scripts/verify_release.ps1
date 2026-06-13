$ErrorActionPreference = "Stop"

Write-Host "Running release verification..."

function Assert-Success {
    param([string]$StepName)
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[FAIL] $StepName failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

if (!(Test-Path outputs)) {
    New-Item -ItemType Directory -Path outputs | Out-Null
}

$sampleYaml = "outputs\release_sample.deck.yaml"
$sampleMd = "outputs\release_sample.md"

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$yamlContent = @"
title: Release Sample
slides:
  - title: Release Sample
    elements:
      - text: This deck verifies YAML input.
      - bullet_list:
          - First point
          - Second point
"@
[System.IO.File]::WriteAllText($sampleYaml, $yamlContent, $utf8NoBom)

$mdContent = @"
# Release Sample

This deck verifies Markdown input.

- First point
- Second point
"@
[System.IO.File]::WriteAllText($sampleMd, $mdContent, $utf8NoBom)

# 1. Test from existing venv
Write-Host "`n--- Running Pytest ---"
& .\.venv\Scripts\python.exe -m pytest
Assert-Success "Pytest"

Write-Host "`n--- Verifying AI Authoring Quality Gate Commands ---"
& .\.venv\Scripts\python.exe -m deck2pptx explain-spec
Assert-Success "explain-spec"
& .\.venv\Scripts\python.exe -m deck2pptx explain-spec --format json
Assert-Success "explain-spec json"
& .\.venv\Scripts\python.exe -m deck2pptx inspect $sampleYaml --format json
Assert-Success "inspect yaml"
& .\.venv\Scripts\python.exe -m deck2pptx inspect $sampleMd --format json
Assert-Success "inspect md"
& .\.venv\Scripts\python.exe -m deck2pptx validate $sampleYaml --format json
Assert-Success "validate yaml"
& .\.venv\Scripts\python.exe -m deck2pptx validate $sampleMd --format json
Assert-Success "validate md"

Write-Host "`n--- Verifying Build ---"
& .\.venv\Scripts\python.exe -m deck2pptx build $sampleYaml outputs\sample.pptx
Assert-Success "build yaml"
& .\.venv\Scripts\python.exe -m deck2pptx build $sampleMd outputs\sample-md.pptx
Assert-Success "build md"

Write-Host "`n--- Verifying Negative Validation ---"
$validateExit = 0
try {
    & .\.venv\Scripts\python.exe -m deck2pptx validate tests\fixtures\multi_error.deck.yaml --format json
    $validateExit = $LASTEXITCODE
} catch {
    $validateExit = $LASTEXITCODE
}
if ($validateExit -eq 0) {
    Write-Error "[FAIL] Negative validation succeeded unexpectedly."
    exit 1
} else {
    Write-Host "[OK] Negative validation failed as expected."
}

# 2. LibreOffice Export
Write-Host "`n--- Checking for LibreOffice ---"
$sofficeFound = $false
try {
    $sofficePath = Get-Command soffice -ErrorAction SilentlyContinue
    if ($sofficePath) {
        $sofficeFound = $true
        $sofficeCmd = "soffice"
    } else {
        $defaultPath = "C:\Program Files\LibreOffice\program\soffice.exe"
        if (Test-Path $defaultPath) {
            $sofficeFound = $true
            $sofficeCmd = $defaultPath
        }
    }
} catch { }

if ($sofficeFound) {
    Write-Host "Running LibreOffice Visual Export..."
    
    # Remove existing PDFs to ensure we aren't seeing old outputs
    if (Test-Path outputs\sample.pdf) { Remove-Item outputs\sample.pdf }
    if (Test-Path outputs\sample-md.pdf) { Remove-Item outputs\sample-md.pdf }

    $p1 = Start-Process -FilePath $sofficeCmd -ArgumentList "--headless","--convert-to","pdf","--outdir","outputs","outputs\sample.pptx" -Wait -NoNewWindow -PassThru
    if ($p1.ExitCode -ne 0) { Write-Error "[FAIL] LibreOffice PDF export failed."; exit $p1.ExitCode }

    $p2 = Start-Process -FilePath $sofficeCmd -ArgumentList "--headless","--convert-to","pdf","--outdir","outputs","outputs\sample-md.pptx" -Wait -NoNewWindow -PassThru
    if ($p2.ExitCode -ne 0) { Write-Error "[FAIL] LibreOffice PDF export failed."; exit $p2.ExitCode }
    
    if (!(Test-Path outputs\sample.pdf) -or !(Test-Path outputs\sample-md.pdf)) {
        Write-Error "[FAIL] PDF export files not found after successful exit code."
        exit 1
    }
    
    $pdf1 = Get-Item outputs\sample.pdf
    $pdf2 = Get-Item outputs\sample-md.pdf
    if ($pdf1.Length -eq 0 -or $pdf2.Length -eq 0) {
        Write-Error "[FAIL] PDF export files are empty."
        exit 1
    }

    Write-Host "[OK] Visual export successful."
} else {
    Write-Host "[SKIP] Skipping Level 3 Visual Export (soffice not found in PATH)."
}

# 3. Clean Environment Package Test
Write-Host "`n--- Testing Clean Environment Package Installation ---"
if (Test-Path .venv-release) {
    try { Remove-Item -Recurse -Force .venv-release -ErrorAction SilentlyContinue } catch { }
}
python -m venv .venv-release
& .\.venv-release\Scripts\python.exe -m pip install --upgrade pip
Assert-Success "pip upgrade"
& .\.venv-release\Scripts\python.exe -m pip install -e . pytest
Assert-Success "pip install deck2pptx"
& .\.venv-release\Scripts\deck2pptx validate $sampleMd --format json
Assert-Success "smoke validate"
& .\.venv-release\Scripts\deck2pptx build $sampleMd outputs\sample-md-release.pptx
Assert-Success "smoke build"

if (Test-Path .venv-release) {
    try { Remove-Item -Recurse -Force .venv-release -ErrorAction SilentlyContinue } catch { }
}
Write-Host "[OK] Clean environment test passed."

# 4. Git Hygiene
Write-Host "`n--- Checking Git Hygiene ---"
& powershell -ExecutionPolicy Bypass -File .\scripts\check_source_hygiene.ps1
Assert-Success "check_source_hygiene"

Write-Host "`n[SUCCESS] Verification Complete!"
