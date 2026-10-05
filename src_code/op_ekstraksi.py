"""
op_ekstraksi.py
Operasi Pembuatan, Karakteristik, dan Ekstraksi Citra Digital.
Mencakup:
- Ekstraksi karakteristik citra: Resolusi, Bit Depth, Jumlah Channel, Tipe Data, Rentang Intensitas
- Ekstraksi dan modifikasi intensitas titik piksel f(x, y)
- Pembacaan header metadata file citra (BMP, PNG, JPG) murni byte tanpa library
- Pembuatan citra digital dari dasar (kosong, gradien, pola catur, dsb.)
- Ekspor & impor citra biner format .BMP murni tanpa library eksternal
- Kompatibel dengan kelas Citra dan alur kerja NoMain PCD.
- Mengacu pada materi Pengolahan Citra Digital (Idhawati Hestiningsih).
- 100% Python murni: tanpa numpy, cv2, scipy, atau dependensi eksternal.
"""

import os
import math
import struct

if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, salin, klem,
                                get_pixel, set_pixel,
                                display_comparison, prompt_int, prompt_float,
                                run_standalone, get_available_images, load_image, IMG_DIR)
else:
    from .utils import (Citra, buat_kosong, salin, klem,
                        get_pixel, set_pixel,
                        display_comparison, prompt_int, prompt_float,
                        run_standalone, get_available_images, load_image, IMG_DIR)



# ===========================================================================
# 1. Ekstraksi Karakteristik Citra (In-Memory)
# ===========================================================================

def ekstrak_karakteristik(citra):
    """
    Mengekstrak informasi karakteristik struktur citra dari objek Citra:
    - Resolusi: lebar (kolom) x tinggi (baris)
    - Total piksel: lebar * tinggi
    - Mode representasi: 'L' (Grayscale) atau 'RGB' (Warna)
    - Jumlah channel: 1 (Grayscale) atau 3 (RGB)
    - Bit Depth (Kedalaman Bit): 8-bit per channel (8 bit untuk 'L', 24 bit untuk 'RGB')
    - Rentang intensitas: nilai minimum dan maksimum intensitas piksel per kanal
    """
    total_piksel = citra.lebar * citra.tinggi
    jumlah_channel = len(citra.kanal)
    bit_depth = 8 * jumlah_channel

    rentang = {}
    if citra.mode == "L":
        vals = [citra.kanal[0][y][x] for y in range(citra.tinggi) for x in range(citra.lebar)]
        rentang['Grayscale'] = {'min': min(vals), 'max': max(vals)}
    else:
        nama_kanal = ['Merah (R)', 'Hijau (G)', 'Biru (B)']
        for c in range(3):
            vals = [citra.kanal[c][y][x] for y in range(citra.tinggi) for x in range(citra.lebar)]
            rentang[nama_kanal[c]] = {'min': min(vals), 'max': max(vals)}

    return {
        "resolusi": (citra.lebar, citra.tinggi),
        "lebar": citra.lebar,
        "tinggi": citra.tinggi,
        "total_piksel": total_piksel,
        "mode": citra.mode,
        "jumlah_channel": jumlah_channel,
        "bit_depth": bit_depth,
        "rentang_intensitas": rentang
    }


def format_laporan_karakteristik(info, nama_sumber="Citra Aktif"):
    """Mengembalikan string teks terformat rapi dari hasil ekstrak_karakteristik."""
    garis = "=" * 55
    teks = [
        garis,
        f"  LAPORAN KARAKTERISTIK CITRA: {nama_sumber}",
        garis,
        f"  Resolusi (Lebar x Tinggi) : {info['lebar']} x {info['tinggi']} piksel",
        f"  Total Piksel             : {info['total_piksel']:,} piksel",
        f"  Mode Warna               : {info['mode']} ({'Grayscale' if info['mode'] == 'L' else 'True Color RGB'})",
        f"  Jumlah Channel           : {info['jumlah_channel']}",
        f"  Bit Depth (Kedalaman)    : {info['bit_depth']} bit ({info['bit_depth'] // info['jumlah_channel']} bit/channel)",
        "  Rentang Intensitas Titik :",
    ]
    for kanal, batas in info['rentang_intensitas'].items():
        teks.append(f"    - {kanal:<18} : min={batas['min']}, max={batas['max']}")
    teks.append(garis)
    return "\n".join(teks)


# ===========================================================================
# 2. Pembacaan Header File Citra Tanpa Library (BMP, PNG, JPG)
# ===========================================================================

def ekstrak_header_file(filepath):
    """
    Mengekstrak informasi metadata langsung dari header byte biner file citra
    tanpa menggunakan library pihak ketiga apa pun.
    Mendukung format: .BMP, .PNG, dan .JPG / .JPEG.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File tidak ditemukan: {filepath}")

    ukuran_file = os.path.getsize(filepath)
    ekstensi = os.path.splitext(filepath)[1].lower()

    with open(filepath, 'rb') as f:
        head = f.read(64)

    # Deteksi BMP (Magic: b'BM')
    if head[:2] == b'BM':
        file_size, _, _, offset = struct.unpack('<IHHI', head[2:14])
        with open(filepath, 'rb') as f:
            f.seek(18)
            lebar, tinggi, planes, bpp, kompresi, img_size = struct.unpack('<iiHHII', f.read(20))
        tinggi_abs = abs(tinggi)
        is_top_down = tinggi < 0
        channel = bpp // 8 if bpp >= 8 else 1
        return {
            "tipe_file": "Windows Bitmap (BMP)",
            "magic_bytes": "BM (0x42 0x4D)",
            "ukuran_file": ukuran_file,
            "lebar": lebar,
            "tinggi": tinggi_abs,
            "resolusi": (lebar, tinggi_abs),
            "bit_depth": bpp,
            "jumlah_channel": channel,
            "kompresi": "Uncompressed (BI_RGB)" if kompresi == 0 else f"Tipe-{kompresi}",
            "offset_piksel": offset,
            "is_top_down": is_top_down
        }

    # Deteksi PNG (Magic: b'\x89PNG\r\n\x1a\n')
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        # IHDR chunk dimulai pada byte 12 (4 byte tipe IHDR, lalu 13 byte data)
        with open(filepath, 'rb') as f:
            f.seek(16)
            lebar, tinggi, bit_depth, color_type = struct.unpack('>IIBB', f.read(10))
        # Color type PNG:
        # 0: Grayscale (1 ch)
        # 2: RGB (3 ch)
        # 3: Indexed (1 ch)
        # 4: Grayscale + Alpha (2 ch)
        # 6: RGBA (4 ch)
        channel_map = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
        mode_map = {0: "Grayscale", 2: "RGB", 3: "Indexed/Palette", 4: "Gray+Alpha", 6: "RGBA"}
        channels = channel_map.get(color_type, 1)
        total_bit_depth = bit_depth * channels
        return {
            "tipe_file": "Portable Network Graphics (PNG)",
            "magic_bytes": "89 50 4E 47 0D 0A 1A 0A",
            "ukuran_file": ukuran_file,
            "lebar": lebar,
            "tinggi": tinggi,
            "resolusi": (lebar, tinggi),
            "bit_depth": total_bit_depth,
            "bit_per_sample": bit_depth,
            "jumlah_channel": channels,
            "mode_warna": mode_map.get(color_type, "Unknown")
        }

    # Deteksi JPEG (Magic: b'\xff\xd8')
    if head[:2] == b'\xff\xd8':
        with open(filepath, 'rb') as f:
            f.seek(2)
            lebar = tinggi = channels = 0
            while True:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                if marker[0] != 0xFF:
                    break
                m_type = marker[1]
                # SOF0 (0xC0) s.d. SOF3 (0xC3) memuat informasi dimensi
                if m_type in (0xC0, 0xC1, 0xC2, 0xC3):
                    f.read(2)  # panjang segmen
                    precision, h, w, ch = struct.unpack('>BHHB', f.read(6))
                    lebar, tinggi, channels = w, h, ch
                    break
                elif m_type in (0xD9, 0xDA):  # EOI atau SOS
                    break
                else:
                    pj_data = struct.unpack('>H', f.read(2))[0]
                    f.seek(pj_data - 2, os.SEEK_CUR)

        return {
            "tipe_file": "JPEG Image (JPG/JPEG)",
            "magic_bytes": "FF D8 (SOI)",
            "ukuran_file": ukuran_file,
            "lebar": lebar,
            "tinggi": tinggi,
            "resolusi": (lebar, tinggi),
            "bit_depth": 8 * channels if channels else 24,
            "jumlah_channel": channels if channels else 3,
            "mode_warna": "Grayscale" if channels == 1 else "RGB / YCbCr"
        }

    return {
        "tipe_file": f"Ekstensi {ekstensi.upper()}",
        "ukuran_file": ukuran_file,
        "keterangan": "Header format biner tidak dikenali sebagai BMP, PNG, atau JPG standar."
    }


# ===========================================================================
# 3. Pembuatan Citra Baru dari Dasar (Pure Python Matrix)
# ===========================================================================

def buat_citra_baru(lebar, tinggi, mode="RGB", pola="kosong", nilai=0, **kwargs):
    """
    Membuat citra digital dari dasar menggunakan struktur data murni tanpa library.

    Parameter:
      lebar  (int) : lebar citra
      tinggi (int) : tinggi citra
      mode   (str) : 'L' (Grayscale) atau 'RGB'
      pola   (str) : 'kosong' | 'gradien' | 'catur' | 'garis' | 'lingkaran'
      nilai  (int/tuple): nilai latar awal (0=hitam, 255=putih, atau (R, G, B))
    """
    citra = buat_kosong(lebar, tinggi, mode)
    
    # Isi warna dasar awal jika nilai bukan 0
    if nilai != 0:
        for y in range(tinggi):
            for x in range(lebar):
                set_pixel(citra, x, y, nilai)

    if pola == "kosong" or pola == "polos":
        return citra

    elif pola == "gradien":
        # Gradien horizontal halus
        for y in range(tinggi):
            for x in range(lebar):
                rasio = x / max(1, lebar - 1)
                if mode == "L":
                    val = int(rasio * 255)
                    set_pixel(citra, x, y, val)
                else:
                    # Gradien spektrum: R naik seiring x, B naik seiring y, G kombinasi
                    r = int(rasio * 255)
                    g = int((y / max(1, tinggi - 1)) * 255)
                    b = int((1.0 - rasio) * 255)
                    set_pixel(citra, x, y, (r, g, b))

    elif pola == "catur" or pola == "checkerboard":
        # Pola papan catur dengan ukuran kotak tertentu
        ukuran_kotak = kwargs.get("ukuran_kotak", max(2, min(lebar, tinggi) // 8))
        warna1 = kwargs.get("warna1", 255 if mode == "L" else (255, 255, 255))
        warna2 = kwargs.get("warna2", 0 if mode == "L" else (0, 0, 0))
        for y in range(tinggi):
            for x in range(lebar):
                kotak_x = (x // ukuran_kotak) % 2
                kotak_y = (y // ukuran_kotak) % 2
                warna = warna1 if (kotak_x ^ kotak_y) == 0 else warna2
                set_pixel(citra, x, y, warna)

    elif pola == "garis":
        lebar_garis = kwargs.get("lebar_garis", max(1, min(lebar, tinggi) // 16))
        warna_garis = kwargs.get("warna_garis", 255 if mode == "L" else (255, 215, 0))
        for y in range(tinggi):
            for x in range(lebar):
                if (x // lebar_garis) % 2 == 0:
                    set_pixel(citra, x, y, warna_garis)

    elif pola == "lingkaran":
        cx = lebar / 2.0
        cy = tinggi / 2.0
        radius = kwargs.get("radius", min(lebar, tinggi) * 0.35)
        warna_lingkaran = kwargs.get("warna_lingkaran", 255 if mode == "L" else (230, 50, 50))
        for y in range(tinggi):
            for x in range(lebar):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist <= radius:
                    set_pixel(citra, x, y, warna_lingkaran)

    return citra


# ===========================================================================
# 4. Binary Writer & Reader Format .BMP Murni (No External Libraries)
# ===========================================================================

def simpan_bmp_manual(citra, filepath):
    """
    Menyimpan citra ke file fisik format BMP 24-bit uncompressed
    menggunakan penulisan byte biner standar (struct.pack).
    """
    lebar = citra.lebar
    tinggi = citra.tinggi

    bytes_per_row = lebar * 3
    padding_size = (4 - (bytes_per_row % 4)) % 4
    image_size = (bytes_per_row + padding_size) * tinggi
    file_size = 54 + image_size  # 14 byte file header + 40 byte DIB header + data

    # 1. BMP File Header (14 bytes): 'BM', file size, 0, 0, offset ke piksel (54)
    file_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)

    # 2. DIB Header (BITMAPINFOHEADER - 40 bytes)
    info_header = struct.pack(
        '<IIIHHIIIIII',
        40, lebar, tinggi, 1, 24, 0, image_size, 2835, 2835, 0, 0
    )

    # 3. Data piksel (Bottom-Up row order, BGR channel order)
    pixel_data = bytearray()
    padding_bytes = b'\x00' * padding_size

    for y in range(tinggi - 1, -1, -1):
        for x in range(lebar):
            if citra.mode == "RGB":
                r = citra.kanal[0][y][x]
                g = citra.kanal[1][y][x]
                b = citra.kanal[2][y][x]
            else:
                gray = citra.kanal[0][y][x]
                r = g = b = gray
            pixel_data.extend(bytes([b, g, r]))
        pixel_data.extend(padding_bytes)

    with open(filepath, 'wb') as f:
        f.write(file_header)
        f.write(info_header)
        f.write(pixel_data)


def muat_bmp_manual(filepath):
    """
    Membaca dan mem-parsing file BMP uncompressed (24-bit atau 8-bit)
    langsung ke objek Citra tanpa dependensi library eksternal.
    Mengembalikan tuple (Citra, metadata_dict).
    """
    metadata = ekstrak_header_file(filepath)
    if metadata.get("tipe_file") != "Windows Bitmap (BMP)":
        raise ValueError(f"File bukan format BMP valid: {filepath}")

    lebar = metadata["lebar"]
    tinggi = metadata["tinggi"]
    bpp = metadata["bit_depth"]
    offset = metadata["offset_piksel"]

    if bpp not in (24, 8):
        raise NotImplementedError(f"Hanya BMP 24-bit dan 8-bit yang didukung parser manual (ditemukan: {bpp}-bit).")

    is_top_down = metadata.get("is_top_down", False)
    baris_range = range(tinggi) if is_top_down else range(tinggi - 1, -1, -1)

    with open(filepath, 'rb') as f:
        if bpp == 24:
            f.seek(offset)
            bytes_per_row = lebar * 3
            padding = (4 - (bytes_per_row % 4)) % 4
            citra = buat_kosong(lebar, tinggi, "RGB")
            for y in baris_range:
                row = f.read(bytes_per_row)
                f.read(padding)
                for x in range(lebar):
                    b = row[x * 3]
                    g = row[x * 3 + 1]
                    r = row[x * 3 + 2]
                    citra.kanal[0][y][x] = r
                    citra.kanal[1][y][x] = g
                    citra.kanal[2][y][x] = b
            return citra, metadata
        else:
            # 8-bit: cek palette jika ada di antara offset 54 dan pixel data
            palette = None
            if offset > 54:
                f.seek(54)
                num_colors = min(256, (offset - 54) // 4)
                raw_pal = f.read(num_colors * 4)
                palette = [(raw_pal[i * 4 + 2], raw_pal[i * 4 + 1], raw_pal[i * 4]) for i in range(num_colors)]  # (R, G, B)

            f.seek(offset)
            padding = (4 - (lebar % 4)) % 4
            is_color_palette = False
            if palette:
                is_color_palette = any(r != g or g != b for r, g, b in palette)

            if is_color_palette:
                citra = buat_kosong(lebar, tinggi, "RGB")
                for y in baris_range:
                    row = f.read(lebar)
                    f.read(padding)
                    for x in range(lebar):
                        idx = row[x]
                        r, g, b = palette[idx] if idx < len(palette) else (idx, idx, idx)
                        citra.kanal[0][y][x] = r
                        citra.kanal[1][y][x] = g
                        citra.kanal[2][y][x] = b
            else:
                citra = buat_kosong(lebar, tinggi, "L")
                for y in baris_range:
                    row = f.read(lebar)
                    f.read(padding)
                    for x in range(lebar):
                        idx = row[x]
                        val = palette[idx][0] if (palette and idx < len(palette)) else idx
                        citra.kanal[0][y][x] = val
            return citra, metadata



# ===========================================================================
# 5. Antarmuka Interaktif Sesuai Standar Proyek PCD (Pola NoMain)
# ===========================================================================

def _tampilkan_karakteristik(citra):
    info = ekstrak_karakteristik(citra)
    print("\n" + format_laporan_karakteristik(info))


def _ekstraksi_intensitas_titik(citra):
    print(f"\n--- EKSTRAKSI INTENSITAS TITIK PIKSEL ---")
    print(f"Batas koordinat x: 0 s.d. {citra.lebar - 1}, y: 0 s.d. {citra.tinggi - 1}")
    x = prompt_int("Masukkan koordinat x (kolom): ", 0, citra.lebar - 1)
    y = prompt_int("Masukkan koordinat y (baris): ", 0, citra.tinggi - 1)
    nilai = get_pixel(citra, x, y)
    if citra.mode == "L":
        print(f"\nIntensitas pada f({x}, {y}) = {nilai} (Derajat keabuan 8-bit)")
    else:
        r, g, b = nilai
        print(f"\nIntensitas pada f({x}, {y}) = [R={r}, G={g}, B={b}]")
        print(f"  - Nilai Kanal Merah (R) : {r}")
        print(f"  - Nilai Kanal Hijau (G) : {g}")
        print(f"  - Nilai Kanal Biru  (B) : {b}")


def _modifikasi_intensitas_titik(citra):
    print(f"\n--- MODIFIKASI INTENSITAS TITIK PIKSEL ---")
    x = prompt_int("Masukkan koordinat x (kolom): ", 0, citra.lebar - 1)
    y = prompt_int("Masukkan koordinat y (baris): ", 0, citra.tinggi - 1)
    sebelum = get_pixel(citra, x, y)
    print(f"Nilai sebelum: {sebelum}")

    if citra.mode == "L":
        baru = prompt_int("Masukkan nilai intensitas baru (0-255): ", 0, 255)
    else:
        r = prompt_int("Masukkan intensitas Merah R (0-255): ", 0, 255)
        g = prompt_int("Masukkan intensitas Hijau G (0-255): ", 0, 255)
        b = prompt_int("Masukkan intensitas Biru  B (0-255): ", 0, 255)
        baru = (r, g, b)

    hasil = salin(citra)
    set_pixel(hasil, x, y, baru)
    print(f"[OK] Piksel f({x}, {y}) berhasil diubah dari {sebelum} menjadi {baru}.")
    display_comparison(citra, hasil, f"Ubah Piksel ({x},{y})")


def _inspeksi_header_file():
    images = get_available_images()
    if not images:
        print("Tidak ada file di folder img/.")
        return
    print("\n=== PILIH FILE CITRA DI FOLDER IMG ===")
    for idx, name in enumerate(images, 1):
        print(f"[{idx}] {name}")
    pilih = prompt_int("Pilih nomor file (0 untuk batal): ", 0, len(images))
    if pilih == 0:
        return
    path = os.path.join(IMG_DIR, images[pilih - 1])
    meta = ekstrak_header_file(path)
    print("\n" + "=" * 55)
    print(f"  HASIL EKSTRAKSI HEADER BINARY (TANPA LIBRARY)")
    print(f"  File: {images[pilih - 1]}")
    print("=" * 55)
    for k, v in meta.items():
        k_str = k.replace("_", " ").title()
        print(f"  - {k_str:<26} : {v}")
    print("=" * 55)


def _buat_citra_interaktif():
    print("\n=== PEMBUATAN CITRA BARU DARI DASAR ===")
    w = prompt_int("Masukkan lebar citra (misal 128): ", 4, 1024)
    h = prompt_int("Masukkan tinggi citra (misal 128): ", 4, 1024)
    print("Pilih mode warna:")
    print("[1] Grayscale (8-bit, 1 channel)")
    print("[2] True Color RGB (24-bit, 3 channel)")
    pilih_mode = prompt_int("Pilihan: ", 1, 2)
    mode = "L" if pilih_mode == 1 else "RGB"

    print("\nPilih pola citra:")
    print("[1] Gradien Halus (Spektrum Warna / Derajat Keabuan)")
    print("[2] Papan Catur (Checkerboard)")
    print("[3] Garis Striping Vertikal")
    print("[4] Lingkaran di Titik Pusat")
    print("[5] Warna Polos Konstan")
    pola_idx = prompt_int("Pola yang diinginkan: ", 1, 5)

    pola_map = {1: "gradien", 2: "catur", 3: "garis", 4: "lingkaran", 5: "kosong"}
    citra_baru = buat_citra_baru(w, h, mode, pola=pola_map[pola_idx])
    
    print("\n[OK] Citra baru berhasil dibuat di memori.")
    info = ekstrak_karakteristik(citra_baru)
    print(format_laporan_karakteristik(info, "Citra Baru Dibuat"))

    tanya_simpan = input("Simpan citra ini ke format file .BMP? (y/n): ").strip().lower()
    if tanya_simpan == 'y':
        nama = input("Masukkan nama file (misal: citra_baru.bmp): ").strip()
        if not nama:
            print("Penyimpanan dibatalkan (nama file kosong).")
        else:
            if not nama.lower().endswith(".bmp"):
                nama += ".bmp"
            path = os.path.join(IMG_DIR, nama)
            simpan_bmp_manual(citra_baru, path)
            print(f"[OK] File tersimpan di: {path}")

    display_comparison(citra_baru, citra_baru, f"Citra Baru ({pola_map[pola_idx]})")


def _ekspor_bmp_interaktif(citra):
    nama = input("Masukkan nama file BMP untuk disimpan (misal: hasil_ekspor.bmp): ").strip()
    if not nama:
        print("Penyimpanan dibatalkan (nama file kosong).")
        return
    if not nama.lower().endswith(".bmp"):
        nama += ".bmp"
    path = os.path.join(IMG_DIR, nama)
    simpan_bmp_manual(citra, path)
    print(f"[OK] Citra berhasil diekspor ke {path} secara manual tanpa library!")


def _impor_bmp_interaktif():
    images = [f for f in get_available_images() if f.lower().endswith('.bmp')]
    if not images:
        print("Tidak ada file format .bmp di folder img/.")
        manual_path = input("Ketik path file .bmp manual (atau Enter untuk batal): ").strip()
        if not manual_path or not os.path.exists(manual_path):
            return
        path = manual_path
    else:
        print("\n=== PILIH FILE BMP DI FOLDER IMG ===")
        for idx, name in enumerate(images, 1):
            print(f"[{idx}] {name}")
        pilih = prompt_int("Pilih nomor file (0 untuk batal): ", 0, len(images))
        if pilih == 0:
            return
        path = os.path.join(IMG_DIR, images[pilih - 1])

    citra, meta = muat_bmp_manual(path)
    print(f"\n[OK] Citra BMP berhasil dimuat secara manual tanpa library!")
    print(f"Resolusi: {citra.lebar}x{citra.tinggi} | Bit Depth: {meta['bit_depth']} bit | Mode: {citra.mode}")
    run(citra)


def run(original_img):
    """Fungsi utama yang dipanggil oleh alur kerja modul PCD."""
    while True:
        print("\n--- OPERASI KARAKTERISTIK, PEMBUATAN & EKSTRAKSI CITRA ---")
        print("[1] Ekstraksi Metadata & Karakteristik Citra (Resolusi, Bit Depth, Channel)")
        print("[2] Ekstraksi Nilai Intensitas Titik Piksel (x, y)")
        print("[3] Modifikasi Intensitas Titik Piksel (x, y)")
        print("[4] Ekstraksi Header File Citra Tanpa Library (BMP / PNG / JPG)")
        print("[5] Pembuatan Citra Baru dari Nol (Gradien, Papan Catur, Polos)")
        print("[6] Ekspor Citra Saat Ini ke File .BMP (Binary Writer Manual)")
        print("[7] Impor & Muat File .BMP (Binary Reader Manual)")
        print("[0] Selesai / Kembali")
        
        pilihan = prompt_int("Pilih menu: ", 0, 7)
        if pilihan == 0:
            break
        elif pilihan == 1:
            _tampilkan_karakteristik(original_img)
        elif pilihan == 2:
            _ekstraksi_intensitas_titik(original_img)
        elif pilihan == 3:
            _modifikasi_intensitas_titik(original_img)
        elif pilihan == 4:
            _inspeksi_header_file()
        elif pilihan == 5:
            _buat_citra_interaktif()
        elif pilihan == 6:
            _ekspor_bmp_interaktif(original_img)
        elif pilihan == 7:
            _impor_bmp_interaktif()



def run_standalone_ekstraksi():
    """Menu peluncur mandiri jika dijalankan langsung via python src_code/op_ekstraksi.py."""
    while True:
        print("\n" + "=" * 60)
        print("  MODUL OPERASI PEMBUATAN & EKSTRAKSI CITRA DIGITAL")
        print("=" * 60)
        print("[1] Pilih Citra yang Tersedia di img/ dan Analisis")
        print("[2] Buat Citra Baru dari Dasar (Tanpa Memuat File)")
        print("[3] Ekstraksi Header File Citra Biner Tanpa Library")
        print("[4] Impor & Muat File .BMP (Binary Reader Manual)")
        print("[0] Keluar")
        pilihan = prompt_int("Pilih opsi awal: ", 0, 4)
        if pilihan == 0:
            print("Keluar dari modul ekstraksi citra.")
            break
        elif pilihan == 1:
            run_standalone(run)
        elif pilihan == 2:
            _buat_citra_interaktif()
        elif pilihan == 3:
            _inspeksi_header_file()
        elif pilihan == 4:
            _impor_bmp_interaktif()


if __name__ == "__main__":
    run_standalone_ekstraksi()

