"""Operasi Thresholding: Histogram Analysis, Otsu, Adaptive Mean, dan Adaptive Gaussian.
(Manual Selection sudah tersedia di op_titik.apply_threshold.)

Global : satu nilai T untuk seluruh citra (Histogram Analysis, Otsu).
Lokal  : T dihitung per piksel dari tetangganya (Adaptive Mean, Adaptive Gaussian).
Semua komputasi memakai loop piksel manual (tanpa numpy).
"""
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.utils import (buat_kosong, compute_histogram, korelasi_kanal,
                                buat_padding_pantul, display_comparison,
                                prompt_int, prompt_float, run_standalone)
    from src.op_titik import convert_color
    from src.noise_gaussian import gaussian_kernel
else:
    from .utils import (buat_kosong, compute_histogram, korelasi_kanal,
                        buat_padding_pantul, display_comparison,
                        prompt_int, prompt_float, run_standalone)
    from .op_titik import convert_color
    from .noise_gaussian import gaussian_kernel


def _ke_gray(citra):
    """Thresholding bekerja pada grayscale; citra RGB dikonversi dahulu."""
    return convert_color(citra) if citra.mode == "RGB" else citra


def _binerkan(gray, threshold):
    """Piksel di atas T menjadi 255 (foreground), selain itu 0 (background)."""
    hasil = buat_kosong(gray.lebar, gray.tinggi, "L")
    k_src = gray.kanal[0]
    k_dst = hasil.kanal[0]
    for y in range(gray.tinggi):
        src_row = k_src[y]
        dst_row = k_dst[y]
        for x in range(gray.lebar):
            dst_row[x] = 255 if src_row[x] > threshold else 0
    return hasil


# ---------------------------------------------------------------------------
# Global
# ---------------------------------------------------------------------------

def histogram_analysis_threshold(citra):
    """
    Histogram Analysis: T = intensitas pertama saat CDF ternormalisasi > 0.5.
    Langkah: grayscale -> histogram -> CDF -> normalisasi [0, 1] -> cari T.
    Piksel di atas T menjadi 255, sama atau di bawah T menjadi 0.
    Mengembalikan (citra biner, T).
    """
    gray  = _ke_gray(citra)
    hist  = compute_histogram(gray)['gray']
    total = gray.lebar * gray.tinggi

    threshold = 255
    kumulatif = 0
    for i in range(256):
        kumulatif += hist[i]
        if kumulatif / total > 0.5:       # CDF ternormalisasi
            threshold = i
            break

    return _binerkan(gray, threshold), threshold


def otsu_threshold(citra):
    """
    Otsu: pilih T yang memaksimalkan varians antar-kelas.
        sigma_b^2(T) = w0 * w1 * (mu0 - mu1)^2
    w0, w1 = bobot kelas background (<= T) dan foreground (> T);
    mu0, mu1 = rerata intensitas masing-masing kelas.
    Mengembalikan (citra biner, T).
    """
    gray  = _ke_gray(citra)
    hist  = compute_histogram(gray)['gray']
    total = gray.lebar * gray.tinggi

    jumlah_total = 0                      # sum(i * hist[i]) seluruh citra
    for i in range(256):
        jumlah_total += i * hist[i]

    terbaik   = -1.0
    threshold = 0
    n0 = 0                                # jumlah piksel background
    jumlah0 = 0                           # sum(i * hist[i]) background
    for t in range(256):
        n0 += hist[t]
        jumlah0 += t * hist[t]
        n1 = total - n0
        if n0 == 0 or n1 == 0:            # salah satu kelas kosong -> lewati
            continue
        mu0 = jumlah0 / n0
        mu1 = (jumlah_total - jumlah0) / n1
        w0  = n0 / total
        w1  = n1 / total
        sigma_b = w0 * w1 * (mu0 - mu1) * (mu0 - mu1)
        if sigma_b > terbaik:
            terbaik   = sigma_b
            threshold = t

    return _binerkan(gray, threshold), threshold


# ---------------------------------------------------------------------------
# Lokal (adaptive)
# ---------------------------------------------------------------------------

def _cek_ukuran_blok(block_size):
    if block_size < 3 or block_size % 2 == 0:
        raise ValueError("Ukuran blok harus bilangan ganjil >= 3.")


def adaptive_mean_threshold(citra, block_size=11, c=2.0):
    """
    Adaptive Mean: T(x,y) = rerata tetangga block_size x block_size - C.
    Padding tepi pantul. Jumlah jendela dihitung dengan bilangan bulat dan
    perbandingan dikali n^2 agar piksel tepat di batas ambang tidak salah
    akibat galat float:  f > S/n^2 - C  <=>  f * n^2 > S - C * n^2.
    """
    _cek_ukuran_blok(block_size)
    gray   = _ke_gray(citra)
    pad    = block_size // 2
    n2     = block_size * block_size
    padded = buat_padding_pantul(gray.kanal[0], gray.tinggi, gray.lebar,
                                 pad, pad, pad, pad)
    hasil  = buat_kosong(gray.lebar, gray.tinggi, "L")
    k_src  = gray.kanal[0]
    k_dst  = hasil.kanal[0]
    for y in range(gray.tinggi):
        src_row = k_src[y]
        dst_row = k_dst[y]
        for x in range(gray.lebar):
            jumlah = 0
            for ky in range(block_size):
                row_p = padded[y + ky]
                for kx in range(block_size):
                    jumlah += row_p[x + kx]
            dst_row[x] = 255 if src_row[x] * n2 > jumlah - c * n2 else 0
    return hasil


def adaptive_gaussian_threshold(citra, block_size=11, c=2.0):
    """
    Adaptive Gaussian: T(x,y) = rerata berbobot Gaussian tetangga - C.
    Sigma diturunkan dari ukuran blok: 0.3 * ((block_size - 1) / 2 - 1) + 0.8.
    Rerata lokal = korelasi mask Gaussian (SUM OF PRODUCTS, padding pantul).
    """
    _cek_ukuran_blok(block_size)
    gray   = _ke_gray(citra)
    sigma  = 0.3 * ((block_size - 1) * 0.5 - 1) + 0.8
    kernel = gaussian_kernel(block_size, sigma)
    rerata = korelasi_kanal(gray.kanal[0], gray.tinggi, gray.lebar,
                            kernel, block_size, block_size)
    hasil  = buat_kosong(gray.lebar, gray.tinggi, "L")
    k_src  = gray.kanal[0]
    k_dst  = hasil.kanal[0]
    for y in range(gray.tinggi):
        src_row = k_src[y]
        rer_row = rerata[y]
        dst_row = k_dst[y]
        for x in range(gray.lebar):
            dst_row[x] = 255 if src_row[x] > rer_row[x] - c else 0
    return hasil


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def _tanya_parameter_blok():
    """Meminta ukuran blok ganjil dan konstanta C; None jika ukuran blok genap."""
    block = prompt_int("Masukkan ukuran blok ganjil (misal 11): ", min_val=3)
    if block % 2 == 0:
        print("Ukuran genap tidak valid.")
        return None
    c = prompt_float("Masukkan konstanta C (misal 2): ")
    return block, c


def run(original_img):
    print("\n--- OPERASI THRESHOLDING ---")
    print("[1] Histogram Analysis / CDF (Global)")
    print("[2] Metode Otsu (Global)")
    print("[3] Adaptive Mean (Lokal)")
    print("[4] Adaptive Gaussian (Lokal)")
    op = prompt_int("Pilih sub-operasi thresholding: ", 1, 4)
    if op == 1:
        result, t = histogram_analysis_threshold(original_img)
        label = f"Thresholding Histogram Analysis (T={t})"
    elif op == 2:
        result, t = otsu_threshold(original_img)
        label = f"Thresholding Otsu (T={t})"
    else:
        params = _tanya_parameter_blok()
        if params is None:
            return
        block, c = params
        if op == 3:
            result = adaptive_mean_threshold(original_img, block, c)
            label  = f"Adaptive Mean (blok={block}, C={c})"
        else:
            result = adaptive_gaussian_threshold(original_img, block, c)
            label  = f"Adaptive Gaussian (blok={block}, C={c})"
    display_comparison(original_img, result, label)


if __name__ == "__main__":
    run_standalone(run)