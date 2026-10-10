"""Cut the two village children's sheets and embed their frames into index.html as KIDS.

Sources (magenta background):
  assets/source-sheets/npc_kid_boy.png   rows: 4 front walk, 4 run (facing right), cart / sit / cheer
  assets/source-sheets/npc_kid_girl.png  rows: front / 3-quarter / 2 side walk, reach / clap / point,
                                         2 sitting-play / crouch / 2 jump
Poses are found as connected blobs and named in reading order (row, then x). Side poses
face right; the game mirrors them for left. Each sheet is scaled by its own front pose,
since the sheets are drawn at slightly different sizes.
Run from the repo root:  python3 tools/kids.py
"""
import io, json, base64, re
import numpy as np, scipy.ndimage as nd
from PIL import Image

KIDS = {
    'boy': ('assets/source-sheets/npc_kid_boy.png', 18,
            'front0 front1 front2 front3 run0 run1 run2 run3 cart sit cheer'.split()),
    'girl': ('assets/source-sheets/npc_kid_girl.png', 17,
             'front walk3q side0 side1 reach clap point sit0 sit1 crouch jump0 jump1'.split()),
}
ROW = 150      # sheet rows are ~180 px apart; poses whose top falls in the same band share a row

def cut(src, names, out):
    a = np.array(Image.open(src).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fg = ~((r - g > 90) & (b - g > 90))
    for _ in range(2):                                  # peel magenta-tinted edge pixels, as magcut does
        e = fg & ~nd.binary_erosion(fg); fg &= ~(e & (r - g > 40) & (b - g > 40))
    lab, n = nd.label(nd.binary_dilation(fg, iterations=3))
    objs = [(o, i + 1) for i, o in enumerate(nd.find_objects(lab))
            if (o[0].stop - o[0].start) * (o[1].stop - o[1].start) > 2000]
    objs.sort(key=lambda t: (t[0][0].start // ROW, t[0][1].start))
    assert len(objs) == len(names), (src, len(objs))
    frames = {}
    for (o, i), nm in zip(objs, names):
        m = (lab[o] == i) & fg[o]
        c = np.dstack([a[o], np.where(m, 255, 0)]).astype('uint8')
        im = Image.fromarray(c, 'RGBA'); im = im.crop(im.getbbox()); im.save(f'{out}/{nm}.png'); frames[nm] = im
    return frames

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

data = {}
for kid, (src, height, names) in KIDS.items():
    frames = cut(src, names, f'assets/sprites/kids/{kid}')
    s = height / frames[names[0]].height
    data[kid] = {}
    for nm, im in frames.items():
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        x = np.array(im); x[..., 3] = np.where(x[..., 3] > 110, 255, 0); im = Image.fromarray(x)
        data[kid][nm] = [uri(im), im.width, im.height]

s = open('index.html').read()
s, n = re.subn(r'const KIDS=.*?;\n', lambda m: 'const KIDS=' + json.dumps(data) + ';\n', s, count=1, flags=re.S)
assert n == 1, 'KIDS placeholder missing'
open('index.html', 'w').write(s)
print({k: {nm: v[1:] for nm, v in d.items()} for k, d in data.items()})
