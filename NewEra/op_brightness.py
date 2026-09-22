"""
op_brightness.py
Menu [2] Modifikasi Brightness.
Menambah/mengurangi kecerahan citra dengan menggeser nilai setiap piksel
sebesar konstanta tertentu, lalu clip ke rentang valid [0, 255].
"""

import numpy as np
from NewEra.utils import display_comparison, prompt_int


def adjust_brightness(img_array, value):
    img_int = img_array.astype(np.int16) + value
    return np.clip(img_int, 0, 255).astype(np.uint8)


def run(original_img):
    val = prompt_int("Masukkan nilai pergeseran brightness (-255 s.d. 255): ",
            min_val=-255, max_val=255)
    result = adjust_brightness(original_img, val)
    display_comparison(original_img, result, f"Brightness ({val:+d})")
