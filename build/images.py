"""Convert Notion screenshots into web-ready captures and thumbnails.

shots/   full-size captures for the lightbox (webp, max 2400px wide)
thumbs/  16:10 crops centred on the red highlight box around our thread
ins/     Reddit post-insight screenshots (webp) + tall crops for the post cards
"""
from pathlib import Path
from PIL import Image

SRC = Path("/Users/aniket/Downloads/Private & Shared 6/mack weldon cycle 1 report")
OUT = Path(__file__).resolve().parent.parent
SERP = [1, *range(4, 15), *range(16, 24), *range(25, 30), *range(31, 45), *range(47, 53),
        54, 55, 57, *range(59, 64), *range(65, 73)]
INSIGHTS = [0, 3, 15, 30, 46, 53, 56, 64]


def src(n):
    return SRC / ("image.png" if n == 0 else f"image {n}.png")


def red_box(im):
    """Bounding box of the red highlight rectangles in the results (left) pane."""
    w, h = im.size
    step = 3
    small = im.convert("RGB")
    px = small.load()
    xs, ys = [], []
    limit = int(w * 0.54)  # the JSON panel sits on the right
    for y in range(0, h, step):
        for x in range(0, limit, step):
            r, g, b = px[x, y]
            if r > 190 and g < 80 and b < 80:
                xs.append(x); ys.append(y)
    if len(xs) < 40:
        return None
    xs.sort(); ys.sort()
    k = max(1, len(xs) // 200)  # trim stray red pixels (logos, icons)
    return xs[k], ys[k], xs[-k - 1], ys[-k - 1]


def crop_16x10(im, box):
    w, h = im.size
    x0, y0, x1, y1 = box
    pad = int(w * 0.03)
    x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)
    bw, bh = x1 - x0, y1 - y0
    tw = max(bw, int(bh * 1.6)); th = int(tw / 1.6)
    if th < bh:
        th = bh; tw = int(th * 1.6)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    L = min(max(0, cx - tw // 2), max(0, w - tw)); T = min(max(0, cy - th // 2), max(0, h - th))
    return im.crop((L, T, min(w, L + tw), min(h, T + th)))


def save(im, path, width, q):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(path, "WEBP", quality=q, method=6)


miss = []
for n in SERP:
    im = Image.open(src(n))
    save(im, OUT / "shots" / f"s{n:02d}.webp", 2400, 84)
    box = red_box(im)
    if box is None:
        miss.append(n)
        thumb = im.crop((0, 0, int(im.width * 0.54), int(im.width * 0.54 / 1.6)))
    else:
        thumb = crop_16x10(im, box)
    save(thumb, OUT / "thumbs" / f"t{n:02d}.webp", 720, 80)

for n in INSIGHTS:
    im = Image.open(src(n))
    save(im, OUT / "ins" / f"i{n:02d}.webp", 1100, 86)

print("no red box found:", miss)
