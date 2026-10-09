"""Build the south garden quarter in layers and embed it in index.html.

Source images share one 1024x577 frame:
  assets/source-sheets/south_layout.png  - the target layout (reference only)
  assets/source-sheets/south_ground.png  - ground layer used as the base
  assets/source-sheets/south_assets.png  - buildings and props on magenta

Most pieces are placed exactly where the layout shows them, so positions are
written in that 1024x577 frame and scaled to the 640x360 game map (x0.625).
Writes into index.html: MAP2 (ground with baked shadows), OBJS2, LANT2, WINS2,
LMASK2, WALK2 (walkable grid) and SPOTS2.

Run from the repo root:  python3 tools/layout_south.py
"""
import json, io, base64, re
import numpy as np, scipy.ndimage as nd
from PIL import Image, ImageOps, ImageDraw, ImageFilter

K = 0.625                      # 1024x577 frame -> 640x360 map
SRC = 'assets/source-sheets/'
P = 'assets/props/'; T = 'assets/trees/'; B = 'assets/buildings/'; S2 = 'assets/south/'

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

# ---------------------------------------------------------------- cut the magenta sheet
sheet = np.array(Image.open(SRC + 'south_assets.png').convert('RGB')).astype(int)
r, g, b = sheet[:, :, 0], sheet[:, :, 1], sheet[:, :, 2]
fg = ~((r - g > 70) & (b - g > 70))
for _ in range(2):
    e = fg & ~nd.binary_erosion(fg); fg &= ~(e & (r - g > 35) & (b - g > 35))
L, n = nd.label(nd.binary_dilation(fg, iterations=3))

def piece(x0, y0, x1, y1, rows=None):
    """RGBA crop of sheet pixels in the box that belong to a magenta-separated object."""
    m = fg[y0:y1, x0:x1] & (L[y0:y1, x0:x1] > 0)
    if rows: m[:rows[0] - y0] = False; m[rows[1] - y0:] = False
    a = np.dstack([sheet[y0:y1, x0:x1], np.where(m, 255, 0)]).astype('uint8')
    return Image.fromarray(a, 'RGBA')

objs = []
def add(key, im, x, y, base, w=None, flip=False):
    """Place an image whose top-left is (x, y) in frame coords; base in frame coords."""
    if w is not None:
        h = round(im.height * w / im.width); im = im.resize((round(w), h), Image.LANCZOS)
    if flip: im = ImageOps.mirror(im)
    bb = im.getbbox()
    if not bb: return
    mw, mh = max(1, round(im.width * K)), max(1, round(im.height * K))
    sm = im.resize((mw, mh), Image.LANCZOS)
    objs.append({'k': key, 'x': round(x * K), 'y': round(y * K), 'w': mw, 'h': mh, 'base': round(base * K), 'src': uri(sm), 'img': sm})

def add_file(key, f, cx, base, w, flip=False):
    im = Image.open(f).convert('RGBA'); h = im.height * w / im.width
    add(key, im, cx - w / 2, base - h, base, w, flip)

# courtyard house: split so the player can stand inside the courtyard
cx0, cy0, cx1, cy1 = 60, 66, 441, 511
court = piece(cx0, cy0, cx1, cy1)
ca = np.array(court)
def part(mask_fn):
    a = ca.copy(); yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    a[~mask_fn(xx + cx0, yy + cy0), 3] = 0
    return Image.fromarray(a)
add('court_back', part(lambda x, y: (y < 212) & (x >= 176) & (x <= 324)), cx0, cy0, 212)
add('court_left', part(lambda x, y: (y < 405) & (x < 176)), cx0, cy0, 405)
add('court_right', part(lambda x, y: (y < 405) & (x > 324)), cx0, cy0, 405)
add('court_front', part(lambda x, y: (y >= 405) & (y < 482)), cx0, cy0, 478)
add('court_beds', part(lambda x, y: y >= 482), cx0, cy0, 506)

add('inn', piece(752, 0, 994, 227), 752, 0, 222)
# pavilion sits on the stone plinth painted into the ground (745-858, ~335-415)
pav = piece(537, 27, 706, 244); add('pavilion', pav, 801 - 120 / 2, 415 - pav.height * 120 / pav.width, 405, 120)
# footbridge: keep the deck only, laid over the stream where the layout shows it
fb = piece(503, 287, 641, 435, rows=(287, 392)); fb = fb.crop(fb.getbbox())
# base 0: the deck is a floor the player walks on, so it always draws beneath characters
add('footbridge', fb, 659 - 86 / 2, 288 - fb.height * 86 / fb.width, 0, 86)
# inn terrace tables and stools, as in the layout
table = piece(689, 463, 772, 542); stool = piece(648, 489, 684, 530)
for i, tx in enumerate((805, 943)):
    add(f'table{i}', table, tx - 26, 213, 250, 52)
    add(f'stoolL{i}', stool, tx - 46, 228, 248, 20); add(f'stoolR{i}', stool, tx + 26, 228, 248, 20)
add('bench', piece(846, 333, 975, 386), 590, 448, 478, 76)

# stalls on the three dirt pads at the bottom right
add_file('stall_veg', 'assets/stalls/buns_umbrella_cart.png', 712, 552, 96)
add_file('stall_cloth', 'assets/stalls/cloth_bamboo.png', 821, 552, 94)
add_file('stall_pots', 'assets/stalls/pottery_cloth.png', 926, 552, 92)
add_file('apples', 'assets/props2/apple_crate.png', 642, 566, 36)
add_file('lanterns', P + 'lantern_string.png', 510, 577, 212)

# trees: willows follow the water, pines and bamboo frame the edges (layout image)
for k, f, cx, base, w, fl in [
    ('w_stream1', P + 'willow.png', 600, 218, 96, 0), ('w_stream2', P + 'willow.png', 600, 458, 96, 1),
    ('w_stream3', T + 'willow_tall.png', 668, 70, 70, 0), ('w_top1', P + 'willow.png', 168, 62, 92, 1),
    ('w_top2', T + 'willow_young.png', 378, 60, 70, 0),
    ('pine_tl', T + 'pine.png', 58, 132, 112, 0), ('pine_t', T + 'pine.png', 306, 56, 78, 1),
    ('pine_tr', T + 'pine.png', 990, 112, 92, 1), ('pine_bl', T + 'pine.png', 58, 577, 112, 1),
    ('bam_l1', T + 'bamboo.png', 26, 282, 52, 0), ('bam_l2', T + 'bamboo.png', 22, 442, 48, 1),
    ('bam_r', T + 'bamboo.png', 1002, 522, 46, 0)]:
    add_file(k, f, cx, base, w, bool(fl))

# ---------------------------------------------------------------- ground, shadows, walk grid
ground = Image.open(SRC + 'south_ground.png').convert('RGBA').resize((640, 361), Image.LANCZOS).crop((0, 0, 640, 360))
SH = {'court_front': (.92, .02, .98), 'court_back': (.30, .30, .70), 'inn': (.98, .05, .95),
      'stall_veg': (.98, .1, .9), 'stall_cloth': (.98, .1, .9), 'stall_pots': (.98, .1, .9), 'pavilion': (.97, .12, .88)}
sh = Image.new('RGBA', (640, 360)); sd = ImageDraw.Draw(sh)
for o in objs:
    if o['k'] in SH:
        fy, a0, a1 = SH[o['k']]; y = o['y'] + fy * o['h']
        sd.ellipse([o['x'] + a0 * o['w'], y - 4, o['x'] + a1 * o['w'], y + 6], fill=(10, 25, 15, 110))
ground.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2)))

ga = np.array(ground).astype(int)
water = (ga[:, :, 1] > ga[:, :, 0] + 30) & (ga[:, :, 2] > ga[:, :, 0] + 18)
water = nd.binary_opening(water, iterations=1)
fbo = next(o for o in objs if o['k'] == 'footbridge')
water[fbo['y']:fbo['y'] + fbo['h'], fbo['x']:fbo['x'] + fbo['w']] = False   # the bridge is walkable
C = 8; walk = ''
for j in range(45):
    for i in range(80):
        cell = water[j * C:(j + 1) * C, i * C:(i + 1) * C]
        walk += '0' if cell.mean() > 0.35 else '1'

# ---------------------------------------------------------------- night lights
def fr(key, boxes):  # window boxes in sheet coords for a building placed 1:1
    o = next(o for o in objs if o['k'] == key)
    return [[round(x0 * K), round(y0 * K), max(2, round((x1 - x0) * K)), max(2, round((y1 - y0) * K)), o['base'], on] for x0, y0, x1, y1, on in boxes]
wins = (fr('court_back', [(196, 155, 221, 176, .95), (285, 155, 310, 176, .95), (234, 150, 262, 196, 1.5)]) +
        fr('court_left', [(112, 245, 142, 270, .92)]) + fr('court_right', [(357, 245, 387, 270, .97)]) +
        fr('court_front', [(132, 433, 157, 450, .9), (323, 433, 348, 450, .93), (222, 428, 262, 470, 1.5)]) +
        fr('inn', [(792, 72, 824, 94, .96), (912, 72, 944, 94, .98), (858, 72, 886, 96, .99),
                   (797, 143, 826, 161, 1.5), (912, 143, 942, 161, 1.5), (862, 150, 886, 180, 1.5)]))
from winmask import layer, add_masks
wins = add_masks(wins, layer(objs, lambda o: o['img']))
lant, masks = [], []
for o in objs:
    if o['k'] != 'lanterns': continue
    a = np.array(o['img']).astype(int)
    red = (a[:, :, 0] > 150) & (a[:, :, 1] < 110) & (a[:, :, 2] < 100) & (a[:, :, 3] > 0)
    lab, n = nd.label(nd.binary_dilation(red, iterations=2))   # one blob per lantern
    sizes = nd.sum(red, lab, range(1, n + 1))
    for c, sz in zip(nd.center_of_mass(red, lab, range(1, n + 1)), sizes):
        if sz >= 4: lant.append([round(o['x'] + c[1]), round(o['y'] + c[0]), 0.7])
    m = a.copy(); m[~nd.binary_dilation(red, iterations=1), 3] = 0
    masks.append([o['x'], o['y'], o['w'], o['h'], o['base'], uri(Image.fromarray(m.astype('uint8')))])

# ---------------------------------------------------------------- click areas (map coords)
def at(key, pad=0):
    o = next(o for o in objs if o['k'] == key)
    bb = o['img'].getbbox(); return o['x'] + bb[0] - pad, o['y'] + bb[1] - pad, bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
def spot(word, key, ax, ay, pad=0):
    x, y, w, h = at(key, pad); return {'word': word, 'x': x, 'y': y, 'w': w, 'h': h, 'ax': ax, 'ay': ay}
spots = [spot('fandian', 'inn', 556, 152), spot('zhuozi', 'table0', 503, 166, 2), spot('yizi', 'bench', 392, 306, 2),
         spot('yifu', 'stall_cloth', 513, 350), spot('cai', 'stall_veg', 445, 350), spot('mifan', 'table1', 589, 166, 2), spot('dongxi', 'stall_pots', 578, 350),
         spot('pv_qiao', 'footbridge', 412, 160, 2),
         {'word': 'li', 'x': 398, 'y': 222, 'w': 54, 'h': 32, 'ax': 432, 'ay': 284},
         {'word': 'pv_he', 'x': 400, 'y': 30, 'w': 40, 'h': 70, 'ax': 448, 'ay': 70},
         {'act': 'north', 'label': 'Back to the village square ↑', 'x': 284, 'y': 0, 'w': 76, 'h': 14, 'ax': 322, 'ay': 6}]

# ---------------------------------------------------------------- write into index.html
for o in objs: o.pop('img')
s = open('index.html').read()
def put(name, value):
    global s
    pat = r'const %s=.*?;\n' % name
    assert re.search(pat, s, re.S), name
    s = re.sub(pat, lambda m: 'const %s=%s;\n' % (name, value), s, count=1, flags=re.S)
put('OBJS2', json.dumps(objs)); put('LANT2', json.dumps(lant)); put('WINS2', json.dumps(wins))
put('LMASK2', json.dumps(masks)); put('WALK2', json.dumps(walk)); put('SPOTS2', json.dumps(spots, ensure_ascii=False))
s = re.sub(r'(const MAP2=new Image\(\);MAP2\.src=")[^"]*"', lambda m: m.group(1) + uri(ground.convert('RGB')) + '"', s, count=1)
open('index.html', 'w').write(s)
print('objects', len(objs), 'lanterns', len(lant), 'windows', len(wins), 'walkable', walk.count('1'))
