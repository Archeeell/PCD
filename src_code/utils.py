"""
utils.py
Berisi fungsi-fungsi bantu yang dipakai bersama oleh semua modul operasi:
- Kelas Citra: representasi citra sebagai daftar kanal 2D tanpa numpy
- Membaca daftar gambar & memuat gambar
- Menghitung histogram (manual, tanpa numpy)
- Membandingkan histogram
- Menampilkan hasil perbandingan (citra asli vs hasil transformasi)
"""

import os
import sys
from PIL import Image
import matplotlib.pyplot as plt

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(PROJECT_DIR, "img")


# ---------------------------------------------------------------------------
# Kelas Citra: representasi internal tanpa numpy
# kanal[c][y][x] -> nilai integer 0-255
# ---------------------------------------------------------------------------

class Citra:
    """
    Representasi citra sebagai daftar kanal 2D.
      lebar  (int) : lebar citra (jumlah kolom)
      tinggi (int) : tinggi citra (jumlah baris)
      mode   (str) : "L" untuk grayscale, "RGB" untuk warna
      kanal  (list): list[kanal_idx][baris][kolom] = nilai int 0-255
    """
    __slots__ = ("lebar", "tinggi", "mode", "kanal")

    def __init__(self, lebar, tinggi, mode, kanal):
        self.lebar  = lebar
        self.tinggi = tinggi
        self.mode   = mode    # "L" atau "RGB"
        self.kanal  = kanal   # list of 2D list of int


def buat_kosong(lebar, tinggi, mode, nilai=0):
    """Buat Citra kosong; semua piksel diisi dengan nilai (default 0)."""
    n = 1 if mode == "L" else 3
    kanal = [[[nilai] * lebar for _ in range(tinggi)] for _ in range(n)]
    return Citra(lebar, tinggi, mode, kanal)


def salin(citra):
    """Buat salinan dalam (deep copy) dari sebuah Citra."""
    kanal_baru = []
    for c in range(len(citra.kanal)):
        kanal_baru.append([list(baris) for baris in citra.kanal[c]])
    return Citra(citra.lebar, citra.tinggi, citra.mode, kanal_baru)


def terapkan_per_kanal(citra, fungsi):
    """
    Terapkan fungsi(kanal_2d, indeks_kanal) -> kanal_2d baru pada tiap kanal.
    Mengembalikan Citra baru dengan mode & ukuran yang sama.
    """
    kanal_baru = [fungsi(citra.kanal[c], c) for c in range(len(citra.kanal))]
    return Citra(citra.lebar, citra.tinggi, citra.mode, kanal_baru)


def ke_pil(citra):
    """Konversi Citra ke objek PIL.Image menggunakan putpixel."""
    img = Image.new(citra.mode, (citra.lebar, citra.tinggi))
    if citra.mode == "L":
        for y in range(citra.tinggi):
            row = citra.kanal[0][y]
            for x in range(citra.lebar):
                img.putpixel((x, y), row[x])
    else:
        r_k, g_k, b_k = citra.kanal[0], citra.kanal[1], citra.kanal[2]
        for y in range(citra.tinggi):
            r_row, g_row, b_row = r_k[y], g_k[y], b_k[y]
            for x in range(citra.lebar):
                img.putpixel((x, y), (r_row[x], g_row[x], b_row[x]))
    return img


def dari_pil(gambar):
    """
    Konversi PIL.Image ke Citra.
    Piksel dibaca sekali dengan getpixel lalu disimpan ke list 2D per kanal.
    gambar harus sudah dalam mode "L" atau "RGB".
    """
    lebar, tinggi = gambar.size
    mode = gambar.mode

    if mode == "L":
        kanal = [[[0] * lebar for _ in range(tinggi)]]
        for y in range(tinggi):
            row = kanal[0][y]
            for x in range(lebar):
                row[x] = gambar.getpixel((x, y))
    else:
        kanal = [[[0] * lebar for _ in range(tinggi)] for _ in range(3)]
        r_k, g_k, b_k = kanal[0], kanal[1], kanal[2]
        for y in range(tinggi):
            r_row, g_row, b_row = r_k[y], g_k[y], b_k[y]
            for x in range(lebar):
                p = gambar.getpixel((x, y))
                r_row[x] = p[0]
                g_row[x] = p[1]
                b_row[x] = p[2]

    return Citra(lebar, tinggi, mode, kanal)


# ---------------------------------------------------------------------------
# Fungsi bantu umum
# ---------------------------------------------------------------------------

def klem(nilai):
    """Batasi nilai integer ke rentang [0, 255]."""
    if nilai < 0:
        return 0
    if nilai > 255:
        return 255
    return nilai


def get_pixel(citra, x, y):
    """
    Mengambil nilai intensitas titik piksel pada koordinat (x, y).
    Grayscale -> integer 0-255.
    RGB       -> tuple (R, G, B) integer 0-255.
    """
    if not (0 <= x < citra.lebar and 0 <= y < citra.tinggi):
        raise IndexError(f"Koordinat ({x}, {y}) di luar batas citra ({citra.lebar}x{citra.tinggi})")
    if citra.mode == "L":
        return citra.kanal[0][y][x]
    return (citra.kanal[0][y][x], citra.kanal[1][y][x], citra.kanal[2][y][x])


def set_pixel(citra, x, y, nilai):
    """
    Mengatur nilai intensitas titik piksel pada koordinat (x, y).
    nilai dapat berupa integer (untuk Grayscale) atau tuple/list (R, G, B).
    """
    if not (0 <= x < citra.lebar and 0 <= y < citra.tinggi):
        raise IndexError(f"Koordinat ({x}, {y}) di luar batas citra ({citra.lebar}x{citra.tinggi})")
    if citra.mode == "L":
        citra.kanal[0][y][x] = klem(int(nilai))
    else:
        if isinstance(nilai, (int, float)):
            v = klem(int(nilai))
            citra.kanal[0][y][x] = v
            citra.kanal[1][y][x] = v
            citra.kanal[2][y][x] = v
        else:
            citra.kanal[0][y][x] = klem(int(nilai[0]))
            citra.kanal[1][y][x] = klem(int(nilai[1]))
            citra.kanal[2][y][x] = klem(int(nilai[2]))



def indeks_pantul(i, n):
    """
    Hitung indeks setelah padding pantul (numpy 'reflect') untuk dimensi n.
    Reflect TIDAK mengulangi piksel tepi: -1 -> 1, n -> n-2.
    """
    if n == 1:
        return 0
    period = 2 * (n - 1)
    i = i % period
    if i < 0:
        i += period
    if i >= n:
        i = period - i
    return i


def buat_padding_pantul(kanal_2d, tinggi, lebar, py_bef, py_aft, px_bef, px_aft):
    """
    Buat salinan kanal dengan padding pantul (reflect) di semua sisi.
    Nilai disimpan sebagai float untuk komputasi numerik.
    """
    h_baru = tinggi + py_bef + py_aft
    w_baru = lebar  + px_bef + px_aft
    hasil = [[0.0] * w_baru for _ in range(h_baru)]

    for y_baru in range(h_baru):
        y_src = indeks_pantul(y_baru - py_bef, tinggi)
        src_baris = kanal_2d[y_src]
        dst_baris = hasil[y_baru]
        for x_baru in range(w_baru):
            x_src = indeks_pantul(x_baru - px_bef, lebar)
            dst_baris[x_baru] = src_baris[x_src]

    return hasil


def korelasi_kanal(kanal_2d, tinggi, lebar, kernel, kh, kw):
    """
    Hitung korelasi (SUM OF PRODUCTS, kernel TIDAK dibalik) antara kanal_2d
    dan kernel berukuran kh x kw. Padding pantul (reflect).
    Mengembalikan list 2D float.
    """
    py_bef = (kh - 1) // 2
    py_aft = kh - 1 - py_bef
    px_bef = (kw - 1) // 2
    px_aft = kw - 1 - px_bef

    padded = buat_padding_pantul(kanal_2d, tinggi, lebar, py_bef, py_aft, px_bef, px_aft)
    hasil  = [[0.0] * lebar for _ in range(tinggi)]

    for y in range(tinggi):
        for x in range(lebar):
            total = 0.0
            for ky in range(kh):
                row_p = padded[y + ky]
                row_k = kernel[ky]
                for kx in range(kw):
                    total += row_p[x + kx] * row_k[kx]
            hasil[y][x] = total

    return hasil


# ---------------------------------------------------------------------------
# Membaca & memuat gambar
# ---------------------------------------------------------------------------

def get_available_images():
    """Mengembalikan daftar nama file gambar yang tersedia di folder IMG_DIR."""
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        return []
    valid_exts = ('.bmp', '.png', '.jpg', '.jpeg', '.webp', '.tiff')
    return [f for f in os.listdir(IMG_DIR) if f.lower().endswith(valid_exts)]


def load_image(filepath):
    """
    Memuat gambar dari path dan mengembalikannya sebagai Citra.
    Mode selain L/RGB dikonversi ke RGB.
    Piksel dibaca sekali saja dengan getpixel; semua proses pakai list.
    """
    img = Image.open(filepath)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    return dari_pil(img)


def simpan_pil(citra, path):
    """Simpan Citra ke file via PIL (dipakai oleh noise_*.py process())."""
    ke_pil(citra).save(path)


# ---------------------------------------------------------------------------
# run_standalone
# ---------------------------------------------------------------------------

def run_standalone(operation):
    """Pilih citra, lalu jalankan satu modul operasi tanpa src_code/main.py."""
    images = get_available_images()
    if not images:
        print(f"Folder '{IMG_DIR}' kosong atau tidak berisi citra yang didukung.")
        return
    print("=== DAFTAR GAMBAR TERSEDIA ===")
    for index, name in enumerate(images, 1):
        print(f"[{index}] {name}")
    choice = prompt_int("Pilih nomor gambar (0 untuk batal): ", 0, len(images))
    if choice == 0:
        print("Operasi dibatalkan.")
        return
    path   = os.path.join(IMG_DIR, images[choice - 1])
    citra  = load_image(path)
    saluran = "Grayscale" if citra.mode == "L" else "RGB"
    print(f"\nMemuat: {path} | Resolusi: {citra.lebar}x{citra.tinggi} | Saluran: {saluran}")
    operation(citra)


# ---------------------------------------------------------------------------
# Histogram (manual, tanpa numpy)
# ---------------------------------------------------------------------------

def compute_histogram(citra):
    """
    Menghitung histogram Citra secara manual (256 bin per kanal).
    Grayscale -> {'gray': list[256]}.
    RGB       -> {'r': list[256], 'g': list[256], 'b': list[256]}.
    """
    if citra.mode == "L":
        hist = [0] * 256
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                hist[citra.kanal[0][y][x]] += 1
        return {'gray': hist}
    else:
        hr, hg, hb = [0]*256, [0]*256, [0]*256
        r_k, g_k, b_k = citra.kanal[0], citra.kanal[1], citra.kanal[2]
        for y in range(citra.tinggi):
            for x in range(citra.lebar):
                hr[r_k[y][x]] += 1
                hg[g_k[y][x]] += 1
                hb[b_k[y][x]] += 1
        return {'r': hr, 'g': hg, 'b': hb}


def are_histograms_identical(hist1, hist2):
    """Mengecek apakah dua histogram identik (kunci & nilai sama persis)."""
    if set(hist1.keys()) != set(hist2.keys()):
        return False
    for k in hist1:
        if hist1[k] != hist2[k]:
            return False
    return True


# ---------------------------------------------------------------------------
# Tampilan
# ---------------------------------------------------------------------------

def display_comparison(citra_asli, citra_hasil, judul_operasi):
    """
    Menampilkan grid 2x2: citra asli, citra hasil, histogram asli, histogram hasil.
    Menerima objek Citra; konversi ke PIL.Image untuk imshow.
    """
    hist_orig  = compute_histogram(citra_asli)
    hist_trans = compute_histogram(citra_hasil)
    identical  = are_histograms_identical(hist_orig, hist_trans)

    pil_asli  = ke_pil(citra_asli)
    pil_hasil = ke_pil(citra_hasil)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    cmap_a = 'gray' if citra_asli.mode  == "L" else None
    cmap_h = 'gray' if citra_hasil.mode == "L" else None
    axes[0, 0].imshow(pil_asli,  cmap=cmap_a, vmin=0, vmax=255)
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis('off')
    axes[0, 1].imshow(pil_hasil, cmap=cmap_h, vmin=0, vmax=255)
    axes[0, 1].set_title(f"Hasil: {judul_operasi}")
    axes[0, 1].axis('off')

    def _plot_hist(ax, hist, judul):
        if 'gray' in hist:
            ax.plot(hist['gray'], color='black', label='Grayscale')
        else:
            ax.plot(hist['r'], color='red',   label='Red')
            ax.plot(hist['g'], color='green', label='Green')
            ax.plot(hist['b'], color='blue',  label='Blue')
        ax.set_title(judul)
        ax.set_xlim([0, 255])
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

    _plot_hist(axes[1, 0], hist_orig, "Histogram Citra Asli")
    status = "IDENTIK (Citra Sama)" if identical else "TIDAK IDENTIK"
    _plot_hist(axes[1, 1], hist_trans, f"Histogram Hasil [{status}]")

    plt.tight_layout()
    plt.show()


def display_dual_input_result(citra_a, citra_b, citra_hasil, judul_operasi):
    """
    Menampilkan citra A, citra B, dan citra hasil operasi bingkai berdampingan.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    pasangan = [
        (citra_a,    "Citra A"),
        (citra_b,    "Citra B"),
        (citra_hasil, f"Hasil: {judul_operasi}"),
    ]
    for ax, (citra, label) in zip(axes, pasangan):
        pil_img = ke_pil(citra)
        cmap = 'gray' if citra.mode == "L" else None
        ax.imshow(pil_img, cmap=cmap, vmin=0, vmax=255)
        ax.set_title(label)
        ax.axis('off')
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Prompt input
# ---------------------------------------------------------------------------

def prompt_int(message, min_val=None, max_val=None):
    """Meminta input integer dari user dengan validasi rentang & penanganan error."""
    while True:
        try:
            val = int(input(message))
            if min_val is not None and val < min_val:
                raise ValueError
            if max_val is not None and val > max_val:
                raise ValueError
            return val
        except ValueError:
            print("Input tidak valid, coba lagi.")


def prompt_float(message):
    """Meminta input float dari user dengan penanganan error."""
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Input tidak valid, masukkan angka desimal (misal 1.5).")


# ---------------------------------------------------------------------------
# Pemilihan citra kedua (untuk op_bingkai)
# ---------------------------------------------------------------------------

def select_second_image(citra_referensi):
    """
    Meminta user memilih citra kedua dari folder IMG_DIR.

    KOREKSI (Deviasi #2): jika ukuran atau mode A & B berbeda,
    potong ke area bersama (min lebar, min tinggi dari pojok kiri-atas),
    dan jika mode berbeda, konversi grayscale ke RGB dengan duplikasi kanal.
    """
    images = get_available_images()
    if not images:
        print("Tidak ada gambar lain yang tersedia di folder img/.")
        return None

    print("\n=== PILIH CITRA KEDUA ===")
    for idx, img_name in enumerate(images, 1):
        print(f"[{idx}] {img_name}")

    choice = prompt_int("Pilih nomor citra kedua (0 untuk batal): ", min_val=0, max_val=len(images))
    if choice == 0:
        return None

    citra_b = load_image(os.path.join(IMG_DIR, images[choice - 1]))

    # Samakan ukuran: potong ke area bersama
    crop_lebar  = min(citra_referensi.lebar,  citra_b.lebar)
    crop_tinggi = min(citra_referensi.tinggi, citra_b.tinggi)

    if crop_lebar != citra_b.lebar or crop_tinggi != citra_b.tinggi:
        print(f"Peringatan: ukuran citra kedua berbeda, dipotong menjadi "
              f"{crop_lebar}x{crop_tinggi} agar sesuai area citra pertama.")
        kanal_crop = []
        for c in range(len(citra_b.kanal)):
            kanal_crop.append([list(citra_b.kanal[c][y][:crop_lebar])
                               for y in range(crop_tinggi)])
        citra_b = Citra(crop_lebar, crop_tinggi, citra_b.mode, kanal_crop)

    # Samakan mode: jika berbeda konversi grayscale ke RGB
    if citra_referensi.mode != citra_b.mode:
        print(f"Peringatan: mode citra berbeda ({citra_referensi.mode} vs {citra_b.mode}), "
              f"grayscale dikonversi ke RGB.")
        if citra_b.mode == "L":
            kanal_rgb = [[list(baris) for baris in citra_b.kanal[0]] for _ in range(3)]
            citra_b = Citra(citra_b.lebar, citra_b.tinggi, "RGB", kanal_rgb)

    return citra_b
