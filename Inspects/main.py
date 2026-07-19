import argparse
import sys
import json

from Inspects.template_inspector import inspect_template
from Inspects.shape_inspector import inspect_shapes
from Inspects.calib_inspector import inspect_calibration
from Inspects.compare_inspector import inspect_compare

def main():
    parser = argparse.ArgumentParser(description="Universal PPTX Inspection Tool")
    subparsers = parser.add_subparsers(dest="command", help="Inspection command to run")

    # Command: inspect
    parser_inspect = subparsers.add_parser("inspect", help="Inspect input as normalized Deck")
    parser_inspect.add_argument("input_file", help="Path to input YAML or MD file")
    parser_inspect.add_argument("--format", dest="output_format", help="Output format (e.g. json)", default=None)
    parser_inspect.add_argument("--input-format", dest="format", choices=["yaml", "markdown", "asciidoc"], help="Force input format (yaml, markdown, or asciidoc)", default=None)

    # Command: inspect-template
    parser_inspect_tmpl = subparsers.add_parser("inspect-template", help="Inspect PPTX template layouts and placeholders")
    parser_inspect_tmpl.add_argument("file", help="Path to the PPTX template file")
    parser_inspect_tmpl.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    parser_inspect_tmpl.add_argument("--calib", action="store_true", help="Also extract and output calibration metrics from the first slide")

    # Command: shapes
    parser_shapes = subparsers.add_parser("shapes", help="Inspect shapes on slides")
    parser_shapes.add_argument("file", help="Path to the PPTX file")
    parser_shapes.add_argument("--search", type=str, help="Only inspect slides containing this text")
    parser_shapes.add_argument("--slide", type=int, help="Only inspect a specific slide number (1-indexed)")

    # Command: calib
    parser_calib = subparsers.add_parser("calib", help="Inspect calibration data (fonts, CPI, line height)")
    parser_calib.add_argument("file", help="Path to the PPTX file")

    # Command: compare
    parser_compare = subparsers.add_parser("compare", help="Compare element heights with LibreOffice recalculation")
    parser_compare.add_argument("file", help="Path to the PPTX file")
    parser_compare.add_argument("--slide", type=int, default=1, help="Slide number to compare (default: 1)")

    args = parser.parse_args()

    if args.command == "inspect":
        from deck2pptx.adapters import load_deck
        from dataclasses import asdict
        try:
            deck = load_deck(args.input_file, format=args.format)
            data = asdict(deck)
            # Default output is JSON, matching original deck2pptx inspect command behavior
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            if getattr(args, 'output_format', None) == 'json':
                print(json.dumps({"ok": False, "errors": [{"message": str(e)}]}, indent=2, ensure_ascii=False), file=sys.stderr)
            else:
                print(f"Inspect failed: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "inspect-template":
        inspect_template(args.file, args.format, args.calib)
    elif args.command == "shapes":
        inspect_shapes(args.file, search_text=args.search, slide_idx=args.slide)
    elif args.command == "calib":
        inspect_calibration(args.file)
    elif args.command == "compare":
        inspect_compare(args.file, slide_idx=args.slide)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
