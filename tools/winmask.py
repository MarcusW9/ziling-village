"""Per-window night-light masks, shared by layout.py and layout_south.py.

A window rectangle covers frame, shutters and the dark room behind. Lighting the
whole rectangle reads as a pasted-on square, so instead each window gets a mask that
lights only the dark interior pixels (the room, the gaps in lattice), fading out on
mid-tone wood and leaving plaster, paper, red couplets and foliage unlit.
"""
import io, base64
import numpy as np
from PIL import Image, ImageFilter

WARM = (255, 176, 92)

def layer(objs, open_img):
    """Composite every object in depth order onto a 640x360 layer."""
    L = Image.new('RGBA', (640, 360))
    for o in sorted(objs, key=lambda o: o['base']):
        im = open_img(o).convert('RGBA').resize((o['w'], o['h']))
        L.alpha_composite(im, (o['x'], o['y']))
    return L

def mask(L, x, y, w, h):
    a = np.array(L.crop((x, y, x + w, y + h))).astype(float)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lum = .3 * r + .59 * g + .11 * b
    k = np.clip((120 - lum) / 70, 0, 1)                      # dark room -> 1, mid wood -> partial, plaster -> 0
    k[(r > 150) & (g < 110)] = 0                             # red couplets and lanterns
    k[(g > r + 6) & (g > b)] = 0                             # leaves in front of the window
    k[al < 128] = 0
    # lamplight inside a room: dimmer at the top and the side edges, brightest low and central
    xs = np.linspace(-1, 1, w)[None, :]
    k *= np.linspace(.45, 1, h)[:, None] * (1 - .4 * xs ** 2)
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = WARM; out[..., 3] = (k * 255).astype(np.uint8)
    im = Image.fromarray(out)
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

def add_masks(wins, L):
    """wins: [[x, y, w, h, base, bed], ...] -> each gets its mask URI appended."""
    return [wn[:6] + [mask(L, *wn[:4])] for wn in wins]
