# Branch `NoMain`

Branch ini mempertahankan menu pada `src_code/main.py` dan menambahkan cara menjalankan setiap modul kategori secara langsung. Setiap modul tetap menyediakan fungsi `run(image)` sehingga alur operasi dan rumusnya mudah dibaca untuk laporan.

## Menjalankan modul secara langsung

```powershell
python src_code/op_titik.py
python src_code/op_geometri.py
python src_code/op_bingkai.py
python src_code/op_global.py
python src_code/op_neighborhood.py
```

Setiap perintah meminta pengguna memilih citra dari folder `img/`, lalu menampilkan submenu modul tersebut. Skrip reduksi noise yang sudah mandiri tetap tersedia: `noise_mean.py`, `noise_gaussian.py`, `noise_median.py`, dan `noise_midpoint.py`.

## Menjalankan menu gabungan

Untuk tetap memakai pemilih kategori yang sudah ada, jalankan `python src_code/main.py`.
