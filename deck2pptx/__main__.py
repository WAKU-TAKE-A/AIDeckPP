import argparse
import sys
import json
from pathlib import Path
from .adapters import load_deck
from .validation import validate_deck, ValidationError
from .renderer import render_deck
from .spec import get_spec, explain_spec_text

def explain_spec(args):
    if getattr(args, 'format', None) == 'json':
        print(json.dumps(get_spec(), indent=2, ensure_ascii=False))
    else:
        print(explain_spec_text())


def validate_cmd(args):
    is_json = getattr(args, 'output_format', None) == 'json'
    try:
        deck = load_deck(args.input_file, format=args.format)
        validate_deck(deck, Path(args.input_file).parent)
        if is_json:
            print(json.dumps({"ok": True, "errors": []}, indent=2, ensure_ascii=False))
        else:
            print(f"Validation successful. Found {len(deck.slides)} slides.")
    except ValidationError as e:
        if is_json:
            print(json.dumps({"ok": False, "errors": getattr(e, 'errors', [{"message": str(e)}])}, indent=2, ensure_ascii=False))
        else:
            errors = getattr(e, 'errors', [{"message": str(e)}])
            print(f"Validation failed with {len(errors)} errors:", file=sys.stderr)
            for err in errors:
                print(f"- {err['message']}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if is_json:
            print(json.dumps({"ok": False, "errors": [{"message": str(e)}]}), file=sys.stderr)
        else:
            print(f"Validation failed: {e}", file=sys.stderr)
        sys.exit(1)

def build_cmd(args):
    try:
        deck = load_deck(args.input_file, format=args.format)
        validate_deck(deck, Path(args.input_file).parent)
        render_deck(deck, args.output_file, base_dir=Path(args.input_file).parent, template_path=getattr(args, 'template', None), calib_first_slide=getattr(args, 'calib_first_slide', False))
        print(f"Built PPTX successfully to {args.output_file}")
    except Exception as e:
        print(f"Build failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate PowerPoint from Semantic Deck Format")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Explain Spec
    p_explain = subparsers.add_parser('explain-spec', help="Output the AI-facing model schema")
    p_explain.add_argument('--format', help="Output format (e.g. json)", default=None)
    p_explain.set_defaults(func=explain_spec)
    
    
    # Validate
    p_validate = subparsers.add_parser('validate', help="Validate an input deck")
    p_validate.add_argument('input_file', help="Path to input YAML or MD file")
    p_validate.add_argument('--format', dest="output_format", help="Output format (e.g. json)", default=None)
    p_validate.add_argument('--input-format', dest="format", choices=["yaml", "markdown", "asciidoc"], help="Force input format (yaml, markdown, or asciidoc)", default=None)
    p_validate.set_defaults(func=validate_cmd)
    
    # Build
    p_build = subparsers.add_parser('build', help="Build PPTX from input deck")
    p_build.add_argument('input_file', help="Path to input YAML or MD file")
    p_build.add_argument('output_file', help="Path to output PPTX file")
    p_build.add_argument('--template', help="Path to PPTX template file to use for rendering", default=None)
    p_build.add_argument('--input-format', dest="format", choices=["yaml", "markdown", "asciidoc"], help="Force input format (yaml, markdown, or asciidoc)", default=None)
    p_build.add_argument('--calib-first-slide', action='store_true', help="Use the first slide of the template for font height/width calibration")
    p_build.set_defaults(func=build_cmd)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)

if __name__ == "__main__":
    main()
