import torch
import torch.nn as nn


class BaselineCNN(nn.Module):
    """
    A simple baseline CNN encoder-decoder with an extensible output head.
    This model receives an input patch (e.g. 32x32) and predicts an output patch.
    """
    def __init__(self, in_channels=3, base_channels=32, out_channels=3, head_type='rgb'):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, base_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_channels, base_channels * 2, kernel_size=3, padding=1, stride=2),
            nn.ReLU(inplace=True),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(base_channels * 2, base_channels, kernel_size=4, padding=1, stride=2),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_channels, base_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

        # Output head based on `head_type`
        if head_type == 'rgb':
            self.head = nn.Conv2d(base_channels, out_channels, kernel_size=3, padding=1)
        elif head_type == 'palette_classification':
            # E.g., for predicting palette indices.
            # out_channels would be the number of classes (palette size).
            self.head = nn.Conv2d(base_channels, out_channels, kernel_size=3, padding=1)
        else:
            raise ValueError(f"Unknown head_type: {head_type}")

        self.head_type = head_type

    def forward(self, x):
        features = self.encoder(x)
        decoded = self.decoder(features)
        out = self.head(decoded)

        # For rgb, we typically constrain to [0, 1] using Sigmoid or similar.
        if self.head_type == 'rgb':
            out = torch.sigmoid(out)

        return out
