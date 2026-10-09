"""Cut the villager sheets and embed them as NPCs in index.html.

Each sheet (assets/source-sheets/npc_<name>.png, magenta background) is split into
poses by empty magenta columns, saved to assets/sprites/npcs/<name>/poseN.png, scaled
so the front pose is HEIGHT px tall (Granny Wang's height), and written into the
NPCS constant with a home position. An NPC shows its 'idle' pose, and its 'greet'
pose when the player is within 48 px.
Run from the repo root:  python3 tools/npcs.py
"""
import json, io, base64, re, os
import numpy as np, scipy.ndimage as nd
from PIL import Image

HEIGHT = 26
# name: (scene, x, y-base on the 640x360 map, idle pose, greet pose, flip-to-face-left, height px)
# heights: the player is 25 px; adults 25-26, so they read as the player's peers
NPCS = {
    'teahouse':    ('village', 178, 151, 0, 5, False, 26),   # beside the tea tray, bows
    'shopkeeper':  ('village', 506, 132, 0, 3, False, 25),   # in front of the stalls, offers an apple
    'calligrapher':('village', 347, 124, 0, 3, False, 26),   # by his studio door, strokes his beard (back view and brush swirl overlap on the sheet, so they cut as one piece)
    'innkeeper':   ('south',   546, 166, 0, 5, False, 25),   # on the inn terrace, waves
}

def split(path):
    im = np.array(Image.open(path).convert('RGB')).astype(int); r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    fg = ~((r - g > 60) & (b - g > 60))
    for _ in range(2):
        e = fg & ~nd.binary_erosion(fg); fg &= ~(e & (r - g > 30) & (b - g > 30))
    lab, n = nd.label(fg); sz = nd.sum(fg, lab, range(1, n + 1))
    fg = np.isin(lab, [i + 1 for i, v in enumerate(sz) if v >= 12])
    cols = fg.sum(0) > 0
    runs, start = [], None
    for x, c in enumerate(list(cols) + [False]):
        if c and start is None: start = x
        if not c and start is not None:
            if runs and start - runs[-1][1] < 6: runs[-1][1] = x      # tiny gaps stay in the same pose
            else: runs.append([start, x])
            start = None
    out = []
    for x0, x1 in runs:
        if x1 - x0 < 20: continue
        a = np.dstack([im[:, x0:x1], np.where(fg[:, x0:x1], 255, 0)]).astype('uint8')
        o = Image.fromarray(a, 'RGBA'); out.append(o.crop(o.getbbox()))
    return out

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

data = []
for name, (scene, x, y, idle, greet, flip, HEIGHT) in NPCS.items():
    poses = split(f'assets/source-sheets/npc_{name}.png')
    os.makedirs(f'assets/sprites/npcs/{name}', exist_ok=True)
    for i, p in enumerate(poses): p.save(f'assets/sprites/npcs/{name}/pose{i}.png')
    s = HEIGHT / poses[0].height
    def fr(p):
        q = p.resize((max(1, round(p.width * s)), max(1, round(p.height * s))), Image.LANCZOS)
        a = np.array(q); a[:, :, 3] = np.where(a[:, :, 3] > 110, 255, 0); q = Image.fromarray(a)
        if flip: q = q.transpose(Image.FLIP_LEFT_RIGHT)
        return [uri(q), q.width, q.height]
    data.append({'name': name, 'scene': scene, 'x': x, 'y': y, 'idle': fr(poses[idle]), 'greet': fr(poses[greet])})
    print(name, len(poses), 'poses')

s = open('index.html').read()
s, n = re.subn(r'const NPCS=.*?;\n', lambda m: 'const NPCS=%s;\n' % json.dumps(data), s, count=1, flags=re.S)
assert n == 1
open('index.html', 'w').write(s)
