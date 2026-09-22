"""
op_contrast.py
Menu [3] Tingkatkan / Ubah Kontras.
Mengubah kontras dengan meregangkan/menekan nilai piksel di sekitar
titik pivot (default 128), dikalikan faktor kontras yang diberikan user.
"""

import numpy as np
from NewEra.utils import display_comparison, prompt_float


def adjust_contrast(img_array, factor, pivot=128):
    img_float = factor * (img_array.astype(np.float32) - pivot) + pivot
    return np.clip(img_float, 0, 255).astype(np.uint8)


def run(original_img):
    factor = prompt_float(
        "Masukkan faktor kontras (misal 1.5 untuk meningkatkan, 0.5 untuk menurunkan): "
    )
    result = adjust_contrast(original_img, factor)
    display_comparison(original_img, result, f"Kontras (x{factor})")
