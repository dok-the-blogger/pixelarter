import torch
import torchvision.transforms.functional as F
from PIL import Image


def run_tiled_inference(model, input_image_path: str, output_image_path: str, input_size: int = 32, target_size: int = 16, device='cpu'):
    """
    Runs simple non-overlapping tiled inference over the input image.
    Extracts input_size x input_size context, predicts, and writes target_size x target_size central region.
    """
    model.eval()

    img = Image.open(input_image_path).convert("RGB")
    w, h = img.size

    # Prepare an output canvas
    out_canvas = torch.zeros(3, h, w)
    img_tensor = F.to_tensor(img).to(device)

    # Calculate padding needed to cover the entire image
    pad_h = (target_size - (h % target_size)) % target_size
    pad_w = (target_size - (w % target_size)) % target_size

    # Add extra padding for the context window (input_size)
    context_pad = (input_size - target_size) // 2

    # Pad image symmetrically to handle edges properly
    padded_img = F.pad(img_tensor, [context_pad, context_pad, context_pad + pad_w, context_pad + pad_h], padding_mode="reflect")

    with torch.no_grad():
        for y in range(0, h, target_size):
            for x in range(0, w, target_size):
                # Extract input_size patch (x, y are top-left of the target patch)
                # The input patch starts context_pad earlier
                px = x
                py = y

                patch = padded_img[:, py:py+input_size, px:px+input_size].unsqueeze(0)

                # Predict
                output = model(patch)

                # Crop to target size
                out_h, out_w = output.shape[-2:]
                h_start = (out_h - target_size) // 2
                w_start = (out_w - target_size) // 2

                cropped_out = output[0, :, h_start:h_start+target_size, w_start:w_start+target_size]

                # Write to canvas (handling edges)
                write_h = min(target_size, h - y)
                write_w = min(target_size, w - x)

                out_canvas[:, y:y+write_h, x:x+write_w] = cropped_out[:, :write_h, :write_w].cpu()

    # Convert back to PIL
    out_img = F.to_pil_image(out_canvas.clamp(0, 1))
    out_img.save(output_image_path)
    print(f"Saved restored image to {output_image_path}")
