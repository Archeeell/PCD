"""Noise reduction dengan filter Median 3x3 untuk tiga citra tugas."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = ("gambar_blur.png", "gambar_noise.png", "gambar_gelap.png")
WINDOW = 3


def median_filter(image: np.ndarray, window: int = WINDOW) -> np.ndarray:
    """Ambil median lokal tiap kanal dengan padding refleksi."""
    if window < 1 or window % 2 == 0:
        raise ValueError("Ukuran jendela harus bilangan ganjil positif.")
    pad = window // 2
    if image.ndim == 2:
        padded = np.pad(image, pad, mode="reflect")
        patches = np.lib.stride_tricks.sliding_window_view(padded, (window, window))
        result = np.median(patches, axis=(-2, -1))
    else:
        channels = []
        for channel in range(image.shape[2]):
            padded = np.pad(image[..., channel], pad, mode="reflect")
            patches = np.lib.stride_tricks.sliding_window_view(padded, (window, window))
            channels.append(np.median(patches, axis=(-2, -1)))
        result = np.stack(channels, axis=-1)
    return np.clip(np.rint(result), 0, 255).astype(np.uint8)


def process(inputs: list[Path], output_dir: Path, window: int = WINDOW) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in inputs:
        with Image.open(path) as source:
            mode = "L" if source.mode == "L" else "RGB"
            image = np.asarray(source.convert(mode), dtype=np.uint8)
        result = median_filter(image, window)
        destination = output_dir / f"{path.stem}_median_{window}x{window}.png"
        Image.fromarray(result).save(destination)
        print(f"Tersimpan: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", type=Path,
                        help="Path gambar input; default: tiga gambar tugas dalam img/.")
    parser.add_argument("--window", type=int, default=WINDOW, help="Ukuran jendela ganjil (default: 3).")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "noise_reduction" / "median")
    args = parser.parse_args()
    inputs = args.inputs or [ROOT / "img" / name for name in DEFAULT_INPUTS]
    missing = [path for path in inputs if not path.is_file()]
    if missing:
        parser.error("File input tidak ditemukan: " + ", ".join(map(str, missing)))
    process(inputs, args.output_dir, args.window)


if __name__ == "__main__":
    main()
