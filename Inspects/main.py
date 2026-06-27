import argparse
import sys

from Inspects.layout_inspector import inspect_layouts
from Inspects.shape_inspector import inspect_shapes
from Inspects.calib_inspector import inspect_calibration
from Inspects.compare_inspector import inspect_compare

def main():
    parser = argparse.ArgumentParser(description="Universal PPTX Inspection Tool")
    subparsers = parser.add_subparsers(dest="command", help="Inspection command to run")

    # Command: layouts
    parser_layouts = subparsers.add_parser("layouts", help="Inspect slide layouts and placeholders")
    parser_layouts.add_argument("file", help="Path to the PPTX file")

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

    if args.command == "layouts":
        inspect_layouts(args.file)
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
