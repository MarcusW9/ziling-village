"""Embed the player's 4-direction walk cycle in index.html.

Source: assets/sprites/player/fNN.png, cut from assets/source-sheets/player_walk.png.
  down = f00-f03, up = f04-f07, right = f10 f14 f15, left = f08 f11 f12.
  (f09 and f13 face the viewer and are unused. Facing was checked by where the face
  sits relative to the hair; mixing directions in one cycle makes the player 'moonwalk'.)
All frames share one scale (the front frame is HEIGHT px tall) and are bottom-centred
in a W x H frame so the feet stay put while walking.
"""
import json, io, base64, re
from PIL import Image

HEIGHT, W = 25, 26
D = 'assets/sprites/player/'
SETS = {'down': [0, 1, 2, 3], 'up': [4, 5, 6, 7], 'right': [10, 14, 15], 'left': [8, 11, 12]}
# Each direction is scaled by its own tallest frame: the sheet draws the side views
# ~12% taller than the front, which clipped the head and made the player grow sideways.
CANVAS = HEIGHT + 6   # headroom so no frame is ever cut off
out = {}
for name, idx in SETS.items():
    scale = HEIGHT / max(Image.open(D + f'f{k:02d}.png').height for k in idx)
    for n, k in enumerate(idx):
        im = Image.open(D + f'f{k:02d}.png').convert('RGBA')
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        f = Image.new('RGBA', (W, CANVAS)); f.paste(im, ((W - im.width) // 2, CANVAS - im.height), im)
        b = io.BytesIO(); f.save(b, 'PNG'); out[f'{name}{n}'] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
s = open('index.html').read()
s, c = re.subn(r'const PL=\{\};for\(const \[k,u\] of Object\.entries\(\{.*?\}\)\)',
               lambda m: 'const PL={};for(const [k,u] of Object.entries(%s))' % json.dumps(out), s, count=1, flags=re.S)
assert c == 1
s = re.sub(r'const PLN=\{.*?\};', 'const PLN=%s;' % json.dumps({k: len(v) for k, v in SETS.items()}), s, count=1)
open('index.html', 'w').write(s); print('frames', len(out))
