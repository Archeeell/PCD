"""
op_histogram.py
Menu [1] Tampilkan Histogram Citra Asli Saja.
Tidak melakukan transformasi apa pun; hanya menampilkan citra asli
berdampingan dengan histogramnya sendiri (sebagai referensi/pembanding).
"""

# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    display_comparison(original_img, original_img, "Citra Asli (No Change)")
