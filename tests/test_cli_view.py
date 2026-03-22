import argparse
from unittest.mock import patch

import numpy as np
import pytest

from pixelarter.cli import cmd_preview, cmd_preview_sidecar, cmd_view
from pixelarter.formats.pixelart import save_pixelart
from pixelarter.models.pixelart import PixelArtImage


@pytest.fixture
def mock_pixelart_file(tmp_path):
    filepath = tmp_path / "test.pixelart"

    indices = np.array([[0]], dtype=np.int32)
    img = PixelArtImage(
        width=1,
        height=1,
        palette_mode="embedded",
        palette_id=None,
        palette=["#FF0000"],
        transparent_index=None,
        indices=indices
    )

    save_pixelart(img, str(filepath))
    return str(filepath)


@patch("pixelarter.cli.load_pixelart")
@patch("pixelarter.cli.render_preview")
def test_cmd_view(mock_render_preview, mock_load_pixelart, mock_pixelart_file):
    args = argparse.Namespace(
        input=mock_pixelart_file,
        scale=8,
        grid=False,
        bg_mode="transparent",
        bg_color=None
    )

    cmd_view(args)

    mock_load_pixelart.assert_called_once_with(mock_pixelart_file)
    mock_render_preview.assert_called_once()
    mock_render_preview.return_value.show.assert_called_once()


@patch("pixelarter.cli.load_pixelart")
@patch("pixelarter.cli.render_preview")
def test_cmd_preview(mock_render_preview, mock_load_pixelart, mock_pixelart_file, tmp_path):
    output_png = str(tmp_path / "out.png")
    args = argparse.Namespace(
        input=mock_pixelart_file,
        output=output_png,
        scale=4,
        grid=True,
        bg_mode="solid",
        bg_color="#FFFFFF"
    )

    cmd_preview(args)

    mock_load_pixelart.assert_called_once_with(mock_pixelart_file)
    mock_render_preview.assert_called_once()
    mock_render_preview.return_value.save.assert_called_once_with(output_png, format="PNG")


@patch("pixelarter.cli.load_pixelart")
@patch("pixelarter.cli.render_preview")
def test_cmd_preview_sidecar(mock_render_preview, mock_load_pixelart, mock_pixelart_file):
    args = argparse.Namespace(
        input=mock_pixelart_file,
        scale=8,
        grid=False,
        bg_mode="transparent",
        bg_color=None
    )

    cmd_preview_sidecar(args)

    expected_sidecar = mock_pixelart_file.replace(".pixelart", ".preview.png")

    mock_load_pixelart.assert_called_once_with(mock_pixelart_file)
    mock_render_preview.assert_called_once()
    mock_render_preview.return_value.save.assert_called_once_with(expected_sidecar, format="PNG")
