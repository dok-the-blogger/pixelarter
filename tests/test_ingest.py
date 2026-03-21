import os
import json
import pytest
import numpy as np
from PIL import Image

from pixelarter.ingest.models import Verdict
from pixelarter.ingest.pipeline import inspect_image, process_ingest

def create_test_image(filepath, mode="clean_pixelart"):
    if mode == "clean_pixelart":
        # 16x16 clean pixel art with discrete regions, no scale
        data = np.zeros((16, 16, 4), dtype=np.uint8)
        data[:, :, 3] = 255
        # Large enough solid block to pass discreteness heuristic
        data[0:8, 0:8, 0] = 255
        data[8:16, 8:16, 2] = 255
        # Add some single pixels to break any scale > 1
        data[2, 10, 1] = 255
        data[10, 2, 1] = 255
    elif mode == "upscaled_pixelart":
        # 2x upscale of 2x2
        # So a 4x4 image
        data = np.zeros((4, 4, 4), dtype=np.uint8)
        data[:, :, 3] = 255
        data[0:2, 0:2] = [255, 0, 0, 255]
        data[0:2, 2:4] = [0, 255, 0, 255]
        data[2:4, 0:2] = [0, 0, 255, 255]
        data[2:4, 2:4] = [255, 255, 0, 255]
    elif mode == "transparent_border":
        # 6x6 with 4x4 center
        data = np.zeros((6, 6, 4), dtype=np.uint8)
        data[1:5, 1:5, :] = [255, 0, 0, 255]
    elif mode == "noisy_rejected":
        # Random noise, 10x10 (should have 100 unique colors)
        np.random.seed(42)
        data = np.random.randint(0, 256, (10, 10, 4), dtype=np.uint8)
        data[:, :, 3] = 255 # solid alpha
    else:
        raise ValueError("Unknown mode")

    img = Image.fromarray(data, "RGBA")
    img.save(filepath)
    return data

def test_inspect_clean_pixelart(tmpdir):
    p = os.path.join(tmpdir, "clean.png")
    data = create_test_image(p, "clean_pixelart")

    res = inspect_image(data)
    assert res.verdict == Verdict.ACCEPTED
    assert res.score == 100
    assert len(res.suggested_normalizations) == 0

def test_inspect_upscaled_pixelart(tmpdir):
    p = os.path.join(tmpdir, "upscaled.png")
    data = create_test_image(p, "upscaled_pixelart")

    res = inspect_image(data)
    assert res.verdict == Verdict.ACCEPTED_WITH_NORMALIZATION
    assert res.suspected_integer_scale == 2
    assert "collapse_integer_upscale" in res.suggested_normalizations

def test_inspect_transparent_border(tmpdir):
    p = os.path.join(tmpdir, "border.png")
    data = create_test_image(p, "transparent_border")

    res = inspect_image(data)
    assert res.verdict == Verdict.ACCEPTED_WITH_NORMALIZATION
    assert "crop_transparent_border" in res.suggested_normalizations

def test_inspect_noisy_rejected(tmpdir):
    p = os.path.join(tmpdir, "noisy.png")
    data = create_test_image(p, "noisy_rejected")

    res = inspect_image(data)
    assert res.verdict == Verdict.REJECTED
    assert res.score < 60
    assert res.unique_colors > 50

def test_ingest_upscaled(tmpdir):
    p = os.path.join(tmpdir, "upscaled.png")
    create_test_image(p, "upscaled_pixelart")

    pixelart, res = process_ingest(p)

    assert pixelart is not None
    assert res.verdict == Verdict.ACCEPTED_WITH_NORMALIZATION
    assert "collapse_integer_upscale" in res.applied_normalizations

    # Original was 4x4, scale is 2, so logical is 2x2
    assert pixelart.width == 2
    assert pixelart.height == 2

def test_ingest_rejects_noisy(tmpdir):
    p = os.path.join(tmpdir, "noisy.png")
    create_test_image(p, "noisy_rejected")

    pixelart, res = process_ingest(p)

    assert pixelart is None
    assert res.verdict == Verdict.REJECTED

def test_ingest_force_noisy(tmpdir):
    p = os.path.join(tmpdir, "noisy.png")
    create_test_image(p, "noisy_rejected")

    pixelart, res = process_ingest(p, force=True)

    assert pixelart is not None
    assert res.verdict == Verdict.REJECTED
