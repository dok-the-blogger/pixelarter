import pytest
import numpy as np
import os
from PIL import Image

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.palette.registry import get_builtin_palette, is_builtin_palette
from pixelarter.formats.pixelart import save_pixelart, load_pixelart
from pixelarter.formats.png import import_from_png, export_to_png


def test_pixelart_image_validation():
    indices = np.array([[0, 1], [1, 0]])
    # Valid builtin
    img = PixelArtImage(
        width=2, height=2, palette_mode="builtin", palette_id="pxa-16-v1",
        palette=None, transparent_index=None, indices=indices
    )
    assert img.width == 2

    # Invalid shape
    with pytest.raises(ValueError):
        PixelArtImage(
            width=3, height=2, palette_mode="builtin", palette_id="pxa-16-v1",
            palette=None, transparent_index=None, indices=indices
        )

    # Missing palette_id for builtin
    with pytest.raises(ValueError):
        PixelArtImage(
            width=2, height=2, palette_mode="builtin", palette_id=None,
            palette=None, transparent_index=None, indices=indices
        )

    # Missing palette for embedded
    with pytest.raises(ValueError):
        PixelArtImage(
            width=2, height=2, palette_mode="embedded", palette_id=None,
            palette=None, transparent_index=None, indices=indices
        )

    # Invalid index bounds for embedded
    bad_indices = np.array([[0, 5], [1, 0]])
    with pytest.raises(ValueError):
        PixelArtImage(
            width=2, height=2, palette_mode="embedded", palette_id=None,
            palette=["#000000", "#FFFFFF"], transparent_index=None, indices=bad_indices
        )

def test_palette_registry():
    assert is_builtin_palette("pxa-16-v1")
    assert not is_builtin_palette("unknown-palette")

    pal = get_builtin_palette("pxa-16-v1")
    assert len(pal) == 16

    with pytest.raises(ValueError):
        get_builtin_palette("unknown-palette")


def test_serialize_deserialize_builtin(tmp_path):
    indices = np.array([[0, 1], [1, 0]], dtype=np.int32)
    img = PixelArtImage(
        width=2, height=2, palette_mode="builtin", palette_id="pxa-16-v1",
        palette=None, transparent_index=None, indices=indices, metadata={"test": True}
    )

    filepath = tmp_path / "test.pixelart"
    save_pixelart(img, str(filepath))

    loaded = load_pixelart(str(filepath))
    assert loaded.width == 2
    assert loaded.height == 2
    assert loaded.palette_mode == "builtin"
    assert loaded.palette_id == "pxa-16-v1"
    assert np.array_equal(loaded.indices, indices)
    assert loaded.metadata == {"test": True}

def test_serialize_deserialize_embedded(tmp_path):
    indices = np.array([[0, 1], [1, 0]], dtype=np.int32)
    palette = ["#000000", "#FFFFFF"]
    img = PixelArtImage(
        width=2, height=2, palette_mode="embedded", palette_id=None,
        palette=palette, transparent_index=None, indices=indices
    )

    filepath = tmp_path / "test2.pixelart"
    save_pixelart(img, str(filepath))

    loaded = load_pixelart(str(filepath))
    assert loaded.palette_mode == "embedded"
    assert loaded.palette == palette
    assert np.array_equal(loaded.indices, indices)

def test_png_roundtrip(tmp_path):
    # Create a simple 2x2 PNG
    png_path = tmp_path / "input.png"
    img_data = np.array([
        [[255, 0, 0, 255], [0, 255, 0, 255]],
        [[0, 0, 255, 255], [0, 0, 0, 0]]
    ], dtype=np.uint8)
    Image.fromarray(img_data, "RGBA").save(png_path)

    # Import
    px_img = import_from_png(str(png_path))
    assert px_img.width == 2
    assert px_img.height == 2
    assert px_img.palette_mode == "embedded"
    assert len(px_img.palette) == 4
    assert px_img.transparent_index is not None

    # Export
    out_png_path = tmp_path / "output.png"
    export_to_png(px_img, str(out_png_path), scale=2)

    out_img = Image.open(out_png_path)
    assert out_img.size == (4, 4)  # scaled by 2
