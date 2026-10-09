"""Make the 双鱼 cream twin by recolouring the red-and-gold 鱼鱼 poses.

AI tools kept redrawing the second twin as a different creature, so instead the
red twin IS 鱼鱼 and the cream twin is the same drawing with the red body mapped
onto the cream of the evolved silver dragon. Gold fins, tail, whiskers and the
pink blush are kept. Output: assets/sprites/twins/{red,cream}_{front,side,happy,sleep}.png
"""
import colorsys
import numpy as np
from PIL import Image

SRC, OUT = 'assets/sprites/yuyu_v2/', 'assets/sprites/twins/'
CREAM, SHADE = np.array([229, 224, 209]), np.array([150, 140, 128])

def recolour(im):
    a = np.array(im.convert('RGBA')).astype(float); out = a.copy(); rgb = a[:, :, :3] / 255
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x, 3] == 0: continue
            h, l, s = colorsys.rgb_to_hls(*rgb[y, x])
            red = (h < 0.04 or h > 0.94) and s > 0.35 and l > 0.15
            if red and l > 0.66: out[y, x, :3] = [240, 170, 170]            # blush
            elif red: out[y, x, :3] = SHADE + (CREAM - SHADE) * min(1, (l - 0.15) / 0.45)
    return Image.fromarray(out.astype('uint8'))

for k in ['front', 'side', 'happy', 'sleep']:
    im = Image.open(SRC + k + '.png'); im.save(OUT + f'red_{k}.png'); recolour(im).save(OUT + f'cream_{k}.png')
print('done')
