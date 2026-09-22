"""
op_brightness.py
Menu [2] Modifikasi Brightness.
Menambah/mengurangi kecerahan citra dengan menggeser nilai setiap piksel
sebesar konstanta tertentu, lalu clip ke rentang valid [0, 255].
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison, prompt_int


# Fungsi inti modifikasi brightness: nilai intensitas setiap piksel digeser dengan konstanta C.
def adjust_brightness(img_array, value):
    # Materi: brightness memakai Ko = Ki + C; array diubah ke integer lebih lebar agar operasi tambah tidak overflow.
    img_int = img_array.astype(np.int16) + value
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.clip(img_int, 0, 255).astype(np.uint8)


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    val = prompt_int("Masukkan nilai pergeseran brightness (-255 s.d. 255): ",
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
            min_val=-255, max_val=255)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = adjust_brightness(original_img, val)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Brightness ({val:+d})")
