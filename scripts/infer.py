import argparse
import os
import sys

import torch

from pixelarter.config import load_config
from pixelarter.inference.pipeline import run_tiled_inference
from pixelarter.models.baseline import BaselineCNN


def main():
    parser = argparse.ArgumentParser(description="Run pixelarter inference on a single image.")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML configuration file.")
    parser.add_argument("--input", type=str, required=True, help="Path to input degraded image.")
    parser.add_argument("--output", type=str, required=True, help="Path to output restored image.")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to model checkpoint.")

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config file not found at {args.config}")
        sys.exit(1)

    config = load_config(args.config)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading checkpoint {args.checkpoint} on {device}")

    model = BaselineCNN(
        in_channels=config.model.in_channels,
        out_channels=config.model.out_channels,
        head_type=config.model.head_type
    )

    checkpoint = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)

    run_tiled_inference(
        model=model,
        input_image_path=args.input,
        output_image_path=args.output,
        input_size=config.dataset.input_size,
        target_size=config.dataset.target_size,
        device=device
    )

if __name__ == "__main__":
    main()
