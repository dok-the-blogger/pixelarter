import pytest
import torch

from pixelarter.models.baseline import BaselineCNN


def test_baseline_cnn_rgb_forward():
    model = BaselineCNN(in_channels=3, base_channels=16, out_channels=3, head_type='rgb')
    x = torch.randn(2, 3, 32, 32)
    out = model(x)

    assert out.shape == (2, 3, 32, 32)
    # Since head_type is rgb, outputs should be mapped to [0, 1] through sigmoid
    assert out.min() >= 0.0
    assert out.max() <= 1.0

def test_baseline_cnn_palette_classification_forward():
    model = BaselineCNN(in_channels=3, base_channels=16, out_channels=16, head_type='palette_classification')
    x = torch.randn(2, 3, 32, 32)
    out = model(x)

    # Check shape
    assert out.shape == (2, 16, 32, 32)

def test_baseline_cnn_invalid_head():
    with pytest.raises(ValueError):
        BaselineCNN(in_channels=3, base_channels=16, out_channels=3, head_type='unknown_head')
