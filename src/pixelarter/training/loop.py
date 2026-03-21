import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from ..config import Config
from ..data.dataset import PixelartDataset
from ..models.baseline import BaselineCNN


def train_loop(config: Config):
    device = torch.device(config.training.device if torch.cuda.is_available() else "cpu")

    # Dataset & DataLoader
    dataset = PixelartDataset(config.dataset, config.degradation)
    dataloader = DataLoader(
        dataset,
        batch_size=config.dataloader.batch_size,
        shuffle=config.dataloader.shuffle,
        num_workers=config.dataloader.num_workers
    )

    # Model
    model = BaselineCNN(
        in_channels=config.model.in_channels,
        out_channels=config.model.out_channels,
        head_type=config.model.head_type
    ).to(device)

    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=config.training.lr)

    # Loss
    if config.model.head_type == 'rgb':
        criterion = nn.MSELoss()
    else:
        # CrossEntropy for classification in future palette mode
        criterion = nn.CrossEntropyLoss()

    # Create save dir
    os.makedirs(config.training.save_dir, exist_ok=True)

    print(f"Starting training on {device}...")
    for epoch in range(config.training.epochs):
        model.train()
        total_loss = 0.0

        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{config.training.epochs}")
        for i, (inputs, targets) in enumerate(progress_bar):
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)

            # Crop output to target size for loss calculation
            # By default, BaselineCNN outputs the full input size (e.g. 32x32).
            # We take the center crop (e.g. 16x16) to match the target.
            b, c, h, w = outputs.shape
            th, tw = targets.shape[-2:]

            h_start = (h - th) // 2
            w_start = (w - tw) // 2

            cropped_outputs = outputs[:, :, h_start:h_start+th, w_start:w_start+tw]

            loss = criterion(cropped_outputs, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if (i + 1) % config.training.log_every_n_steps == 0:
                progress_bar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{config.training.epochs}] Average Loss: {avg_loss:.4f}")

        # Save checkpoint
        ckpt_path = os.path.join(config.training.save_dir, "latest_model.pth")
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
            'config': config
        }, ckpt_path)
    print("Training complete.")
