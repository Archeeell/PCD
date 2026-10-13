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


def tampilkan_tabel_hex_negasi(tampilkan_semua=False):
    """
    Menampilkan tabel pemetaan perubahan intensitas dari citra awal ke citra negasi (0-255)
    dalam representasi Desimal dan Heksadesimal (Hex).
    """
    print("\n" + "=" * 65)
    print("     TABEL PEMETAAN TRANSFORMASI INTENSITAS & HEX (NEGASI)      ")
    print("=" * 65)
    print(f"{'Nilai Awal (Ki)':^28} | {'Nilai Negasi (Ko)':^28}")
    print(f"{'Desimal':<12} {'Hexadecimal':<14} | {'Desimal':<12} {'Hexadecimal':<14}")
    print("-" * 65)

    if tampilkan_semua:
        rentang = range(256)
    else:
        # Tampilkan sampel terstruktur: awal, pertengahan (pivot), dan akhir
        rentang = list(range(0, 11)) + [64, 127, 128, 191] + list(range(245, 256))

    prev = -1
    for i in rentang:
        if prev != -1 and i > prev + 1:
            print(f"{'...':^12} {'...':^14} | {'...':^12} {'...':^14}")
        val_negasi = 255 - i
        print(f"{i:<12} {f'0x{i:02X}':<14} | {val_negasi:<12} {f'0x{val_negasi:02X}':<14}")
        prev = i
    print("=" * 65 + "\n")


def tampilkan_grid_hex_piksel(citra_awal, citra_negasi, grid_w, grid_h):
    """
    Menampilkan perbandingan nilai piksel HEX dari pojok kiri atas (0, 0)
    sebesar grid_w x grid_h piksel.
    """
    w = min(grid_w, citra_awal.lebar)
    h = min(grid_h, citra_awal.tinggi)

    def _format_pixel_hex(c_obj, x, y):
        if c_obj.mode == "RGB":
            r = c_obj.kanal[0][y][x]
            g = c_obj.kanal[1][y][x]
            b = c_obj.kanal[2][y][x]
            return f"#{r:02X}{g:02X}{b:02X}"
        else:
            val = c_obj.kanal[0][y][x]
            return f"0x{val:02X}"

    print("\n" + "=" * 70)
    print(f"  MATRIKS NILAI HEX PIKSEL (Ukuran {w}x{h} px dari kiri atas [0, 0])  ")
    print(f"  Mode Citra: {citra_awal.mode}")
    print("=" * 70)

    print("\n--- [1] CITRA ASLI (Sebelum Negasi) ---")
    header_x = "      " + " ".join(f"{x:>7}" for x in range(w))
    print(header_x)
    print("     " + "-" * (len(header_x) - 5))
    for y in range(h):
        baris_str = f"y={y:<3}| " + " ".join(f"{_format_pixel_hex(citra_awal, x, y):>7}" for x in range(w))
        print(baris_str)

    print("\n--- [2] CITRA HASIL NEGASI ---")
    print(header_x)
    print("     " + "-" * (len(header_x) - 5))
    for y in range(h):
        baris_str = f"y={y:<3}| " + " ".join(f"{_format_pixel_hex(citra_negasi, x, y):>7}" for x in range(w))
        print(baris_str)
    print("=" * 70 + "\n")


def negate(citra, cetak_tabel=False):

    """Negasi: Ko = 255 - Ki."""
    if cetak_tabel:
        tampilkan_tabel_hex_negasi(tampilkan_semua=False)

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
        pilihan_tabel = input("Tampilkan tabel pemetaan 0-255 HEX? (y/N): ").strip().lower()
        if pilihan_tabel == "y":
            pilihan_semua = input("Tampilkan seluruh 256 baris penuh? (y/N): ").strip().lower()
            tampilkan_tabel_hex_negasi(tampilkan_semua=(pilihan_semua == "y"))

        result = negate(original_img, cetak_tabel=False)

        input_grid = input(f"Masukkan ukuran grid piksel HEX dari kiri atas (contoh: 50x50, maks {original_img.lebar}x{original_img.tinggi}, atau tekan Enter untuk skip): ").strip().lower()
        if input_grid:
            try:
                if "x" in input_grid:
                    gw_str, gh_str = input_grid.split("x", 1)
                elif "," in input_grid:
                    gw_str, gh_str = input_grid.split(",", 1)
                else:
                    gw_str = gh_str = input_grid
                gw, gh = int(gw_str.strip()), int(gh_str.strip())
                if gw > 0 and gh > 0:
                    tampilkan_grid_hex_piksel(original_img, result, gw, gh)
                else:
                    print("Ukuran grid harus lebih besar dari 0.")
            except ValueError:
                print("Format input ukuran grid tidak valid, melewati tampilan grid.")

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
