"""
op_threshold.py
Menu [6] Thresholding (Pengambangan).
Mengubah citra menjadi biner (0 atau 255) berdasarkan nilai ambang batas.
Citra RGB akan dikonversi ke grayscale terlebih dahulu sebelum diambang.
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.op_color_convert import convert_color
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison, prompt_int


# Fungsi inti thresholding: menentukan keluaran biner berdasarkan nilai ambang.
def apply_threshold(img_array, threshold_val):
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_array.ndim == 3:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        gray = convert_color(img_array)
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        gray = img_array
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.where(gray >= threshold_val, 255, 0).astype(np.uint8)


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    thresh = prompt_int("Masukkan nilai ambang batas threshold (0-255): ",
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
                         min_val=0, max_val=255)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = apply_threshold(original_img, thresh)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Thresholding (T={thresh})")
