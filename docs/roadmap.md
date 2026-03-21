# Roadmap

This outlines the development stages and future plans for **pixelarter**.

The goal is to grow the project systematically from a simple baseline to a robust tool for restoring degraded near-pixel-art images to pixel-perfect discrete outputs.

## Stage 0: Baseline RGB Patch Restoration (Current)
- Basic structure and setup of the repository.
- Synthetic degradation data pipeline (nearest/bilinear scaling, subpixel shifts, mild blur, small noise, color drift, JPEG-like artifacts).
- Baseline dataset for local patch-based training (e.g., input context $32 \times 32$, output target $16 \times 16$).
- Baseline RGB model (e.g., simple CNN or U-Net).
- Training loop and tiled inference logic.

## Stage 1: Palette-Aware Restoration
- Incorporate palette considerations into the loss function or input features without hard classification.
- Start penalizing non-discrete colors.

## Stage 2: Explicit Palette-Index Prediction
- Transition from RGB-output to palette-index-output.
- Provide a global image palette as an input, and predict the index of the color from the palette for each pixel.
- Enforce strict pixel-perfect output with no continuous RGB deviations.

## Stage 3: Grid/Phase Estimation
- Explicitly learn the scaling grid and block structure of scaled pixel art to prevent shifting artifacts.
- Subpixel alignment logic.

## Stage 4: Smarter Tiled Inference / Consensus Across Patches
- Implement more robust overlapping strategies for prediction consensus to remove artifacts on tile borders.
- Advanced overlapping and blending for prediction consistency.

## Stage 5: Advanced Cleanup of AA/Dithering/Line Thickness
- Explicit tasks to remove anti-aliasing artifacts cleanly.
- Restoring correct dithering patterns and single-pixel thick lines where appropriate.
