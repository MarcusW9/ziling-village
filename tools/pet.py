"""Cut the chow chow puppy sheet and embed his frames into index.html as PET.

Source: assets/source-sheets/pet_chowchow.png, an 8x3 grid on magenta. The rows mix
directions, so frames are picked by hand below after checking which way each faces
(f<row><col>). Every side frame must face its direction, or he 'moonwalks'.

All frames come from one sheet at one scale, so one factor (from the front walk
frame) sizes them all. Run from the repo root:  python3 tools/pet.py
"""
import io, json, base64, re
import numpy as np, scipy.ndimage as nd
from PIL import Image

SRC = 'assets/source-sheets/pet_chowchow.png'
OUT = 'assets/sprites/pet/'
HEIGHT = 13                      # standing puppy, against a 25 px player
SETS = {'down': ['00', '01', '02', '03'], 'up': ['10', '11', '12', '13'],
        'right': ['04', '14', '07', '21'], 'left': ['15', '16', '17', '22'],
        'sit': ['24', '25'], 'sleep': ['26', '27']}

def cut():
    a = np.array(Image.open(SRC).convert('RGBA')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r - g > 60) & (b - g > 60)
    H, W = bg.shape; cw, rh = W / 8, H / 3
    for j in range(3):
        for i in range(8):
            x0, y0, x1, y1 = int(i * cw) + 3, int(j * rh) + 3, int((i + 1) * cw) - 3, int((j + 1) * rh) - 3
            m = nd.binary_erosion(~bg[y0:y1, x0:x1], iterations=1)
            lab, n = nd.label(m); sz = nd.sum(m, lab, range(1, n + 1))
            keep = np.isin(lab, [k + 1 for k, s in enumerate(sz) if s > 40])
            keep = nd.binary_dilation(keep, iterations=1) & ~bg[y0:y1, x0:x1]
            c = a[y0:y1, x0:x1].copy(); c[..., 3] = np.where(keep, 255, 0)
            fr = Image.fromarray(c.astype('uint8')); fr.crop(fr.getbbox()).save(f'{OUT}f{j}{i}.png')

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

cut()
scale = HEIGHT / Image.open(f'{OUT}f00.png').height
pet = {}
for k, ids in SETS.items():
    fr = []
    for f in ids:
        im = Image.open(f'{OUT}f{f}.png').convert('RGBA')
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        x = np.array(im); x[..., 3] = np.where(x[..., 3] > 110, 255, 0)
        im = Image.fromarray(x); fr.append([uri(im), im.width, im.height])
    pet[k] = fr

# a crisp portrait for the gift panel: the sitting pose at 64 px, nearest-neighbour from a small render
por = Image.open(f'{OUT}f24.png').convert('RGBA'); por.thumbnail((40, 40), Image.LANCZOS)
x = np.array(por); x[..., 3] = np.where(x[..., 3] > 110, 255, 0); pet['portrait'] = uri(Image.fromarray(x))

s = open('index.html').read()
s, n = re.subn(r'const PET=.*?;\n', lambda m: 'const PET=' + json.dumps(pet) + ';\n', s, count=1, flags=re.S)
assert n == 1, 'PET placeholder missing'
open('index.html', 'w').write(s)
print({k: [f[1:] for f in v] for k, v in pet.items() if k != 'portrait'})
