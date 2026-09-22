"""
op_bingkai.py
Menu Operasi Berbasis Bingkai (Frame) / Operasi Multi Image:
Penggabungan citra (blending), Deteksi gerakan, dan Operasi Logika.

Semua operasi ini melibatkan 2 citra (A dan B) yang dioperasikan
titik per titik pada lokasi yang bersesuaian, sesuai materi kuliah
Pengolahan Citra (Idhawati Hestiningsih).
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import (
    # Menampilkan tiga citra: A, B, dan hasil operasi untuk memeriksa proses multi-image.
    display_dual_input_result,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    select_second_image,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    prompt_int,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    prompt_float,
# Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
)


# --- 1. Penggabungan Citra (Image Blending) ---

# Fungsi image blending: C = wa*A + wb*B.
def blend_images(img_a, img_b, wa, wb):
    """C(x,y) = wa * A(x,y) + wb * B(x,y), dengan wa + wb idealnya = 1."""
    # Materi: image blending memakai C(x,y) = wa*A(x,y) + wb*B(x,y), dengan bobot idealnya berjumlah 1.
    result = wa * img_a.astype(np.float32) + wb * img_b.astype(np.float32)
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.clip(result, 0, 255).astype(np.uint8)


# --- 2. Deteksi Gerakan ---

# Fungsi deteksi gerakan: mencari selisih nilai piksel antara citra A dan B.
def detect_motion(img_a, img_b):
    """
    C(x,y) = A(x,y) - B(x,y). Bagian yang tidak bergerak bernilai mendekati 0,
    bagian yang bergerak menghasilkan nilai berbeda dari 0.
    Menggunakan nilai absolut agar hasil selisih mudah divisualisasikan.
    """
    # Materi: deteksi gerakan dilakukan dengan C(x,y) = A(x,y) - B(x,y) pada lokasi yang bersesuaian.
    diff = img_a.astype(np.int16) - img_b.astype(np.int16)
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.abs(diff).astype(np.uint8)


# --- 3. Operasi Logika ---

# Mendefinisikan fungsi _to_binary untuk bagian tertentu dari program.
def _to_binary(img_array):
    """Bantu: pastikan citra dalam bentuk biner 0/1 untuk operasi logika."""
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_array.ndim == 3:
    # Konversi RGB ke grayscale menggunakan pembobot luminance; kode memakai 0.299, 0.587, 0.114.
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        gray = img_array
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (gray >= 128).astype(np.uint8)


# Operasi logika AND pada citra biner.
def logic_and(img_a, img_b):
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (_to_binary(img_a) & _to_binary(img_b)) * 255


# Operasi logika OR pada citra biner.
def logic_or(img_a, img_b):
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (_to_binary(img_a) | _to_binary(img_b)) * 255


# Operasi logika XOR pada citra biner.
def logic_xor(img_a, img_b):
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (_to_binary(img_a) ^ _to_binary(img_b)) * 255


# Operasi SUB: A-B, tetapi hasil negatif diganti 0.
def logic_sub(img_a, img_b):
    """A SUB B = A - B jika A >= B, else 0 (pada representasi biner 0/1)."""
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    a, b = _to_binary(img_a).astype(np.int16), _to_binary(img_b).astype(np.int16)
    # Materi: A SUB B mengikuti A-B jika A>=B dan 0 jika A<B.
    result = np.where(a >= b, a - b, 0)
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (result * 255).astype(np.uint8)


# Operasi logika NOT terhadap citra A.
def logic_not(img_a):
    """C(x,y) = NOT A(x,y) pada representasi biner."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return (1 - _to_binary(img_a)) * 255


# --- Menu ---

# Mendefinisikan fungsi _submenu_blending untuk bagian tertentu dari program.
def _submenu_blending(img_a, img_b):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    wa = prompt_float("Masukkan bobot wa untuk citra A (misal 0.4): ")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    wb = prompt_float("Masukkan bobot wb untuk citra B (misal 0.6, idealnya wa+wb=1): ")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = blend_images(img_a, img_b, wa, wb)
    # Menampilkan tiga citra: A, B, dan hasil operasi untuk memeriksa proses multi-image.
    display_dual_input_result(img_a, img_b, result, f"Blending (wa={wa}, wb={wb})")


# Mendefinisikan fungsi _submenu_motion untuk bagian tertentu dari program.
def _submenu_motion(img_a, img_b):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = detect_motion(img_a, img_b)
    # Menampilkan tiga citra: A, B, dan hasil operasi untuk memeriksa proses multi-image.
    display_dual_input_result(img_a, img_b, result, "Deteksi Gerakan (A - B)")


# Mendefinisikan fungsi _submenu_logic untuk bagian tertentu dari program.
def _submenu_logic(img_a, img_b):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n[1] AND  [2] OR  [3] XOR  [4] SUB  [5] NOT (hanya citra A)")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("Pilih operasi logika: ", min_val=1, max_val=5)

    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 1:
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        result, label = logic_and(img_a, img_b), "A AND B"
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 2:
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        result, label = logic_or(img_a, img_b), "A OR B"
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 3:
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        result, label = logic_xor(img_a, img_b), "A XOR B"
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 4:
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        result, label = logic_sub(img_a, img_b), "A SUB B"
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
        result, label = logic_not(img_a), "NOT A"

    # Menampilkan tiga citra: A, B, dan hasil operasi untuk memeriksa proses multi-image.
    display_dual_input_result(img_a, img_b, result, label)


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n--- OPERASI BERBASIS BINGKAI (Multi Image) ---")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("Operasi ini membutuhkan citra kedua (citra A = citra yang sedang aktif).")

    # Meminta citra B dan menyesuaikannya untuk operasi berbasis bingkai.
    img_b = select_second_image(original_img.shape)
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_b is None:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print("Dibatalkan: citra kedua tidak dipilih.")
    # Menghentikan fungsi tanpa menghasilkan nilai baru.
        return

    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n[1] Penggabungan Citra (Image Blending)")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[2] Deteksi Gerakan")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[3] Operasi Logika (AND/OR/XOR/SUB/NOT)")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("Pilih sub-operasi: ", min_val=1, max_val=3)

    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 1:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_blending(original_img, img_b)
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 2:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_motion(original_img, img_b)
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 3:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_logic(original_img, img_b)
