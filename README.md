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

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the development stages and future plans.
