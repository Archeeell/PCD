"""
op_contrast.py
Menu [3] Tingkatkan / Ubah Kontras.
Mengubah kontras dengan meregangkan/menekan nilai piksel di sekitar
titik pivot (default 128), dikalikan faktor kontras yang diberikan user.
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison, prompt_float


# Fungsi inti peningkatan/penurunan kontras menggunakan rumus Ko = G(Ki - P) + P.
def adjust_contrast(img_array, factor, pivot=128):
    # Materi: kontras memakai Ko = G(Ki - P) + P; factor berperan sebagai G dan pivot sebagai P.
    img_float = factor * (img_array.astype(np.float32) - pivot) + pivot
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.clip(img_float, 0, 255).astype(np.uint8)


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    factor = prompt_float(
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        "Masukkan faktor kontras (misal 1.5 untuk meningkatkan, 0.5 untuk menurunkan): "
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    )
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = adjust_contrast(original_img, factor)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Kontras (x{factor})")
