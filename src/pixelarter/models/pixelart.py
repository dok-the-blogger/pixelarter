import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class PixelArtImage:
    width: int
    height: int
    palette_mode: str  # 'builtin' or 'embedded'
    palette_id: Optional[str]
    palette: Optional[List[str]]  # List of hex colors (e.g., '#FF0000')
    transparent_index: Optional[int]
    indices: np.ndarray  # 2D array of logical palette indices
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        # Validate indices shape
        if self.indices.shape != (self.height, self.width):
            raise ValueError(
                f"Indices shape {self.indices.shape} does not match "
                f"height x width ({self.height} x {self.width})."
            )

        # Validate palette mode
        if self.palette_mode not in ["builtin", "embedded"]:
            raise ValueError(f"Unknown palette_mode: '{self.palette_mode}'. Must be 'builtin' or 'embedded'.")

        # Validate builtin palette mode
        if self.palette_mode == "builtin":
            if not self.palette_id:
                raise ValueError("palette_id must be provided when palette_mode is 'builtin'.")

        # Validate embedded palette mode
        if self.palette_mode == "embedded":
            if not self.palette:
                raise ValueError("palette must be provided when palette_mode is 'embedded'.")

        # Validate indices values (if palette is available)
        # Note: We can only validate this for 'embedded' right now unless we check the registry for 'builtin'.
        # Assuming the caller has properly validated 'builtin' palette sizes.
        if self.palette_mode == "embedded" and self.palette:
            max_index = len(self.palette) - 1
            if self.indices.max() > max_index:
                raise ValueError(
                    f"Indices contain value {self.indices.max()} which exceeds "
                    f"the embedded palette size ({len(self.palette)} colors, max index {max_index})."
                )

        # Validate transparent_index
        if self.transparent_index is not None:
            # We don't strictly require it to be within the current palette size (it might just be empty)
            # but usually it should be. We'll add a warning or a simple check if possible.
            if self.palette_mode == "embedded" and self.palette:
                if self.transparent_index < 0 or self.transparent_index >= len(self.palette):
                    raise ValueError(
                        f"transparent_index {self.transparent_index} is out of bounds for "
                        f"embedded palette size {len(self.palette)}."
                    )
