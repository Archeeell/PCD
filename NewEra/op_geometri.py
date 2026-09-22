"""
op_geometri.py
Menu Operasi Geometri: Pencerminan (flipping), Rotasi (rotating),
Pemotongan (cropping), dan Penskalaan (scaling).

Rumus mengikuti materi kuliah Pengolahan Citra (Idhawati Hestiningsih):
- Pencerminan horisontal : x' = w - 1 - x , y' = y
- Pencerminan vertikal   : y' = h - 1 - y , x' = x
- Pencerminan kombinasi  : x' = w - 1 - x , y' = h - 1 - y
- Rotasi 90 CW           : tukar lebar & tinggi, x' = w'-1-y, y' = x
- Rotasi 180 CW          : x' = w'-1-x, y' = h'-1-y
- Rotasi bebas (CCW)     : x' = x cos(t) + y sin(t), y' = -x sin(t) + y cos(t)
- Cropping               : x' = x - xL, y' = y - yT
- Scaling                : x' = Sh * x, y' = Sv * y
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import numpy as np
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import display_comparison, prompt_int, prompt_float


# --- 1. Pencerminan (Flipping) ---

# Fungsi pencerminan horizontal: koordinat x dibalik sedangkan y tetap.
def flip_horizontal(img_array):
    """x' = w - 1 - x -> membalik kolom (kiri-kanan)."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return img_array[:, ::-1, ...] if img_array.ndim == 3 else img_array[:, ::-1]


# Fungsi pencerminan vertikal: koordinat y dibalik sedangkan x tetap.
def flip_vertical(img_array):
    """y' = h - 1 - y -> membalik baris (atas-bawah)."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return img_array[::-1, :, ...] if img_array.ndim == 3 else img_array[::-1, :]


# Menggabungkan pencerminan horizontal dan vertikal sesuai rumus kombinasi pada materi.
def flip_combined(img_array):
    """Kombinasi pencerminan horisontal + vertikal."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return flip_vertical(flip_horizontal(img_array))


# --- 2. Rotasi (Rotating) ---

# Fungsi rotasi 90° searah jarum jam; ukuran lebar dan tinggi bertukar.
def rotate_90_cw(img_array):
    """Rotasi 1/4 putaran (90 derajat) searah jarum jam. Lebar & tinggi tertukar."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.rot90(img_array, k=-1)


# Fungsi rotasi 180° searah jarum jam.
def rotate_180_cw(img_array):
    """Rotasi 1/2 putaran (180 derajat) searah jarum jam."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return np.rot90(img_array, k=2)


# Fungsi rotasi bebas dengan sudut CCW dan inverse mapping nearest-neighbor.
def rotate_free(img_array, angle_degrees):
    """
    Rotasi bebas berlawanan arah jarum jam (CCW) sebesar angle_degrees,
    menggunakan rumus x' = x cos(t) + y sin(t), y' = -x sin(t) + y cos(t),
    dengan interpolasi nearest-neighbor sederhana dan ukuran kanvas baru
    w' = |w cos(t)| + |h sin(t)|, h' = |w sin(t)| + |h cos(t)|.
    """
    # Mengubah sudut derajat menjadi radian karena fungsi trigonometri NumPy menggunakan radian.
    theta = np.radians(angle_degrees)
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    h, w = img_array.shape[0], img_array.shape[1]

    # Materi: lebar kanvas baru dihitung dari w' = |w cos(theta)| + |h sin(theta)|.
    new_w = int(abs(w * np.cos(theta)) + abs(h * np.sin(theta)))
    # Materi: tinggi kanvas baru dihitung dari h' = |w sin(theta)| + |h cos(theta)|.
    new_h = int(abs(w * np.sin(theta)) + abs(h * np.cos(theta)))

    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if img_array.ndim == 3:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = np.zeros((new_h, new_w, img_array.shape[2]), dtype=np.uint8)
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = np.zeros((new_h, new_w), dtype=np.uint8)

    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    cx_old, cy_old = w / 2, h / 2
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    cx_new, cy_new = new_w / 2, new_h / 2

    # Untuk setiap piksel tujuan, cari piksel sumber (inverse mapping) agar tidak ada lubang.
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    ys, xs = np.meshgrid(np.arange(new_h), np.arange(new_w), indexing='ij')
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    x_rel = xs - cx_new
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    y_rel = ys - cy_new

    # Inverse rotation (CW) untuk memetakan tujuan -> sumber
    # Inverse mapping untuk mencari koordinat sumber yang memetakan ke setiap piksel tujuan setelah rotasi.
    src_x = x_rel * np.cos(theta) - y_rel * np.sin(theta) + cx_old
    # Melengkapi inverse mapping koordinat y untuk rotasi bebas.
    src_y = x_rel * np.sin(theta) + y_rel * np.cos(theta) + cy_old

    # Nearest-neighbor: koordinat sumber dibulatkan ke piksel terdekat agar setiap piksel keluaran mendapat nilai.
    src_x_round = np.round(src_x).astype(int)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    src_y_round = np.round(src_y).astype(int)

    # Memastikan koordinat sumber masih berada di dalam batas citra sebelum mengambil nilainya.
    valid = (src_x_round >= 0) & (src_x_round < w) & (src_y_round >= 0) & (src_y_round < h)

    # Menyalin piksel sumber yang valid ke posisi tujuan; inilah realisasi transformasi geometri pada matriks citra.
    result[ys[valid], xs[valid]] = img_array[src_y_round[valid], src_x_round[valid]]

    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return result


# --- 3. Pemotongan (Cropping) ---

# Fungsi cropping: mengambil area di antara koordinat kiri-atas dan kanan-bawah.
def crop_image(img_array, xl, yt, xr, yb):
    """x' = x - xL, y' = y - yT -> memotong area [xL:xR, yT:yB]."""
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return img_array[yt:yb, xl:xr, ...] if img_array.ndim == 3 else img_array[yt:yb, xl:xr]


# --- 4. Penskalaan (Scaling) ---

# Fungsi scaling/zooming berdasarkan faktor skala horizontal dan vertikal.
def scale_image(img_array, sh, sv):
    """
    x' = Sh * x, y' = Sv * y -> memperbesar/memperkecil citra.
    Menggunakan nearest-neighbor sesuai prinsip penyalinan piksel pada materi
    (misal zoom-in faktor 2 menyalin tiap piksel jadi 4 piksel).
    """
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    h, w = img_array.shape[0], img_array.shape[1]
    # Materi: ukuran hasil scaling berubah menjadi w' = Sh*w; dibulatkan agar ukuran piksel berupa integer.
    new_w = max(1, int(round(w * sh)))
    # Materi: ukuran hasil scaling berubah menjadi h' = Sv*h; dibulatkan agar ukuran piksel berupa integer.
    new_h = max(1, int(round(h * sv)))

    # Reverse mapping scaling: setiap koordinat piksel hasil dipetakan kembali ke koordinat sumber berdasarkan faktor Sh.
    src_x = np.clip((np.arange(new_w) / sh).astype(int), 0, w - 1)
    # Reverse mapping scaling: setiap koordinat piksel hasil dipetakan kembali ke koordinat sumber berdasarkan faktor Sv.
    src_y = np.clip((np.arange(new_h) / sv).astype(int), 0, h - 1)

    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return img_array[np.ix_(src_y, src_x)] if img_array.ndim == 2 else img_array[src_y][:, src_x]


# --- Menu ---

# Mendefinisikan fungsi _submenu_flip untuk bagian tertentu dari program.
def _submenu_flip(original_img):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n[1] Horisontal  [2] Vertikal  [3] Kombinasi")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("Pilih jenis pencerminan: ", min_val=1, max_val=3)
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 1:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = flip_horizontal(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = "Pencerminan Horisontal"
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 2:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = flip_vertical(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = "Pencerminan Vertikal"
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = flip_combined(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = "Pencerminan Kombinasi"
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, label)


# Mendefinisikan fungsi _submenu_rotate untuk bagian tertentu dari program.
def _submenu_rotate(original_img):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n[1] 90 derajat CW  [2] 180 derajat CW  [3] Rotasi bebas (CCW)")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("Pilih jenis rotasi: ", min_val=1, max_val=3)
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 1:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = rotate_90_cw(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = "Rotasi 90 CW"
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 2:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = rotate_180_cw(original_img)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = "Rotasi 180 CW"
    # Menangani kasus ketika kondisi sebelumnya tidak terpenuhi.
    else:
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        angle = prompt_float("Masukkan sudut rotasi CCW dalam derajat (misal 25): ")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        result = rotate_free(original_img, angle)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        label = f"Rotasi Bebas ({angle} CCW)"
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, label)


# Mendefinisikan fungsi _submenu_crop untuk bagian tertentu dari program.
def _submenu_crop(original_img):
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    h, w = original_img.shape[0], original_img.shape[1]
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print(f"\nUkuran citra saat ini: {w}x{h} (lebar x tinggi)")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    xl = prompt_int(f"Masukkan xL (0 s.d. {w - 2}): ", min_val=0, max_val=w - 2)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    xr = prompt_int(f"Masukkan xR ({xl + 1} s.d. {w}): ", min_val=xl + 1, max_val=w)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    yt = prompt_int(f"Masukkan yT (0 s.d. {h - 2}): ", min_val=0, max_val=h - 2)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    yb = prompt_int(f"Masukkan yB ({yt + 1} s.d. {h}): ", min_val=yt + 1, max_val=h)
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = crop_image(original_img, xl, yt, xr, yb)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Cropping ({xl},{yt})-({xr},{yb})")


# Mendefinisikan fungsi _submenu_scale untuk bagian tertentu dari program.
def _submenu_scale(original_img):
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    sh = prompt_float("Masukkan faktor skala horisontal Sh (misal 2 untuk 2x, 0.5 untuk setengah): ")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    sv = prompt_float("Masukkan faktor skala vertikal Sv (misal 2 untuk 2x, 0.5 untuk setengah): ")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    result = scale_image(original_img, sh, sv)
    # Menampilkan perbandingan input dan hasil sekaligus histogram keduanya untuk memvisualisasikan efek operasi.
    display_comparison(original_img, result, f"Scaling (Sh={sh}, Sv={sv})")


# Mendefinisikan fungsi run untuk bagian tertentu dari program.
def run(original_img):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("\n--- OPERASI GEOMETRI ---")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[1] Pencerminan (Flipping)")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[2] Rotasi (Rotating)")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[3] Pemotongan (Cropping)")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("[4] Penskalaan (Scaling)")
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("Pilih sub-operasi geometri: ", min_val=1, max_val=4)

    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 1:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_flip(original_img)
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 2:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_rotate(original_img)
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 3:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_crop(original_img)
    # Memeriksa alternatif kondisi berikutnya.
    elif choice == 4:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        _submenu_scale(original_img)
