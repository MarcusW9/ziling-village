"""Cut objects out of a painted map (grass / paving / dirt / water background).

Background = pixels whose colour matches a ground class AND that connect to the
crop's border. Holes inside the object are kept. Used for pieces taken from the
painted south map, which has no magenta background.
"""
import sys, json
import numpy as np, scipy.ndimage as nd
from PIL import Image

def ground(c, kinds):
    r, g, b = c[:, :, 0], c[:, :, 1], c[:, :, 2]
    mx, mn = c.max(2), c.min(2); m = c.mean(2); sat = mx - mn
    out = np.zeros(c.shape[:2], bool)
    if 'grass' in kinds: out |= (g > r + 12) & (g > b + 25) & (g > 90)
    if 'paving' in kinds: out |= (sat < 32) & (m > 118) & (m < 185) & (r - b > 14) & (r - b < 30)
    if 'dirt' in kinds: out |= (r - b > 70) & (r > 175) & (g > 140) & (sat < 110) & (m > 150)
    if 'water' in kinds: out |= (g > r + 15) & (b > r) & (g < 150) & (m < 130)
    return out

def cut(src, box, kinds, keep_min=30, keep_rects=()):
    im = np.array(Image.open(src).convert('RGB')).astype(int)
    x0, y0, x1, y1 = box; c = im[y0:y1, x0:x1]
    gnd = ground(c, kinds)
    gnd = nd.binary_closing(np.pad(gnd, 2, mode='edge'), iterations=1)[2:-2, 2:-2]
    lab, n = nd.label(gnd)
    ring = np.zeros_like(gnd); ring[:3] = ring[-3:] = True; ring[:, :3] = ring[:, -3:] = True
    edge = set(np.unique(lab[ring])) - {0}
    bg = np.isin(lab, list(edge))
    fg = nd.binary_fill_holes(~bg)
    fg = nd.binary_opening(fg, iterations=1)
    lab, n = nd.label(fg); sz = nd.sum(fg, lab, range(1, n + 1))
    if n:
        # keep the main object plus any piece touching it of it (pots, posts), drop stray specks
        main = lab == int(np.argmax(sz)) + 1
        near = nd.binary_dilation(main, iterations=1)
        for kx0, ky0, kx1, ky1 in keep_rects:  # map-space rectangles whose pieces must be kept
            near[max(0, ky0 - y0):ky1 - y0, max(0, kx0 - x0):kx1 - x0] = True
        keep = [i + 1 for i, v in enumerate(sz) if v >= keep_min and (near & (lab == i + 1)).any()]
        fg = np.isin(lab, keep)
    a = np.dstack([c, np.where(fg, 255, 0)]).astype('uint8')
    o = Image.fromarray(a, 'RGBA'); return o.crop(o.getbbox())

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    for name, item in spec['items'].items():
        box, kinds = item[0], item[1]
        o = cut(spec['src'], box, kinds, keep_rects=item[2] if len(item) > 2 else ()); o.save(f"{spec['out']}/{name}.png"); print(name, o.size)
