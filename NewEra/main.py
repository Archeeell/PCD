"""
main.py
Entry point program. Menangani pemilihan gambar dan loop menu utama,
lalu mendelegasikan tiap operasi ke modul op_*.py masing-masing.
"""

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import os
# Mengambil fungsi/bantuan yang dipakai oleh modul ini agar kode tetap modular.
from NewEra.utils import get_available_images, load_image, IMG_DIR, prompt_int

# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_histogram
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_brightness
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_contrast
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_invert
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_color_convert
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_threshold
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_geometri
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_bingkai
# Mengimpor modul yang dibutuhkan agar operasi pengolahan citra dapat dijalankan.
import NewEra.op_global

# Peta nomor menu -> modul yang menanganinya.
# Untuk menambah operasi baru: buat file op_baru.py dengan fungsi run(original_img),
# lalu tambahkan satu baris di sini dan satu baris di MENU_LABELS.
# Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
MENU_HANDLERS = {
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    1: op_histogram.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    2: op_brightness.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    3: op_contrast.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    4: op_invert.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    5: op_color_convert.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    6: op_threshold.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    7: op_geometri.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    8: op_bingkai.run,
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    9: op_global.run,
# Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
}

# Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
MENU_LABELS = {
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    1: "Tampilkan Histogram Citra Asli Saja",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    2: "Modifikasi Brightness",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    3: "Tingkatkan / Ubah Kontras",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    4: "Negasi / Inversi Citra",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    5: "Konversi Ruang Warna (RGB <-> Grayscale)",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    6: "Thresholding (Pengambangan)",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    7: "Operasi Geometri (Flip / Rotasi / Crop / Scaling)",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    8: "Operasi Berbasis Bingkai (Blending / Deteksi Gerakan / Logika)",
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
    9: "Operasi Global (Ekualisasi Histogram)",
# Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
}


# Mendefinisikan fungsi select_image untuk bagian tertentu dari program.
def select_image():
    """Menampilkan daftar gambar tersedia dan meminta user memilih satu."""
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    images = get_available_images()
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if not images:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print(f"Folder '{IMG_DIR}' kosong atau tidak ditemukan file citra yang didukung.")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print(f"Silakan letakkan file gambar di dalam folder '{IMG_DIR}'.")
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return None

    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print("=== DAFTAR GAMBAR TERSEDIA ===")
    # Mengulang pemrosesan untuk setiap elemen/kanal yang diperlukan.
    for idx, img_name in enumerate(images, 1):
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print(f"[{idx}] {img_name}")

    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    choice = prompt_int("\nPilih nomor gambar (0 untuk keluar): ", min_val=0, max_val=len(images))
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if choice == 0:
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
        return None
    # Mengembalikan hasil pengolahan ke pemanggil fungsi.
    return os.path.join(IMG_DIR, images[choice - 1])


# Mendefinisikan fungsi run_menu_loop untuk bagian tertentu dari program.
def run_menu_loop(original_img):
    """Loop menu utama: menampilkan pilihan operasi dan menjalankan handler yang sesuai."""
    # Mengulang sampai masukan pengguna memenuhi aturan validasi.
    while True:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print("\n=== MENU OPERASI TITIK ===")
    # Mengulang pemrosesan untuk setiap elemen/kanal yang diperlukan.
        for num, label in MENU_LABELS.items():
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
            print(f"[{num}] {label}")
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print("[0] Keluar")

    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
        op = prompt_int("Pilih operasi: ", min_val=0, max_val=len(MENU_LABELS))

    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
        if op == 0:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
            print("Keluar dari program.")
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
            break

    # Mengambil fungsi handler sesuai nomor operasi yang dipilih.
        handler = MENU_HANDLERS[op]
    # Menjalankan operasi terpilih menggunakan citra asli sebagai input.
        handler(original_img)


# Mendefinisikan fungsi main untuk bagian tertentu dari program.
def main():
    # Menyimpan nilai antara yang digunakan oleh langkah pemrosesan berikutnya.
    selected_file = select_image()
    # Memeriksa kondisi agar algoritma memilih jalur pemrosesan yang sesuai.
    if selected_file is None:
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
        print("Program selesai.")
    # Menghentikan fungsi tanpa menghasilkan nilai baru.
        return

    # Memuat citra pilihan pengguna sebagai input utama seluruh operasi.
    original_img = load_image(selected_file)
    # Mengidentifikasi citra sebagai grayscale atau RGB berdasarkan jumlah dimensinya.
    channels = "Grayscale" if original_img.ndim == 2 else "RGB"
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    print(f"\nMemuat: {selected_file} | "
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
          f"Resolusi: {original_img.shape[1]}x{original_img.shape[0]} | "
    # Baris ini mendukung alur pemrosesan operasi yang sedang dijalankan.
          f"Saluran: {channels}")

    # Memulai siklus menu sehingga pengguna dapat memilih operasi pengolahan citra.
    run_menu_loop(original_img)


# Menjalankan main() hanya ketika file ini dieksekusi langsung.
if __name__ == "__main__":
    # Menjalankan langkah pemrosesan atau menampilkan hasil pada tahap ini.
    main()
