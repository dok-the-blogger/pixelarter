# Ingest Pipeline

The ingest pipeline is a crucial "gatekeeper" designed to ensure that PNGs fed into the `pixelarter` project are actually suitable as pixel-art targets.

Its primary job is NOT to restore or stylize a photograph into pixel art, nor is it to guess how a badly ruined image should look. Instead, its job is to:
1. Filter out completely inappropriate images (e.g., highly continuous textures, noise, thousands of unique colors).
2. Accept clean pixel-art images.
3. Automatically apply **Safe Normalizations** to mechanical issues.

## Difference Between `inspect` and `ingest`

- `inspect-png`: Performs the heuristic analysis of the PNG image and reports on the findings (score, verdict, suggested normalizations). It does not modify files. Useful for generating data validation reports.
- `ingest-png`: Analyzes the PNG and, if accepted, safely applies the necessary normalizations to convert it into the `.pixelart` format. By default, it refuses to ingest images that are rejected by the heuristic rules.

## The Heuristic Score and Verdict System

Every image is assigned a score (0 to 100) and evaluated against hard rules. Based on this, it receives one of three verdicts:
- `accepted`: The image is clean, discrete pixel art. No normalizations required.
- `accepted_with_normalization`: The image is generally acceptable but has minor technical issues (e.g., transparent borders, strict integer upscales) that can be mechanically fixed.
- `rejected`: The image failed a hard heuristic or its score dropped too low.

### Rejection Criteria

An image may be rejected for several reasons:
- Too many unique colors (e.g., > 256) indicating standard raster graphics or heavy bilinear scaling.
- Heavy anti-aliasing ("dirty alpha").
- Very low discreteness (lack of flat, contiguous colored areas).
- Near-integer upscaling artifacts that cannot be safely collapsed without aggressive averaging.

## Safe Normalizations

The normalizations performed during ingest are explicitly non-destructive and do not impart "artistic decisions":

1. **Crop Transparent Border**: Removes entirely empty transparent regions around the image bounds.
2. **Collapse Integer Upscale**: Detects if an image is perfectly scaled up by an integer factor (2x, 3x, etc.) using nearest-neighbor logic, and safely collapses it back to its canonical logical grid.
3. **Optional Binarize Alpha (`--binarize-alpha`)**: A cautious mode that forces semi-transparent pixels to 0 or 255 if the user permits it.
4. **Optional Near-Color Merge (`--allow-near-color-merge`)**: If enabled by the user, this conservatively merges colors that are nearly identical (e.g., compression artifacts) prior to checking upscale logic.

Any changes applied are fully documented in the `--report` JSON.
