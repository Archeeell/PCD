"""Noise reduction dengan filter Median 3x3 untuk tiga citra tugas."""
from __future__ import annotations

import argparse
from pathlib import Path

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, buat_padding_pantul,
                                dari_pil, simpan_pil,
                                display_comparison, prompt_int, run_standalone)
else:
    from .utils import (Citra, buat_kosong, buat_padding_pantul,
                        dari_pil, simpan_pil,
                        display_comparison, prompt_int, run_standalone)

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = ("gambar_blur.png", "gambar_noise.png", "gambar_gelap.png")
WINDOW = 3


def median_filter(citra: Citra, window: int = WINDOW) -> Citra:
    """
    Ambil median lokal tiap kanal dengan padding refleksi.
    Gunakan sorted() -> nilai tengah -> round() -> klem.
    """
    if window < 1 or window % 2 == 0:
        raise ValueError("Ukuran jendela harus bilangan ganjil positif.")
    pad    = window // 2
    tengah = (window * window) // 2
    hasil  = buat_kosong(citra.lebar, citra.tinggi, citra.mode)

    for c in range(len(citra.kanal)):
        k_src  = citra.kanal[c]
        k_dst  = hasil.kanal[c]
        padded = buat_padding_pantul(k_src, citra.tinggi, citra.lebar,
                                     pad, pad, pad, pad)
        for y in range(citra.tinggi):
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                vals = []
                for wy in range(window):
                    row_p = padded[y + wy]
                    for wx in range(window):
                        vals.append(row_p[x + wx])
                vals.sort()
                v = round(vals[tengah])
                dst_row[x] = 0 if v < 0 else (255 if v > 255 else v)
    return hasil


def _load_pil_as_citra(path: Path) -> Citra:
    with Image.open(path) as src:
        mode = "L" if src.mode == "L" else "RGB"
        return dari_pil(src.convert(mode))


def process(inputs: list, output_dir: Path, window: int = WINDOW) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in inputs:
        citra  = _load_pil_as_citra(path)
        result = median_filter(citra, window)
        destination = output_dir / f"{path.stem}_median_{window}x{window}.png"
        simpan_pil(result, destination)
        print(f"Tersimpan: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--window", type=int, default=WINDOW)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "output" / "noise_reduction" / "median")
    args = parser.parse_args()
    inputs = args.inputs or [ROOT / "img" / name for name in DEFAULT_INPUTS]
    missing = [p for p in inputs if not p.is_file()]
    if missing:
        parser.error("File input tidak ditemukan: " + ", ".join(map(str, missing)))
    process(inputs, args.output_dir, args.window)


def run(original_img: Citra) -> None:
    print("\n--- REDUKSI NOISE: FILTER MEDIAN ---")
    window = prompt_int("Masukkan ukuran jendela Median ganjil (3, 5, 7, ...): ", min_val=1)
    if window % 2 == 0:
        print("Ukuran genap tidak valid.")
        return
    result = median_filter(original_img, window)
    display_comparison(original_img, result, f"Median {window}x{window}")


if __name__ == "__main__":
    run_standalone(run)
