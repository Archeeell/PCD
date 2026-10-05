"""
op_neighborhood.py
Operasi Bertetangga / Persekitaran sesuai materi kuliah (mask SUM OF PRODUCTS).

Rumus dari materi kuliah Pengolahan Citra (Idhawati Hestiningsih):
- Korelasi (bukan konvolusi): kernel TIDAK dibalik
- Padding pantul (reflect): -1 -> 1, n -> n-2
- Penghalusan: rerata 5-titik (plus), 3x3, 5x5 (koreksi: lihat README)
- Penajaman: 5-titik (pusat 1+4a, tetangga -a), 9-titik (pusat 1+8a)
- Deteksi tepi: Roberts, Prewitt, Sobel, Isotropik, Laplacian
- Emboss: kernel non-nol dikali beta, pusat=1; hasil = 128 + respons
- Median: nilai tengah dari jendela ganjil, sorted()
"""

import math
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, korelasi_kanal, buat_padding_pantul,
                                display_comparison, prompt_int, prompt_float, run_standalone)
else:
    from .utils import (Citra, buat_kosong, korelasi_kanal, buat_padding_pantul,
                        display_comparison, prompt_int, prompt_float, run_standalone)

SQRT2 = math.sqrt(2.0)

# Kernel deteksi tepi (list 2D float)
GRADIENTS = {
    "Roberts": (
        [[1.0, 0.0], [0.0, -1.0]],
        [[0.0, 1.0], [-1.0, 0.0]],
    ),
    "Prewitt": (
        [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
        [[-1.0, -1.0, -1.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]],
    ),
    "Sobel": (
        [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
        [[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]],
    ),
    "Isotropik": (
        [[-1.0, 0.0, 1.0], [-SQRT2, 0.0, SQRT2], [-1.0, 0.0, 1.0]],
        [[-1.0, -SQRT2, -1.0], [0.0, 0.0, 0.0], [1.0, SQRT2, 1.0]],
    ),
}
LAPLACIANS = {
    "Laplacian 5 titik":   [[0.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 0.0]],
    "Laplacian 9 titik I": [[-1.0, -1.0, -1.0], [-1.0, 8.0, -1.0], [-1.0, -1.0, -1.0]],
    "Laplacian 9 titik II":[[-2.0, 1.0, -2.0], [1.0, 4.0, 1.0], [-2.0, 1.0, -2.0]],
}
EMBOSS = {
    "Dari arah kiri":       [[-1.0, 0.0, 1.0], [-1.0, 1.0, 1.0], [-1.0, 0.0, 1.0]],
    "Dari arah kanan atas": [[0.0, -1.0, -1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 0.0]],
}


def _terapkan_kernel(citra, kernel):
    """
    Terapkan kernel (list 2D) ke semua kanal citra menggunakan korelasi.
    Mengembalikan list kanal baru sebagai list 2D float.
    """
    kh = len(kernel)
    kw = len(kernel[0])
    hasil_kanal = []
    for c in range(len(citra.kanal)):
        hasil_kanal.append(
            korelasi_kanal(citra.kanal[c], citra.tinggi, citra.lebar, kernel, kh, kw)
        )
    return hasil_kanal


def _uint8_dari_float_kanal(kanal_float, tinggi, lebar, mode):
    """
    Konversi list kanal float ke Citra uint8:
    round() (half-to-even) lalu klem ke 0-255.
    """
    hasil = buat_kosong(lebar, tinggi, mode)
    for c in range(len(kanal_float)):
        k_src = kanal_float[c]
        k_dst = hasil.kanal[c]
        for y in range(tinggi):
            src_row = k_src[y]
            dst_row = k_dst[y]
            for x in range(lebar):
                v = round(src_row[x])   # half-to-even, sesuai np.rint
                if v < 0:
                    v = 0
                elif v > 255:
                    v = 255
                dst_row[x] = v
    return hasil


def _gabungkan(gx_kanal, gy_kanal, tinggi, lebar, method):
    """
    Gabungkan dua kanal float gradien dengan metode yang dipilih.
    method: 1=jumlah, 2=maksimum, 3=rerata, 4=magnitudo Euclidean.
    """
    hasil_kanal = []
    for c in range(len(gx_kanal)):
        gx_k = gx_kanal[c]
        gy_k = gy_kanal[c]
        out = [[0.0] * lebar for _ in range(tinggi)]
        for y in range(tinggi):
            gx_row = gx_k[y]
            gy_row = gy_k[y]
            out_row = out[y]
            for x in range(lebar):
                ax = abs(gx_row[x])
                ay = abs(gy_row[x])
                if method == 1:
                    out_row[x] = ax + ay
                elif method == 2:
                    out_row[x] = ax if ax > ay else ay
                elif method == 3:
                    out_row[x] = (ax + ay) / 2
                else:  # 4: magnitudo Euclidean
                    gx_v = gx_row[x]
                    gy_v = gy_row[x]
                    out_row[x] = math.sqrt(gx_v * gx_v + gy_v * gy_v)
        hasil_kanal.append(out)
    return hasil_kanal


def edge_detection(citra, operator="Sobel", combination=4):
    """Operator gradien dari materi; kombinasi: jumlah, maksimum, rerata, magnitudo."""
    if operator in GRADIENTS:
        kx, ky = GRADIENTS[operator]
        gx_kanal = _terapkan_kernel(citra, kx)
        gy_kanal = _terapkan_kernel(citra, ky)
        return _gabungkan(gx_kanal, gy_kanal, citra.tinggi, citra.lebar, combination)
    else:
        lap_kanal = _terapkan_kernel(citra, LAPLACIANS[operator])
        # Nilai absolut untuk Laplacian
        hasil_kanal = []
        for c in range(len(lap_kanal)):
            k = lap_kanal[c]
            out = [[abs(k[y][x]) for x in range(citra.lebar)] for y in range(citra.tinggi)]
            hasil_kanal.append(out)
        return hasil_kanal


def smoothing(citra, neighborhood=3):
    """
    Penghalusan citra.
    neighborhood=5  -> mask 5-titik plus: [[0,1,0],[1,1,1],[0,1,0]] / 5
    neighborhood=3  -> mask 3x3 penuh: 1/9
    neighborhood=25 -> mask 5x5 penuh: 1/25 (KOREKSI Deviasi #1)
    """
    if neighborhood == 5:
        kernel = [[0.0, 1/5, 0.0], [1/5, 1/5, 1/5], [0.0, 1/5, 0.0]]
    elif neighborhood == 25:
        w = 1/25
        kernel = [[w]*5 for _ in range(5)]
    else:  # 3x3
        w = 1/9
        kernel = [[w]*3 for _ in range(3)]
    return _terapkan_kernel(citra, kernel)


def sharpening(citra, alpha=1.0, neighborhood=5):
    """
    Penajaman citra.
    5-titik: pusat = 1+4*alpha, tetangga atas/bawah/kiri/kanan = -alpha.
    9-titik: pusat = 1+8*alpha, semua tetangga = -alpha.
    """
    if neighborhood == 5:
        kernel = [
            [0.0,    -alpha,         0.0],
            [-alpha, 1 + 4 * alpha, -alpha],
            [0.0,    -alpha,         0.0],
        ]
    else:
        kernel = [
            [-alpha, -alpha, -alpha],
            [-alpha, 1 + 8 * alpha, -alpha],
            [-alpha, -alpha, -alpha],
        ]
    return _terapkan_kernel(citra, kernel)


def median_filter(citra, window=3):
    """
    Reduksi noise dengan median pada jendela ganjil.
    Gunakan sorted() -> ambil nilai tengah.
    """
    if window < 1 or window % 2 == 0:
        raise ValueError("Ukuran jendela median harus bilangan ganjil positif.")
    pad = window // 2

    # buat_padding_pantul sudah diimpor di atas melalui utils

    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    tengah = (window * window) // 2

    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]

        padded = buat_padding_pantul(k_src, citra.tinggi, citra.lebar, pad, pad, pad, pad)

        if citra.tinggi > 50:
            print(f"  Median kanal {c}: 0%", end="", flush=True)

        for y in range(citra.tinggi):
            if citra.tinggi > 50 and y % max(1, citra.tinggi // 10) == 0:
                pct = int(100 * y / citra.tinggi)
                print(f"\r  Median kanal {c}: {pct}%", end="", flush=True)
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                vals = []
                for wy in range(window):
                    row_p = padded[y + wy]
                    for wx in range(window):
                        vals.append(row_p[x + wx])
                vals.sort()
                v = vals[tengah]
                # round lalu klem (konsisten dengan np.rint + clip)
                v_r = round(v)
                dst_row[x] = max(0, min(255, v_r))

        if citra.tinggi > 50:
            print(f"\r  Median kanal {c}: 100%")

    return hasil


def emboss_response(citra, beta=2, direction="Dari arah kiri"):
    """
    Respons SUM OF PRODUCTS mentah sesuai contoh perhitungan materi.
    Kernel: entri non-nol dari template dikali beta, pusat=1.
    """
    template = EMBOSS[direction]
    kh, kw = len(template), len(template[0])
    kernel = [[0.0] * kw for _ in range(kh)]
    for ky in range(kh):
        for kx in range(kw):
            v = template[ky][kx]
            if v != 0.0:
                kernel[ky][kx] = v * beta
    # Pusat kernel = 1
    cy, cx = kh // 2, kw // 2
    kernel[cy][cx] = 1.0
    return _terapkan_kernel(citra, kernel)


def emboss(citra, beta=2, direction="Dari arah kiri"):
    """Efek emboss: 128 + respons mentah."""
    resp_kanal = emboss_response(citra, beta, direction)
    hasil_kanal = []
    for c in range(len(resp_kanal)):
        k = resp_kanal[c]
        out = [[128.0 + k[y][x] for x in range(citra.lebar)] for y in range(citra.tinggi)]
        hasil_kanal.append(out)
    return hasil_kanal


def run(original_img):
    print("\n--- OPERASI BERTETANGGA / PERSEKITARAN ---")
    print("[1] Deteksi Tepi  [2] Penghalusan Citra  [3] Penajaman Citra")
    print("[4] Reduksi Noise (Median)  [5] Efek Emboss")
    op = prompt_int("Pilih sub-operasi neighborhood: ", 1, 5)

    if op == 1:
        names = list(GRADIENTS) + list(LAPLACIANS)
        for i, name in enumerate(names, 1):
            print(f"[{i}] {name}")
        operator = names[prompt_int("Pilih operator: ", 1, len(names)) - 1]
        if operator in GRADIENTS:
            print("[1] Jumlah  [2] Maksimum  [3] Rerata  [4] Magnitudo Euclidean")
            method = prompt_int("Pilih kombinasi K1 dan K2: ", 1, 4)
        else:
            method = 4
        kanal_float = edge_detection(original_img, operator, method)
        result = _uint8_dari_float_kanal(kanal_float, original_img.tinggi,
                                         original_img.lebar, original_img.mode)
        label = f"Deteksi Tepi {operator}"

    elif op == 2:
        print("[1] 5 titik  [2] 9 titik (3x3)  [3] 25 titik (5x5)")
        choice = prompt_int("Pilih mask smoothing: ", 1, 3)
        n_map = {1: 5, 2: 3, 3: 25}
        n = n_map[choice]
        kanal_float = smoothing(original_img, n)
        result = _uint8_dari_float_kanal(kanal_float, original_img.tinggi,
                                         original_img.lebar, original_img.mode)
        label = f"Smoothing {n} tetangga"

    elif op == 3:
        print("[1] 5 titik  [2] 9 titik")
        n = 5 if prompt_int("Pilih mask sharpening: ", 1, 2) == 1 else 9
        alpha = prompt_float("Masukkan derajat penajaman alpha: ")
        kanal_float = sharpening(original_img, alpha, n)
        result = _uint8_dari_float_kanal(kanal_float, original_img.tinggi,
                                         original_img.lebar, original_img.mode)
        label = f"Sharpening {n} titik (alpha={alpha})"

    elif op == 4:
        window = prompt_int("Masukkan ukuran jendela median ganjil (3, 5, 7, ...): ", 1)
        if window % 2 == 0:
            print("Ukuran genap tidak valid.")
            return
        result = median_filter(original_img, window)
        label  = f"Reduksi Noise Median {window}x{window}"

    else:
        print("[1] Dari arah kiri  [2] Dari arah kanan atas")
        direction = list(EMBOSS)[prompt_int("Pilih arah emboss: ", 1, 2) - 1]
        beta = prompt_float("Masukkan derajat emboss beta: ")
        kanal_float = emboss(original_img, beta, direction)
        result = _uint8_dari_float_kanal(kanal_float, original_img.tinggi,
                                         original_img.lebar, original_img.mode)
        label = f"Emboss {direction} (beta={beta})"

    display_comparison(original_img, result, label)


if __name__ == "__main__":
    run_standalone(run)
