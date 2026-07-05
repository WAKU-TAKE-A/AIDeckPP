def get_spec() -> dict:
    return {
        "description": "Deck to PPTX MVP Format Spec",
        "concept": "The deck2pptx tool accepts YAML, Markdown, or AsciiDoc input files. These are only adapters; the canonical model is the Deck object.",
        "deck_metadata": {
            "title": "The presentation title (string).",
            "orientation": "'landscape' (default) or 'portrait'.",
            "theme": "Theme name, e.g. 'default'.",
            "toc": "Generate table of contents slide automatically (boolean).",
            "toc_title": "Custom TOC slide title (string).",
            "indent": "Indentation size for lists in points (integer). Default is 40.",
            "content_align": "Vertical alignment of slide content. Enum: ['top', 'semi-top', 'center', 'semi-bottom', 'bottom']."
        },
        "slide_metadata": {
            "title": "Slide title (string).",
            "subtitle": "Slide subtitle (string).",
            "notes": "Presenter notes (string).",
            "layout_hint": "Target PPTX layout name, or built-in hints like 'title', 'content'."
        },
        "elements": {
            "description": "All elements support an optional `placeholder` field (string) to target PPTX placeholders.",
            "text": "A simple text block (Markdown normal paragraph, or AsciiDoc block).",
            "bullet_list": "A list of strings (Markdown `-`/`*` list, or AsciiDoc `*`/`-` list).",
            "image": "A relative path to an image file, or an object with `source` and `caption`.",
            "table": "An object with `headers` and `rows`.",
            "gallery": {
                "description": "A grid of images.",
                "fields": {
                    "images": "List of image objects or path strings.",
                    "rows": "Optional explicit row count (integer).",
                    "columns": "Optional explicit column count (integer)."
                }
            },
            "flow": {
                "description": "A flowchart.",
                "fields": {
                    "direction": "'horizontal' or 'vertical'.",
                    "nodes": "List of objects with `id` and `label`.",
                    "edges": "List of objects with `from` and `to` matching node IDs."
                }
            },
            "comparison": {
                "description": "A comparison matrix.",
                "fields": {
                    "columns": "List of objects with `label` and `items` (list of strings).",
                    "title": "Optional title string."
                }
            },
            "timeline": {
                "description": "A timeline of events.",
                "fields": {
                    "events": "List of objects with `label`, `title`, and optional `description`."
                }
            },
            "code_block": {
                "description": "A source code block.",
                "fields": {
                    "code": "The raw code string.",
                    "language": "Optional programming language name.",
                    "caption": "Optional caption string."
                }
            },
            "tree": {
                "description": "A hierarchical tree.",
                "fields": {
                    "root": "A node object with `label` and optional `children` (list of nodes)."
                }
            },
            "split": {
                "description": "A layout split into multiple panels.",
                "fields": {
                    "direction": "'horizontal' or 'vertical'.",
                    "panels": "List of panel objects, each containing an optional `title` and a list of `elements`."
                }
            }
        },
        "markdown_notes": "In Markdown, `#`, `##`, and `###` headings start new slides. Use control comments. In AsciiDoc, `=`, `==`, `===` start slides, and `//` comments are used for controls. For business blocks, use `[block_name]` + `----` syntax.",
        "validation_rules": [
            "Deck orientation must be 'landscape' or 'portrait'.",
            "Image paths and gallery image paths must exist relative to the input file.",
            "Gallery rows and columns must be positive integers.",
            "Flow direction must be supported.",
            "Flow edges must reference known node IDs.",
            "Comparison must have at least 2 columns.",
            "Timeline must have at least 1 event.",
            "CodeBlock must have code content.",
            "Tree must have a root node.",
            "Split direction must be 'horizontal' or 'vertical'.",
            "Split must have at least 1 panel.",
            "A Split panel must have either a title or elements.",
            "Nested Split elements are not supported."
        ],
        "non_goals": [
            "Natural Language adapter.",
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
