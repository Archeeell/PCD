# NoLibrary — Versi Manual tanpa NumPy

Cabang `NoLibrary` dari repositori [Archeeell/PCD](https://github.com/Archeeell/PCD).
Semua komputasi ditulis secara manual menggunakan **loop piksel dan formula dari
materi kuliah Pengolahan Citra (Idhawati Hestiningsih)**, tanpa numpy, cv2, scipy,
atau modul pemrosesan PIL.

---

## Cara Menjalankan (Pola NoMain)

Setiap modul berjalan mandiri tanpa `main.py`:

```bash
# Instal dependensi
pip install -r requirements.txt

# Jalankan modul secara langsung
python src_code/op_titik.py
python src_code/op_geometri.py
python src_code/op_bingkai.py
python src_code/op_global.py
python src_code/op_neighborhood.py
python src_code/noise_mean.py
python src_code/noise_median.py
python src_code/noise_midpoint.py
python src_code/noise_gaussian.py

# Jalankan uji materi (tanpa pytest)
python tests/uji_materi.py
```

---

## Representasi Citra (Kelas `Citra`)

| Atribut | Tipe | Keterangan |
|---------|------|-----------|
| `lebar`  | int | jumlah kolom |
| `tinggi` | int | jumlah baris |
| `mode`   | str | `"L"` = grayscale, `"RGB"` = warna |
| `kanal`  | list | `kanal[c][y][x]` = nilai piksel int 0–255 |

Piksel dibaca **sekali** saat `load_image()` via `getpixel`; semua operasi
bekerja pada list Python biasa; hasil ditulis kembali ke PIL hanya via `ke_pil()`
untuk tampilan/simpan.

---

## Pemetaan NumPy → Manual

| NumPy / SciPy | Pendekatan Manual |
|---|---|
| `np.array(img)` | `dari_pil(img)` → `Citra` |
| `np.clip(val, 0, 255)` | fungsi `klem(val)` |
| `np.pad(..., mode='reflect')` | `buat_padding_pantul()` dengan `indeks_pantul()` |
| `np.sum(patch * kernel)` | loop `korelasi_kanal()` |
| `np.histogram(channel, bins=256)` | loop `compute_histogram()` |
| `np.cumsum(hist)` | loop kumulatif manual |
| `np.floor(...)` | `math.floor(...)` |
| `np.rint(val)` | `round(val)` (half-to-even) |
| `np.median(patch)` | `sorted(vals)[tengah]` |
| `np.rot90(arr, k=-1)` | loop `rotate_90_cw()` |
| `np.rot90(arr, k=2)` | loop `rotate_180_cw()` |
| `np.meshgrid(...)` | nested loop `rotate_free()` |
| `np.exp(...)` | `math.exp(...)` |
| `np.sqrt(...)` | `math.sqrt(...)` |
| `np.dot(rgb, [0.299,...])` | loop float `0.299*R + 0.587*G + 0.114*B` |
| `Image.fromarray(arr)` | `ke_pil(citra)` menggunakan `putpixel` |

---

## Formula PDF yang Digunakan

1. **Brightness**: Ko = Ki + c, klem [0, 255]
2. **Contrast**: Ko = factor × (Ki − pivot) + pivot, klem lalu truncation
3. **Negasi**: Ko = 255 − Ki
4. **Grayscale**: Ko = 0.299R + 0.587G + 0.114B, truncation
5. **Threshold**: Ko = 255 jika Ki ≥ T, else 0
6. **Flip H**: x' = w − 1 − x
7. **Flip V**: y' = h − 1 − y
8. **Rotasi 90 CW**: x_dst = h_baru−1−y_src, y_dst = x_src
9. **Rotasi bebas (CCW)**: inverse mapping dengan nearest-neighbor, round()
10. **Crop**: x' = x − xL, y' = y − yT
11. **Scale NN**: src_x = int(x/Sh) diklem ke w−1
12. **Blending**: C = wa·A + wb·B, klem, truncation
13. **Deteksi Gerakan**: C = |A − B|
14. **Logika AND/OR/XOR/SUB/NOT**: dari luminance ≥ 128 → biner
15. **Ekualisasi**: LUT[i] = floor(Ci × max_level / (w·h) + ε)
16. **Korelasi (neighborhood)**: ΣΣ f(x,y)·h(s,t) (kernel tidak dibalik)
17. **Emboss**: 128 + Σ(kernel × piksel), pusat kernel = 1
18. **Gaussian**: exp(−(x²+y²)/(2σ²)) dinormalisasi

---

## Deviasi dari Versi NumPy

### Koreksi #1: Smoothing "25 titik (5x5)"
**Versi numpy**: opsi 3 (n=5) memanggil `smoothing(n=5)` yang memakai
mask **plus 5-titik** (bukan 5x5 penuh). Ini adalah bug.

**Versi manual**: opsi 3 memakai mask **5x5 penuh** dengan bobot 1/25,
sesuai materi PDF. Opsi 1 (5-titik) dan opsi 2 (3x3) tidak berubah.

### Koreksi #2: Operasi Bingkai dengan ukuran/mode berbeda
**Versi numpy**: crash `ValueError` (broadcast) jika A dan B berbeda
ukuran atau satu grayscale satu RGB.

**Versi manual**: potong ke area bersama (min lebar, min tinggi, dari
pojok kiri-atas) dan konversi grayscale ke RGB jika perlu.

---

## Temuan (Findings)

1. **Isotropik K2 di PDF**: PDF halaman menulis K2 = 177, tetapi
   perhitungan manual dengan formula −(A + √2·B + C) dari matriks 5×5
   menghasilkan ≈ −174.85 → |K2| ≈ 175. Perbedaan ini tampaknya
   merupakan kesalahan aritmetika di PDF. Implementasi mengikuti
   formula yang benar; uji menggunakan toleransi ±3.

2. **Formula ekualisasi PDF (teks vs tabel)**: Teks PDF menggunakan
   `round(Ci × (2^k − 1) / N)` yang menghasilkan hasil berbeda dari
   tabel PDF hlm. 24. Implementasi mengikuti tabel (identik dengan
   kode numpy asli: `floor(Ci × max_level / N + 1e-9)`).

3. **Rotasi bebas dan piksel di luar batas**: Piksel tujuan yang
   sumbernya di luar batas citra dibiarkan hitam (0), konsisten
   dengan `np.zeros` pada versi numpy.

4. **Median di noise_*.py vs op_neighborhood.py**: Keduanya
   menggunakan sorted() + nilai tengah. Versi op_neighborhood.py
   menampilkan progres untuk citra besar.

---

## Larangan yang Dipenuhi

Tidak ada `import numpy`, `import cv2`, `import scipy`, atau
fungsi PIL terlarang (`PIL.ImageOps`, `Image.filter`, `Image.fromarray`,
`np.asarray`, dst.) di dalam folder `src_code/`.

Verifikasi:
```bash
grep -r "import numpy\|import cv2\|import scipy\|fromarray\|np\." src_code/
```
