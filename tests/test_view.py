import numpy as np
import pytest

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.view.render import get_sidecar_path, render_preview


@pytest.fixture
def sample_pixelart():
    # Create a 2x2 image
    # Palette: Red, Green
    indices = np.array([
        [0, 1],
        [1, 0]
    ], dtype=np.int32)
    return PixelArtImage(
        width=2,
        height=2,
        palette_mode="embedded",
        palette_id=None,
        palette=["#FF0000", "#00FF00"],
        transparent_index=None,
        indices=indices
    )

@pytest.fixture
def sample_pixelart_transparent():
    # 2x2, index 0 is red, index 1 is transparent
    indices = np.array([
        [0, 1],
        [1, 0]
    ], dtype=np.int32)
    return PixelArtImage(
        width=2,
        height=2,
        palette_mode="embedded",
        palette_id=None,
        palette=["#FF0000", "#000000"], # the hex for transparent doesn't matter much as it gets zeroed
        transparent_index=1,
        indices=indices
    )


def test_render_preview_basic(sample_pixelart):
    img = render_preview(sample_pixelart, scale=1, grid=False)
    assert img.size == (2, 2)
    assert img.mode == "RGBA"

    # Check pixels
    data = np.array(img)
    # Top-left (0,0) -> idx 0 (Red)
    assert tuple(data[0, 0]) == (255, 0, 0, 255)
    # Top-right (0,1) -> idx 1 (Green)
    assert tuple(data[0, 1]) == (0, 255, 0, 255)


def test_render_preview_scale(sample_pixelart):
    img = render_preview(sample_pixelart, scale=4, grid=False)
    assert img.size == (8, 8)
    data = np.array(img)
    # The 2x2 block should all be red
    assert tuple(data[0, 0]) == (255, 0, 0, 255)
    assert tuple(data[3, 3]) == (255, 0, 0, 255)
    # Block next to it should be green
    assert tuple(data[0, 4]) == (0, 255, 0, 255)


def test_render_preview_transparency(sample_pixelart_transparent):
    img = render_preview(sample_pixelart_transparent, scale=1, bg_mode="transparent")
    data = np.array(img)
    # Index 0 (Red)
    assert tuple(data[0, 0]) == (255, 0, 0, 255)
    # Index 1 (Transparent)
    assert tuple(data[0, 1]) == (0, 0, 0, 0)


def test_render_preview_bg_solid(sample_pixelart_transparent):
    img = render_preview(sample_pixelart_transparent, scale=1, bg_mode="solid", bg_color="#0000FF")
    data = np.array(img)
    # Index 0 (Red) composite over Blue -> Red
    assert tuple(data[0, 0]) == (255, 0, 0, 255)
    # Index 1 (Transparent) composite over Blue -> Blue
    assert tuple(data[0, 1]) == (0, 0, 255, 255)


def test_get_sidecar_path():
    assert get_sidecar_path("image.pixelart") == "image.preview.png"
    assert get_sidecar_path("foo/bar/image.pixelart") == "foo/bar/image.preview.png"
    assert get_sidecar_path("image.png") == "image.png.preview.png" # Falls back safely
