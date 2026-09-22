"""
op_histogram.py
Menu [1] Tampilkan Histogram Citra Asli Saja.
Tidak melakukan transformasi apa pun; hanya menampilkan citra asli
berdampingan dengan histogramnya sendiri (sebagai referensi/pembanding).
"""

from NewEra.utils import display_comparison


def run(original_img):
    display_comparison(original_img, original_img, "Citra Asli (No Change)")
