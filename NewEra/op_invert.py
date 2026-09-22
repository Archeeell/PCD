"""
op_invert.py
Menu [4] Negasi / Inversi Citra.
Membalik nilai setiap piksel: hasil = 255 - nilai_asli.
"""

# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison


# Fungsi inti negasi: membalik intensitas piksel terhadap nilai maksimum 255.
def invert_image(img_array):
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (255 - img_array).astype("uint8")


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = invert_image(original_img)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, "Negasi (Inversi)")
