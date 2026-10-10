"""Build sprites for the spirits added after the first six: 牛牛 (niu), 鱼鱼 (fish), 饱饱 (bao) and 喵喵 (mao).

Writes into index.html:
  SPR2 - in-world frames {spirit: {stage: {pose: [dataURI, w, h]}}}
  AV2  - Spirits-tab portraits {spirit: {stage: dataURI}}

Poses per stage are 'front', 'happy' and 'sleep'. Single spirits are scaled so the
main body is TARGET px tall, matching tools/spirits.py; pair poses (twins, dragons)
are scaled so each creature in the pair is about that height, so a pair reads as two
spirits, not one giant one.

鱼鱼 has three stages: 0 = 鱼鱼, 1 = 双鱼 twins, 2 = 双龙 dragons.
Run from the repo root:  python3 tools/spirits_new.py
"""
import json, io, base64, re
import numpy as np, scipy.ndimage as nd
from PIL import Image

TARGET = 16
S = 'assets/sprites/'

def body_h(im):
    a = np.array(im)[:, :, 3] > 0
    lab, n = nd.label(a); sz = nd.sum(a, lab, range(1, n + 1))
    ys, _ = np.where(lab == int(np.argmax(sz)) + 1); return ys.max() - ys.min() + 1

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

def frame(path, scale):
    im = Image.open(path).convert('RGBA'); im = im.crop(im.getbbox())
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    a = np.array(im); a[:, :, 3] = np.where(a[:, :, 3] > 110, 255, 0)
    return Image.fromarray(a)

def stage(poses, ref, ref_h=TARGET):
    """poses: {pose: path}; ref: the pose whose body height sets the scale."""
    s = ref_h / body_h(Image.open(ref).convert('RGBA'))
    return {p: frame(f, s) for p, f in poses.items()}

def side_by_side(a, b, gap=-2):
    w = a.width + b.width + gap; h = max(a.height, b.height)
    c = Image.new('RGBA', (w, h)); c.paste(a, (0, h - a.height), a); c.paste(b, (a.width + gap, h - b.height), b); return c

T = S + 'twins/'; D = S + 'dragons/'
sets = {
    # 牛牛 is the painted clay Spring Ox (春牛); his blocky body reads larger than the rounder spirits at the same height
    'niu': {0: stage({k: S + f'niuniu_clay/{k}.png' for k in ('front', 'happy', 'sleep')}, S + 'niuniu_clay/front.png', 14)},
    'fish': {0: stage({k: S + f'yuyu_v2/{k}.png' for k in ('front', 'happy', 'sleep')}, S + 'yuyu_v2/front.png')},
    # 饱饱 the clay stove: round and wide, so 15 px matches the others' visual weight
    'bao': {0: stage({k: S + f'baobao/{k}.png' for k in ('front', 'happy', 'sleep')}, S + 'baobao/front.png', 15)},
    # 喵喵 the porcelain cat: the side poses (watch, crouch, a two-frame walk) face right; the game mirrors them for left
    'mao': {0: stage({k: S + f'miaomiao/{k}.png' for k in ('front', 'happy', 'sleep', 'watch', 'crouch', 'walk1', 'walk2')}, S + 'miaomiao/front.png', 15)},
}
# twins: single poses at the base size, then joined into pairs
tw = stage({f'{c}_{k}': T + f'{c}_{k}.png' for c in ('red', 'cream') for k in ('front', 'happy', 'sleep')}, T + 'red_front.png', 14)
# the wave and yin-yang poses come from a sheet drawn at another scale: size them by that sheet's own front pose
tw |= stage({'cream_wave': T + 'cream_wave.png', 'yinyang': T + 'pair_yinyang.png'}, T + 'red_peace.png', 14)
sets['fish'][1] = {'front': side_by_side(tw['red_front'], tw['cream_front']),
                   'happy': side_by_side(tw['red_happy'], tw['cream_wave']),
                   'sleep': side_by_side(tw['red_sleep'], tw['cream_sleep'])}
yin = tw['yinyang']
# dragons: long bodies, so scale by height of a single dragon to ~20 px
dr = stage({'red': D + 'red.png', 'cream': D + 'cream.png', 'coil': D + 'pair_coil.png', 'fly': D + 'pair_fly.png'}, D + 'red.png', 20)
sets['fish'][2] = {'front': side_by_side(dr['red'], dr['cream'], -4), 'happy': dr['fly'], 'sleep': dr['coil']}

spr = {k: {st: {p: [uri(im), im.width, im.height] for p, im in poses.items()} for st, poses in stages.items()} for k, stages in sets.items()}

def portrait(path):
    im = Image.open(path).convert('RGBA'); im = im.crop(im.getbbox()); im.thumbnail((30, 30), Image.LANCZOS)
    c = Image.new('RGBA', (32, 32)); c.paste(im, ((32 - im.width) // 2, (32 - im.height) // 2), im); return uri(c)
av = {'niu': {0: portrait(S + 'niuniu_clay/front.png')}, 'mao': {0: portrait(S + 'miaomiao/front.png')}, 'bao': {0: portrait(S + 'baobao/front.png')},
      'fish': {0: portrait(S + 'yuyu_v2/front.png'), 1: portrait(T + 'pair_yinyang.png'), 2: portrait(D + 'pair_coil.png')}}

s = open('index.html').read()
for name, val in (('SPR2', spr), ('AV2', av)):
    s, n = re.subn(r'const %s=.*?;\n' % name, lambda m: 'const %s=%s;\n' % (name, json.dumps(val)), s, count=1, flags=re.S)
    assert n == 1, name
open('index.html', 'w').write(s)
print({k: {st: {p: v[1:] for p, v in poses.items()} for st, poses in stages.items()} for k, stages in spr.items()})
