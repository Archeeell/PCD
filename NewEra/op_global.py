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

import numpy as np
from NewEra.utils import display_comparison


def _equalize_channel(channel, max_level=255):
    """
    Melakukan histogram equalization pada satu kanal (2D array skala keabuan).
    max_level = nilai keabuan tertinggi yang dipakai sebagai (2^k - 1) pada rumus.
    Untuk citra 8-bit sesungguhnya, max_level = 255 (default).
    """
    h, w = channel.shape

    hist, _ = np.histogram(channel, bins=max_level + 1, range=(0, max_level + 1))
    cumulative = np.cumsum(hist)

    # Ko = floor( Ci * (2^k - 1) / (w * h) ) -- lihat CATATAN PEMBULATAN di atas
    lookup_table = np.floor(cumulative * max_level / (w * h) + 1e-9).astype(np.uint8)

    return lookup_table[channel]


def histogram_equalization(img_array, max_level=255):
    """Menerapkan ekualisasi histogram. Untuk citra RGB, dilakukan per kanal."""
    if img_array.ndim == 2:
        return _equalize_channel(img_array, max_level)
    else:
        result = np.zeros_like(img_array)
        for c in range(img_array.shape[2]):
            result[:, :, c] = _equalize_channel(img_array[:, :, c], max_level)
        return result


def run(original_img):
    result = histogram_equalization(original_img)
    display_comparison(original_img, result, "Ekualisasi Histogram (Histogram Equalization)")
