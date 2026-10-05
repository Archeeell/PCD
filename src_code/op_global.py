"""Operasi Global: histogram citra dan ekualisasi histogram."""
import math
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong,
                                display_comparison, prompt_int, run_standalone)
else:
    from .utils import (Citra, buat_kosong,
                        display_comparison, prompt_int, run_standalone)


def _equalize_channel(kanal_2d, tinggi, lebar, max_level=255):
    """
    Ekualisasi satu kanal.
    LUT: Ko = floor(Ci * max_level / (w*h) + 1e-9)
    di mana Ci = histogram kumulatif pada nilai i.
    bins = max_level + 1, range [0, max_level].
    """
    n_bins = max_level + 1
    total  = lebar * tinggi

    # Hitung histogram
    hist = [0] * n_bins
    for y in range(tinggi):
        row = kanal_2d[y]
        for x in range(lebar):
            v = row[x]
            if 0 <= v <= max_level:
                hist[v] += 1

    # Hitung LUT dari histogram kumulatif
    lut      = [0] * n_bins
    kumulatif = 0
    for i in range(n_bins):
        kumulatif += hist[i]
        lut[i] = int(math.floor(kumulatif * max_level / total + 1e-9))
        if lut[i] > max_level:
            lut[i] = max_level

    # Terapkan LUT
    kanal_out = [[lut[kanal_2d[y][x]] for x in range(lebar)] for y in range(tinggi)]
    return kanal_out


def histogram_equalization(citra, max_level=255):
    """
    Ekualisasi histogram; citra RGB diproses per kanal.
    Rumus: Ko = floor(Ci * max_level / (w*h) + epsilon).
    """
    if citra.mode == "L":
        kanal_baru = [_equalize_channel(citra.kanal[0], citra.tinggi, citra.lebar, max_level)]
        return Citra(citra.lebar, citra.tinggi, "L", kanal_baru)
    else:
        kanal_baru = [
            _equalize_channel(citra.kanal[c], citra.tinggi, citra.lebar, max_level)
            for c in range(3)
        ]
        return Citra(citra.lebar, citra.tinggi, "RGB", kanal_baru)


def show_histogram(citra):
    """Menampilkan citra dan histogram aslinya memakai visualisasi bersama."""
    display_comparison(citra, citra, "Histogram Citra Asli")


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


if __name__ == "__main__":
    run_standalone(run)
