"""Rebuild the six spirit sprites at one shared visible height and embed them in index.html.

Each spirit's art fills its frame differently, so a fixed frame size makes some look
bigger than others. This scales every spirit so its front pose is TARGET px tall,
applies the same scale to its other poses, and bottom-aligns them in a 22x22 frame.
"""
import json, io, base64, re
import numpy as np
from PIL import Image

TARGET = 16          # visible spirit height in px (player is ~28 px tall)
FRAME = 22
SHEETS = {'XZ': 'xz', 'CC': 'cc', 'QQ': 'qq', 'JJ': 'jj', 'RY': 'ry', 'YY': 'yy'}
POSES = ['front', 'happy', 'sleep']

def frames(pre):
    sheet = Image.open(f'assets/sprites/{pre}_sheet_32.png').convert('RGBA')
    return {p: sheet.crop((i * 32, 0, i * 32 + 32, 32)) for i, p in enumerate(POSES)}

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

s = open('index.html').read()
for const, pre in SHEETS.items():
    fr = frames(pre)
    bb = fr['front'].getbbox()
    scale = TARGET / (bb[3] - bb[1])
    out = {}
    for p, im in fr.items():
        im = im.crop(im.getbbox())
        w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        im = im.resize((min(w, FRAME), min(h, FRAME)), Image.LANCZOS)
        a = np.array(im); a[:, :, 3] = np.where(a[:, :, 3] > 110, 255, 0); im = Image.fromarray(a)
        f = Image.new('RGBA', (FRAME, FRAME)); f.paste(im, ((FRAME - im.width) // 2, FRAME - im.height), im)
        out[p] = uri(f)
    pat = r"const %s=\{\};for\(const \[k,u\] of Object\.entries\(\{.*?\}\)\)" % const
    new = "const %s={};for(const [k,u] of Object.entries(%s))" % (const, json.dumps(out))
    s, n = re.subn(pat, lambda m: new, s, count=1, flags=re.S)
    assert n == 1, const
    print(const, 'scale %.2f' % scale)
open('index.html', 'w').write(s)
