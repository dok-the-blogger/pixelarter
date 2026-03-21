import numpy as np
from PIL import Image
from typing import Tuple, List, Optional, Dict
from collections import Counter

def analyze_alpha(img_rgba: np.ndarray) -> Tuple[str, bool]:
    """
    Analyze the alpha channel.
    Returns:
        alpha_mode_summary: "none", "binary", "semi-transparent", "dirty"
        has_dirty_alpha: bool indicating if it has semi-transparent pixels
    """
    if img_rgba.shape[-1] != 4:
        return "none", False

    alpha = img_rgba[:, :, 3]
    unique_alphas = np.unique(alpha)

    if len(unique_alphas) == 1 and unique_alphas[0] == 255:
        return "none", False

    is_binary = True
    for a in unique_alphas:
        if a not in (0, 255):
            is_binary = False
            break

    if is_binary:
        return "binary", False

    # Heuristic for "dirty" vs "intentional semi-transparent"
    total_pixels = alpha.size
    semi_transparent_pixels = np.sum((alpha > 0) & (alpha < 255))
    semi_ratio = semi_transparent_pixels / total_pixels

    if semi_ratio > 0.05:
        # Lots of semi-transparent, maybe intentional or very blurred
        return "semi-transparent", True
    else:
        # Only a few semi-transparent, likely dirty anti-aliasing on edges
        return "dirty", True

def analyze_colors(img_rgba: np.ndarray) -> Tuple[int, int, float, float]:
    """
    Analyze colors.
    Returns:
        num_unique (int)
        num_rare (int)
        unique_ratio (float)
        rare_ratio (float)
    """
    # Flatten to list of tuples
    pixels = img_rgba.reshape(-1, img_rgba.shape[-1])
    # Ignore fully transparent pixels for color counting
    if img_rgba.shape[-1] == 4:
        valid_pixels = pixels[pixels[:, 3] > 0]
    else:
        valid_pixels = pixels

    if len(valid_pixels) == 0:
        return 0, 0, 0.0, 0.0

    # Convert to contiguous array for faster unique
    valid_pixels = np.ascontiguousarray(valid_pixels)
    # view as single type
    dtype = np.dtype((np.void, valid_pixels.dtype.itemsize * valid_pixels.shape[1]))
    unique_rows, counts = np.unique(valid_pixels.view(dtype), return_counts=True)

    num_unique = len(unique_rows)

    # Rare colors (appear very few times, e.g. < 5 or < 0.1% depending on size)
    rare_threshold = max(3, len(valid_pixels) * 0.0005)
    num_rare = np.sum(counts < rare_threshold)

    unique_ratio = num_unique / len(valid_pixels)
    rare_ratio = num_rare / num_unique if num_unique > 0 else 0

    return num_unique, num_rare, unique_ratio, rare_ratio

def detect_integer_scale(img_rgba: np.ndarray, max_scale: int = 6) -> Tuple[Optional[int], bool]:
    """
    Detect if the image is an integer upscale.
    Returns:
        scale (int or None): The detected scale factor (2 to max_scale).
        is_strict (bool): True if the upscale is strictly mechanical without deviations inside blocks.
    """
    h, w, c = img_rgba.shape

    # Check scales from max_scale down to 2
    for scale in range(max_scale, 1, -1):
        if h % scale == 0 and w % scale == 0:
            new_h, new_w = h // scale, w // scale

            # Reshape image into blocks of scale x scale
            blocks = img_rgba.reshape(new_h, scale, new_w, scale, c)
            blocks = blocks.transpose(0, 2, 1, 3, 4).reshape(new_h * new_w, scale * scale, c)

            # For each block, find the min and max across pixels
            block_mins = blocks.min(axis=1)
            block_maxs = blocks.max(axis=1)

            # Check if all pixels within every block are exactly the same
            diffs = block_maxs - block_mins
            max_diff_overall = diffs.max()

            if max_diff_overall == 0:
                # Strictly uniform blocks!
                return scale, True

            # For near-misses, we can check if it's "mostly" uniform
            # But the requirement is to only allow strict collapse without flags.
            # We return the scale if it's very close, but set is_strict=False
            if max_diff_overall < 10:
                return scale, False

    return None, False

def analyze_discreteness(img_rgba: np.ndarray) -> float:
    """
    Heuristics to check how discrete/pixel-art-like the image is.
    Check flat regions. Returns flat_ratio.
    """
    if img_rgba.shape[0] < 2 or img_rgba.shape[1] < 2:
        return 1.0

    diff_h = np.sum(np.abs(img_rgba[:, 1:].astype(int) - img_rgba[:, :-1].astype(int)), axis=-1)
    diff_v = np.sum(np.abs(img_rgba[1:, :].astype(int) - img_rgba[:-1, :].astype(int)), axis=-1)

    flat_h = diff_h == 0
    flat_v = diff_v == 0

    total_h = flat_h.size
    total_v = flat_v.size

    flat_ratio_h = np.sum(flat_h) / total_h
    flat_ratio_v = np.sum(flat_v) / total_v

    avg_flat_ratio = (flat_ratio_h + flat_ratio_v) / 2

    return avg_flat_ratio
