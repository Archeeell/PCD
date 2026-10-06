"""Operasi Titik (GST): brightness, contrast, negation, grayscale, dan thresholding."""
import math
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, klem, get_pixel,
                                display_comparison, prompt_int, prompt_float, run_standalone)
else:
    from .utils import (Citra, buat_kosong, klem, get_pixel,
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


def negate(citra, verbose=False):
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
    if verbose:
        tampilkan_perubahan_pixel_negasi(citra, hasil, interaktif=False)
    return hasil


def tampilkan_perubahan_pixel_negasi(citra_awal, citra_hasil, interaktif=True):
    """
    Menampilkan rincian perubahan nilai piksel dari citra awal ke citra hasil negasi:
    - Rumus matematis transformasi negasi (Ko = 255 - Ki).
    - Tabel sampel nilai piksel pada titik-titik koordinat kunci (kiri atas, pusat, dll).
    - Cuplikan matriks piksel sebelum vs sesudah negasi.
    - Opsi interaktif untuk menginspeksi koordinat piksel tertentu.
    """
    w = citra_awal.lebar
    h = citra_awal.tinggi
    mode = citra_awal.mode
    garis = "=" * 78
    garis_tipis = "-" * 78

    print(f"\n{garis}")
    print("        PERUBAHAN NILAI PIKSEL: CITRA AWAL -> CITRA HASIL NEGASI")
    print(garis)
    print("Prinsip Operasi Negasi (Inversi Derajat Keabuan / Warna):")
    if mode == "L":
        print("  Rumus : Ko = 255 - Ki")
        print("  Sifat : Nilai piksel gelap (0) menjadi terang (255) dan sebaliknya.")
    else:
        print("  Rumus : R' = 255 - R,  G' = 255 - G,  B' = 255 - B")
        print("  Sifat : Dihitung per-kanal warna (RGB) secara independen.")
    print(f"Mode Citra  : {mode} ({'Grayscale 8-bit' if mode == 'L' else 'RGB True Color 24-bit'})")
    print(f"Ukuran Citra: {w} x {h} piksel")

    # 1. Sampel Titik Koordinat Kunci
    titik_kunci = [
        ("Pojok Kiri-Atas", 0, 0),
        ("Pojok Kanan-Atas", w - 1, 0),
        ("Titik Tengah / Pusat", w // 2, h // 2),
        ("Pojok Kiri-Bawah", 0, h - 1),
        ("Pojok Kanan-Bawah", w - 1, h - 1),
    ]

    titik_unik = []
    seen = set()
    for nama, x, y in titik_kunci:
        if (x, y) not in seen:
            seen.add((x, y))
            titik_unik.append((nama, x, y))

    print(f"\n[1] Sampel Perubahan Nilai Piksel pada Koordinat Representatif:")
    print(garis_tipis)
    if mode == "L":
        print(f"  {'Lokasi':<21} | {'Koordinat':<12} | {'Awal':<6} | {'Negasi':<6} | {'Perhitungan (255 - Ki)'}")
        print("  " + "-" * 74)
        for nama, x, y in titik_unik:
            val_awal = get_pixel(citra_awal, x, y)
            val_hasil = get_pixel(citra_hasil, x, y)
            hitung = f"255 - {val_awal} = {val_hasil}"
            coord_str = f"({x}, {y})"
            print(f"  {nama:<21} | {coord_str:<12} | {val_awal:<6} | {val_hasil:<6} | {hitung}")
    else:
        print(f"  {'Lokasi':<20} | {'Koordinat':<10} | {'Nilai Awal (R,G,B)':<18} | {'Nilai Negasi (R,G,B)':<18} | {'Detail Perhitungan (255 - C)'}")
        print("  " + "-" * 115)
        for nama, x, y in titik_unik:
            r0, g0, b0 = get_pixel(citra_awal, x, y)
            r1, g1, b1 = get_pixel(citra_hasil, x, y)
            awal_str = f"({r0}, {g0}, {b0})"
            hasil_str = f"({r1}, {g1}, {b1})"
            hitung = f"R: 255-{r0}={r1} | G: 255-{g0}={g1} | B: 255-{b0}={b1}"
            coord_str = f"({x}, {y})"
            print(f"  {nama:<20} | {coord_str:<10} | {awal_str:<18} | {hasil_str:<18} | {hitung}")

    # 2. Cuplikan Submatriks Piksel
    sub_w = min(5 if mode == "L" else 3, w)
    sub_h = min(5 if mode == "L" else 3, h)

    print(f"\n[2] Cuplikan Matriks Nilai Piksel (Area {sub_w}x{sub_h} Pojok Kiri-Atas [0..{sub_w-1}, 0..{sub_h-1}]):")
    if mode == "L":
        print("\n  >> Matriks Citra Awal (Sebelum Negasi):")
        for y in range(sub_h):
            baris_awal = [f"{citra_awal.kanal[0][y][x]:3d}" for x in range(sub_w)]
            print("     [ " + ", ".join(baris_awal) + " ]")

        print("\n  >> Matriks Citra Hasil (Setelah Negasi: 255 - Ki):")
        for y in range(sub_h):
            baris_hasil = [f"{citra_hasil.kanal[0][y][x]:3d}" for x in range(sub_w)]
            print("     [ " + ", ".join(baris_hasil) + " ]")
    else:
        print("\n  >> Matriks Citra Awal (R, G, B):")
        for y in range(sub_h):
            baris_awal = [f"({citra_awal.kanal[0][y][x]:3d},{citra_awal.kanal[1][y][x]:3d},{citra_awal.kanal[2][y][x]:3d})" for x in range(sub_w)]
            print("     [ " + ", ".join(baris_awal) + " ]")

        print("\n  >> Matriks Citra Hasil Negasi (255-R, 255-G, 255-B):")
        for y in range(sub_h):
            baris_hasil = [f"({citra_hasil.kanal[0][y][x]:3d},{citra_hasil.kanal[1][y][x]:3d},{citra_hasil.kanal[2][y][x]:3d})" for x in range(sub_w)]
            print("     [ " + ", ".join(baris_hasil) + " ]")

    print(f"{garis}")

    # 3. Interaktif: Cek koordinat piksel custom
    if interaktif:
        try:
            tanya = input("\nApakah Anda ingin memeriksa piksel pada koordinat tertentu? (y/n, default n): ").strip().lower()
            while tanya in ("y", "ya", "yes"):
                print(f"Batas koordinat x: 0 s.d. {w - 1}, y: 0 s.d. {h - 1}")
                px = prompt_int("  Masukkan koordinat x (kolom): ", 0, w - 1)
                py = prompt_int("  Masukkan koordinat y (baris): ", 0, h - 1)
                if mode == "L":
                    v0 = get_pixel(citra_awal, px, py)
                    v1 = get_pixel(citra_hasil, px, py)
                    print(f"  Piksel f({px}, {py}):")
                    print(f"    - Nilai Awal   : {v0}")
                    print(f"    - Nilai Negasi : {v1}  (255 - {v0} = {v1})")
                else:
                    r0, g0, b0 = get_pixel(citra_awal, px, py)
                    r1, g1, b1 = get_pixel(citra_hasil, px, py)
                    print(f"  Piksel f({px}, {py}):")
                    print(f"    - Nilai Awal   : R={r0}, G={g0}, B={b0}")
                    print(f"    - Nilai Negasi : R={r1}, G={g1}, B={b1}")
                    print(f"    - Perhitungan  : R: 255-{r0}={r1} | G: 255-{g0}={g1} | B: 255-{b0}={b1}")
                tanya = input("\nPeriksa koordinat lain? (y/n, default n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            pass


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
        tampilkan_perubahan_pixel_negasi(original_img, result, interaktif=True)
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
