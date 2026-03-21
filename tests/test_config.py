import yaml

from pixelarter.config import load_config


def test_config_load(tmp_path):
    config_data = {
        "dataset": {
            "data_dir": "test_dir",
            "input_size": 32,
            "target_size": 16,
            "epoch_length": 100
        },
        "dataloader": {
            "batch_size": 16,
            "num_workers": 2,
            "shuffle": True
        },
        "model": {
            "name": "baseline_unet",
            "in_channels": 3,
            "out_channels": 3,
            "head_type": "rgb"
        },
        "training": {
            "epochs": 10,
            "lr": 0.001,
            "device": "cpu",
            "save_dir": "runs/test",
            "log_every_n_steps": 10
        },
        "degradation": {
            "enabled": True,
            "scale_range": [1.0, 2.0]
        }
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    config = load_config(str(config_file))

    assert config.dataset.input_size == 32
    assert config.model.head_type == "rgb"
    assert config.degradation.scale_range == (1.0, 2.0)
