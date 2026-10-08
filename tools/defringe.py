"""Remove light paper fringes from a cut-out sprite.

An edge pixel (touching transparency) is dropped when it is clearly lighter than
the art just inside it - the typical halo left when art was cut from a pale
background. Small enclosed holes are refilled afterwards.

Usage: python3 tools/defringe.py assets/buildings/home.png [more files...]
"""
import sys
import numpy as np, scipy.ndimage as nd
from PIL import Image

def defringe(path, passes=3, delta=22):
    a = np.array(Image.open(path).convert('RGBA')); c = a[:, :, :3].astype(float)
    lum = c @ [0.299, 0.587, 0.114]
    al = a[:, :, 3] > 0; orig = al.copy()
    for _ in range(passes):
        edge = al & ~nd.binary_erosion(al, border_value=0)
        inner = al & ~edge
        # mean luminance of interior pixels within 2 px
        k = np.ones((5, 5))
        s = nd.convolve(np.where(inner, lum, 0), k, mode='constant')
        n = nd.convolve(inner.astype(float), k, mode='constant')
        ref = np.where(n > 0, s / np.maximum(n, 1), lum)
        kill = edge & (lum > ref + delta)
        if not kill.any(): break
        al &= ~kill
    holes = nd.binary_fill_holes(al) & ~al
    lab, n = nd.label(holes); sz = nd.sum(holes, lab, range(1, n + 1))
    al |= np.isin(lab, [i + 1 for i, v in enumerate(sz) if v < 400]) & orig
    lab, n = nd.label(al); sz = nd.sum(al, lab, range(1, n + 1))
    al &= np.isin(lab, [i + 1 for i, v in enumerate(sz) if v >= 6])
    a[:, :, 3] = np.where(al, 255, 0); Image.fromarray(a).save(path)
    return int((orig & ~al).sum())

if __name__ == '__main__':
    for p in sys.argv[1:]: print(p, 'removed', defringe(p))
