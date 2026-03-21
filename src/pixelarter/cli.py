import argparse
import sys
from pixelarter.formats.png import import_from_png, export_to_png
from pixelarter.formats.pixelart import save_pixelart, load_pixelart


def cmd_import_png(args):
    print(f"Importing PNG: {args.input}")
    try:
        img = import_from_png(args.input, palette_id=args.palette)
        save_pixelart(img, args.output)
        print(f"Successfully saved .pixelart to {args.output}")
    except Exception as e:
        print(f"Error during import: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export_png(args):
    print(f"Exporting .pixelart: {args.input}")
    try:
        img = load_pixelart(args.input)
        export_to_png(img, args.output, scale=args.scale)
        print(f"Successfully exported PNG to {args.output} (scale x{args.scale})")
    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_inspect(args):
    try:
        img = load_pixelart(args.input)
        print(f"--- PixelArtImage Inspector ---")
        print(f"File:         {args.input}")
        print(f"Dimensions:   {img.width} x {img.height}")
        print(f"Palette Mode: {img.palette_mode}")
        if img.palette_mode == "builtin":
            print(f"Palette ID:   {img.palette_id}")
        elif img.palette_mode == "embedded":
            print(f"Palette Size: {len(img.palette) if img.palette else 0} colors")

        if img.transparent_index is not None:
            print(f"Transparency: index {img.transparent_index}")
        else:
            print(f"Transparency: none")

        # Standard encoding info for v1-alpha
        print(f"Version:      1")
        print(f"Encoding:     rows")

        if img.metadata:
            print(f"Metadata:     {img.metadata}")

    except Exception as e:
        print(f"Error inspecting file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="pixelarter CLI tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # import-png command
    parser_import = subparsers.add_parser("import-png", help="Convert PNG to .pixelart format")
    parser_import.add_argument("-i", "--input", required=True, help="Input PNG file")
    parser_import.add_argument("-o", "--output", required=True, help="Output .pixelart file")
    parser_import.add_argument("-p", "--palette", help="Builtin palette ID to use (e.g., pxa-16-v1). If not provided, embedded mode is used.")
    parser_import.set_defaults(func=cmd_import_png)

    # export-png command
    parser_export = subparsers.add_parser("export-png", help="Convert .pixelart to PNG format")
    parser_export.add_argument("-i", "--input", required=True, help="Input .pixelart file")
    parser_export.add_argument("-o", "--output", required=True, help="Output PNG file")
    parser_export.add_argument("-s", "--scale", type=int, default=1, help="Integer scale factor for the output PNG (default 1)")
    parser_export.set_defaults(func=cmd_export_png)

    # inspect command
    parser_inspect = subparsers.add_parser("inspect", help="Inspect a .pixelart file")
    parser_inspect.add_argument("input", help="The .pixelart file to inspect")
    parser_inspect.set_defaults(func=cmd_inspect)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
