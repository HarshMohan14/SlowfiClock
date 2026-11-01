# Adding designs to SlowfiClock

Every design is four parts put together. Each part lives in its own folder under `web/content/`,
so you can add one part and reuse the rest.

| Part | Folder | What it is |
| --- | --- | --- |
| Clock | `clocks/<id>/` | The hourglass frame (wood, brass, caps, base) and the shape of its glass |
| Background | `backgrounds/<id>/` | The scene behind the clock, plus light effects such as stars or a lamp glow |
| Sand | `sands/<id>/` | The sand colours and the picture the sand settles into |
| Music | `music/<id>/` | A music file, or the lofi loop the app plays live |

A design is one line in `web/content/designs.json` that names one of each:

```json
{ "id": "mona", "title": "Mona Lisa", "tier": "legendary",
  "clock": "walnut-lamp", "background": "night-desk", "sand": "mona-lisa", "music": "lofi-keys" }
```

- `tier` is the rarity it is collected at: `common` (under 1 hr), `uncommon` (1–2 hr), `rare` (2–3 hr),
  `epic` (3–5 hr) or `legendary` (5–8 hr). A session gets a random design from its tier.
- `"enabled": false` keeps a design out of the app while you try it. Open the app with
  `?design=<id>` at the end of the address to see it anyway.

After any change, run:

```
python3 tools/build_catalog.py
```

It checks every part, tells you exactly what is missing, and writes `web/content/catalog.json`
(the one file the app reads) and the offline list in `web/sw.js`.

## Adding a sand (the easiest part)

Any picture works: a painting, a photo, an illustration.

```
python3 tools/make_sand.py starry-night starry.jpg --name "Starry Night" --by "Vincent van Gogh, in sand" --colors 6 --focus 0.5,0.4
```

- `--colors` is how many sand colours to take from the picture (6–7 suits most). Or choose them
  yourself: `--palette "#C82D32,#F0E4CC,#282321,#C38B5B,#42704A,#C39A48"`.
- `--focus` is what stays in view when the picture is cropped to the bulb's shape
  (fractions of width and height; `0.5,0.3` keeps the upper middle).
- Look at `preview.png` in the new folder to see roughly how it will settle.

The app works out the exact grains for every clock, so one sand fits any clock.

## Adding a background

1. A picture of **941 × 1672** (or larger with the same shape, for example 1882 × 3344), as JPEG.
   Paint it **without an hourglass**: an empty desk or surface where a clock can stand.
2. Make `backgrounds/<id>/background.json`:

```json
{
  "name": "Rainy library",
  "alt": "A wooden library desk by a rainy window at night",
  "image": "image.jpg",
  "size": [941, 1672],
  "desk": [477.5, 1388.7],
  "effects": [
    { "type": "glow", "x": -200, "y": 200, "w": 520, "h": 520, "color": [255, 196, 110], "strength": 0.32, "pulse": "lamp" },
    { "type": "stars", "area": [240, 16, 930, 336], "avoid": [[330, 70, 620, 235]], "count": 26 }
  ]
}
```

- `desk` is the point on the picture where the bottom centre of the clock stands.
- Effects are optional. A `glow` is a soft light (`pulse` can be `lamp`, `flood` or left out);
  `stars` twinkle inside `area` and stay out of the `avoid` boxes (all in picture pixels).

The two current backgrounds (`night-desk`, `stadium-dusk`) already have the walnut hourglass painted
in, so they only fit the two walnut clocks. The catalog tool warns if a design pairs them with another clock.

Prompt idea for an image generator: *"Lofi anime illustration, portrait 9:16, a cosy desk by a
window at night, warm lamp light, empty space in the centre of the desk for an object, no hourglass,
no people, soft painterly detail."*

## Adding a clock

Two images of the same size, drawn at the scene's scale (the scene is 941 × 1672; the walnut clock
is about 600 × 1150):

- `frame.png`: the frame only (caps, posts, base, brass) on a transparent background, with the glass
  itself left transparent. The app draws the glass, its shine and the sand.
- `glass.png`: a black-and-white mask, white where the sand can be (inside both bulbs).

```
python3 tools/make_clock.py brass-slim frame.png glass.png --name "Brass, slim"
```

It finds the neck, the bulbs, how much sand the clock holds and where it stands, and writes
`clocks/brass-slim/clock.json`. Shine lines on the glass are added automatically and can be edited
in `glass.highlights`.

## Adding music

- A file: put `track.mp3` in `music/<id>/` with

```json
{ "name": "Rain on paper", "type": "file", "file": "track.mp3", "gain": 0.62, "credit": "Music: “Rain on paper” by …" }
```

- The built-in loop: `{ "name": "Lofi keys", "type": "synth", "preset": "lofi-keys", "credit": "Music: a lofi loop the app plays live." }`

Use only music you have the rights to, and put the credit the licence asks for in `credit`
(it shows in Settings).
