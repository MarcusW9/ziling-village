"""Embed the rowing-boat animation (boatman + covered boat) in index.html.

Frames: assets/sprites/boat/frame0-3.png, cut from assets/source-sheets/boat_rower.png.
The frames are aligned on the black canopy (same size in every frame) so the boat
stays still and only the boatman and oar move, then scaled so the hull is ~66 px,
the length of the earlier boat sprite. The bow sits at canvas x = BOW_X, the keel
at the canvas bottom, so the game can place it exactly where the old boat was.
"""
import json, io, base64, re
import numpy as np, scipy.ndimage as nd
from PIL import Image

frames = [Image.open(f'assets/sprites/boat/frame{k}.png').convert('RGBA') for k in range(4)]
def canopy(im):
    a = np.array(im).astype(int); al = a[:, :, 3] > 0
    dark = (a[:, :, :3].max(2) < 50) & al
    lab, n = nd.label(nd.binary_closing(dark, iterations=2)); sz = nd.sum(dark, lab, range(1, n + 1))
    ys, xs = np.where(lab == int(np.argmax(sz)) + 1); return xs.max(), ys.max()
anch = [canopy(f) for f in frames]
ax, ay = max(a[0] for a in anch), max(a[1] for a in anch)
big = []
for f, (cx, cy) in zip(frames, anch):
    c = Image.new('RGBA', (900, 500)); c.paste(f, (200 + ax - cx, 100 + ay - cy), f); big.append(c)
bb = [c.getbbox() for c in big]
box = (min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb))
S = 0.16
out = []
for c in big:
    c = c.crop(box); c = c.resize((round(c.width * S), round(c.height * S)), Image.LANCZOS)
    a = np.array(c); a[:, :, 3] = np.where(a[:, :, 3] > 100, 255, 0)
    b = io.BytesIO(); Image.fromarray(a).save(b, 'PNG'); out.append('data:image/png;base64,' + base64.b64encode(b.getvalue()).decode())
W, H = round((box[2] - box[0]) * S), round((box[3] - box[1]) * S)
s = open('index.html').read()
s, n = re.subn(r'const BOATF=.*?;\n', lambda m: 'const BOATF=%s;\n' % json.dumps({'w': W, 'h': H, 'frames': out}), s, count=1, flags=re.S)
assert n == 1
open('index.html', 'w').write(s); print('frame size', W, H)
