import argparse
import os
import sys

from pixelarter.config import load_config
from pixelarter.training.loop import train_loop


def main():
    parser = argparse.ArgumentParser(description="Run pixelarter baseline training.")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML configuration file.")

    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"Error: Config file not found at {args.config}")
        sys.exit(1)

    config = load_config(args.config)
    print(f"Loaded config: {config}")

    train_loop(config)

if __name__ == "__main__":
    main()
