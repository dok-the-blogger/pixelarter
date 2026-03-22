
import numpy as np


def crop_transparent_border(img_rgba: np.ndarray) -> tuple[np.ndarray, bool]:
    """
    Crops the fully transparent border around the image.
    Returns:
        cropped_img (np.ndarray)
        was_cropped (bool)
    """
    if img_rgba.shape[-1] != 4:
        return img_rgba, False

    alpha = img_rgba[:, :, 3]

    # Find bounding box of non-transparent pixels
    non_transparent = np.where(alpha > 0)

    if len(non_transparent[0]) == 0:
        # Image is completely transparent
        return img_rgba, False

    min_y = int(np.min(non_transparent[0]))
    max_y = int(np.max(non_transparent[0]))
    min_x = int(np.min(non_transparent[1]))
    max_x = int(np.max(non_transparent[1]))

    # Check if a crop is actually needed
    if min_y == 0 and max_y == img_rgba.shape[0] - 1 and min_x == 0 and max_x == img_rgba.shape[1] - 1:
        return img_rgba, False

    cropped_img = img_rgba[min_y:max_y+1, min_x:max_x+1]
    return cropped_img.copy(), True

def collapse_integer_upscale(img_rgba: np.ndarray, scale: int) -> tuple[np.ndarray, bool]:
    """
    Collapses an integer upscale by taking the exact top-left pixel of each block,
    or the modal pixel if strictly required. We'll use the top-left pixel
    as it is faster and deterministic, and we assume the block is uniform.
    Returns:
        collapsed_img (np.ndarray)
        was_collapsed (bool)
    """
    h, w, c = img_rgba.shape
    if h % scale != 0 or w % scale != 0:
        return img_rgba, False

    new_h, new_w = h // scale, w // scale

    # Since blocks are supposed to be uniform, we can just take the top-left pixel of each block
    collapsed_img = img_rgba[0::scale, 0::scale, :].copy()

    return collapsed_img, True

def apply_near_color_merge(img_rgba: np.ndarray, threshold: float = 10.0) -> tuple[np.ndarray, bool]:
    """
    Merges very similar colors using a simple Euclidean distance threshold.
    It maps colors to the most frequent color in the cluster.
    Returns:
        merged_img (np.ndarray)
        was_merged (bool)
    """
    # Flatten to list of tuples
    pixels = img_rgba.reshape(-1, img_rgba.shape[-1])

    # Convert to contiguous array for faster unique
    pixels_contig = np.ascontiguousarray(pixels)
    dtype = np.dtype((np.void, pixels_contig.dtype.itemsize * img_rgba.shape[-1]))
    unique_rows, counts = np.unique(pixels_contig.view(dtype), return_counts=True)

    unique_colors = np.frombuffer(unique_rows.tobytes(), dtype=pixels.dtype).reshape(-1, img_rgba.shape[-1])

    if len(unique_colors) <= 1:
        return img_rgba, False

    # Sort by frequency (most common first)
    sorted_indices = np.argsort(-counts)
    unique_colors = unique_colors[sorted_indices]
    counts = counts[sorted_indices]

    mapping = {}
    was_merged = False

    for i in range(len(unique_colors)):
        color = unique_colors[i]

        # Don't merge based on fully transparent colors
        if len(color) == 4 and color[3] == 0:
            mapping[tuple(color)] = color
            continue

        mapped = False
        # Compare to already established "cluster centers"
        for j in range(i):
            cluster_center = unique_colors[j]
            if len(cluster_center) == 4 and cluster_center[3] == 0:
                continue

            # Exact alpha match required for safety
            if len(color) == 4 and color[3] != cluster_center[3]:
                continue

            dist_rgb = np.linalg.norm(color[:3].astype(float) - cluster_center[:3].astype(float))

            if dist_rgb <= threshold:
                mapping[tuple(color)] = cluster_center
                mapped = True
                was_merged = True
                break

        if not mapped:
            mapping[tuple(color)] = color

    if not was_merged:
        return img_rgba, False

    # Apply mapping using a simple dictionary lookup for each pixel
    # This is slow but safe for small pixel art
    merged_img = np.zeros_like(pixels)
    for i, p in enumerate(pixels):
        merged_img[i] = mapping[tuple(p)]

    return merged_img.reshape(img_rgba.shape), True

def binarize_alpha(img_rgba: np.ndarray, threshold: int = 128) -> tuple[np.ndarray, bool]:
    """
    Binarizes the alpha channel.
    Returns:
        binarized_img (np.ndarray)
        was_binarized (bool)
    """
    if img_rgba.shape[-1] != 4:
        return img_rgba, False

    alpha = img_rgba[:, :, 3]
    unique_alphas = np.unique(alpha)

    # Check if already binary
    is_binary = True
    for a in unique_alphas:
        if a not in (0, 255):
            is_binary = False
            break

    if is_binary:
        return img_rgba, False

    binarized_img = img_rgba.copy()

    # Binarize based on threshold
    binarized_img[:, :, 3] = np.where(alpha >= threshold, 255, 0)

    # For pixels that became fully transparent, set RGB to 0 to canonicalize
    transparent_mask = binarized_img[:, :, 3] == 0
    binarized_img[transparent_mask, :3] = 0

    return binarized_img, True
