#!/usr/bin/env python3
"""Make a sand part from any picture.

    python3 tools/make_sand.py <id> photo.jpg --name "Starry Night" --by "Vincent van Gogh, in sand"

The picture is cropped to the shape of the lower bulb (use --focus 0.5,0.3 to choose what stays in
view, as fractions of width and height), and its own colours become the sand: --colors sets how many
(6 or 7 suits most pictures), or pass --palette "#C82D32,#F0E4CC,..." to choose them yourself.
The top of the picture is left as a light layer of loose sand, like the original designs.
Writes web/content/sands/<id>/ with sand.json, picture.png and preview.png (how it will look).
"""
import argparse, json, os, re
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, '..', 'web', 'content')
ap = argparse.ArgumentParser()
ap.add_argument('id'); ap.add_argument('image')
ap.add_argument('--name'); ap.add_argument('--by', default='')
ap.add_argument('--colors', type=int, default=6); ap.add_argument('--palette')
ap.add_argument('--focus', default='0.5,0.4'); ap.add_argument('--match', choices=['lab', 'rgb'], default='lab')
a = ap.parse_args()

# the shape: the same light top layer as the Mona Lisa sand, at twice the grid size for detail
ref = Image.open(os.path.join(CONTENT, 'sands', 'mona-lisa', 'picture.png'))
GW, GH = ref.size[0] * 2, ref.size[1] * 2
shape = np.asarray(ref.split()[-1].resize((GW, GH), Image.NEAREST)) > 127
src = Image.open(a.image).convert('RGB')
fx, fy = (float(v) for v in a.focus.split(','))
sw, sh = src.size; want = GW / GH
if sw / sh > want: cw, ch = int(sh * want), sh
else: cw, ch = sw, int(sw / want)
x0 = int(min(max(0, fx * sw - cw / 2), sw - cw)); y0 = int(min(max(0, fy * sh - ch / 2), sh - ch))
pic = np.asarray(src.crop((x0, y0, x0 + cw, y0 + ch)).resize((GW, GH), Image.LANCZOS))
px = pic[shape].reshape(-1, 3).astype(np.float32)
if a.palette:
    pal = [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in a.palette.split(',')]
else:
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
    _, _, centers = cv2.kmeans(px, a.colors, None, crit, 6, cv2.KMEANS_PP_CENTERS)
    pal = np.clip(centers, 0, 255)[np.argsort(centers.sum(1))].round().astype(int).tolist()
lum = [0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2] for c in pal]
order = np.argsort(lum)[::-1]
mix = [0.0] * len(pal); mix[int(order[0])] = 0.75; mix[int(order[1])] = 0.25   # loose sand on top: the two lightest colours
out = os.path.join(CONTENT, 'sands', a.id); os.makedirs(out, exist_ok=True)
Image.fromarray(np.dstack([pic, (shape * 255).astype(np.uint8)]), 'RGBA').save(os.path.join(out, 'picture.png'), optimize=True)
data = {'name': a.name or a.id, 'by': a.by, 'picture': 'picture.png', 'palette': pal, 'shades': [0.8, 0.94, 1.08, 1.2],
        'topMix': mix, 'match': a.match, 'diffusion': 0.85}
s = json.dumps(data, indent=2, ensure_ascii=False, default=lambda o: o.item())
s = re.sub(r'\[\s*((?:-?[\d.]+,\s*)*-?[\d.]+)\s*\]', lambda m: '[' + re.sub(r',\s*', ', ', m.group(1)) + ']', s)
open(os.path.join(out, 'sand.json'), 'w').write(s + '\n')
# preview: the picture in sand colours (nearest colour, no dithering), at grid size
small = np.asarray(Image.fromarray(pic).resize((GW // 2, GH // 2), Image.LANCZOS)).astype(np.float32)
cands = np.array([[min(255, c * f) for c in col] for col in pal for f in data['shades']], np.float32)
d = ((small[..., None, :] - cands[None, None]) ** 2).sum(-1)
prev = cands[d.argmin(-1)].astype(np.uint8)
m = shape[::2, ::2]; prev[~m] = cands[int(order[0]) * 4 + 2].astype(np.uint8)
Image.fromarray(prev).resize((GW * 2, GH * 2), Image.NEAREST).save(os.path.join(out, 'preview.png'))
print(f'sands/{a.id}: {len(pal)} colours {pal}. Check preview.png, then run tools/build_catalog.py')
