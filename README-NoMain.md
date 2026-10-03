# Branch `NoMain`

Branch ini tidak menyertakan `src_code/main.py`. Jalankan modul operasi yang dibutuhkan secara langsung; tiap modul menyediakan fungsi `run(image)` sehingga alur operasi dan rumusnya mudah dibaca untuk laporan.

## Menjalankan modul secara langsung

```powershell
python src_code/op_titik.py
python src_code/op_geometri.py
python src_code/op_bingkai.py
python src_code/op_global.py
python src_code/op_neighborhood.py
```

Setiap perintah meminta pengguna memilih citra dari folder `img/`, lalu menampilkan submenu modul kategori. Skrip reduksi noise yang sudah mandiri tetap tersedia: `src_code/noise_mean.py`, `src_code/noise_gaussian.py`, `src_code/noise_median.py`, dan `src_code/noise_midpoint.py`.
