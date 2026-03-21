import io
import random

import torch
import torchvision.transforms.functional as F
from PIL import Image, ImageFilter


class DegradationPipeline:
    """
    Baseline degradation pipeline to synthesize 'nearly-pixel-art' from clean pixel art.
    """
    def __init__(self, config):
        self.cfg = config
        self.resample_methods = [
            Image.Resampling.NEAREST,
            Image.Resampling.BILINEAR,
            Image.Resampling.BICUBIC
        ]

    def apply(self, img: Image.Image) -> Image.Image:
        """
        Applies synthetic degradations to a clean PIL image.
        """
        if not self.cfg.enabled:
            return img

        # 1. Scaling degradation (simulate upscaled pixel art with artifacts)
        scale = random.uniform(self.cfg.scale_range[0], self.cfg.scale_range[1])
        w, h = img.size
        new_w, new_h = max(1, int(w / scale)), max(1, int(h / scale))

        # Downscale
        down_method = random.choice(self.resample_methods)
        img_down = img.resize((new_w, new_h), resample=down_method)

        # Upscale back to original size (adds scaling artifacts)
        up_method = random.choice([Image.Resampling.BILINEAR, Image.Resampling.BICUBIC])
        img = img_down.resize((w, h), resample=up_method)

        # 2. Blur (anti-aliasing-like effect)
        if random.random() < self.cfg.blur_prob:
            radius = random.uniform(0.1, 1.0)
            img = img.filter(ImageFilter.GaussianBlur(radius))

        # 3. Subpixel shift
        if random.random() < self.cfg.shift_prob:
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            img = img.transform((w, h), Image.Transform.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.Resampling.BILINEAR)

        # 4. Color jitter / palette drift
        if self.cfg.color_jitter_strength > 0:
            # simple brightness/contrast/hue adjustments
            b = random.uniform(max(0, 1 - self.cfg.color_jitter_strength), 1 + self.cfg.color_jitter_strength)
            c = random.uniform(max(0, 1 - self.cfg.color_jitter_strength), 1 + self.cfg.color_jitter_strength)
            h_f = random.uniform(-self.cfg.color_jitter_strength, self.cfg.color_jitter_strength)

            t_img = F.to_tensor(img)
            t_img = F.adjust_brightness(t_img, b)
            t_img = F.adjust_contrast(t_img, c)
            t_img = F.adjust_hue(t_img, h_f)
            img = F.to_pil_image(t_img)

        # 5. JPEG-like artifact
        if random.random() < self.cfg.jpeg_prob:
            quality = random.randint(60, 95)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            img = Image.open(buffer).convert("RGB")

        # 6. Noise
        noise_var = random.uniform(self.cfg.noise_var_range[0], self.cfg.noise_var_range[1])
        if noise_var > 0:
            t_img = F.to_tensor(img)
            noise = torch.randn_like(t_img) * (noise_var ** 0.5)
            t_img = torch.clamp(t_img + noise, 0.0, 1.0)
            img = F.to_pil_image(t_img)

        return img
