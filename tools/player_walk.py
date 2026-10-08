"""Embed the player's 4-direction walk cycle in index.html.

Source: assets/sprites/player/fNN.png, cut from assets/source-sheets/player_walk.png.
  down  = f00-f03, up = f04-f07, right = f10 f11 f14 f15 (left is the right cycle mirrored;
  the sheet's own left frames f08/f12 are only two, and f09/f13 face the viewer).
All frames share one scale (the front frame is HEIGHT px tall) and are bottom-centred
in a W x H frame so the feet stay put while walking.
"""
import json, io, base64, re
from PIL import Image

HEIGHT, W = 28, 28
D = 'assets/sprites/player/'
SETS = {'down': [0, 1, 2, 3], 'up': [4, 5, 6, 7], 'right': [10, 11, 14, 15]}
scale = HEIGHT / Image.open(D + 'f01.png').height
out = {}
for name, idx in SETS.items():
    for n, k in enumerate(idx):
        im = Image.open(D + f'f{k:02d}.png').convert('RGBA')
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        f = Image.new('RGBA', (W, HEIGHT + 2)); f.paste(im, ((W - im.width) // 2, HEIGHT + 2 - im.height), im)
        b = io.BytesIO(); f.save(b, 'PNG'); out[f'{name}{n}'] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
s = open('index.html').read()
s, c = re.subn(r'const PL=\{\};for\(const \[k,u\] of Object\.entries\(\{.*?\}\)\)',
               lambda m: 'const PL={};for(const [k,u] of Object.entries(%s))' % json.dumps(out), s, count=1, flags=re.S)
assert c == 1
open('index.html', 'w').write(s); print('frames', len(out))
