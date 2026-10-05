"""Operasi Titik (GST): brightness, contrast, negation, grayscale, dan thresholding."""
import math
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, klem,
                                display_comparison, prompt_int, prompt_float, run_standalone)
else:
    from .utils import (Citra, buat_kosong, klem,
                        display_comparison, prompt_int, prompt_float, run_standalone)


def adjust_brightness(citra, value):
    """
    Modifikasi kecemerlangan: Ko = Ki + c, dibatasi pada rentang 0-255.
    value adalah bilangan bulat positif (cerah) atau negatif (gelap).
    """
    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(citra.tinggi):
            src_row = k_src[y]
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                dst_row[x] = klem(src_row[x] + value)
    return hasil


def adjust_contrast(citra, factor, pivot=128):
    """
    Peningkatan kontras linear: Ko = factor * (Ki - pivot) + pivot.
    Hasil diklem ke 0-255 lalu dipotong ke integer (sesuai astype(uint8)).
    """
    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(citra.tinggi):
            src_row = k_src[y]
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                # float32-like: astype(uint8) = truncation, bukan round
                val = factor * (src_row[x] - pivot) + pivot
                # klem ke 0..255 (float), lalu potong ke int (truncation ke bawah)
                if val < 0.0:
                    val = 0.0
                elif val > 255.0:
                    val = 255.0
                dst_row[x] = int(val)
    return hasil


def negate(citra):
    """Negasi: Ko = 255 - Ki."""
    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(citra.tinggi):
            src_row = k_src[y]
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                dst_row[x] = 255 - src_row[x]
    return hasil


def convert_color(citra):
    """
    RGB -> grayscale dengan bobot luminance 0.299R + 0.587G + 0.114B,
    diklem ke 0-255 lalu dipotong ke int (truncation, sesuai astype uint8).
    Grayscale -> RGB dengan duplikasi kanal.
    """
    if citra.mode == "RGB":
        # RGB ke Grayscale
        hasil = buat_kosong(citra.lebar, citra.tinggi, "L")
        k_dst = hasil.kanal[0]
        r_k, g_k, b_k = citra.kanal[0], citra.kanal[1], citra.kanal[2]
        for y in range(citra.tinggi):
            r_row, g_row, b_row = r_k[y], g_k[y], b_k[y]
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                val = 0.299 * r_row[x] + 0.587 * g_row[x] + 0.114 * b_row[x]
                if val < 0.0:
                    val = 0.0
                elif val > 255.0:
                    val = 255.0
                dst_row[x] = int(val)   # truncation
        return hasil
    else:
        # Grayscale ke RGB: duplikasi kanal
        hasil = buat_kosong(citra.lebar, citra.tinggi, "RGB")
        k_src = citra.kanal[0]
        for y in range(citra.tinggi):
            src_row = k_src[y]
            for c in range(3):
                dst_row = hasil.kanal[c][y]
                for x in range(citra.lebar):
                    dst_row[x] = src_row[x]
        return hasil


def apply_threshold(citra, threshold_val):
    """
    Pengambangan biner; citra RGB dikonversi ke grayscale dahulu.
    Piksel >= threshold_val -> 255, lainnya -> 0.
    """
    gray = convert_color(citra) if citra.mode == "RGB" else citra
    hasil = buat_kosong(gray.lebar, gray.tinggi, "L")
    k_src = gray.kanal[0]
    k_dst = hasil.kanal[0]
    for y in range(gray.tinggi):
        src_row = k_src[y]
        dst_row = k_dst[y]
        for x in range(gray.lebar):
            dst_row[x] = 255 if src_row[x] >= threshold_val else 0
    return hasil


def _choose_and_show(original_img, choice):
    if choice == 1:
        value = prompt_int("Masukkan nilai pergeseran brightness (-255 s.d. 255): ", -255, 255)
        result = adjust_brightness(original_img, value)
        label  = f"Brightness ({value:+d})"
    elif choice == 2:
        factor = prompt_float("Masukkan faktor kontras (misal 1.5 untuk meningkatkan): ")
        result = adjust_contrast(original_img, factor)
        label  = f"Kontras (x{factor})"
    elif choice == 3:
        result = negate(original_img)
        label  = "Negasi (Inversi)"
    elif choice == 4:
        result = convert_color(original_img)
        label  = "Konversi ke Grayscale" if original_img.mode == "RGB" else "Konversi ke RGB"
    else:
        threshold = prompt_int("Masukkan nilai ambang batas threshold (0-255): ", 0, 255)
        result = apply_threshold(original_img, threshold)
        label  = f"Thresholding (T={threshold})"
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
