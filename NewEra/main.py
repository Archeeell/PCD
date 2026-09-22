"""
main.py
Entry point program. Menangani pemilihan gambar dan loop menu utama,
lalu mendelegasikan tiap operasi ke modul op_*.py masing-masing.
"""

import os
from NewEra.utils import get_available_images, load_image, IMG_DIR, prompt_int

import NewEra.op_histogram
import NewEra.op_brightness
import NewEra.op_contrast
import NewEra.op_invert
import NewEra.op_color_convert
import NewEra.op_threshold
import NewEra.op_geometri
import NewEra.op_bingkai
import NewEra.op_global

# Peta nomor menu -> modul yang menanganinya.
# Untuk menambah operasi baru: buat file op_baru.py dengan fungsi run(original_img),
# lalu tambahkan satu baris di sini dan satu baris di MENU_LABELS.
MENU_HANDLERS = {
    1: op_histogram.run,
    2: op_brightness.run,
    3: op_contrast.run,
    4: op_invert.run,
    5: op_color_convert.run,
    6: op_threshold.run,
    7: op_geometri.run,
    8: op_bingkai.run,
    9: op_global.run,
}

MENU_LABELS = {
    1: "Tampilkan Histogram Citra Asli Saja",
    2: "Modifikasi Brightness",
    3: "Tingkatkan / Ubah Kontras",
    4: "Negasi / Inversi Citra",
    5: "Konversi Ruang Warna (RGB <-> Grayscale)",
    6: "Thresholding (Pengambangan)",
    7: "Operasi Geometri (Flip / Rotasi / Crop / Scaling)",
    8: "Operasi Berbasis Bingkai (Blending / Deteksi Gerakan / Logika)",
    9: "Operasi Global (Ekualisasi Histogram)",
}


def select_image():
    """Menampilkan daftar gambar tersedia dan meminta user memilih satu."""
    images = get_available_images()
    if not images:
        print(f"Folder '{IMG_DIR}' kosong atau tidak ditemukan file citra yang didukung.")
        print(f"Silakan letakkan file gambar di dalam folder '{IMG_DIR}'.")
        return None

    print("=== DAFTAR GAMBAR TERSEDIA ===")
    for idx, img_name in enumerate(images, 1):
        print(f"[{idx}] {img_name}")

    choice = prompt_int("\nPilih nomor gambar (0 untuk keluar): ", min_val=0, max_val=len(images))
    if choice == 0:
        return None
    return os.path.join(IMG_DIR, images[choice - 1])


def run_menu_loop(original_img):
    """Loop menu utama: menampilkan pilihan operasi dan menjalankan handler yang sesuai."""
    while True:
        print("\n=== MENU OPERASI TITIK ===")
        for num, label in MENU_LABELS.items():
            print(f"[{num}] {label}")
        print("[0] Keluar")

        op = prompt_int("Pilih operasi: ", min_val=0, max_val=len(MENU_LABELS))

        if op == 0:
            print("Keluar dari program.")
            break

        handler = MENU_HANDLERS[op]
        handler(original_img)


def main():
    selected_file = select_image()
    if selected_file is None:
        print("Program selesai.")
        return

    original_img = load_image(selected_file)
    channels = "Grayscale" if original_img.ndim == 2 else "RGB"
    print(f"\nMemuat: {selected_file} | "
          f"Resolusi: {original_img.shape[1]}x{original_img.shape[0]} | "
          f"Saluran: {channels}")

    run_menu_loop(original_img)


if __name__ == "__main__":
    main()
