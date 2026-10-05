"""
op_bingkai.py
Menu Operasi Berbasis Bingkai (Frame) / Operasi Multi Image:
Penggabungan citra (blending), Deteksi gerakan, dan Operasi Logika.

Semua operasi melibatkan 2 citra (A dan B) yang dioperasikan
titik per titik pada lokasi yang bersesuaian, sesuai materi kuliah
Pengolahan Citra (Idhawati Hestiningsih).

KOREKSI (Deviasi #2): jika ukuran/mode A dan B berbeda, potong ke
area bersama dan konversi grayscale ke RGB.
"""

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, klem,
                                display_dual_input_result, select_second_image,
                                prompt_int, prompt_float, run_standalone)
else:
    from .utils import (Citra, buat_kosong, klem,
                        display_dual_input_result, select_second_image,
                        prompt_int, prompt_float, run_standalone)


# --- 1. Penggabungan Citra (Image Blending) ---

def blend_images(citra_a, citra_b, wa, wb):
    """C(x,y) = wa * A(x,y) + wb * B(x,y), diklem 0-255 lalu dipotong ke int."""
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, citra_a.mode)
    for c in range(len(citra_a.kanal)):
        ka = citra_a.kanal[c]
        kb = citra_b.kanal[c]
        kd = hasil.kanal[c]
        for y in range(citra_a.tinggi):
            ra, rb, rd = ka[y], kb[y], kd[y]
            for x in range(citra_a.lebar):
                val = wa * ra[x] + wb * rb[x]
                if val < 0.0:
                    val = 0.0
                elif val > 255.0:
                    val = 255.0
                rd[x] = int(val)   # truncation sesuai astype(uint8)
    return hasil


# --- 2. Deteksi Gerakan ---

def detect_motion(citra_a, citra_b):
    """
    C(x,y) = |A(x,y) - B(x,y)| per kanal (int16, lalu ambil nilai absolut).
    """
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, citra_a.mode)
    for c in range(len(citra_a.kanal)):
        ka = citra_a.kanal[c]
        kb = citra_b.kanal[c]
        kd = hasil.kanal[c]
        for y in range(citra_a.tinggi):
            ra, rb, rd = ka[y], kb[y], kd[y]
            for x in range(citra_a.lebar):
                diff = ra[x] - rb[x]
                rd[x] = diff if diff >= 0 else -diff
    return hasil


# --- 3. Operasi Logika ---

def _piksel_ke_biner(val_r, val_g, val_b, mode):
    """
    Konversi nilai piksel ke bit biner (0 atau 1).
    RGB: luminance float 0.299R + 0.587G + 0.114B >= 128 (tanpa truncation).
    Grayscale: langsung >= 128.
    """
    if mode == "RGB":
        lum = 0.299 * val_r + 0.587 * val_g + 0.114 * val_b
        return 1 if lum >= 128 else 0
    else:
        return 1 if val_r >= 128 else 0


def _buat_biner(citra):
    """Bantu: buat Citra grayscale biner 0/255 dari luminance piksel."""
    hasil = buat_kosong(citra.lebar, citra.tinggi, "L")
    kd = hasil.kanal[0]
    if citra.mode == "L":
        k = citra.kanal[0]
        for y in range(citra.tinggi):
            src_row = k[y]
            dst_row = kd[y]
            for x in range(citra.lebar):
                dst_row[x] = 1 if src_row[x] >= 128 else 0
    else:
        r_k, g_k, b_k = citra.kanal[0], citra.kanal[1], citra.kanal[2]
        for y in range(citra.tinggi):
            r_row, g_row, b_row = r_k[y], g_k[y], b_k[y]
            dst_row = kd[y]
            for x in range(citra.lebar):
                lum = 0.299 * r_row[x] + 0.587 * g_row[x] + 0.114 * b_row[x]
                dst_row[x] = 1 if lum >= 128 else 0
    return hasil


def _biner_ke_255(citra_biner):
    """Konversi Citra biner (0/1) ke 0/255."""
    hasil = buat_kosong(citra_biner.lebar, citra_biner.tinggi, "L")
    kb = citra_biner.kanal[0]
    kd = hasil.kanal[0]
    for y in range(citra_biner.tinggi):
        src_row = kb[y]
        dst_row = kd[y]
        for x in range(citra_biner.lebar):
            dst_row[x] = src_row[x] * 255
    return hasil


def logic_and(citra_a, citra_b):
    """Operasi logika AND; output 0/255."""
    ba = _buat_biner(citra_a)
    bb = _buat_biner(citra_b)
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, "L")
    kd = hasil.kanal[0]
    for y in range(citra_a.tinggi):
        a_row = ba.kanal[0][y]
        b_row = bb.kanal[0][y]
        d_row = kd[y]
        for x in range(citra_a.lebar):
            d_row[x] = (a_row[x] & b_row[x]) * 255
    return hasil


def logic_or(citra_a, citra_b):
    """Operasi logika OR; output 0/255."""
    ba = _buat_biner(citra_a)
    bb = _buat_biner(citra_b)
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, "L")
    kd = hasil.kanal[0]
    for y in range(citra_a.tinggi):
        a_row = ba.kanal[0][y]
        b_row = bb.kanal[0][y]
        d_row = kd[y]
        for x in range(citra_a.lebar):
            d_row[x] = (a_row[x] | b_row[x]) * 255
    return hasil


def logic_xor(citra_a, citra_b):
    """Operasi logika XOR; output 0/255."""
    ba = _buat_biner(citra_a)
    bb = _buat_biner(citra_b)
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, "L")
    kd = hasil.kanal[0]
    for y in range(citra_a.tinggi):
        a_row = ba.kanal[0][y]
        b_row = bb.kanal[0][y]
        d_row = kd[y]
        for x in range(citra_a.lebar):
            d_row[x] = (a_row[x] ^ b_row[x]) * 255
    return hasil


def logic_sub(citra_a, citra_b):
    """A SUB B = A - B jika A >= B, else 0 (pada representasi biner 0/1)."""
    ba = _buat_biner(citra_a)
    bb = _buat_biner(citra_b)
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, "L")
    kd = hasil.kanal[0]
    for y in range(citra_a.tinggi):
        a_row = ba.kanal[0][y]
        b_row = bb.kanal[0][y]
        d_row = kd[y]
        for x in range(citra_a.lebar):
            a_val, b_val = a_row[x], b_row[x]
            d_row[x] = (a_val - b_val) * 255 if a_val >= b_val else 0
    return hasil


def logic_not(citra_a):
    """C(x,y) = NOT A(x,y) pada representasi biner."""
    ba = _buat_biner(citra_a)
    hasil = buat_kosong(citra_a.lebar, citra_a.tinggi, "L")
    kd = hasil.kanal[0]
    for y in range(citra_a.tinggi):
        a_row = ba.kanal[0][y]
        d_row = kd[y]
        for x in range(citra_a.lebar):
            d_row[x] = (1 - a_row[x]) * 255
    return hasil


# --- Menu ---

def _submenu_blending(citra_a, citra_b):
    wa = prompt_float("Masukkan bobot wa untuk citra A (misal 0.4): ")
    wb = prompt_float("Masukkan bobot wb untuk citra B (misal 0.6, idealnya wa+wb=1): ")
    result = blend_images(citra_a, citra_b, wa, wb)
    display_dual_input_result(citra_a, citra_b, result, f"Blending (wa={wa}, wb={wb})")


def _submenu_motion(citra_a, citra_b):
    result = detect_motion(citra_a, citra_b)
    display_dual_input_result(citra_a, citra_b, result, "Deteksi Gerakan (A - B)")


def _submenu_logic(citra_a, citra_b):
    print("\n[1] AND  [2] OR  [3] XOR  [4] SUB  [5] NOT (hanya citra A)")
    choice = prompt_int("Pilih operasi logika: ", min_val=1, max_val=5)

    if choice == 1:
        result, label = logic_and(citra_a, citra_b), "A AND B"
    elif choice == 2:
        result, label = logic_or(citra_a, citra_b),  "A OR B"
    elif choice == 3:
        result, label = logic_xor(citra_a, citra_b), "A XOR B"
    elif choice == 4:
        result, label = logic_sub(citra_a, citra_b), "A SUB B"
    else:
        result, label = logic_not(citra_a),           "NOT A"

    display_dual_input_result(citra_a, citra_b, result, label)


def run(original_img):
    print("\n--- OPERASI BERBASIS BINGKAI (Multi Image) ---")
    print("Operasi ini membutuhkan citra kedua (citra A = citra yang sedang aktif).")

    img_b = select_second_image(original_img)
    if img_b is None:
        print("Dibatalkan: citra kedua tidak dipilih.")
        return

    # Terapkan koreksi ukuran pada citra A jika perlu (area bersama)
    crop_lebar  = min(original_img.lebar,  img_b.lebar)
    crop_tinggi = min(original_img.tinggi, img_b.tinggi)
    if crop_lebar != original_img.lebar or crop_tinggi != original_img.tinggi:
        from .utils import Citra  # noqa: F401 -- sudah diimpor di atas
        kanal_crop = []
        for c in range(len(original_img.kanal)):
            kanal_crop.append([list(original_img.kanal[c][y][:crop_lebar])
                               for y in range(crop_tinggi)])
        original_img = Citra(crop_lebar, crop_tinggi, original_img.mode, kanal_crop)

    print("\n[1] Penggabungan Citra (Image Blending)")
    print("[2] Deteksi Gerakan")
    print("[3] Operasi Logika (AND/OR/XOR/SUB/NOT)")
    choice = prompt_int("Pilih sub-operasi: ", min_val=1, max_val=3)

    if choice == 1:
        _submenu_blending(original_img, img_b)
    elif choice == 2:
        _submenu_motion(original_img, img_b)
    elif choice == 3:
        _submenu_logic(original_img, img_b)


if __name__ == "__main__":
    run_standalone(run)
