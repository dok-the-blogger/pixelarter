from PIL import Image

from pixelarter.config import DatasetConfig, DegradationConfig
from pixelarter.data.dataset import PixelartDataset
from pixelarter.data.degradations import DegradationPipeline


def test_degradation_pipeline():
    cfg = DegradationConfig(
        enabled=True,
        scale_range=(1.5, 2.5),
        blur_prob=1.0, # force blur
        jpeg_prob=1.0, # force jpeg
        shift_prob=1.0, # force shift
        noise_var_range=(0.01, 0.02)
    )

    pipeline = DegradationPipeline(cfg)

    img = Image.new("RGB", (64, 64), color="blue")
    degraded = pipeline.apply(img)

    assert degraded.size == (64, 64)
    assert degraded.mode == "RGB"

def test_dataset(tmp_path):
    img_dir = tmp_path / "data"
    img_dir.mkdir()

    # Create a mock image
    img = Image.new("RGB", (128, 128), color="red")
    img.save(img_dir / "test.png")

    config = type('obj', (object,), {
        'dataset': DatasetConfig(
            data_dir=str(img_dir),
            input_size=32,
            target_size=16,
            epoch_length=5
        ),
        'degradation': DegradationConfig(enabled=False)
    })

    dataset = PixelartDataset(config.dataset, config.degradation)

    assert len(dataset) == 5

    input_patch, target_patch = dataset[0]

    assert input_patch.shape == (3, 32, 32)
    assert target_patch.shape == (3, 16, 16)
