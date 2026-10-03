"""
op_bingkai.py
Menu Operasi Berbasis Bingkai (Frame) / Operasi Multi Image:
Penggabungan citra (blending), Deteksi gerakan, dan Operasi Logika.

Semua operasi ini melibatkan 2 citra (A dan B) yang dioperasikan
titik per titik pada lokasi yang bersesuaian, sesuai materi kuliah
Pengolahan Citra (Idhawati Hestiningsih).
"""

import numpy as np
from NewEra.utils import (
    display_dual_input_result,
    select_second_image,
    prompt_int,
    prompt_float,
)


# --- 1. Penggabungan Citra (Image Blending) ---

def blend_images(img_a, img_b, wa, wb):
    """C(x,y) = wa * A(x,y) + wb * B(x,y), dengan wa + wb idealnya = 1."""
    result = wa * img_a.astype(np.float32) + wb * img_b.astype(np.float32)
    return np.clip(result, 0, 255).astype(np.uint8)


# --- 2. Deteksi Gerakan ---

def detect_motion(img_a, img_b):
    """
    C(x,y) = A(x,y) - B(x,y). Bagian yang tidak bergerak bernilai mendekati 0,
    bagian yang bergerak menghasilkan nilai berbeda dari 0.
    Menggunakan nilai absolut agar hasil selisih mudah divisualisasikan.
    """
    diff = img_a.astype(np.int16) - img_b.astype(np.int16)
    return np.abs(diff).astype(np.uint8)


# --- 3. Operasi Logika ---

def _to_binary(img_array):
    """Bantu: pastikan citra dalam bentuk biner 0/1 untuk operasi logika."""
    if img_array.ndim == 3:
        gray = np.dot(img_array[..., :3], [0.299, 0.587, 0.114])
    else:
        gray = img_array
    return (gray >= 128).astype(np.uint8)


def logic_and(img_a, img_b):
    return (_to_binary(img_a) & _to_binary(img_b)) * 255


def logic_or(img_a, img_b):
    return (_to_binary(img_a) | _to_binary(img_b)) * 255


def logic_xor(img_a, img_b):
    return (_to_binary(img_a) ^ _to_binary(img_b)) * 255


def logic_sub(img_a, img_b):
    """A SUB B = A - B jika A >= B, else 0 (pada representasi biner 0/1)."""
    a, b = _to_binary(img_a).astype(np.int16), _to_binary(img_b).astype(np.int16)
    result = np.where(a >= b, a - b, 0)
    return (result * 255).astype(np.uint8)


def logic_not(img_a):
    """C(x,y) = NOT A(x,y) pada representasi biner."""
    return (1 - _to_binary(img_a)) * 255


# --- Menu ---

def _submenu_blending(img_a, img_b):
    wa = prompt_float("Masukkan bobot wa untuk citra A (misal 0.4): ")
    wb = prompt_float("Masukkan bobot wb untuk citra B (misal 0.6, idealnya wa+wb=1): ")
    result = blend_images(img_a, img_b, wa, wb)
    display_dual_input_result(img_a, img_b, result, f"Blending (wa={wa}, wb={wb})")


def _submenu_motion(img_a, img_b):
    result = detect_motion(img_a, img_b)
    display_dual_input_result(img_a, img_b, result, "Deteksi Gerakan (A - B)")


def _submenu_logic(img_a, img_b):
    print("\n[1] AND  [2] OR  [3] XOR  [4] SUB  [5] NOT (hanya citra A)")
    choice = prompt_int("Pilih operasi logika: ", min_val=1, max_val=5)

    if choice == 1:
        result, label = logic_and(img_a, img_b), "A AND B"
    elif choice == 2:
        result, label = logic_or(img_a, img_b), "A OR B"
    elif choice == 3:
        result, label = logic_xor(img_a, img_b), "A XOR B"
    elif choice == 4:
        result, label = logic_sub(img_a, img_b), "A SUB B"
    else:
        result, label = logic_not(img_a), "NOT A"

    display_dual_input_result(img_a, img_b, result, label)


def run(original_img):
    print("\n--- OPERASI BERBASIS BINGKAI (Multi Image) ---")
    print("Operasi ini membutuhkan citra kedua (citra A = citra yang sedang aktif).")

    img_b = select_second_image(original_img.shape)
    if img_b is None:
        print("Dibatalkan: citra kedua tidak dipilih.")
        return

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
