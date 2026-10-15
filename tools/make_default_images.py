"""Generates the neutral placeholder pictures in static/default_images/ (needs Pillow).

Run from the project folder:  python tools/make_default_images.py
You do not need to run it again: the pictures are already included.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / 'static' / 'default_images'
OUT.mkdir(parents=True, exist_ok=True)


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(size, c1, c2, horizontal=False):
    w, h = size
    mask = Image.linear_gradient('L')
    mask = mask.rotate(90, expand=True) if horizontal else mask
    mask = mask.resize(size)
    return Image.composite(Image.new('RGB', size, hexrgb(c2)), Image.new('RGB', size, hexrgb(c1)), mask).convert('RGBA')


def layer(base, draw_fn):
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(ov, 'RGBA'))
    return Image.alpha_composite(base, ov)


def circles(size, seed, c1, c2, n=9):
    rnd = random.Random(seed)
    img = gradient(size, c1, c2)
    w, h = size

    def d(dr):
        for _ in range(n):
            r = rnd.randint(h // 10, h // 3)
            x, y = rnd.randint(0, w), rnd.randint(0, h)
            dr.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(25, 70)))
    return layer(img, d)


def waves(size, seed, c1, c2):
    rnd = random.Random(seed)
    img = gradient(size, c1, c2, horizontal=True)
    w, h = size

    def d(dr):
        for i in range(7):
            y = h * (0.25 + i * 0.12)
            pts = [(0, h)]
            for x in range(0, w + 40, 40):
                pts.append((x, y + rnd.randint(-30, 30) + (x / w) * 60))
            pts.append((w, h))
            dr.polygon(pts, fill=(255, 255, 255, 28))
    return layer(img, d)


def window(size, seed, c1, c2, accent):
    """A neutral 'screen mock-up' look for portfolio samples."""
    rnd = random.Random(seed)
    img = gradient(size, c1, c2)
    w, h = size
    x0, y0, x1, y1 = int(w * .12), int(h * .14), int(w * .88), int(h * .86)

    def d(dr):
        dr.rounded_rectangle((x0, y0, x1, y1), 24, fill=(255, 255, 255, 235))
        dr.rounded_rectangle((x0, y0, x1, y0 + 46), 24, fill=(235, 238, 245, 255))
        for i, c in enumerate(((240, 100, 90), (245, 190, 70), (90, 200, 120))):
            dr.ellipse((x0 + 20 + i * 24, y0 + 15, x0 + 36 + i * 24, y0 + 31), fill=c + (255,))
        ac = hexrgb(accent) + (255,)
        dr.rounded_rectangle((x0 + 40, y0 + 90, x0 + 40 + int(w * .3), y0 + 120), 10, fill=ac)
        for k in range(3):
            dr.rounded_rectangle((x0 + 40, y0 + 145 + k * 28, x0 + 40 + int(w * (.42 - k * .06)), y0 + 159 + k * 28), 7, fill=(205, 212, 226, 255))
        cw = int((x1 - x0 - 120) / 3)
        for k in range(3):
            cx = x0 + 40 + k * (cw + 20)
            dr.rounded_rectangle((cx, y1 - 190, cx + cw, y1 - 40), 14, fill=(236, 240, 250, 255))
            dr.rounded_rectangle((cx + 16, y1 - 174, cx + cw - 16, y1 - 120), 10, fill=hexrgb(accent) + (rnd.randint(110, 220),))
    return layer(img, d)


def logo(path):
    size = (192, 192)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle((8, 8, 184, 184), 44, fill=hexrgb('#1f5eff') + (255,))
    dr.ellipse((48, 48, 144, 144), fill=(255, 255, 255, 255))
    dr.ellipse((76, 76, 116, 116), fill=hexrgb('#0b1f4d') + (255,))
    img.save(path, optimize=True)


def save(img, name, quality=82):
    img.convert('RGB').save(OUT / name, 'JPEG', quality=quality, optimize=True)


if __name__ == '__main__':
    logo(OUT / 'logo.png')
    save(circles((1200, 900), 1, '#1f5eff', '#0b1f4d'), 'hero.jpg')
    save(circles((1200, 800), 2, '#0b1f4d', '#2a7bff', 7), 'intro.jpg')
    save(circles((1200, 800), 3, '#14346b', '#3ba4ff', 8), 'about.jpg')
    for i, (a, b) in enumerate([('#1f5eff', '#0b1f4d'), ('#0f766e', '#134e4a'), ('#7c3aed', '#312e81'), ('#ea580c', '#7c2d12')], 1):
        save(waves((1200, 675), 10 + i, a, b), 'article-%d.jpg' % i)
    pal = [('#dbe7ff', '#9db8ff', '#1f5eff'), ('#d9f3ee', '#8fd6c9', '#0f766e'), ('#ece4ff', '#bba6f5', '#7c3aed'),
           ('#ffe8d9', '#f5b58f', '#ea580c'), ('#e0f2fe', '#8ccdf0', '#0369a1'), ('#fde4ec', '#f3a3bf', '#be185d')]
    for i, (a, b, acc) in enumerate(pal, 1):
        save(window((1200, 800), 20 + i, a, b, acc), 'portfolio-%d.jpg' % i)
    save(waves((1000, 700), 31, '#1f5eff', '#0b1f4d'), 'gallery-1.jpg')
    save(circles((1000, 700), 32, '#0f766e', '#134e4a'), 'gallery-2.jpg')
    print('Done:', len(list(OUT.iterdir())), 'files')
