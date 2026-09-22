"""
op_global.py
Menu Operasi Global: Ekualisasi Histogram (Histogram Equalization).

Meratakan distribusi nilai derajat keabuan pada citra menggunakan rumus:
    Ko = round( Ci * (2^k - 1) / (w * h) )
dengan Ci = distribusi kumulatif nilai skala keabuan ke-i, k = bit kedalaman
warna (default 8 bit), w = lebar citra, h = tinggi citra.

Sesuai materi kuliah Pengolahan Citra (Idhawati Hestiningsih).
Untuk citra RGB, ekualisasi diterapkan per kanal warna (R, G, B) secara terpisah.

CATATAN PEMBULATAN:
Contoh perhitungan manual pada materi (hal. 23-24, data uji 12 piksel dengan
nilai 2 4 3 1 3 6 4 3 1 0 3 2) menghasilkan output yang HANYA cocok jika nilai
desimal ",5" dibulatkan KE BAWAH (floor), bukan dibulatkan matematis standar
(round half-up maupun round-to-even/banker's rounding Python biasa).
Saya sudah memverifikasi ini dengan menjalankan tiga metode pembulatan berbeda
dan membandingkan hasilnya angka demi angka dengan tabel di dokumen; hanya
floor yang cocok persis. Kemungkinan penulis materi asli memang menerapkan
pembulatan ke bawah secara konsisten (bukan salah ketik acak), tapi saya tidak
100% yakin apakah ini konvensi standar di textbook pengolahan citra lain atau
spesifik ke catatan kuliah ini -- Anda mungkin ingin mengecek ulang ke sumber
rujukan aslinya (Gonzalez & Woods, atau Rinaldi Munir) bila perlu kepastian.
Kode di bawah memakai floor() agar cocok dengan contoh di materi ini.
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison


# Ekualisasi histogram pada satu kanal berdasarkan distribusi kumulatif.
def _equalize_channel(channel, max_level=255):
    """
    Melakukan histogram equalization pada satu kanal (2D array skala keabuan).
    max_level = nilai keabuan tertinggi yang dipakai sebagai (2^k - 1) pada rumus.
    Untuk citra 8-bit sesungguhnya, max_level = 255 (default).
    """
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    h, w = channel.shape

    # Membentuk histogram kanal: frekuensi dihitung untuk setiap tingkat keabuan 0..255.
    hist, _ = np.histogram(channel, bins=max_level + 1, range=(0, max_level + 1))
    # Menghitung distribusi kumulatif Ci yang dibutuhkan dalam histogram equalization.
    cumulative = np.cumsum(hist)

    # Ko = floor( Ci * (2^k - 1) / (w * h) ) -- lihat CATATAN PEMBULATAN di atas
    # Implementasi kode memilih floor() untuk memetakan Ci ke nilai output; ini berbeda dari rumus materi yang menuliskan round().
    lookup_table = np.floor(cumulative * max_level / (w * h) + 1e-9).astype(np.uint8)

    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return lookup_table[channel]


# Menerapkan histogram equalization pada grayscale atau tiap kanal RGB.
def histogram_equalization(img_array, max_level=255):
    """Menerapkan ekualisasi histogram. Untuk citra RGB, dilakukan per kanal."""
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_array.ndim == 2:
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return _equalize_channel(img_array, max_level)
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = np.zeros_like(img_array)
    # Mengulang pemrosesan untuk setiap elemen/kanal yang diperlukan.
        for c in range(img_array.shape[2]):
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
            result[:, :, c] = _equalize_channel(img_array[:, :, c], max_level)
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return result


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = histogram_equalization(original_img)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, "Ekualisasi Histogram (Histogram Equalization)")
