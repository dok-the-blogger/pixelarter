# pixelarter

**Status: Early Experimental MVP**

`pixelarter` is a localized restoration and discretization tool designed to bring almost-pixel-art (or degraded pixel-art) images to a pixel-perfect state.

**What this is NOT:**
- This is NOT an image generator.
- This is NOT a "photo to pixel-art" stylization filter.

**What this IS:**
- A restoration, cleanup, and discretization tool for images that are *already* very close to pixel art (e.g., scaled-up pixel art with bilinear artifacts, slight noise, or color drift).
- The primary focus is **local, patch-based restoration**. The model does not need to understand the global scene; it reconstructs the correct pixel structure and clean discrete colors within small patches.
- The ultimate goal is **pixel-perfect output**.
- Currently, the baseline model operates in RGB space, but the architecture is designed to be compatible with a future **palette-aware mode** (where the output is palette indices).

## Project Setup

The project uses a standard `pyproject.toml` setup.

### Environment Installation

1. Create a virtual environment (e.g., using `venv` or `conda`). Recommended: Python 3.11+.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the project in editable mode with dependencies:
   ```bash
   pip install -e .
   ```
3. (Optional) Install development dependencies (for testing and linting):
   ```bash
   pip install -e ".[dev]"
   ```

## Running the Baseline

### Training

To run the baseline training on synthetic degraded pairs:
1. Put your clean pixel-art target images in a folder (e.g., `data/raw/`).
2. Update the config file at `configs/baseline_train.yaml` with the correct path to your data.
3. Run the training script:
   ```bash
   python scripts/train.py --config configs/baseline_train.yaml
   ```

### Inference

To run inference on a single degraded image:
1. Ensure you have a trained checkpoint (e.g., `runs/baseline/best_model.pth`).
2. Run the inference script:
   ```bash
   python scripts/infer.py --config configs/baseline_infer.yaml \
       --input data/test_image.png \
       --output data/test_image_restored.png \
       --checkpoint runs/baseline/best_model.pth
   ```

## The `.pixelart` Format

The `pixelarter` project introduces a canonical representation of pixel art via the `.pixelart` (v1-alpha) JSON format.
This format stores the **logical pixel grid** (dimensions, palette, and indices) rather than the screen-rendered raster image, avoiding display-related data like scaling.

The format supports two main palette modes:
- **Builtin (`"builtin"`)**: Uses a predefined project palette (e.g., `pxa-16-v1`).
- **Embedded (`"embedded"`)**: Extracts and embeds the exact colors directly within the file.

For more details, see the [Format Specification](docs/pixelart_format.md).

### CLI Usage

The project includes a unified CLI to interact with `.pixelart` files and PNG images.

1. **Importing from PNG**:
   ```bash
   pixelarter import-png -i input.png -o output.pixelart

   # Or, remap explicitly to a builtin palette:
   pixelarter import-png -i input.png -o output.pixelart -p pxa-16-v1
   ```

2. **Exporting to PNG**:
   ```bash
   pixelarter export-png -i input.pixelart -o output.png

   # Optional: Render with integer scaling (nearest-neighbor)
   pixelarter export-png -i input.pixelart -o output.png -s 4
   ```

3. **Viewing a `.pixelart` file**:
   ```bash
   # Opens the file in the default system viewer with an 8x scale
   pixelarter view input.pixelart

   # With grid and custom background mode
   pixelarter view input.pixelart -s 16 --grid --bg-mode checker
   ```

4. **Generating Previews**:
   The `.pixelart` format is logical. For sharing or viewing in external tools (like IrfanView), you can generate a **Preview PNG**.
   ```bash
   # Generate a preview PNG with scale 4
   pixelarter preview input.pixelart -o output.png -s 4

   # Generate a sidecar preview (creates input.preview.png)
   pixelarter preview-sidecar input.pixelart -s 8
   ```
   You can also generate sidecars automatically during import or ingest by adding the `--write-preview` flag.

5. **Inspecting a `.pixelart` file**:
   ```bash
   pixelarter inspect input.pixelart
   ```

6. **Inspecting a PNG for Ingest Suitability**:
   ```bash
   # Analyzes the PNG and prints an inspection report
   pixelarter inspect-png input.png

   # For machine-readable output:
   pixelarter inspect-png input.png --json
   ```

7. **Ingesting a PNG (Gatekeeper Pipeline)**:
   ```bash
   # Evaluates the PNG and creates a .pixelart file ONLY if it is a suitable pixel-art target.
   # Safe normalizations (like cropping transparent borders and collapsing strict upscales) are automatically applied.
   pixelarter ingest-png input.png -o output.pixelart --report ingest_report.json
   ```

   For detailed rules and heuristics about the ingest process, refer to the [Ingest Pipeline Documentation](docs/ingest_pipeline.md).
   For more on the viewing and preview philosophy, see the [Viewing and Previews Documentation](docs/viewing_and_preview.md).

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the development stages and future plans.
