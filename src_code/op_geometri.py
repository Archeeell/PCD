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

import numpy as np
from NewEra.utils import display_comparison, prompt_int, prompt_float


# --- 1. Pencerminan (Flipping) ---

def flip_horizontal(img_array):
    """x' = w - 1 - x -> membalik kolom (kiri-kanan)."""
    return img_array[:, ::-1, ...] if img_array.ndim == 3 else img_array[:, ::-1]


def flip_vertical(img_array):
    """y' = h - 1 - y -> membalik baris (atas-bawah)."""
    return img_array[::-1, :, ...] if img_array.ndim == 3 else img_array[::-1, :]


def flip_combined(img_array):
    """Kombinasi pencerminan horisontal + vertikal."""
    return flip_vertical(flip_horizontal(img_array))


# --- 2. Rotasi (Rotating) ---

def rotate_90_cw(img_array):
    """Rotasi 1/4 putaran (90 derajat) searah jarum jam. Lebar & tinggi tertukar."""
    return np.rot90(img_array, k=-1)


def rotate_180_cw(img_array):
    """Rotasi 1/2 putaran (180 derajat) searah jarum jam."""
    return np.rot90(img_array, k=2)


def rotate_free(img_array, angle_degrees):
    """
    Rotasi bebas berlawanan arah jarum jam (CCW) sebesar angle_degrees,
    menggunakan rumus x' = x cos(t) + y sin(t), y' = -x sin(t) + y cos(t),
    dengan interpolasi nearest-neighbor sederhana dan ukuran kanvas baru
    w' = |w cos(t)| + |h sin(t)|, h' = |w sin(t)| + |h cos(t)|.
    """
    theta = np.radians(angle_degrees)
    h, w = img_array.shape[0], img_array.shape[1]

    new_w = int(abs(w * np.cos(theta)) + abs(h * np.sin(theta)))
    new_h = int(abs(w * np.sin(theta)) + abs(h * np.cos(theta)))

    if img_array.ndim == 3:
        result = np.zeros((new_h, new_w, img_array.shape[2]), dtype=np.uint8)
    else:
        result = np.zeros((new_h, new_w), dtype=np.uint8)

    cx_old, cy_old = w / 2, h / 2
    cx_new, cy_new = new_w / 2, new_h / 2

    # Untuk setiap piksel tujuan, cari piksel sumber (inverse mapping) agar tidak ada lubang.
    ys, xs = np.meshgrid(np.arange(new_h), np.arange(new_w), indexing='ij')
    x_rel = xs - cx_new
    y_rel = ys - cy_new

    # Inverse rotation (CW) untuk memetakan tujuan -> sumber
    src_x = x_rel * np.cos(theta) - y_rel * np.sin(theta) + cx_old
    src_y = x_rel * np.sin(theta) + y_rel * np.cos(theta) + cy_old

    src_x_round = np.round(src_x).astype(int)
    src_y_round = np.round(src_y).astype(int)

    valid = (src_x_round >= 0) & (src_x_round < w) & (src_y_round >= 0) & (src_y_round < h)

    result[ys[valid], xs[valid]] = img_array[src_y_round[valid], src_x_round[valid]]

    return result


# --- 3. Pemotongan (Cropping) ---

def crop_image(img_array, xl, yt, xr, yb):
    """x' = x - xL, y' = y - yT -> memotong area [xL:xR, yT:yB]."""
    return img_array[yt:yb, xl:xr, ...] if img_array.ndim == 3 else img_array[yt:yb, xl:xr]


# --- 4. Penskalaan (Scaling) ---

def scale_image(img_array, sh, sv):
    """
    x' = Sh * x, y' = Sv * y -> memperbesar/memperkecil citra.
    Menggunakan nearest-neighbor sesuai prinsip penyalinan piksel pada materi
    (misal zoom-in faktor 2 menyalin tiap piksel jadi 4 piksel).
    """
    h, w = img_array.shape[0], img_array.shape[1]
    new_w = max(1, int(round(w * sh)))
    new_h = max(1, int(round(h * sv)))

    src_x = np.clip((np.arange(new_w) / sh).astype(int), 0, w - 1)
    src_y = np.clip((np.arange(new_h) / sv).astype(int), 0, h - 1)

    return img_array[np.ix_(src_y, src_x)] if img_array.ndim == 2 else img_array[src_y][:, src_x]


# --- Menu ---

def _submenu_flip(original_img):
    print("\n[1] Horisontal  [2] Vertikal  [3] Kombinasi")
    choice = prompt_int("Pilih jenis pencerminan: ", min_val=1, max_val=3)
    if choice == 1:
        result = flip_horizontal(original_img)
        label = "Pencerminan Horisontal"
    elif choice == 2:
        result = flip_vertical(original_img)
        label = "Pencerminan Vertikal"
    else:
        result = flip_combined(original_img)
        label = "Pencerminan Kombinasi"
    display_comparison(original_img, result, label)


def _submenu_rotate(original_img):
    print("\n[1] 90 derajat CW  [2] 180 derajat CW  [3] Rotasi bebas (CCW)")
    choice = prompt_int("Pilih jenis rotasi: ", min_val=1, max_val=3)
    if choice == 1:
        result = rotate_90_cw(original_img)
        label = "Rotasi 90 CW"
    elif choice == 2:
        result = rotate_180_cw(original_img)
        label = "Rotasi 180 CW"
    else:
        angle = prompt_float("Masukkan sudut rotasi CCW dalam derajat (misal 25): ")
        result = rotate_free(original_img, angle)
        label = f"Rotasi Bebas ({angle} CCW)"
    display_comparison(original_img, result, label)


def _submenu_crop(original_img):
    h, w = original_img.shape[0], original_img.shape[1]
    print(f"\nUkuran citra saat ini: {w}x{h} (lebar x tinggi)")
    xl = prompt_int(f"Masukkan xL (0 s.d. {w - 2}): ", min_val=0, max_val=w - 2)
    xr = prompt_int(f"Masukkan xR ({xl + 1} s.d. {w}): ", min_val=xl + 1, max_val=w)
    yt = prompt_int(f"Masukkan yT (0 s.d. {h - 2}): ", min_val=0, max_val=h - 2)
    yb = prompt_int(f"Masukkan yB ({yt + 1} s.d. {h}): ", min_val=yt + 1, max_val=h)
    result = crop_image(original_img, xl, yt, xr, yb)
    display_comparison(original_img, result, f"Cropping ({xl},{yt})-({xr},{yb})")


def _submenu_scale(original_img):
    sh = prompt_float("Masukkan faktor skala horisontal Sh (misal 2 untuk 2x, 0.5 untuk setengah): ")
    sv = prompt_float("Masukkan faktor skala vertikal Sv (misal 2 untuk 2x, 0.5 untuk setengah): ")
    result = scale_image(original_img, sh, sv)
    display_comparison(original_img, result, f"Scaling (Sh={sh}, Sv={sv})")


def run(original_img):
    print("\n--- OPERASI GEOMETRI ---")
    print("[1] Pencerminan (Flipping)")
    print("[2] Rotasi (Rotating)")
    print("[3] Pemotongan (Cropping)")
    print("[4] Penskalaan (Scaling)")
    choice = prompt_int("Pilih sub-operasi geometri: ", min_val=1, max_val=4)

    if choice == 1:
        _submenu_flip(original_img)
    elif choice == 2:
        _submenu_rotate(original_img)
    elif choice == 3:
        _submenu_crop(original_img)
    elif choice == 4:
        _submenu_scale(original_img)
