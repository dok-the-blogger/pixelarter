from typing import Optional, List, Tuple
from PIL import Image
import numpy as np

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.palette.registry import get_builtin_palette

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #RRGGBB hex string to (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert (R, G, B) tuple to #RRGGBB hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"

def _build_palette_from_image(img: Image.Image) -> Tuple[List[str], np.ndarray, Optional[int]]:
    """
    Extract exact unique colors from the image to build an embedded palette.
    Returns (palette_hex_list, indices_array, transparent_index).
    Raises an error if the number of unique colors is too large.
    """
    # Convert image to RGBA to easily handle transparency
    img = img.convert("RGBA")
    data = np.array(img)

    # Flatten array to list of (R, G, B, A) tuples
    pixels = data.reshape(-1, 4)
    pixels_tuples = [tuple(p) for p in pixels]

    unique_pixels = list(dict.fromkeys(pixels_tuples))  # Preserve order, unique

    # Simple limit to prevent massive files or accidental non-pixel-art images
    MAX_COLORS = 256
    if len(unique_pixels) > MAX_COLORS:
        raise ValueError(
            f"Image contains {len(unique_pixels)} unique colors, which exceeds the limit of {MAX_COLORS} "
            f"for automatic embedded palette. This may not be a valid pixel-art image or requires quantization."
        )

    # Build the palette list (ignoring alpha for the hex colors, but we track transparent index)
    palette_hex = []
    transparent_index = None
    color_to_idx = {}

    for idx, (r, g, b, a) in enumerate(unique_pixels):
        if a == 0:
            # We treat any fully transparent pixel as the transparent color
            if transparent_index is None:
                transparent_index = idx
                palette_hex.append(rgb_to_hex(0, 0, 0)) # Store as black for the palette array
            else:
                # If there are multiple transparent colors, we can just map them to the same transparent_index
                pass
            color_to_idx[(r, g, b, a)] = transparent_index
        else:
            palette_hex.append(rgb_to_hex(r, g, b))
            color_to_idx[(r, g, b, a)] = len(palette_hex) - 1

    # Remap image data to indices
    indices_flat = np.array([color_to_idx[p] for p in pixels_tuples], dtype=np.int32)
    indices = indices_flat.reshape(data.shape[0], data.shape[1])

    return palette_hex, indices, transparent_index


def _remap_to_builtin_palette(img: Image.Image, palette_id: str) -> Tuple[np.ndarray, Optional[int]]:
    """
    Remaps an image exactly to a builtin palette.
    Raises ValueError if a color in the image is not found in the builtin palette.
    """
    palette_hex = get_builtin_palette(palette_id)
    palette_rgb = [hex_to_rgb(c) for c in palette_hex]
    color_to_idx = {color: idx for idx, color in enumerate(palette_rgb)}

    img = img.convert("RGBA")
    data = np.array(img)
    pixels = data.reshape(-1, 4)

    indices_flat = np.zeros(len(pixels), dtype=np.int32)
    transparent_index = None

    # Check if there is a transparent color in the image
    for i, (r, g, b, a) in enumerate(pixels):
        if a == 0:
            if transparent_index is None:
                # We need to assign a transparent index or append one if the palette doesn't have it natively.
                # Since builtin palettes are fixed length, we could append or use a specific index.
                # For simplicity, if we find transparency but the palette doesn't support it, we raise an error,
                # or we define that builtin palettes don't natively support transparency without an explicit index.
                # For now, let's say the last index is transparent or raise an error if unsupported.
                raise ValueError(f"Image contains transparency, but remapping to builtin palette '{palette_id}' does not support transparency yet.")
            indices_flat[i] = transparent_index
        else:
            color = (r, g, b)
            if color not in color_to_idx:
                raise ValueError(f"Color {color} found in image is not present in builtin palette '{palette_id}'.")
            indices_flat[i] = color_to_idx[color]

    indices = indices_flat.reshape(data.shape[0], data.shape[1])
    return indices, transparent_index


def import_from_png(filepath: str, palette_id: Optional[str] = None) -> PixelArtImage:
    """
    Import a PNG image into a PixelArtImage.
    If palette_id is provided, remaps to the builtin palette.
    Otherwise, builds an embedded palette from exact image colors.
    """
    try:
        img = Image.open(filepath)
    except Exception as e:
        raise ValueError(f"Failed to load PNG from {filepath}: {e}")

    width, height = img.size

    if palette_id:
        indices, transparent_index = _remap_to_builtin_palette(img, palette_id)
        return PixelArtImage(
            width=width,
            height=height,
            palette_mode="builtin",
            palette_id=palette_id,
            palette=None,
            transparent_index=transparent_index,
            indices=indices,
        )
    else:
        palette, indices, transparent_index = _build_palette_from_image(img)
        return PixelArtImage(
            width=width,
            height=height,
            palette_mode="embedded",
            palette_id=None,
            palette=palette,
            transparent_index=transparent_index,
            indices=indices,
        )


def export_to_png(image: PixelArtImage, filepath: str, scale: int = 1) -> None:
    """
    Export a PixelArtImage to a PNG file.
    Uses nearest-neighbor scaling for export/preview.
    """
    if scale < 1:
        raise ValueError(f"Scale must be an integer >= 1, got {scale}")

    # Resolve palette
    if image.palette_mode == "builtin":
        if not image.palette_id:
            raise ValueError("palette_id is missing for builtin palette mode.")
        palette_hex = get_builtin_palette(image.palette_id)
    else:
        if not image.palette:
            raise ValueError("palette is missing for embedded palette mode.")
        palette_hex = image.palette

    # Build RGB(A) image data from indices
    palette_rgb = [hex_to_rgb(c) for c in palette_hex]

    # We will build an RGBA image array
    h, w = image.height, image.width
    out_data = np.zeros((h, w, 4), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            idx = image.indices[y, x]
            if idx == image.transparent_index:
                out_data[y, x] = (0, 0, 0, 0)
            else:
                r, g, b = palette_rgb[idx]
                out_data[y, x] = (r, g, b, 255)

    img = Image.fromarray(out_data, mode="RGBA")

    if scale > 1:
        new_size = (w * scale, h * scale)
        img = img.resize(new_size, resample=Image.Resampling.NEAREST)

    img.save(filepath, format="PNG")
