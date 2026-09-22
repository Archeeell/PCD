"""
op_color_convert.py
Menu [5] Konversi Ruang Warna (RGB <-> Grayscale).
- RGB -> Grayscale: menggunakan bobot luminance standar (0.299R + 0.587G + 0.114B).
- Grayscale -> RGB: menduplikasi kanal tunggal menjadi 3 kanal identik.
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison


# Fungsi konversi ruang warna: RGB menjadi grayscale atau grayscale menjadi RGB.
def convert_color(img_array):
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_array.ndim == 3:
    # Konversi RGB ke grayscale menggunakan pembobot luminance; kode memakai 0.299, 0.587, 0.114.
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return np.clip(gray, 0, 255).astype(np.uint8)
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return np.stack([img_array] * 3, axis=-1)


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = convert_color(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    target = "Grayscale" if original_img.ndim == 3 else "RGB"
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Konversi ke {target}")
