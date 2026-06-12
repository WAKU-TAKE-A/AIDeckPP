# AI Authoring Guide

The canonical AI-facing entry point is [`../README_AI.md`](../README_AI.md).

`deck2pptx` is designed to be highly reliable for AI agents to generate PowerPoint presentations without manual coordinate math or visual tweaking. 
Agents should use the canonical `Deck` semantic format (via YAML or Markdown adapters) and rely on the `deck2pptx` renderer.

## Recommended AI Authoring Loop

If you are an AI generating a presentation for a user, follow this loop to guarantee success:

1. **Check the Specification**:
   Call `python -m deck2pptx explain-spec --format json` to see the current Deck schema, validation rules, and supported adapter formats.

2. **Generate the Input**:
   Author the presentation using the requested adapter (e.g. YAML or Markdown) adhering to the rules from the spec.

3. **Inspect the Output**:
   Call `python -m deck2pptx inspect your_file.md --format json`.
   This command parses your input via the adapter and dumps the raw `Deck` semantic model. Verify that your content maps properly to slides and elements.

4. **Validate**:
   Call `python -m deck2pptx validate your_file.md --format json`.
   If `ok` is `true`, your deck is ready to build.
   If `ok` is `false`, read the `errors` list. Each error contains specific context (`slide_index`, `element_index`, `field`) to help you repair the input file.

5. **Repair**:
   If there were validation errors, fix the issues in your input file and repeat step 4. Do not guess what's wrong; use the structured error output.

6. **Build**:
   Once validation passes, generate the final PPTX using:
   `python -m deck2pptx build your_file.md output.pptx`
