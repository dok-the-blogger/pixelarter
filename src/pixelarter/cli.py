import argparse
import json
import sys

from pixelarter.formats.pixelart import load_pixelart, save_pixelart
from pixelarter.formats.png import export_to_png, import_from_png
from pixelarter.ingest.pipeline import inspect_image, load_image_rgba, process_ingest
from pixelarter.view.render import get_sidecar_path, render_preview


def cmd_import_png(args):
    print(f"Importing PNG: {args.input}")
    try:
        img = import_from_png(args.input, palette_id=args.palette)
        save_pixelart(img, args.output)
        print(f"Successfully saved .pixelart to {args.output}")
        if args.write_preview:
            preview_img = render_preview(img, scale=8) # Default scale 8 for sidecars
            sidecar_path = get_sidecar_path(args.output)
            preview_img.save(sidecar_path, format="PNG")
            print(f"Successfully saved sidecar preview to {sidecar_path}")
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
        print("--- PixelArtImage Inspector ---")
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
            print("Transparency: none")

        # Standard encoding info for v1-alpha
        print("Version:      1")
        print("Encoding:     rows")

        if img.metadata:
            print(f"Metadata:     {img.metadata}")

    except Exception as e:
        print(f"Error inspecting file: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_inspect_png(args):
    try:
        img_rgba = load_image_rgba(args.input)
        res = inspect_image(
            img_rgba,
            max_scale=args.max_scale_candidate,
            allow_near_color_merge=args.allow_near_color_merge,
            binarize_alpha_flag=args.binarize_alpha
        )

        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            print("--- PNG Inspection Report ---")
            print(f"File:        {args.input}")
            print(f"Verdict:     {res.verdict.value.upper()}")
            print(f"Score:       {res.score}/100")
            print(f"Dimensions:  {res.source_width} x {res.source_height}")
            print(f"Colors:      {res.unique_colors} unique")
            print(f"Alpha:       {res.alpha_mode_summary}")

            if res.suspected_integer_scale:
                print(f"Suspected Scale: x{res.suspected_integer_scale}")

            if res.reasons:
                print("\nReasons:")
                for r in res.reasons:
                    print(f"  - {r}")

            if res.warnings:
                print("\nWarnings:")
                for w in res.warnings:
                    print(f"  - {w}")

            if res.suggested_normalizations:
                print("\nSuggested Normalizations:")
                for n in res.suggested_normalizations:
                    print(f"  - {n}")

    except Exception as e:
        print(f"Error inspecting PNG: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_ingest_png(args):
    print(f"Ingesting PNG: {args.input}")
    try:
        pixelart, res = process_ingest(
            filepath=args.input,
            max_scale=args.max_scale_candidate,
            allow_near_color_merge=args.allow_near_color_merge,
            binarize_alpha_flag=args.binarize_alpha,
            force=args.force,
            palette_id=args.builtin_palette
        )

        if args.report:
            with open(args.report, "w", encoding="utf-8") as f:
                json.dump(res.to_dict(), f, indent=2)
            print(f"Saved ingest report to {args.report}")

        if pixelart is None:
            print(f"Ingest rejected. Verdict: {res.verdict.value}", file=sys.stderr)
            sys.exit(1)

        save_pixelart(pixelart, args.output)
        print(f"Successfully ingested and saved .pixelart to {args.output}")
        print(f"Verdict: {res.verdict.value}")
        if res.applied_normalizations:
            print(f"Applied normalizations: {', '.join(res.applied_normalizations)}")

        if args.write_preview and pixelart is not None:
            preview_img = render_preview(pixelart, scale=8) # Default scale 8 for sidecars
            sidecar_path = get_sidecar_path(args.output)
            preview_img.save(sidecar_path, format="PNG")
            print(f"Successfully saved sidecar preview to {sidecar_path}")

    except Exception as e:
        print(f"Error during ingest: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_view(args):
    try:
        img = load_pixelart(args.input)
        preview_img = render_preview(
            img,
            scale=args.scale,
            grid=args.grid,
            bg_mode=args.bg_mode,
            bg_color=args.bg_color
        )
        print(f"Opening viewer for {args.input}...")
        preview_img.show(title=f"pixelarter view: {args.input}")
    except Exception as e:
        print(f"Error viewing .pixelart: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_preview(args):
    try:
        img = load_pixelart(args.input)
        preview_img = render_preview(
            img,
            scale=args.scale,
            grid=args.grid,
            bg_mode=args.bg_mode,
            bg_color=args.bg_color
        )
        preview_img.save(args.output, format="PNG")
        print(f"Successfully exported preview PNG to {args.output} (scale x{args.scale})")
    except Exception as e:
        print(f"Error generating preview: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_preview_sidecar(args):
    try:
        img = load_pixelart(args.input)
        preview_img = render_preview(
            img,
            scale=args.scale,
            grid=args.grid,
            bg_mode=args.bg_mode,
            bg_color=args.bg_color
        )
        sidecar_path = get_sidecar_path(args.input)
        preview_img.save(sidecar_path, format="PNG")
        print(f"Successfully saved sidecar preview to {sidecar_path}")
    except Exception as e:
        print(f"Error generating sidecar preview: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="pixelarter CLI tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # import-png command
    parser_import = subparsers.add_parser("import-png", help="Convert PNG to .pixelart format")
    parser_import.add_argument("-i", "--input", required=True, help="Input PNG file")
    parser_import.add_argument("-o", "--output", required=True, help="Output .pixelart file")
    parser_import.add_argument("-p", "--palette", help="Builtin palette ID to use (e.g., pxa-16-v1). If not provided, embedded mode is used.")
    parser_import.add_argument("--write-preview", action="store_true", help="Automatically generate a sidecar preview PNG")
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

    # inspect-png command
    parser_inspect_png = subparsers.add_parser("inspect-png", help="Inspect a PNG file for pixel-art ingest suitability")
    parser_inspect_png.add_argument("input", help="Input PNG file")
    parser_inspect_png.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser_inspect_png.add_argument("--max-scale-candidate", type=int, default=6, help="Maximum integer scale to check (default: 6)")
    parser_inspect_png.add_argument("--allow-near-color-merge", action="store_true", help="Allow merging very similar colors")
    parser_inspect_png.add_argument("--binarize-alpha", action="store_true", help="Allow binarizing slightly dirty alpha channels")
    parser_inspect_png.set_defaults(func=cmd_inspect_png)

    # ingest-png command
    parser_ingest_png = subparsers.add_parser("ingest-png", help="Ingest a PNG file, normalize safely, and save as .pixelart")
    parser_ingest_png.add_argument("input", help="Input PNG file")
    parser_ingest_png.add_argument("-o", "--output", required=True, help="Output .pixelart file")
    parser_ingest_png.add_argument("--report", help="Save a detailed ingest report to a JSON file")
    parser_ingest_png.add_argument("--force", action="store_true", help="Force ingest even if rejected")
    parser_ingest_png.add_argument("--allow-near-color-merge", action="store_true", help="Allow merging very similar colors")
    parser_ingest_png.add_argument("--binarize-alpha", action="store_true", help="Allow binarizing slightly dirty alpha channels")
    parser_ingest_png.add_argument("--max-scale-candidate", type=int, default=6, help="Maximum integer scale to check (default: 6)")
    parser_ingest_png.add_argument("--builtin-palette", help="Remap to a builtin palette ID (e.g., pxa-16-v1)")
    parser_ingest_png.add_argument("--embedded-palette", action="store_true", help="Explicitly use embedded palette (default behavior)")
    parser_ingest_png.add_argument("--write-preview", action="store_true", help="Automatically generate a sidecar preview PNG")
    parser_ingest_png.set_defaults(func=cmd_ingest_png)

    # view command
    parser_view = subparsers.add_parser("view", help="View a .pixelart file")
    parser_view.add_argument("input", help="The .pixelart file to view")
    parser_view.add_argument("-s", "--scale", type=int, default=8, help="Integer scale factor for viewing (default 8)")
    parser_view.add_argument("--grid", action="store_true", help="Show grid overlay")
    parser_view.add_argument("--bg-mode", choices=["transparent", "checker", "solid"], default="transparent", help="Background compositing mode")
    parser_view.add_argument("--bg-color", help="Background hex color for solid mode (e.g., '#FFFFFF')")
    parser_view.set_defaults(func=cmd_view)

    # preview command
    parser_preview = subparsers.add_parser("preview", help="Generate a preview PNG from a .pixelart file")
    parser_preview.add_argument("input", help="Input .pixelart file")
    parser_preview.add_argument("-o", "--output", required=True, help="Output PNG file")
    parser_preview.add_argument("-s", "--scale", type=int, default=1, help="Integer scale factor for the output PNG (default 1)")
    parser_preview.add_argument("--grid", action="store_true", help="Show grid overlay")
    parser_preview.add_argument("--bg-mode", choices=["transparent", "checker", "solid"], default="transparent", help="Background compositing mode")
    parser_preview.add_argument("--bg-color", help="Background hex color for solid mode (e.g., '#FFFFFF')")
    parser_preview.set_defaults(func=cmd_preview)

    # preview-sidecar command
    parser_preview_sidecar = subparsers.add_parser("preview-sidecar", help="Generate a sidecar preview PNG next to a .pixelart file")
    parser_preview_sidecar.add_argument("input", help="Input .pixelart file")
    parser_preview_sidecar.add_argument("-s", "--scale", type=int, default=8, help="Integer scale factor for the sidecar PNG (default 8)")
    parser_preview_sidecar.add_argument("--grid", action="store_true", help="Show grid overlay")
    parser_preview_sidecar.add_argument("--bg-mode", choices=["transparent", "checker", "solid"], default="transparent", help="Background compositing mode")
    parser_preview_sidecar.add_argument("--bg-color", help="Background hex color for solid mode (e.g., '#FFFFFF')")
    parser_preview_sidecar.set_defaults(func=cmd_preview_sidecar)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
