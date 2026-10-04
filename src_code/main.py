"""
Entry point: pemilihan gambar dan menu operasi pengolahan citra.
Setiap kategori materi dikelola oleh satu modul operasi.
"""
import os

if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import get_available_images, load_image, IMG_DIR, prompt_int
    from src_code import op_titik, op_geometri, op_bingkai, op_global, op_neighborhood
    from src_code import noise_gaussian, noise_mean, noise_median, noise_midpoint
else:
    from .utils import get_available_images, load_image, IMG_DIR, prompt_int
    from . import op_titik, op_geometri, op_bingkai, op_global, op_neighborhood
    from . import noise_gaussian, noise_mean, noise_median, noise_midpoint

NOISE_HANDLERS = {
    1: noise_gaussian.run,
    2: noise_mean.run,
    3: noise_median.run,
    4: noise_midpoint.run,
}
NOISE_LABELS = {
    1: "Filter Gaussian",
    2: "Filter Mean",
    3: "Filter Median",
    4: "Filter Mid-point",
}

def run_noise_menu(original_img):
    print("\n--- REDUKSI NOISE ---")
    for num, label in NOISE_LABELS.items():
        print(f"[{num}] {label}")
    print("[0] Kembali")
    op = prompt_int("Pilih filter noise: ", min_val=0, max_val=len(NOISE_LABELS))
    if op == 0:
        return
    NOISE_HANDLERS[op](original_img)

MENU_HANDLERS = {
    1: op_titik.run,
    2: op_geometri.run,
    3: op_bingkai.run,
    4: op_global.run,
    5: op_neighborhood.run,
    6: run_noise_menu,
}
MENU_LABELS = {
    1: "Operasi Titik (Brightness / Contrast / Negasi / Grayscale / Thresholding)",
    2: "Operasi Geometri (Flip / Rotasi / Crop / Scaling)",
    3: "Operasi Berbasis Bingkai (Blending / Gerakan / Logika)",
    4: "Operasi Global (Histogram / Ekualisasi Histogram)",
    5: "Operasi Bertetangga (Edge / Smoothing / Sharpening / Noise / Emboss)",
    6: "Reduksi Noise (Gaussian / Mean / Median / Mid-point)",
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
