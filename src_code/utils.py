"""
utils.py
Berisi fungsi-fungsi bantu yang dipakai bersama oleh semua modul operasi:
- Membaca daftar gambar & memuat gambar
- Menghitung histogram
- Membandingkan histogram
- Menampilkan hasil perbandingan (citra asli vs hasil transformasi)
"""

import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

IMG_DIR = "img"


def get_available_images():
    """Mengembalikan daftar nama file gambar yang tersedia di folder IMG_DIR."""
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        return []
    valid_exts = ('.bmp', '.png', '.jpg', '.jpeg', '.webp', '.tiff')
    return [f for f in os.listdir(IMG_DIR) if f.lower().endswith(valid_exts)]


def load_image(filepath):
    """Memuat gambar dari path dan mengembalikannya sebagai array numpy (uint8)."""
    img = Image.open(filepath)
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    return np.array(img, dtype=np.uint8)


def compute_histogram(img_array):
    """Menghitung histogram citra. Grayscale -> {'gray': ...}, RGB -> {'r','g','b': ...}."""
    if img_array.ndim == 2:
        hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
        return {'gray': hist}
    elif img_array.ndim == 3:
        hist_r, _ = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))
        hist_g, _ = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))
        hist_b, _ = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))
        return {'r': hist_r, 'g': hist_g, 'b': hist_b}


def are_histograms_identical(hist1, hist2):
    """Mengecek apakah dua histogram identik (jumlah kunci dan nilai sama persis)."""
    if set(hist1.keys()) != set(hist2.keys()):
        return False
    for k in hist1:
        if not np.array_equal(hist1[k], hist2[k]):
            return False
    return True


def display_comparison(original, transformed, title_operation):
    """Menampilkan 2x2 grid: citra asli, citra hasil, histogram asli, histogram hasil."""
    hist_orig = compute_histogram(original)
    hist_trans = compute_histogram(transformed)
    identical = are_histograms_identical(hist_orig, hist_trans)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # Tampilan Citra Asli
    if original.ndim == 2:
        axes[0, 0].imshow(original, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 0].imshow(original)
    axes[0, 0].set_title("Citra Asli")
    axes[0, 0].axis('off')

    # Tampilan Citra Transformasi
    if transformed.ndim == 2:
        axes[0, 1].imshow(transformed, cmap='gray', vmin=0, vmax=255)
    else:
        axes[0, 1].imshow(transformed)
    axes[0, 1].set_title(f"Hasil: {title_operation}")
    axes[0, 1].axis('off')

    # Plot Histogram Asli
    if 'gray' in hist_orig:
        axes[1, 0].plot(hist_orig['gray'], color='black', label='Grayscale')
    else:
        axes[1, 0].plot(hist_orig['r'], color='red', label='Red')
        axes[1, 0].plot(hist_orig['g'], color='green', label='Green')
        axes[1, 0].plot(hist_orig['b'], color='blue', label='Blue')
    axes[1, 0].set_title("Histogram Citra Asli")
    axes[1, 0].set_xlim([0, 255])
    axes[1, 0].legend()
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Plot Histogram Transformasi
    if 'gray' in hist_trans:
        axes[1, 1].plot(hist_trans['gray'], color='black', label='Grayscale')
    else:
        axes[1, 1].plot(hist_trans['r'], color='red', label='Red')
        axes[1, 1].plot(hist_trans['g'], color='green', label='Green')
        axes[1, 1].plot(hist_trans['b'], color='blue', label='Blue')

    status_text = "IDENTIK (Citra Sama)" if identical else "TIDAK IDENTIK"
    axes[1, 1].set_title(f"Histogram Hasil [{status_text}]")
    axes[1, 1].set_xlim([0, 255])
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()


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


def select_second_image(reference_shape):
    """
    Meminta user memilih citra kedua dari folder IMG_DIR untuk operasi
    berbasis bingkai (dua citra). Citra kedua akan otomatis di-resize
    (crop/pad sederhana) agar sesuai ukuran citra pertama bila berbeda.
    Mengembalikan array numpy citra kedua, atau None jika dibatalkan.
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

    second_img = load_image(os.path.join(IMG_DIR, images[choice - 1]))

    # Samakan dimensi tinggi x lebar dengan citra pertama (crop ke ukuran terkecil)
    target_h, target_w = reference_shape[0], reference_shape[1]
    h, w = second_img.shape[0], second_img.shape[1]
    crop_h, crop_w = min(h, target_h), min(w, target_w)
    second_img = second_img[:crop_h, :crop_w]

    if crop_h != target_h or crop_w != target_w:
        print(f"Peringatan: ukuran citra kedua berbeda, dipotong menjadi {crop_w}x{crop_h} "
              f"agar sesuai area citra pertama.")

    return second_img


def display_dual_input_result(img_a, img_b, result, title_operation):
    """
    Menampilkan citra A, citra B, dan citra hasil operasi berbasis bingkai
    (dipakai untuk blending, deteksi gerakan, operasi logika) berdampingan.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 5))

    for ax, img, label in zip(axes, [img_a, img_b, result], ["Citra A", "Citra B", f"Hasil: {title_operation}"]):
        if img.ndim == 2:
            ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        else:
            ax.imshow(img)
        ax.set_title(label)
        ax.axis('off')

    plt.tight_layout()
    plt.show()
