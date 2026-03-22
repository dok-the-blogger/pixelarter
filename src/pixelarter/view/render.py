import os
from typing import Literal

import numpy as np
from PIL import Image, ImageDraw

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.palette.registry import get_builtin_palette


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB hex string to (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def render_preview(
    image: PixelArtImage,
    scale: int = 1,
    grid: bool = False,
    bg_mode: Literal["transparent", "checker", "solid"] = "transparent",
    bg_color: str | None = None
) -> Image.Image:
    """
    Renders a PixelArtImage to a PIL Image suitable for viewing or exporting as a preview.

    Args:
        image: The PixelArtImage to render.
        scale: Integer scale factor (nearest-neighbor).
        grid: Whether to draw a grid overlay.
        bg_mode: Background compositing mode for transparent pixels.
        bg_color: Hex color string for solid background mode (e.g. '#FF00FF').

    Returns:
        PIL.Image.Image in RGBA or RGB mode.
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

    palette_rgb = [hex_to_rgb(c) for c in palette_hex]
    h, w = image.height, image.width

    # Initialize output array (RGBA)
    out_data = np.zeros((h, w, 4), dtype=np.uint8)

    # Fast rendering logic using numpy indexing if possible, but fallback to loops for transparency
    # For now, explicit loop or vectorization:
    if image.transparent_index is None:
        # Vectorized mapping
        # Convert palette_rgb to a numpy array for advanced indexing
        pal_array = np.array(palette_rgb, dtype=np.uint8)
        # indices shape is (h, w), output will be (h, w, 3)
        rgb_data = pal_array[image.indices]
        # Set alpha to 255
        out_data[:, :, :3] = rgb_data
        out_data[:, :, 3] = 255
    else:
        # Vectorized mapping with transparency
        pal_array = np.array(palette_rgb, dtype=np.uint8)
        rgb_data = pal_array[image.indices]
        alpha_data = np.full((h, w), 255, dtype=np.uint8)

        # Identify transparent pixels
        transp_mask = (image.indices == image.transparent_index)

        # Apply RGB and Alpha
        out_data[:, :, :3] = rgb_data
        out_data[:, :, 3] = alpha_data

        # Zero out transparent pixels
        out_data[transp_mask] = (0, 0, 0, 0)

    # Create PIL Image
    img = Image.fromarray(out_data, mode="RGBA")

    # Apply scaling (nearest neighbor)
    if scale > 1:
        img = img.resize((w * scale, h * scale), resample=Image.Resampling.NEAREST)

    # Background Compositing
    if image.transparent_index is not None and bg_mode != "transparent":
        bg_img = Image.new("RGBA", img.size)
        if bg_mode == "solid":
            if not bg_color:
                bg_color = "#FFFFFF" # default to white if not provided
            solid_rgb = hex_to_rgb(bg_color)
            bg_img.paste(solid_rgb + (255,), (0, 0, img.width, img.height))
        elif bg_mode == "checker":
            # Draw a checkerboard pattern
            checker_size = max(8, scale) # Reasonable checker size
            draw = ImageDraw.Draw(bg_img)
            color1 = (200, 200, 200, 255)
            color2 = (255, 255, 255, 255)

            for y in range(0, img.height, checker_size):
                for x in range(0, img.width, checker_size):
                    c = color1 if ((x // checker_size) + (y // checker_size)) % 2 == 0 else color2
                    draw.rectangle([x, y, x + checker_size - 1, y + checker_size - 1], fill=c)

        # Composite the image over the background
        bg_img.paste(img, (0, 0), img)
        img = bg_img

    # Grid Overlay
    if grid and scale > 1:
        # Draw grid lines
        draw = ImageDraw.Draw(img)
        # Choose a grid color with some transparency
        grid_color = (128, 128, 128, 128)

        # Draw vertical lines
        for x in range(0, img.width + 1, scale):
            draw.line([(x, 0), (x, img.height)], fill=grid_color, width=1)
        # Draw horizontal lines
        for y in range(0, img.height + 1, scale):
            draw.line([(0, y), (img.width, y)], fill=grid_color, width=1)

    return img

def get_sidecar_path(filepath: str) -> str:
    """
    Generates the sidecar preview path for a given .pixelart file.
    Example: 'sprite.pixelart' -> 'sprite.preview.png'
    """
    base, ext = os.path.splitext(filepath)
    if ext.lower() == ".pixelart":
        return f"{base}.preview.png"
    return f"{filepath}.preview.png"
