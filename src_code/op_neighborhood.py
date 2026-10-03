"""Operasi Bertetangga / Persekitaran sesuai materi kuliah (mask SUM OF PRODUCTS)."""
import numpy as np
if __package__ in (None, ""):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src_code.utils import display_comparison, prompt_int, prompt_float, run_standalone
else:
    from .utils import display_comparison, prompt_int, prompt_float, run_standalone

SQRT2 = np.sqrt(2.0)
GRADIENTS = {
    "Roberts": (np.array([[1, 0], [0, -1]], float), np.array([[0, 1], [-1, 0]], float)),
    "Prewitt": (np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], float),
                np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], float)),
    "Sobel": (np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float),
              np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], float)),
    "Isotropik": (np.array([[-1, 0, 1], [-SQRT2, 0, SQRT2], [-1, 0, 1]], float),
                  np.array([[-1, -SQRT2, -1], [0, 0, 0], [1, SQRT2, 1]], float)),
}
LAPLACIANS = {
    "Laplacian 5 titik": np.array([[0,-1,0],[-1,4,-1],[0,-1,0]], float),
    "Laplacian 9 titik I": np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]], float),
    "Laplacian 9 titik II": np.array([[-2,1,-2],[1,4,1],[-2,1,-2]], float),
}

def _convolve_2d(channel, kernel):
    """Korelasi mask (SUM OF PRODUCTS) dengan padding tepi terpantul."""
    kh, kw = kernel.shape
    py_before, px_before = (kh - 1) // 2, (kw - 1) // 2
    py_after, px_after = kh - 1 - py_before, kw - 1 - px_before
    padded = np.pad(channel.astype(np.float64),
                    ((py_before, py_after), (px_before, px_after)), mode="reflect")
    out = np.zeros(channel.shape, dtype=np.float64)
    for y in range(channel.shape[0]):
        for x in range(channel.shape[1]):
            out[y, x] = np.sum(padded[y:y+kh, x:x+kw] * kernel)
    return out

def apply_kernel(img_array, kernel):
    if img_array.ndim == 2:
        return _convolve_2d(img_array, kernel)
    return np.stack([_convolve_2d(img_array[..., c], kernel) for c in range(img_array.shape[2])], axis=-1)

def _uint8(values):
    return np.clip(np.rint(values), 0, 255).astype(np.uint8)

def _combine(gx, gy, method):
    ax, ay = np.abs(gx), np.abs(gy)
    if method == 1: return ax + ay
    if method == 2: return np.maximum(ax, ay)
    if method == 3: return (ax + ay) / 2
    return np.sqrt(gx * gx + gy * gy)

def edge_detection(img_array, operator="Sobel", combination=4):
    """Operator gradien dari materi; kombinasi: jumlah, maksimum, rerata, magnitudo."""
    if operator in GRADIENTS:
        kx, ky = GRADIENTS[operator]
        return _combine(apply_kernel(img_array, kx), apply_kernel(img_array, ky), combination)
    return np.abs(apply_kernel(img_array, LAPLACIANS[operator]))

def smoothing(img_array, neighborhood=3):
    """Rerata seragam 5-tetangga, 3x3, atau 5x5 seperti mask materi."""
    if neighborhood == 5:
        kernel = np.array([[0,1,0],[1,1,1],[0,1,0]], float) / 5
    else:
        kernel = np.ones((neighborhood, neighborhood), float) / (neighborhood * neighborhood)
    return apply_kernel(img_array, kernel)

def sharpening(img_array, alpha=1.0, neighborhood=5):
    """Mask 5/9 titik; pusat 1+n*alpha dan tetangga -alpha."""
    if neighborhood == 5:
        kernel = np.array([[0,-alpha,0],[-alpha,1+4*alpha,-alpha],[0,-alpha,0]], float)
    else:
        kernel = np.full((3,3), -alpha, float)
        kernel[1,1] = 1 + 8*alpha
    return apply_kernel(img_array, kernel)

def median_filter(img_array, window=3):
    """Reduksi noise dengan median pada jendela tanpa bobot berukuran ganjil."""
    if window < 1 or window % 2 == 0:
        raise ValueError("Ukuran jendela median harus bilangan ganjil positif.")
    pad = window // 2
    def median_channel(channel):
        padded = np.pad(channel, ((pad,pad),(pad,pad)), mode="reflect")
        out = np.empty(channel.shape, dtype=np.float64)
        for y in range(channel.shape[0]):
            for x in range(channel.shape[1]):
                out[y,x] = np.median(padded[y:y+window, x:x+window])
        return out
    if img_array.ndim == 2: return median_channel(img_array)
    return np.stack([median_channel(img_array[...,c]) for c in range(img_array.shape[2])], axis=-1)

EMBOSS = {
    "Dari arah kiri": np.array([[-1,0,1],[-1,1,1],[-1,0,1]], float),
    "Dari arah kanan atas": np.array([[0,-1,-1],[1,1,-1],[1,1,0]], float),
}
def emboss_response(img_array, beta=2, direction="Dari arah kiri"):
    """Respons SUM OF PRODUCTS mentah sesuai contoh perhitungan materi."""
    kernel = EMBOSS[direction].copy()
    kernel[kernel != 0] *= beta
    kernel[1,1] = 1
    return apply_kernel(img_array, kernel)

def emboss(img_array, beta=2, direction="Dari arah kiri"):
    """Efek emboss ditampilkan dengan level dasar 128 agar terang/gelap tampak timbul."""
    return 128 + emboss_response(img_array, beta, direction)

def run(original_img):
    print("\n--- OPERASI BERTETANGGA / PERSEKITARAN ---")
    print("[1] Deteksi Tepi  [2] Penghalusan Citra  [3] Penajaman Citra")
    print("[4] Reduksi Noise (Median)  [5] Efek Emboss")
    op = prompt_int("Pilih sub-operasi neighborhood: ", 1, 5)
    if op == 1:
        names = list(GRADIENTS) + list(LAPLACIANS)
        for i, name in enumerate(names, 1): print(f"[{i}] {name}")
        operator = names[prompt_int("Pilih operator: ", 1, len(names))-1]
        if operator in GRADIENTS:
            print("[1] Jumlah  [2] Maksimum  [3] Rerata  [4] Magnitudo Euclidean")
            method = prompt_int("Pilih kombinasi K1 dan K2: ", 1, 4)
        else: method = 4
        result = _uint8(edge_detection(original_img, operator, method))
        label = f"Deteksi Tepi {operator}"
    elif op == 2:
        print("[1] 5 titik  [2] 9 titik (3x3)  [3] 25 titik (5x5)")
        choice = prompt_int("Pilih mask smoothing: ", 1, 3)
        n = [5,3,5][choice-1]
        result, label = _uint8(smoothing(original_img, n)), f"Smoothing {n} tetangga"
    elif op == 3:
        print("[1] 5 titik  [2] 9 titik")
        n = 5 if prompt_int("Pilih mask sharpening: ", 1, 2) == 1 else 9
        alpha = prompt_float("Masukkan derajat penajaman alpha: ")
        result, label = _uint8(sharpening(original_img, alpha, n)), f"Sharpening {n} titik (alpha={alpha})"
    elif op == 4:
        window = prompt_int("Masukkan ukuran jendela median ganjil (3, 5, 7, ...): ", 1)
        if window % 2 == 0: print("Ukuran genap tidak valid."); return
        result, label = _uint8(median_filter(original_img, window)), f"Reduksi Noise Median {window}x{window}"
    else:
        print("[1] Dari arah kiri  [2] Dari arah kanan atas")
        direction = list(EMBOSS)[prompt_int("Pilih arah emboss: ", 1, 2)-1]
        beta = prompt_float("Masukkan derajat emboss beta: ")
        result, label = _uint8(emboss(original_img, beta, direction)), f"Emboss {direction} (beta={beta})"
    display_comparison(original_img, result, label)


if __name__ == "__main__":
    run_standalone(run)
