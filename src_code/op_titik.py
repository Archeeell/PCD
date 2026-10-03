"""Operasi Titik (GST): brightness, contrast, negation, grayscale, dan thresholding."""
import numpy as np
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import display_comparison, prompt_int, prompt_float, run_standalone
else:
    from .utils import display_comparison, prompt_int, prompt_float, run_standalone

def adjust_brightness(img_array, value):
    """Modifikasi kecemerlangan: Ko = Ki + c, dibatasi pada rentang 0-255."""
    return np.clip(img_array.astype(np.int16) + value, 0, 255).astype(np.uint8)

def adjust_contrast(img_array, factor, pivot=128):
    """Peningkatan kontras linear: Ko = factor * (Ki - pivot) + pivot."""
    values = factor * (img_array.astype(np.float32) - pivot) + pivot
    return np.clip(values, 0, 255).astype(np.uint8)

def negate(img_array):
    """Negasi: Ko = 255 - Ki."""
    return (255 - img_array).astype(np.uint8)

def convert_color(img_array):
    """RGB -> grayscale dengan bobot luminance; grayscale -> RGB dengan duplikasi kanal."""
    if img_array.ndim == 3:
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
        return np.clip(gray, 0, 255).astype(np.uint8)
    return np.stack([img_array] * 3, axis=-1)

def apply_threshold(img_array, threshold_val):
    """Pengambangan biner; citra RGB dikonversi ke grayscale dahulu."""
    gray = convert_color(img_array) if img_array.ndim == 3 else img_array
    return np.where(gray >= threshold_val, 255, 0).astype(np.uint8)

def _choose_and_show(original_img, choice):
    if choice == 1:
        value = prompt_int("Masukkan nilai pergeseran brightness (-255 s.d. 255): ", -255, 255)
        result, label = adjust_brightness(original_img, value), f"Brightness ({value:+d})"
    elif choice == 2:
        factor = prompt_float("Masukkan faktor kontras (misal 1.5 untuk meningkatkan): ")
        result, label = adjust_contrast(original_img, factor), f"Kontras (x{factor})"
    elif choice == 3:
        result, label = negate(original_img), "Negasi (Inversi)"
    elif choice == 4:
        result = convert_color(original_img)
        label = "Konversi ke Grayscale" if original_img.ndim == 3 else "Konversi ke RGB"
    else:
        threshold = prompt_int("Masukkan nilai ambang batas threshold (0-255): ", 0, 255)
        result, label = apply_threshold(original_img, threshold), f"Thresholding (T={threshold})"
    display_comparison(original_img, result, label)

def run(original_img):
    print("\n--- OPERASI TITIK ---")
    print("[1] Modifikasi Kecemerlangan (Brightness)")
    print("[2] Peningkatan Kontras (Contrast)")
    print("[3] Negasi (Negation)")
    print("[4] Konversi Grayscale / RGB")
    print("[5] Pengambangan (Thresholding)")
    _choose_and_show(original_img, prompt_int("Pilih sub-operasi titik: ", 1, 5))


if __name__ == "__main__":
    run_standalone(run)
