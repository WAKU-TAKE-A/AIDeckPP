def get_spec() -> dict:
    return {
        "description": "Deck to PPTX MVP Format Spec",
        "concept": "The deck2pptx tool accepts YAML or Markdown input files. Both are only adapters; the canonical model is the Deck object.",
        "deck_metadata": {
            "title": "The presentation title (string).",
            "orientation": "'landscape' (default) or 'portrait'.",
            "theme": "Theme name, e.g. 'default'."
        },
        "slide_metadata": {
            "title": "Slide title (string).",
            "subtitle": "Slide subtitle (string).",
            "notes": "Presenter notes (string).",
            "layout_hint": "Force layout to 'title', 'content', 'gallery', 'flow', or 'image_only'."
        },
        "elements": {
            "text": "A simple text block (Markdown normal paragraph).",
            "bullet_list": "A list of strings (Markdown `-` or `*` list).",
            "image": "A relative path to an image file (Markdown `![alt](path)`).",
            "table": "An object with `headers` and `rows` (Markdown tables with `|`).",
            "gallery": "An object with `images` (Markdown consecutive images).",
            "flow": {
                "description": "A flowchart.",
                "fields": {
                    "direction": "'horizontal' or 'vertical'.",
                    "nodes": "List of objects with `id` and `label`.",
                    "edges": "List of objects with `from` and `to` matching node IDs."
                }
            }
        },
        "markdown_notes": "In Markdown, deck metadata is specified via YAML front matter (---). Slide titles are `#` or `##` headers. Flow uses fenced blocks like ```flow horizontal",
        "validation_rules": [
            "Deck orientation must be 'landscape' or 'portrait'.",
            "Image paths and gallery image paths must exist relative to the input file.",
            "Flow direction must be supported.",
            "Flow edges must reference known node IDs."
        ],
        "non_goals": [
            "Tree, Timeline, Comparison, CodeBlock.",
            "AsciiDoc adapter, Natural Language adapter.",
            "Full template/theme systems or broad visual redesigns.",
            "Manual coordinate specification (x, y, width, height) in the Deck model."
        ]
    }

def explain_spec_text() -> str:
    spec = get_spec()
    text = f"{spec['description']}\n\n{spec['concept']}\n\nSupported Deck-level metadata:\n"
    for k, v in spec["deck_metadata"].items():
        text += f"- `{k}`: {v}\n"
        
    text += "\nSupported Slide-level metadata:\n"
    for k, v in spec["slide_metadata"].items():
        text += f"- `{k}`: {v}\n"
        
    text += "\nSupported elements inside `elements`:\n"
    for k, v in spec["elements"].items():
        if isinstance(v, dict):
            text += f"- `{k}`: {v['description']}\n"
            for fk, fv in v["fields"].items():
                text += f"    - `{fk}`: {fv}\n"
        else:
            text += f"- `{k}`: {v}\n"
            
    text += f"\n({spec['markdown_notes']})\n"
    text += "\nValidation Rules:\n"
    for rule in spec["validation_rules"]:
        text += f"- {rule}\n"
        
    text += "\nNon-Goals:\n"
    for goal in spec["non_goals"]:
        text += f"- {goal}\n"
        
    return text
