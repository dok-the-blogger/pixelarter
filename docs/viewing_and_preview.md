# Viewing and Previews

## Philosophy
The `.pixelart` format is the canonical logical representation of pixel art in `pixelarter`. It intentionally leaves out physical rendering aspects such as upscaling, blurring, interpolation, and grid display.

However, to build a practical workflow, you need to be able to see and share what you're working with. `pixelarter` provides commands for **Viewing** and generating **Previews**.

These preview images are intentionally distinct from canonical exports. A preview image is a temporary visual aid designed for humans and standard image viewers like IrfanView or your OS's default viewer.

## The Viewer (`pixelarter view`)
The built-in viewer is intentionally minimal. It is designed around simplicity and strict visualization, avoiding heavy GUI frameworks.
- It parses the logical data.
- It performs integer nearest-neighbor upscaling (default 8x) so you can clearly see individual pixels.
- It optionally renders a grid or provides background compositing.
- It launches your OS's native image viewer (via `Pillow`) with the preview.

This fallback is sufficient for early workflow stages while strictly adhering to the architectural goal of avoiding bloated UI dependencies.

## The Sidecar Preview Workflow
Standard image viewers cannot natively read `.pixelart` JSON files. To seamlessly browse directories containing `.pixelart` files, `pixelarter` supports a **sidecar workflow**.

A sidecar preview is simply a PNG file rendered next to the canonical file:
```
my_asset.pixelart
my_asset.preview.png
```

You can generate sidecar previews manually via the `preview-sidecar` command, or automatically during import/ingest by supplying the `--write-preview` flag.

## Why Not Native Plugins Yet?
While it's possible to build native plugins (e.g., for IrfanView) to read `.pixelart` files directly, this adds significant maintenance and limits interoperability across different tools. Using sidecar PNG previews ensures maximum compatibility across **all** tools, cloud storage previews, and chat applications with virtually zero integration cost.

Native integrations are left as a future direction once the format thoroughly matures.
