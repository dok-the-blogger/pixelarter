import random
from pathlib import Path

import torchvision.transforms.functional as F
from PIL import Image
from torch.utils.data import Dataset

from .degradations import DegradationPipeline


class PixelartDataset(Dataset):
    """
    Dataset for patch-based local restoration training.
    Assumes images in data_dir are clean, high-quality pixel art.
    """
    def __init__(self, config, degradation_config):
        self.cfg = config
        self.data_dir = Path(self.cfg.data_dir)
        self.input_size = self.cfg.input_size
        self.target_size = self.cfg.target_size
        self.epoch_length = self.cfg.epoch_length
        self.pipeline = DegradationPipeline(degradation_config)

        # Load all valid image paths
        self.image_paths = []
        if self.data_dir.exists():
            for ext in ['.png', '.jpg', '.jpeg']:
                self.image_paths.extend(list(self.data_dir.rglob(f"*{ext}")))

        # Avoid crashing if empty, but issue warning
        if len(self.image_paths) == 0:
            print(f"Warning: No images found in {self.data_dir}")

    def __len__(self):
        return self.epoch_length

    def __getitem__(self, idx):
        if not self.image_paths:
            # Fallback for empty dataset (e.g., during tests)
            img = Image.new("RGB", (64, 64), color="black")
        else:
            path = random.choice(self.image_paths)
            img = Image.open(path).convert("RGB")

        w, h = img.size
        # Ensure image is large enough for the patch
        if w < self.input_size or h < self.input_size:
            img = img.resize((max(w, self.input_size), max(h, self.input_size)), Image.Resampling.NEAREST)
            w, h = img.size

        # Random crop for the clean target
        top = random.randint(0, h - self.input_size)
        left = random.randint(0, w - self.input_size)

        clean_patch = F.crop(img, top, left, self.input_size, self.input_size)

        # Apply synthetic degradation to the same patch to create the input
        degraded_patch = self.pipeline.apply(clean_patch.copy())

        # Convert to tensors
        input_tensor = F.to_tensor(degraded_patch)
        target_tensor = F.to_tensor(clean_patch)

        # For baseline: output the full patch and calculate loss on the center region.
        # Alternatively, physically crop the target tensor to target_size:
        # F.center_crop(target_tensor, [self.target_size, self.target_size])

        center_crop = F.center_crop(target_tensor, [self.target_size, self.target_size])

        return input_tensor, center_crop
