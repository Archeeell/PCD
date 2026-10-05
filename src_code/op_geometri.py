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

import math
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong,
                                display_comparison, prompt_int, prompt_float, run_standalone)
else:
    from .utils import (Citra, buat_kosong,
                        display_comparison, prompt_int, prompt_float, run_standalone)


# --- 1. Pencerminan (Flipping) ---

def flip_horizontal(citra):
    """x' = w - 1 - x -> membalik kolom (kiri-kanan)."""
    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    w = citra.lebar
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(citra.tinggi):
            src_row = k_src[y]
            dst_row = k_dst[y]
            for x in range(w):
                dst_row[x] = src_row[w - 1 - x]
    return hasil


def flip_vertical(citra):
    """y' = h - 1 - y -> membalik baris (atas-bawah)."""
    hasil = buat_kosong(citra.lebar, citra.tinggi, citra.mode)
    h = citra.tinggi
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(h):
            dst_row = k_dst[y]
            src_row = k_src[h - 1 - y]
            for x in range(citra.lebar):
                dst_row[x] = src_row[x]
    return hasil


def flip_combined(citra):
    """Kombinasi pencerminan horisontal + vertikal."""
    return flip_vertical(flip_horizontal(citra))


# --- 2. Rotasi (Rotating) ---

def rotate_90_cw(citra):
    """
    Rotasi 1/4 putaran (90 derajat) searah jarum jam (sesuai np.rot90(k=-1)).
    Dimensi baru: lebar_baru = tinggi_src, tinggi_baru = lebar_src.
    Rumus inverse: dst[y_dst=x_src][x_dst=h_src-1-y_src] = src[y_src][x_src].
    """
    # np.rot90(k=-1) mengubah (tinggi, lebar) -> (lebar, tinggi)
    lebar_baru  = citra.tinggi   # kolom baru = baris lama
    tinggi_baru = citra.lebar    # baris baru = kolom lama
    hasil = buat_kosong(lebar_baru, tinggi_baru, citra.mode)
    h_src = citra.tinggi
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y_src in range(citra.tinggi):
            src_row = k_src[y_src]
            x_dst = h_src - 1 - y_src   # kolom tujuan
            for x_src in range(citra.lebar):
                y_dst = x_src            # baris tujuan
                k_dst[y_dst][x_dst] = src_row[x_src]
    return hasil


def rotate_180_cw(citra):
    """
    Rotasi 1/2 putaran (180 derajat). Rumus: x' = w-1-x, y' = h-1-y.
    (sesuai np.rot90(k=2))
    """
    w, h = citra.lebar, citra.tinggi
    hasil = buat_kosong(w, h, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(h):
            src_row = k_src[y]
            dst_row = k_dst[h - 1 - y]
            for x in range(w):
                dst_row[w - 1 - x] = src_row[x]
    return hasil


def rotate_free(citra, angle_degrees):
    """
    Rotasi bebas berlawanan arah jarum jam (CCW) sebesar angle_degrees.
    Menggunakan inverse mapping dengan nearest-neighbor dan padding hitam.
    Ukuran kanvas: new_w = int(...), new_h = int(...) (truncation).
    Koordinat sumber dibulatkan dengan round() (half-to-even seperti np.round).
    Piksel di luar batas sumber = hitam (0).
    """
    theta = math.radians(angle_degrees)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    h, w  = citra.tinggi, citra.lebar

    new_w = int(abs(w * cos_t) + abs(h * sin_t))
    new_h = int(abs(w * sin_t) + abs(h * cos_t))

    hasil = buat_kosong(new_w, new_h, citra.mode)

    cx_old, cy_old = w / 2, h / 2
    cx_new, cy_new = new_w / 2, new_h / 2

    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y_dst in range(new_h):
            dst_row = k_dst[y_dst]
            y_rel = y_dst - cy_new
            for x_dst in range(new_w):
                x_rel = x_dst - cx_new
                # Inverse rotation (CW) untuk memetakan tujuan -> sumber
                src_x = x_rel * cos_t - y_rel * (-sin_t) + cx_old
                src_y = x_rel * (-sin_t) + y_rel * cos_t + cy_old
                # numpy 'reflect' round() = half-to-even (Python built-in round)
                src_xi = round(src_x)
                src_yi = round(src_y)
                if 0 <= src_xi < w and 0 <= src_yi < h:
                    dst_row[x_dst] = k_src[src_yi][src_xi]
                # else: tetap 0 (hitam)
    return hasil


# --- 3. Pemotongan (Cropping) ---

def crop_image(citra, xl, yt, xr, yb):
    """x' = x - xL, y' = y - yT -> memotong area [xL:xR) x [yT:yB)."""
    new_w = xr - xl
    new_h = yb - yt
    hasil = buat_kosong(new_w, new_h, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y in range(new_h):
            src_row = k_src[yt + y]
            dst_row = k_dst[y]
            for x in range(new_w):
                dst_row[x] = src_row[xl + x]
    return hasil


# --- 4. Penskalaan (Scaling) ---

def scale_image(citra, sh, sv):
    """
    x' = Sh * x, y' = Sv * y -> memperbesar/memperkecil citra.
    Nearest-neighbor: sumber = int(x/Sh) diklem ke w-1.
    new_w = max(1, int(round(w*Sh))), dst[y][x] = src[int(y/Sv)][int(x/Sh)].
    """
    h, w  = citra.tinggi, citra.lebar
    new_w = max(1, int(round(w * sh)))
    new_h = max(1, int(round(h * sv)))

    # Hitung indeks sumber untuk setiap posisi tujuan (sekali, efisien)
    src_x = [min(int(x / sh), w - 1) for x in range(new_w)]
    src_y = [min(int(y / sv), h - 1) for y in range(new_h)]

    hasil = buat_kosong(new_w, new_h, citra.mode)
    for c in range(len(citra.kanal)):
        k_src = citra.kanal[c]
        k_dst = hasil.kanal[c]
        for y_dst in range(new_h):
            src_row = k_src[src_y[y_dst]]
            dst_row = k_dst[y_dst]
            for x_dst in range(new_w):
                dst_row[x_dst] = src_row[src_x[x_dst]]
    return hasil


# --- Menu ---

def _submenu_flip(original_img):
    print("\n[1] Horisontal  [2] Vertikal  [3] Kombinasi")
    choice = prompt_int("Pilih jenis pencerminan: ", min_val=1, max_val=3)
    if choice == 1:
        result, label = flip_horizontal(original_img), "Pencerminan Horisontal"
    elif choice == 2:
        result, label = flip_vertical(original_img),   "Pencerminan Vertikal"
    else:
        result, label = flip_combined(original_img),   "Pencerminan Kombinasi"
    display_comparison(original_img, result, label)


def _submenu_rotate(original_img):
    print("\n[1] 90 derajat CW  [2] 180 derajat CW  [3] Rotasi bebas (CCW)")
    choice = prompt_int("Pilih jenis rotasi: ", min_val=1, max_val=3)
    if choice == 1:
        result, label = rotate_90_cw(original_img),  "Rotasi 90 CW"
    elif choice == 2:
        result, label = rotate_180_cw(original_img), "Rotasi 180 CW"
    else:
        angle = prompt_float("Masukkan sudut rotasi CCW dalam derajat (misal 25): ")
        result = rotate_free(original_img, angle)
        label  = f"Rotasi Bebas ({angle} CCW)"
    display_comparison(original_img, result, label)


def _submenu_crop(original_img):
    h, w = original_img.tinggi, original_img.lebar
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


if __name__ == "__main__":
    run_standalone(run)
