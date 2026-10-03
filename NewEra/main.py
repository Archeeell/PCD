"""
Entry point: pemilihan gambar dan menu operasi pengolahan citra.
Setiap kategori materi dikelola oleh satu modul operasi.
"""
import os
from NewEra.utils import get_available_images, load_image, IMG_DIR, prompt_int
from NewEra import op_titik, op_geometri, op_bingkai, op_global, op_neighborhood

MENU_HANDLERS = {
    1: op_titik.run,
    2: op_geometri.run,
    3: op_bingkai.run,
    4: op_global.run,
    5: op_neighborhood.run,
}
MENU_LABELS = {
    1: "Operasi Titik (Brightness / Contrast / Negasi / Grayscale / Thresholding)",
    2: "Operasi Geometri (Flip / Rotasi / Crop / Scaling)",
    3: "Operasi Berbasis Bingkai (Blending / Gerakan / Logika)",
    4: "Operasi Global (Histogram / Ekualisasi Histogram)",
    5: "Operasi Bertetangga (Edge / Smoothing / Sharpening / Noise / Emboss)",
}

def select_image():
    images = get_available_images()
    if not images:
        print(f"Folder '{IMG_DIR}' kosong atau tidak ditemukan file citra yang didukung.")
        print(f"Silakan letakkan file gambar di dalam folder '{IMG_DIR}'.")
        return None
    print("=== DAFTAR GAMBAR TERSEDIA ===")
    for idx, img_name in enumerate(images, 1):
        print(f"[{idx}] {img_name}")
    choice = prompt_int("\nPilih nomor gambar (0 untuk keluar): ", min_val=0, max_val=len(images))
    return None if choice == 0 else os.path.join(IMG_DIR, images[choice - 1])

def run_menu_loop(original_img):
    while True:
        print("\n=== MENU PENGOLAHAN CITRA ===")
        for num, label in MENU_LABELS.items(): print(f"[{num}] {label}")
        print("[0] Keluar")
        op = prompt_int("Pilih operasi: ", min_val=0, max_val=len(MENU_LABELS))
        if op == 0:
            print("Keluar dari program.")
            break
        MENU_HANDLERS[op](original_img)

def main():
    selected_file = select_image()
    if selected_file is None:
        print("Program selesai.")
        return
    original_img = load_image(selected_file)
    channels = "Grayscale" if original_img.ndim == 2 else "RGB"
    print(f"\nMemuat: {selected_file} | Resolusi: {original_img.shape[1]}x{original_img.shape[0]} | Saluran: {channels}")
    run_menu_loop(original_img)

if __name__ == "__main__":
    main()
