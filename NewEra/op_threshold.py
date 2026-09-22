"""
op_threshold.py
Menu [6] Thresholding (Pengambangan).
Mengubah citra menjadi biner (0 atau 255) berdasarkan nilai ambang batas.
Citra RGB akan dikonversi ke grayscale terlebih dahulu sebelum diambang.
"""

import numpy as np
from NewEra.op_color_convert import convert_color
from NewEra.utils import display_comparison, prompt_int


def apply_threshold(img_array, threshold_val):
    if img_array.ndim == 3:
        gray = convert_color(img_array)
    else:
        gray = img_array
    return np.where(gray >= threshold_val, 255, 0).astype(np.uint8)


def run(original_img):
    thresh = prompt_int("Masukkan nilai ambang batas threshold (0-255): ",
                         min_val=0, max_val=255)
    result = apply_threshold(original_img, thresh)
    display_comparison(original_img, result, f"Thresholding (T={thresh})")
