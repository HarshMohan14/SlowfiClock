#!/usr/bin/env python3
"""Check every part in web/content and gather them into web/content/catalog.json.

Run this after adding or changing a clock, background, sand, music or design:

    python3 tools/build_catalog.py

It also refreshes the offline list in web/sw.js, so new files work without a connection.
"""
import json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
CONTENT = os.path.join(ROOT, 'content')
KINDS = {'clocks': 'clock.json', 'backgrounds': 'background.json', 'sands': 'sand.json', 'music': 'music.json'}
TIERS = ['common', 'uncommon', 'rare', 'epic', 'legendary']
problems = []

def need(cond, msg):
    if not cond: problems.append(msg)

def load_parts(kind):
    out = {}
    base = os.path.join(CONTENT, kind)
    for pid in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        f = os.path.join(base, pid, KINDS[kind])
        if not os.path.isfile(f): continue
        try: out[pid] = json.load(open(f))
        except Exception as e: problems.append(f'{kind}/{pid}: {KINDS[kind]} is not valid JSON ({e})')
    return out

def has_file(kind, pid, name):
    return bool(name) and os.path.isfile(os.path.join(CONTENT, kind, pid, name))

cat = {k: load_parts(k) for k in KINDS}
for pid, c in cat['clocks'].items():
    w = f'clocks/{pid}'
    need(has_file('clocks', pid, c.get('frame')), f'{w}: frame image "{c.get("frame")}" is missing')
    g = c.get('grid', {})
    rows, cols, neck = g.get('rows', []), g.get('cols', 0), g.get('neck', -1)
    need(rows and cols and 0 < neck < len(rows) - 1, f'{w}: grid needs rows, cols and a neck inside the glass')
    need(all(len(r) == 2 for r in rows), f'{w}: every grid row is [first column, last column]')
    need(len(c.get('pile', [])) == cols, f'{w}: pile needs one value per column ({cols})')
    need(len(c.get('anchor', [])) == 2 and len(c.get('size', [])) == 2, f'{w}: size and anchor are [x, y]')
    need(len(c.get('glass', {}).get('outline', [])) >= 4, f'{w}: glass outline needs at least 4 points')
for pid, b in cat['backgrounds'].items():
    w = f'backgrounds/{pid}'
    need(has_file('backgrounds', pid, b.get('image')), f'{w}: image "{b.get("image")}" is missing')
    need(len(b.get('desk', [])) == 2, f'{w}: desk is the [x, y] point where the clock stands')
    need(b.get('size') == [941, 1672], f'{w}: size should be [941, 1672] (the image may be larger, same shape)')
for pid, s in cat['sands'].items():
    w = f'sands/{pid}'
    need(has_file('sands', pid, s.get('picture')), f'{w}: picture "{s.get("picture")}" is missing')
    pal, sh = s.get('palette', []), s.get('shades', [])
    need(2 <= len(pal) and len(pal) * len(sh) <= 255, f'{w}: palette needs 2+ colours, and colours x shades at most 255')
    need(not s.get('topMix') or len(s['topMix']) == len(pal), f'{w}: topMix needs one weight per palette colour')
    need(s.get('match', 'lab') in ('lab', 'rgb'), f'{w}: match is "lab" or "rgb"')
for pid, m in cat['music'].items():
    w = f'music/{pid}'
    need(m.get('type') in ('synth', 'file'), f'{w}: type is "synth" or "file"')
    if m.get('type') == 'file': need(has_file('music', pid, m.get('file')), f'{w}: file "{m.get("file")}" is missing')

designs = json.load(open(os.path.join(CONTENT, 'designs.json')))['designs']
ids = set()
for d in designs:
    w = f'design "{d.get("id")}"'
    need(d.get('id') and d['id'] not in ids, f'{w}: needs a unique id'); ids.add(d.get('id'))
    need(d.get('tier') in TIERS, f'{w}: tier is one of {", ".join(TIERS)}')
    for key, kind in (('clock', 'clocks'), ('background', 'backgrounds'), ('sand', 'sands'), ('music', 'music')):
        need(d.get(key) in cat[kind], f'{w}: {key} "{d.get(key)}" not found in content/{kind}/')

warnings = []
for d in designs:
    b = cat['backgrounds'].get(d.get('background'), {})
    if b.get('clockPainted') and d.get('clock') not in b['clockPainted']:
        warnings.append(f'design "{d["id"]}": background "{d["background"]}" has a clock painted in it, so "{d["clock"]}" will show the old one behind it')
for wtxt in warnings: print('Warning:', wtxt)
if problems:
    print('Not built. Please fix:'); [print(' -', p) for p in problems]; sys.exit(1)

cat['designs'] = designs
json.dump(cat, open(os.path.join(CONTENT, 'catalog.json'), 'w'), separators=(',', ':'), ensure_ascii=False)

# everything the app needs offline
files = ['./', './index.html', './manifest.webmanifest', './content/catalog.json']
for sub in ('icons', 'fonts'):
    files += [f'./{sub}/{f}' for f in sorted(os.listdir(os.path.join(ROOT, sub))) if not f.endswith('.txt')]
for d in designs:
    if d.get('enabled') is False: continue
    c, b, s, m = cat['clocks'][d['clock']], cat['backgrounds'][d['background']], cat['sands'][d['sand']], cat['music'][d['music']]
    files += [f"./content/clocks/{d['clock']}/{c['frame']}", f"./content/backgrounds/{d['background']}/{b['image']}", f"./content/sands/{d['sand']}/{s['picture']}"]
    if m['type'] == 'file': files.append(f"./content/music/{d['music']}/{m['file']}")
files = list(dict.fromkeys(files))
sw = os.path.join(ROOT, 'sw.js'); txt = open(sw).read()
a, b = txt.index('// precache:start'), txt.index('// precache:end')
txt = txt[:a] + '// precache:start\nconst ASSETS = ' + json.dumps(files, indent=2) + ';\n' + txt[b:]
open(sw, 'w').write(txt)
on = [d['id'] for d in designs if d.get('enabled') is not False]
print(f"catalog.json: {len(cat['clocks'])} clocks, {len(cat['backgrounds'])} backgrounds, {len(cat['sands'])} sands, {len(cat['music'])} music, {len(designs)} designs ({len(on)} on: {', '.join(on)})")
