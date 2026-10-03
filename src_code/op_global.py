"""Operasi Global: histogram citra dan ekualisasi histogram."""
import numpy as np
from NewEra.utils import display_comparison, prompt_int

def _equalize_channel(channel, max_level=255):
    """Ko = floor(Ci * (2^k - 1) / (w*h)); Ci adalah histogram kumulatif."""
    h, w = channel.shape
    hist, _ = np.histogram(channel, bins=max_level + 1, range=(0, max_level + 1))
    cumulative = np.cumsum(hist)
    lut = np.floor(cumulative * max_level / (w * h) + 1e-9).astype(np.uint8)
    return lut[channel]

def histogram_equalization(img_array, max_level=255):
    """Ekualisasi histogram; citra RGB diproses per kanal seperti implementasi semula."""
    if img_array.ndim == 2:
        return _equalize_channel(img_array, max_level)
    return np.stack([_equalize_channel(img_array[..., c], max_level)
                     for c in range(img_array.shape[2])], axis=-1)

def show_histogram(img_array):
    """Menampilkan citra dan histogram aslinya memakai visualisasi bersama."""
    display_comparison(img_array, img_array, "Histogram Citra Asli")

def run(original_img):
    print("\n--- OPERASI GLOBAL ---")
    print("[1] Tampilkan Histogram Citra")
    print("[2] Ekualisasi Histogram (Histogram Equalization)")
    choice = prompt_int("Pilih sub-operasi global: ", 1, 2)
    if choice == 1:
        show_histogram(original_img)
    elif choice == 2:
        result = histogram_equalization(original_img)
        display_comparison(original_img, result, "Ekualisasi Histogram")
    else:
        print("Pilihan tidak valid.")
