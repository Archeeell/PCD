"""
utils.py
Berisi fungsi-fungsi bantu yang dipakai bersama oleh semua modul operasi:
- Membaca daftar gambar & memuat gambar
- Menghitung histogram
- Membandingkan histogram
- Menampilkan hasil perbandingan (citra asli vs hasil transformasi)
"""

# Mendukung alur pemrosesan citra pada fungsi ini.
import os
# Mendukung alur pemrosesan citra pada fungsi ini.
import numpy as np
# Mendukung alur pemrosesan citra pada fungsi ini.
from PIL import Image
# Mendukung alur pemrosesan citra pada fungsi ini.
import matplotlib.pyplot as plt

# Folder default tempat program mencari file citra input.
IMG_DIR = "img"


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def get_available_images():
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Mengembalikan daftar nama file gambar yang tersedia di folder IMG_DIR."""
    # Mengecek apakah folder input citra tersedia sebelum membaca isinya.
    if not os.path.exists(IMG_DIR):
        # Membuat folder input secara otomatis jika belum ada.
        os.makedirs(IMG_DIR)
        # Mengembalikan hasil fungsi kepada pemanggil.
        return []
    # Menentukan format file citra yang dapat diproses oleh program.
    valid_exts = ('.bmp', '.png', '.jpg', '.jpeg', '.webp', '.tiff')
    # Mengambil daftar file dari folder citra.
    return [f for f in os.listdir(IMG_DIR) if f.lower().endswith(valid_exts)]


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def load_image(filepath):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Memuat gambar dari path dan mengembalikannya sebagai array numpy (uint8)."""
    # Membuka file citra menjadi objek gambar Pillow.
    img = Image.open(filepath)
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if img.mode not in ('L', 'RGB'):
        # Mengubah mode gambar yang tidak didukung menjadi RGB.
        img = img.convert('RGB')
    # Merepresentasikan citra digital sebagai matriks/array NumPy dengan intensitas 8-bit 0–255.
    return np.array(img, dtype=np.uint8)


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def compute_histogram(img_array):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Menghitung histogram citra. Grayscale -> {'gray': ...}, RGB -> {'r','g','b': ...}."""
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if img_array.ndim == 2:
        # Menghitung frekuensi kemunculan tiap tingkat intensitas, sesuai konsep histogram pada materi.
        hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
        # Mengembalikan histogram citra grayscale.
        return {'gray': hist}
    # Memilih jalur pemrosesan berdasarkan kondisi.
    elif img_array.ndim == 3:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        hist_r, _ = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))
        # Mendukung alur pemrosesan citra pada fungsi ini.
        hist_g, _ = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))
        # Mendukung alur pemrosesan citra pada fungsi ini.
        hist_b, _ = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))
        # Mengembalikan histogram masing-masing kanal R, G, dan B.
        return {'r': hist_r, 'g': hist_g, 'b': hist_b}


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def are_histograms_identical(hist1, hist2):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Mengecek apakah dua histogram identik (jumlah kunci dan nilai sama persis)."""
    # Memastikan dua histogram mempunyai jenis kanal yang sama.
    if set(hist1.keys()) != set(hist2.keys()):
        # Mengembalikan hasil fungsi kepada pemanggil.
        return False
    # Mengulang proses untuk elemen citra atau data yang sedang diperiksa.
    for k in hist1:
        # Membandingkan frekuensi tiap tingkat intensitas untuk menentukan apakah histogram identik.
        if not np.array_equal(hist1[k], hist2[k]):
            # Mengembalikan hasil fungsi kepada pemanggil.
            return False
    # Mengembalikan hasil fungsi kepada pemanggil.
    return True


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def display_comparison(original, transformed, title_operation):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Menampilkan 2x2 grid: citra asli, citra hasil, histogram asli, histogram hasil."""
    # Mendukung alur pemrosesan citra pada fungsi ini.
    hist_orig = compute_histogram(original)
    # Mendukung alur pemrosesan citra pada fungsi ini.
    hist_trans = compute_histogram(transformed)
    # Mendukung alur pemrosesan citra pada fungsi ini.
    identical = are_histograms_identical(hist_orig, hist_trans)

    # Membuat tampilan 2x2 untuk input, output, histogram input, dan histogram output.
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Tampilan Citra Asli
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if original.ndim == 2:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[0, 0].imshow(original, cmap='gray', vmin=0, vmax=255)
    # Memilih jalur pemrosesan berdasarkan kondisi.
    else:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[0, 0].imshow(original)
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[0, 0].set_title("Citra Asli")
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[0, 0].axis('off')

    # Tampilan Citra Transformasi
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if transformed.ndim == 2:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[0, 1].imshow(transformed, cmap='gray', vmin=0, vmax=255)
    # Memilih jalur pemrosesan berdasarkan kondisi.
    else:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[0, 1].imshow(transformed)
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[0, 1].set_title(f"Hasil: {title_operation}")
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[0, 1].axis('off')

    # Plot Histogram Asli
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if 'gray' in hist_orig:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 0].plot(hist_orig['gray'], color='black', label='Grayscale')
    # Memilih jalur pemrosesan berdasarkan kondisi.
    else:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 0].plot(hist_orig['r'], color='red', label='Red')
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 0].plot(hist_orig['g'], color='green', label='Green')
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 0].plot(hist_orig['b'], color='blue', label='Blue')
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 0].set_title("Histogram Citra Asli")
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 0].set_xlim([0, 255])
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 0].legend()
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Plot Histogram Transformasi
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if 'gray' in hist_trans:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 1].plot(hist_trans['gray'], color='black', label='Grayscale')
    # Memilih jalur pemrosesan berdasarkan kondisi.
    else:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 1].plot(hist_trans['r'], color='red', label='Red')
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 1].plot(hist_trans['g'], color='green', label='Green')
        # Mendukung alur pemrosesan citra pada fungsi ini.
        axes[1, 1].plot(hist_trans['b'], color='blue', label='Blue')

    # Mendukung alur pemrosesan citra pada fungsi ini.
    status_text = "IDENTIK (Citra Sama)" if identical else "TIDAK IDENTIK"
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 1].set_title(f"Histogram Hasil [{status_text}]")
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 1].set_xlim([0, 255])
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 1].legend()
    # Mendukung alur pemrosesan citra pada fungsi ini.
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    # Mendukung alur pemrosesan citra pada fungsi ini.
    plt.tight_layout()
    # Menampilkan hasil visual kepada pengguna.
    plt.show()


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def prompt_int(message, min_val=None, max_val=None):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Meminta input integer dari user dengan validasi rentang & penanganan error."""
    # Mengulang pembacaan input sampai nilai yang valid diperoleh.
    while True:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        try:
            # Membaca masukan pengguna sebagai parameter operasi.
            val = int(input(message))
            # Memilih jalur pemrosesan berdasarkan kondisi.
            if min_val is not None and val < min_val:
                # Mendukung alur pemrosesan citra pada fungsi ini.
                raise ValueError
            # Memilih jalur pemrosesan berdasarkan kondisi.
            if max_val is not None and val > max_val:
                # Mendukung alur pemrosesan citra pada fungsi ini.
                raise ValueError
            # Mengembalikan hasil fungsi kepada pemanggil.
            return val
        # Mendukung alur pemrosesan citra pada fungsi ini.
        except ValueError:
            # Mendukung alur pemrosesan citra pada fungsi ini.
            print("Input tidak valid, coba lagi.")


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def prompt_float(message):
    # Mendukung alur pemrosesan citra pada fungsi ini.
    """Meminta input float dari user dengan penanganan error."""
    # Mengulang pembacaan input sampai nilai yang valid diperoleh.
    while True:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        try:
            # Membaca masukan pengguna sebagai parameter operasi.
            return float(input(message))
        # Mendukung alur pemrosesan citra pada fungsi ini.
        except ValueError:
            # Mendukung alur pemrosesan citra pada fungsi ini.
            print("Input tidak valid, masukkan angka desimal (misal 1.5).")


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def select_second_image(reference_shape):
    """
    Meminta user memilih citra kedua dari folder IMG_DIR untuk operasi
    berbasis bingkai (dua citra). Citra kedua akan otomatis di-resize
    (crop/pad sederhana) agar sesuai ukuran citra pertama bila berbeda.
    Mengembalikan array numpy citra kedua, atau None jika dibatalkan.
    """
    # Mendukung alur pemrosesan citra pada fungsi ini.
    images = get_available_images()
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if not images:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        print("Tidak ada gambar lain yang tersedia di folder img/.")
        # Mengembalikan hasil fungsi kepada pemanggil.
        return None

    # Mendukung alur pemrosesan citra pada fungsi ini.
    print("\n=== PILIH CITRA KEDUA ===")
    # Mengulang proses untuk elemen citra atau data yang sedang diperiksa.
    for idx, img_name in enumerate(images, 1):
        # Mendukung alur pemrosesan citra pada fungsi ini.
        print(f"[{idx}] {img_name}")

    # Mendukung alur pemrosesan citra pada fungsi ini.
    choice = prompt_int("Pilih nomor citra kedua (0 untuk batal): ", min_val=0, max_val=len(images))
    # Memilih jalur pemrosesan berdasarkan kondisi.
    if choice == 0:
        # Mengembalikan hasil fungsi kepada pemanggil.
        return None

    # Memuat citra B yang akan diproses pada operasi berbasis bingkai.
    second_img = load_image(os.path.join(IMG_DIR, images[choice - 1]))

    # Samakan dimensi tinggi x lebar dengan citra pertama (crop ke ukuran terkecil)
    # Menentukan ukuran target berdasarkan citra A.
    target_h, target_w = reference_shape[0], reference_shape[1]
    # Mendukung alur pemrosesan citra pada fungsi ini.
    h, w = second_img.shape[0], second_img.shape[1]
    # Memilih ukuran yang aman agar citra B tidak melebihi dimensi citra A.
    crop_h, crop_w = min(h, target_h), min(w, target_w)
    # Melakukan crop sederhana pada citra B agar operasi titik-per-titik dapat dilakukan pada ukuran yang sama.
    second_img = second_img[:crop_h, :crop_w]

    # Memilih jalur pemrosesan berdasarkan kondisi.
    if crop_h != target_h or crop_w != target_w:
        # Mendukung alur pemrosesan citra pada fungsi ini.
        print(f"Peringatan: ukuran citra kedua berbeda, dipotong menjadi {crop_w}x{crop_h} "
              # Mendukung alur pemrosesan citra pada fungsi ini.
              f"agar sesuai area citra pertama.")

    # Mengembalikan hasil fungsi kepada pemanggil.
    return second_img


# Mendefinisikan fungsi bantuan yang dipakai oleh modul-modul pengolahan citra.
def display_dual_input_result(img_a, img_b, result, title_operation):
    """
    Menampilkan citra A, citra B, dan citra hasil operasi berbasis bingkai
    (dipakai untuk blending, deteksi gerakan, operasi logika) berdampingan.
    """
    # Membuat tampilan tiga citra untuk operasi multi-image: A, B, dan hasil.
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))

    # Mengulang proses untuk elemen citra atau data yang sedang diperiksa.
    for ax, img, label in zip(axes, [img_a, img_b, result], ["Citra A", "Citra B", f"Hasil: {title_operation}"]):
        # Memilih jalur pemrosesan berdasarkan kondisi.
        if img.ndim == 2:
            # Menampilkan citra atau histogram pada panel Matplotlib.
            ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        # Memilih jalur pemrosesan berdasarkan kondisi.
        else:
            # Menampilkan citra atau histogram pada panel Matplotlib.
            ax.imshow(img)
        # Mendukung alur pemrosesan citra pada fungsi ini.
        ax.set_title(label)
        # Mendukung alur pemrosesan citra pada fungsi ini.
        ax.axis('off')

    # Mendukung alur pemrosesan citra pada fungsi ini.
    plt.tight_layout()
    # Menampilkan hasil visual kepada pengguna.
    plt.show()
