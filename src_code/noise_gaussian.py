"""Noise reduction dengan filter Gaussian 3x3 untuk tiga citra tugas."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = ("gambar_blur.png", "gambar_noise.png", "gambar_gelap.png")
SIGMA = 1.0


def gaussian_kernel(size: int = 3, sigma: float = SIGMA) -> np.ndarray:
    """Buat mask Gaussian diskret yang dinormalisasi agar jumlah bobot = 1."""
    if size < 1 or size % 2 == 0:
        raise ValueError("Ukuran mask harus bilangan ganjil positif.")
    if sigma <= 0:
        raise ValueError("Sigma harus lebih besar dari nol.")
    coords = np.arange(size, dtype=np.float64) - size // 2
    xx, yy = np.meshgrid(coords, coords)
    kernel = np.exp(-(xx * xx + yy * yy) / (2 * sigma * sigma))
    return kernel / kernel.sum()


def gaussian_filter(image: np.ndarray, size: int = 3, sigma: float = SIGMA) -> np.ndarray:
    """Konvolusi tiap kanal citra dengan mask Gaussian dan padding refleksi."""
    kernel = gaussian_kernel(size, sigma)
    pad = size // 2
    if image.ndim == 2:
        padded = np.pad(image.astype(np.float64), pad, mode="reflect")
        patches = np.lib.stride_tricks.sliding_window_view(padded, (size, size))
        result = np.einsum("ijkl,kl->ij", patches, kernel, optimize=True)
    else:
        channels = []
        for channel in range(image.shape[2]):
            padded = np.pad(image[..., channel].astype(np.float64), pad, mode="reflect")
            patches = np.lib.stride_tricks.sliding_window_view(padded, (size, size))
            channels.append(np.einsum("ijkl,kl->ij", patches, kernel, optimize=True))
        result = np.stack(channels, axis=-1)
    return np.clip(np.rint(result), 0, 255).astype(np.uint8)


def process(inputs: list[Path], output_dir: Path, size: int = 3, sigma: float = SIGMA) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in inputs:
        with Image.open(path) as source:
            mode = "L" if source.mode == "L" else "RGB"
            image = np.asarray(source.convert(mode), dtype=np.uint8)
        result = gaussian_filter(image, size, sigma)
        destination = output_dir / f"{path.stem}_gaussian_{size}x{size}.png"
        Image.fromarray(result).save(destination)
        print(f"Tersimpan: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path,
                        help="Path gambar input; default: tiga gambar tugas dalam img/.")
    parser.add_argument("--size", type=int, default=3, help="Ukuran mask Gaussian ganjil (default: 3).")
    parser.add_argument("--sigma", type=float, default=SIGMA, help="Sigma Gaussian (default: 1.0).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "noise_reduction" / "gaussian")
    args = parser.parse_args()
    inputs = args.inputs or [ROOT / "img" / name for name in DEFAULT_INPUTS]
    missing = [path for path in inputs if not path.is_file()]
    if missing:
        parser.error("File input tidak ditemukan: " + ", ".join(map(str, missing)))
    process(inputs, args.output_dir, args.size, args.sigma)


if __name__ == "__main__":
    main()
