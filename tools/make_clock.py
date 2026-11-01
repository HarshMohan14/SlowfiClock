#!/usr/bin/env python3
"""Make a clock part from two images of the same size.

    python3 tools/make_clock.py <id> frame.png glass.png --name "Brass, slim"

frame.png  the hourglass frame (wood, brass, caps, base) on a transparent background.
           Leave the glass itself transparent: the app draws the glass and the sand.
glass.png  a mask, white where the sand can be (the inside of both bulbs), black elsewhere.
           The narrowest white row near the middle is taken as the neck.

Both images use the app's scene scale: the scene is 941 x 1672, so a clock about 600 px wide and
1150 px tall sits like the original one. The result goes to web/content/clocks/<id>/.
"""
import argparse, json, os, re
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('id'); ap.add_argument('frame'); ap.add_argument('glass')
ap.add_argument('--name', default=None); ap.add_argument('--cell', type=int, default=2, help='size of one grain in scene px')
ap.add_argument('--fill', type=float, default=0.6, help='share of the lower bulb the sand fills')
a = ap.parse_args()

frame = Image.open(a.frame).convert('RGBA')
mask = np.asarray(Image.open(a.glass).convert('L')) > 127
assert frame.size == (mask.shape[1], mask.shape[0]), 'frame and glass must be the same size'
ys, xs = np.nonzero(mask)
assert len(ys), 'glass mask is empty'
C = a.cell
ox, oy = int(xs.min()) // C * C, int(ys.min()) // C * C           # grid origin, in the clock image
cols = (int(xs.max()) - ox) // C + 1; nrows = (int(ys.max()) - oy) // C + 1
rows = []
for r in range(nrows):
    y = oy + r * C + C // 2
    line = np.nonzero(mask[min(y, mask.shape[0] - 1), :])[0]
    cells = sorted({(x - ox) // C for x in line if ox <= x < ox + cols * C})
    rows.append([cells[0], cells[-1]] if cells else [1, 0])
widths = np.array([b - a_ + 1 if b >= a_ else 10 ** 6 for a_, b in rows])
mid = slice(nrows // 3, 2 * nrows // 3)
neck = int(np.argmin(widths[mid])) + nrows // 3
rows[neck] = [rows[neck][0], rows[neck][1]]
lower = [(gy, a_, b) for gy, (a_, b) in enumerate(rows) if gy > neck and b >= a_]
upper = [(gy, a_, b) for gy, (a_, b) in enumerate(rows) if gy < neck and b >= a_]
lower_cells = sum(b - a_ + 1 for _, a_, b in lower); upper_cells = sum(b - a_ + 1 for _, a_, b in upper)
N = int(min(lower_cells * a.fill, upper_cells * 0.9))
# the settled pile: a low mound, highest in the middle
cx = (rows[neck][0] + rows[neck][1]) / 2
def count(level):
    n = 0
    for gy, a_, b in lower:
        for x in range(a_, b + 1):
            if gy >= level + 0.5 * abs(x - cx): n += 1
    return n
lo, hi = neck, nrows
while hi - lo > 1:
    m = (lo + hi) // 2
    if count(m) >= N: lo = m
    else: hi = m
level = lo
pile = []
for x in range(cols):
    top = None
    for gy, a_, b in lower:
        if a_ <= x <= b and gy >= level + 0.5 * abs(x - cx): top = gy; break
    pile.append(top if top is not None else -1)
# outline: sampled left and right edges, in clock image px
outline = []
step = max(1, nrows // 22)
for gy in list(range(0, nrows, step)) + [nrows - 1]:
    a_, b = rows[gy]
    if b < a_: continue
    outline.append([oy + gy * C + C / 2, ox + a_ * C, ox + (b + 1) * C])
# anchor: bottom centre of the frame
al = np.asarray(frame)[..., 3] > 40
fy, fx = np.nonzero(al)
anchor = [round(float((fx.min() + fx.max()) / 2), 1), float(fy.max())]
# soft highlights along the inside of each bulb
def streak(y0, y1, side, color, op, w):
    pts = [o for o in outline if y0 <= o[0] <= y1]
    if len(pts) < 3: return None
    x = [(o[1] + 10 if side < 0 else o[2] - 10) for o in pts]
    d = f'M{x[0]:.0f} {pts[0][0]:.0f} C{x[len(x) // 3]:.0f} {pts[len(pts) // 3][0]:.0f} {x[2 * len(x) // 3]:.0f} {pts[2 * len(pts) // 3][0]:.0f} {x[-1]:.0f} {pts[-1][0]:.0f}'
    return dict(d=d, color=color, opacity=op, width=w)
ny = oy + neck * C; top_y = outline[0][0]; bot_y = outline[-1][0]
hl = [h for h in (streak(top_y + 30, ny - 120, -1, '#FFFFFF', .16, 12), streak(ny + 120, bot_y - 20, -1, '#FFFFFF', .13, 12),
                  streak(top_y + 60, ny - 160, 1, '#FFD9A0', .22, 3), streak(ny + 160, bot_y - 30, 1, '#FFD9A0', .2, 3)) if h]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'content', 'clocks', a.id)
os.makedirs(out, exist_ok=True)
frame.save(os.path.join(out, 'frame.webp'), 'WEBP', quality=88, method=6)
data = {'name': a.name or a.id, 'frame': 'frame.webp', 'size': list(frame.size), 'anchor': anchor,
        'grid': {'origin': [ox, oy], 'cell': C, 'cols': cols, 'neck': neck, 'rows': rows}, 'pile': pile,
        'glass': {'outline': outline, 'highlights': hl}}
s = json.dumps(data, indent=2, default=lambda o: o.item())
s = re.sub(r'\[\s*((?:-?[\d.]+,\s*)*-?[\d.]+)\s*\]', lambda m: '[' + re.sub(r',\s*', ', ', m.group(1)) + ']', s)
open(os.path.join(out, 'clock.json'), 'w').write(s + '\n')
print(f'clocks/{a.id}: {cols} x {nrows} cells, neck at row {neck}, holds {N} grains. Now run tools/build_catalog.py')
