"""
op_color_convert.py
Menu [5] Konversi Ruang Warna (RGB <-> Grayscale).
- RGB -> Grayscale: menggunakan bobot luminance standar (0.299R + 0.587G + 0.114B).
- Grayscale -> RGB: menduplikasi kanal tunggal menjadi 3 kanal identik.
"""

import numpy as np
from NewEra.utils import display_comparison


def convert_color(img_array):
    if img_array.ndim == 3:
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
        return np.clip(gray, 0, 255).astype(np.uint8)
    else:
        return np.stack([img_array] * 3, axis=-1)


def run(original_img):
    result = convert_color(original_img)
    target = "Grayscale" if original_img.ndim == 3 else "RGB"
    display_comparison(original_img, result, f"Konversi ke {target}")
