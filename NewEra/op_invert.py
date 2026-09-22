"""
op_invert.py
Menu [4] Negasi / Inversi Citra.
Membalik nilai setiap piksel: hasil = 255 - nilai_asli.
"""

from NewEra.utils import display_comparison


def invert_image(img_array):
    return (255 - img_array).astype("uint8")


def run(original_img):
    result = invert_image(original_img)
    display_comparison(original_img, result, "Negasi (Inversi)")
