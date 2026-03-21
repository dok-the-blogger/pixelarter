import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.formats.png import _build_palette_from_image, _remap_to_builtin_palette

from .models import PngInspectionResult, Verdict
from .analyzer import analyze_alpha, analyze_colors, detect_integer_scale, analyze_discreteness
from .normalizer import crop_transparent_border, collapse_integer_upscale, apply_near_color_merge, binarize_alpha

def load_image_rgba(filepath: str) -> np.ndarray:
    """Load image and ensure it's RGBA numpy array."""
    img = Image.open(filepath).convert("RGBA")
    return np.array(img)

def inspect_image(img_rgba: np.ndarray,
                  max_scale: int = 6,
                  allow_near_color_merge: bool = False,
                  binarize_alpha_flag: bool = False) -> PngInspectionResult:
    """
    Analyzes the image and returns an inspection result with verdict and suggested normalizations.
    """
    h, w, _ = img_rgba.shape
    res = PngInspectionResult(
        verdict=Verdict.REJECTED,
        score=100,
        source_width=w,
        source_height=h,
        logical_width=w,
        logical_height=h
    )

    # 1. Basic Analysis
    num_unique, num_rare, unique_ratio, rare_ratio = analyze_colors(img_rgba)
    res.unique_colors = num_unique

    alpha_mode, has_dirty_alpha = analyze_alpha(img_rgba)
    res.alpha_mode_summary = alpha_mode

    scale, is_strict_scale = detect_integer_scale(img_rgba, max_scale)
    res.suspected_integer_scale = scale

    flat_ratio = analyze_discreteness(img_rgba)

    # Track reasons and deductions
    score = 100

    # 2. Rule-based Evaluation & Penalty

    # Too many colors for pixel art
    if num_unique > 256:
        if allow_near_color_merge:
            res.warnings.append(f"High color count ({num_unique}). Near-color merge may help.")
            score -= 20
        else:
            res.reasons.append(f"Too many unique colors ({num_unique} > 256) without near-color merge allowed.")
            score -= 50

    # High rare color ratio (noise/fringe)
    if num_unique > 10 and rare_ratio > 0.1:
        res.warnings.append(f"High ratio of rare colors ({rare_ratio:.2f}). Possible noise/resampling.")
        score -= 15
        if not allow_near_color_merge:
             score -= 10

    # Dirty alpha
    if has_dirty_alpha:
        if binarize_alpha_flag:
            res.warnings.append("Dirty alpha detected. Will attempt to binarize.")
            res.suggested_normalizations.append("binarize_alpha")
            score -= 10
        else:
            res.reasons.append("Dirty semi-transparent alpha detected. Use --binarize-alpha to attempt fix.")
            score -= 30

    # Continuous texture (not pixel art)
    if flat_ratio < 0.2:
        res.reasons.append(f"Very low discreteness (flat_ratio={flat_ratio:.2f}). Likely not pixel art.")
        score -= 40

    # Integer upscale
    if scale is not None:
        if is_strict_scale:
            res.warnings.append(f"Strict integer upscale detected (x{scale}).")
            res.suggested_normalizations.append("collapse_integer_upscale")
        else:
            if allow_near_color_merge:
                res.warnings.append(f"Near-integer upscale detected (x{scale}). Will attempt collapse because near-color-merge is active.")
                res.suggested_normalizations.append("collapse_integer_upscale")
                score -= 10
            else:
                res.reasons.append(f"Non-strict upscale detected (x{scale}) without near-color-merge allowed. Rejecting hidden magic.")
                score -= 40

    # Transparent border crop
    _, was_cropped = crop_transparent_border(img_rgba)
    if was_cropped:
        res.warnings.append("Transparent border detected.")
        res.suggested_normalizations.append("crop_transparent_border")

    if allow_near_color_merge:
        res.suggested_normalizations.append("apply_near_color_merge")

    # Set Score bounds
    score = max(0, min(100, int(score)))
    res.score = score

    # 3. Verdict assignment based on score and hard rules
    if score >= 85:
        if len(res.suggested_normalizations) > 0:
            res.verdict = Verdict.ACCEPTED_WITH_NORMALIZATION
        else:
            res.verdict = Verdict.ACCEPTED
    elif score >= 60:
        res.verdict = Verdict.ACCEPTED_WITH_NORMALIZATION
    else:
        res.verdict = Verdict.REJECTED

    res.metadata = {
        "unique_ratio": float(unique_ratio),
        "rare_ratio": float(rare_ratio),
        "flat_ratio": float(flat_ratio),
        "is_strict_scale": bool(is_strict_scale) if scale is not None else False
    }

    return res

def process_ingest(filepath: str,
                   max_scale: int = 6,
                   allow_near_color_merge: bool = False,
                   binarize_alpha_flag: bool = False,
                   force: bool = False,
                   palette_id: Optional[str] = None) -> Tuple[Optional[PixelArtImage], PngInspectionResult]:
    """
    Main ingest pipeline.
    Reads image, inspects, applies normalizations, and converts to PixelArtImage.
    """
    try:
        img_rgba = load_image_rgba(filepath)
    except Exception as e:
        raise ValueError(f"Failed to load PNG: {e}")

    res = inspect_image(img_rgba, max_scale, allow_near_color_merge, binarize_alpha_flag)

    if res.verdict == Verdict.REJECTED and not force:
        return None, res

    # Apply normalizations safely
    working_img = img_rgba.copy()

    if "crop_transparent_border" in res.suggested_normalizations:
        working_img, was_cropped = crop_transparent_border(working_img)
        if was_cropped:
            res.applied_normalizations.append("crop_transparent_border")

    if binarize_alpha_flag and "binarize_alpha" in res.suggested_normalizations:
        working_img, was_binarized = binarize_alpha(working_img)
        if was_binarized:
            res.applied_normalizations.append("binarize_alpha")

    if allow_near_color_merge and "apply_near_color_merge" in res.suggested_normalizations:
        working_img, was_merged = apply_near_color_merge(working_img)
        if was_merged:
            res.applied_normalizations.append("apply_near_color_merge")

    if "collapse_integer_upscale" in res.suggested_normalizations:
        scale = res.suspected_integer_scale
        if scale is not None:
            working_img, was_collapsed = collapse_integer_upscale(working_img, scale)
            if was_collapsed:
                res.applied_normalizations.append("collapse_integer_upscale")

    # Update stats post-normalization
    res.logical_height, res.logical_width, _ = working_img.shape

    final_unique, _, _, _ = analyze_colors(working_img)
    res.effective_colors = final_unique

    # If it was still bad after forced ingest...
    if final_unique > 256 and not force:
         res.reasons.append(f"Even after normalizations, too many colors ({final_unique}). Rejecting.")
         res.verdict = Verdict.REJECTED
         return None, res

    # Construct PixelArtImage
    try:
        img_pil = Image.fromarray(working_img, mode="RGBA")
        if palette_id:
            indices, trans_idx = _remap_to_builtin_palette(img_pil, palette_id)
            pixelart = PixelArtImage(
                width=res.logical_width, height=res.logical_height,
                palette_mode="builtin", palette_id=palette_id, palette=None,
                transparent_index=trans_idx, indices=indices, metadata={"ingest_report": res.to_dict()}
            )
        else:
            palette, indices, trans_idx = _build_palette_from_image(img_pil)
            pixelart = PixelArtImage(
                width=res.logical_width, height=res.logical_height,
                palette_mode="embedded", palette_id=None, palette=palette,
                transparent_index=trans_idx, indices=indices, metadata={"ingest_report": res.to_dict()}
            )
    except Exception as e:
        res.reasons.append(f"Failed to build pixelart: {e}")
        res.verdict = Verdict.REJECTED
        if not force:
            return None, res
        else:
            raise ValueError(f"Forced ingest failed during format conversion: {e}")

    return pixelart, res
