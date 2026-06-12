# README_AI

You are generating a PowerPoint deck for this repository.

Use `deck2pptx` through the canonical `Deck` model. Do not manually specify PowerPoint coordinates, text box positions, or shape dimensions. YAML and Markdown are only input adapters. The renderer consumes `Deck`, not adapter-specific syntax.

## Core Rule

The `Deck` model is canonical.

- YAML is only an input adapter.
- Markdown is only an input adapter.
- Future AsciiDoc or Natural Language inputs must target the same `Deck` model.
- Renderer changes must not be required just because a new input adapter is added.
- PowerPoint is only one renderer.

## Current Supported Elements

Use only these first-class Deck elements unless the repository has been updated and `explain-spec` says otherwise:

- `Text`
- `BulletList`
- `Image`
- `Table`
- `Gallery`
- `Flow`

Do not assume support for these yet:

- `Comparison`
- `Timeline`
- `CodeBlock`
- `Tree`

## Required Authoring Loop

Run commands with the repo-local virtual environment:

```powershell
.\.venv\Scripts\python.exe -m deck2pptx explain-spec --format json
```

Use the returned schema as the source of truth. Then:

1. Generate an input file in YAML or Markdown.
2. Inspect the parsed Deck model:

```powershell
.\.venv\Scripts\python.exe -m deck2pptx inspect your_file.md --format json
```

3. Validate the input:

```powershell
.\.venv\Scripts\python.exe -m deck2pptx validate your_file.md --format json
```

4. If validation fails, repair the input using the structured `errors` list. Do not guess.
5. Build the PPTX only after validation passes:

```powershell
.\.venv\Scripts\python.exe -m deck2pptx build your_file.md output.pptx
```

## Input Guidance

Prefer Markdown when the user wants a simple text-first deck.

Prefer YAML when the deck needs explicit semantic structures such as `gallery`, `flow`, image lists, or precise metadata.

For images, use paths relative to the input file location.

For Flow, define nodes and edges using supported IDs. Always validate because edges must reference existing node IDs.

## Quality Gate

Before reporting completion, run at least:

```powershell
.\.venv\Scripts\python.exe -m deck2pptx validate your_file.md --format json
.\.venv\Scripts\python.exe -m deck2pptx build your_file.md output.pptx
```

For repository-level verification, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_release.ps1
```

## Do Not

- Do not add `x`, `y`, `width`, or `height` fields to Deck input.
- Do not make the renderer parse YAML or Markdown directly.
- Do not invent unsupported elements without updating the Deck model, adapters, validation, renderer, spec, examples, and tests together.
- Do not ignore validation errors.
- Do not claim a PPTX is ready until validation and build have both succeeded.
