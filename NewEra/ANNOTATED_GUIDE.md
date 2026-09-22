# PCD — Annotated Code

Branch ini berisi versi kode dengan komentar penjelas pada setiap statement penting agar hubungan implementasi program dengan materi Pengolahan Citra lebih mudah dipelajari dan dipresentasikan.

## Pemetaan materi → kode

| Materi | File | Implementasi |
|---|---|---|
| Operasi titik — Brightness | `NewEra/op_brightness.py` | (K_o = K_i + C) |
| Operasi titik — Contrast | `NewEra/op_contrast.py` | (K_o = G(K_i-P)+P) |
| Operasi titik — Negasi | `NewEra/op_invert.py` | (K_o = 255-K_i) |
| Konversi RGB → Grayscale | `NewEra/op_color_convert.py` | pembobot RGB |
| Operasi titik — Thresholding | `NewEra/op_threshold.py` | ambang tunggal → 0/255 |
| Operasi geometri | `NewEra/op_geometri.py` | flipping, rotating, cropping, scaling |
| Operasi berbasis bingkai | `NewEra/op_bingkai.py` | blending, motion detection, logic |
| Operasi global | `NewEra/op_global.py` | histogram equalization |
| Dukungan umum | `NewEra/utils.py` | loading citra, histogram, visualisasi, input |
| Pengendali program | `NewEra/main.py` | pemilihan citra dan menu operasi |

## Catatan kesesuaian dengan materi

1. Grayscale: materi yang terbaca menuliskan bobot NTSC R=0.299, G=0.587, B=0.144, sedangkan kode menggunakan B=0.114. Komentar pada kode menandai nilai yang benar-benar digunakan implementasi.
2. Histogram equalization: materi menuliskan fungsi pembulatan `round`, sedangkan kode menggunakan `floor`. Komentar pada `op_global.py` menandai perbedaan ini.
3. Thresholding pada kode menggunakan keluaran 0 dan 255. Secara konsep materi menyebut citra biner sebagai 0 dan 1; penggunaan 0/255 merupakan representasi tampilan 8-bit dari dua kelas tersebut.
4. Rotasi bebas pada kode menggunakan inverse mapping dan nearest-neighbor supaya piksel keluaran dapat dipetakan kembali ke citra sumber.

Branch dibuat terpisah dari `main`, sehingga kode utama tidak diubah oleh anotasi ini.
