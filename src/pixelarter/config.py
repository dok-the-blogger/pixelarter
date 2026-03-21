from dataclasses import dataclass, field

import yaml


@dataclass
class DatasetConfig:
    data_dir: str
    input_size: int = 32
    target_size: int = 16
    epoch_length: int = 1000

@dataclass
class DataLoaderConfig:
    batch_size: int = 32
    num_workers: int = 4
    shuffle: bool = True

@dataclass
class ModelConfig:
    name: str = "baseline_unet"
    in_channels: int = 3
    out_channels: int = 3
    head_type: str = "rgb"

@dataclass
class TrainingConfig:
    epochs: int = 100
    lr: float = 1e-4
    device: str = "cuda"
    save_dir: str = "runs/baseline"
    log_every_n_steps: int = 50

@dataclass
class DegradationConfig:
    enabled: bool = True
    scale_range: tuple[float, float] = (1.0, 4.0)
    noise_var_range: tuple[float, float] = (0.0, 0.005)
    color_jitter_strength: float = 0.05
    blur_prob: float = 0.3
    jpeg_prob: float = 0.2
    shift_prob: float = 0.5

@dataclass
class Config:
    dataset: DatasetConfig
    dataloader: DataLoaderConfig
    model: ModelConfig
    training: TrainingConfig
    degradation: DegradationConfig = field(default_factory=DegradationConfig)

def load_config(path: str) -> Config:
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Simple manual mapping to dataclasses
    dataset_cfg = DatasetConfig(**data.get('dataset', {}))
    dataloader_cfg = DataLoaderConfig(**data.get('dataloader', {}))
    model_cfg = ModelConfig(**data.get('model', {}))
    training_cfg = TrainingConfig(**data.get('training', {}))

    deg_data = data.get('degradation', {})
    if 'scale_range' in deg_data and isinstance(deg_data['scale_range'], list):
        deg_data['scale_range'] = tuple(deg_data['scale_range'])
    if 'noise_var_range' in deg_data and isinstance(deg_data['noise_var_range'], list):
        deg_data['noise_var_range'] = tuple(deg_data['noise_var_range'])

    degradation_cfg = DegradationConfig(**deg_data)

    return Config(
        dataset=dataset_cfg,
        dataloader=dataloader_cfg,
        model=model_cfg,
        training=training_cfg,
        degradation=degradation_cfg
    )
