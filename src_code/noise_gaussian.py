"""Noise reduction dengan filter Gaussian 3x3 untuk tiga citra tugas."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import (Citra, buat_kosong, korelasi_kanal,
                                dari_pil, simpan_pil,
                                display_comparison, prompt_int, run_standalone)
else:
    from .utils import (Citra, buat_kosong, korelasi_kanal,
                        dari_pil, simpan_pil,
                        display_comparison, prompt_int, run_standalone)

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = ("gambar_blur.png", "gambar_noise.png", "gambar_gelap.png")
SIGMA = 1.0


def gaussian_kernel(size: int = 3, sigma: float = SIGMA) -> list:
    """
    Buat mask Gaussian diskret yang dinormalisasi agar jumlah bobot = 1.
    Identik dengan versi numpy: coords = arange - size//2, kernel[y][x] =
    exp(-(x^2+y^2)/(2*sigma^2)), dibagi total.
    """
    if size < 1 or size % 2 == 0:
        raise ValueError("Ukuran mask harus bilangan ganjil positif.")
    if sigma <= 0:
        raise ValueError("Sigma harus lebih besar dari nol.")
    half = size // 2
    # Buat kernel mentah
    kernel_raw = [[0.0] * size for _ in range(size)]
    total = 0.0
    for ky in range(size):
        y_coord = ky - half
        for kx in range(size):
            x_coord = kx - half
            v = math.exp(-(x_coord * x_coord + y_coord * y_coord) / (2.0 * sigma * sigma))
            kernel_raw[ky][kx] = v
            total += v
    # Normalisasi
    for ky in range(size):
        for kx in range(size):
            kernel_raw[ky][kx] /= total
    return kernel_raw


def gaussian_filter(citra: Citra, size: int = 3, sigma: float = SIGMA) -> Citra:
    """
    Konvolusi tiap kanal citra dengan mask Gaussian dan padding refleksi.
    Hasil = round() lalu klem ke 0-255 (sesuai np.rint + clip).
    """
    kernel = gaussian_kernel(size, sigma)
    hasil  = buat_kosong(citra.lebar, citra.tinggi, citra.mode)

    for c in range(len(citra.kanal)):
        kanal_float = korelasi_kanal(citra.kanal[c], citra.tinggi, citra.lebar,
                                      kernel, size, size)
        k_dst = hasil.kanal[c]
        for y in range(citra.tinggi):
            src_row = kanal_float[y]
            dst_row = k_dst[y]
            for x in range(citra.lebar):
                v = round(src_row[x])
                dst_row[x] = 0 if v < 0 else (255 if v > 255 else v)
    return hasil


def _load_pil_as_citra(path: Path) -> Citra:
    with Image.open(path) as src:
        mode = "L" if src.mode == "L" else "RGB"
        return dari_pil(src.convert(mode))


def process(inputs: list, output_dir: Path, size: int = 3,
            sigma: float = SIGMA) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in inputs:
        citra  = _load_pil_as_citra(path)
        result = gaussian_filter(citra, size, sigma)
        destination = output_dir / f"{path.stem}_gaussian_{size}x{size}.png"
        simpan_pil(result, destination)
        print(f"Tersimpan: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--size",  type=int,   default=3)
    parser.add_argument("--sigma", type=float, default=SIGMA)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "output" / "noise_reduction" / "gaussian")
    args = parser.parse_args()
    inputs = args.inputs or [ROOT / "img" / name for name in DEFAULT_INPUTS]
    missing = [p for p in inputs if not p.is_file()]
    if missing:
        parser.error("File input tidak ditemukan: " + ", ".join(map(str, missing)))
    process(inputs, args.output_dir, args.size, args.sigma)


def run(original_img: Citra) -> None:
    print("\n--- REDUKSI NOISE: FILTER GAUSSIAN ---")
    size = prompt_int("Masukkan ukuran mask Gaussian ganjil (3, 5, 7, ...): ", min_val=1)
    if size % 2 == 0:
        print("Ukuran genap tidak valid.")
        return
    sigma_val = float(input("Masukkan nilai sigma Gaussian (default 1.0): ").strip() or "1.0")
    result = gaussian_filter(original_img, size, sigma_val)
    display_comparison(original_img, result, f"Gaussian {size}x{size} (sigma={sigma_val})")


if __name__ == "__main__":
    run_standalone(run)
