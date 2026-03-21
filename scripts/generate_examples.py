import numpy as np
from PIL import Image
import os
import json

from pixelarter.models.pixelart import PixelArtImage
from pixelarter.formats.pixelart import save_pixelart
from pixelarter.formats.png import export_to_png

def generate_examples():
    os.makedirs("examples", exist_ok=True)

    # 1. Very small .pixelart with builtin palette
    indices_builtin = np.array([
        [0, 1, 0],
        [1, 2, 1],
        [0, 1, 0]
    ], dtype=np.int32)

    img_builtin = PixelArtImage(
        width=3, height=3, palette_mode="builtin", palette_id="pxa-16-v1",
        palette=None, transparent_index=None, indices=indices_builtin,
        metadata={"description": "Small builtin example"}
    )
    save_pixelart(img_builtin, "examples/small_builtin.pixelart")

    # 2. Very small .pixelart with embedded palette
    indices_embedded = np.array([
        [0, 0, 1, 1],
        [0, 1, 2, 1],
        [1, 2, 2, 1],
        [1, 1, 1, 1]
    ], dtype=np.int32)

    img_embedded = PixelArtImage(
        width=4, height=4, palette_mode="embedded", palette_id=None,
        palette=["#000000", "#ff0000", "#ffffff"], transparent_index=0, indices=indices_embedded,
        metadata={"description": "Small embedded example"}
    )
    save_pixelart(img_embedded, "examples/small_embedded.pixelart")

    # 3. Small PNG for roundtrip/demo
    # We export the embedded one to a scale=4 PNG
    export_to_png(img_embedded, "examples/small_demo.png", scale=4)
    print("Generated examples in examples/")

if __name__ == "__main__":
    generate_examples()
