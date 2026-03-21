import json
import numpy as np
from typing import Dict, Any

from pixelarter.models.pixelart import PixelArtImage


def save_pixelart(image: PixelArtImage, filepath: str) -> None:
    """
    Serialize a PixelArtImage to a .pixelart JSON file.
    """
    data = {
        "format": "pixelart",
        "version": 1,
        "width": image.width,
        "height": image.height,
        "palette_mode": image.palette_mode,
        "transparent_index": image.transparent_index,
        "encoding": "rows",
        "rows": image.indices.tolist(),
        "metadata": image.metadata,
    }

    if image.palette_mode == "builtin":
        data["palette_id"] = image.palette_id
    elif image.palette_mode == "embedded":
        data["palette"] = image.palette

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_pixelart(filepath: str) -> PixelArtImage:
    """
    Deserialize a .pixelart JSON file into a PixelArtImage.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse .pixelart file as JSON: {e}")

    # Validate basic format metadata
    if data.get("format") != "pixelart":
        raise ValueError(f"Invalid format identifier: '{data.get('format')}'. Expected 'pixelart'.")
    if data.get("version") != 1:
        raise ValueError(f"Unsupported format version: {data.get('version')}. Expected 1.")
    if data.get("encoding") != "rows":
        raise ValueError(f"Unsupported encoding: '{data.get('encoding')}'. Expected 'rows'.")

    # Extract required fields with basic validation
    try:
        width = int(data["width"])
        height = int(data["height"])
        palette_mode = data["palette_mode"]
        rows = data["rows"]
    except KeyError as e:
        raise ValueError(f"Missing required field in .pixelart file: {e}")

    # Process optional fields
    transparent_index = data.get("transparent_index")
    metadata = data.get("metadata", {})
    palette_id = data.get("palette_id")
    palette = data.get("palette")

    # Convert rows back to numpy array
    try:
        indices = np.array(rows, dtype=np.int32)
    except Exception as e:
        raise ValueError(f"Failed to parse 'rows' into numpy array: {e}")

    return PixelArtImage(
        width=width,
        height=height,
        palette_mode=palette_mode,
        palette_id=palette_id,
        palette=palette,
        transparent_index=transparent_index,
        indices=indices,
        metadata=metadata
    )
