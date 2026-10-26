# SlowfiClock — installable web app

A slow lofi focus clock. Pick a time and a mode, and real falling sand settles into a picture as your session ends. Every finished clock joins your clock gallery.

Everything in this folder is the app: `index.html`, `manifest.webmanifest`, `sw.js`, `icons/`, the two clock images and the music file.
Motion sensors and installing only work over **https**, so it needs a static host (this repo deploys on Vercel; no build step).

## Install it on your phone

- **iPhone (Safari):** open the link → Share → **Add to Home Screen**. Allow **Motion & Orientation** when asked.
- **Android (Chrome):** open the link → menu → **Install app**.

## How a session goes

1. **Home:** pick a time (30 min, 1, 2, 3 hr or custom up to 8 hr) and a mode (Reading, Studying, Coding, Designing, Writing, Deep work, Hobby). The session starts as soon as both are picked.
2. **Silence notifications:** a gentle prompt to turn on Do Not Disturb, with the steps for your phone. It can be switched off in the prompt or in Settings. A web app can't switch Do Not Disturb on by itself.
3. **Session:** only the hourglass, with sound, play/pause and settings. Tilt, shake, or turn the phone over like a real hourglass.
4. **Complete:** a quiet thank-you card with the clock you collected, its rarity and a short quote. Start a new session or open the gallery.

## Clock gallery and rarity

Rarity follows the length of the session that made the clock:

| Rarity | Session length |
| --- | --- |
| Common | under 1 hr |
| Uncommon | 1–2 hr |
| Rare | 2–3 hr |
| Epic | 3–5 hr |
| Legendary | 5–8 hr |

Each theme belongs to one rarity (CR7 is Rare, Mona Lisa is Legendary). A session gets a random theme from its rarity; while a rarity has no theme of its own yet, any theme can appear. The home screen shows this month as a row of dots (filled on days you focused) and your latest clocks. Nothing is lost for missed days. History is kept on the device only.

## Music

- **CR7** (stadium at dusk) plays “Transformation” by Purrple Cat, licensed CC BY 4.0, credit: Purrple Cat.
- **Mona Lisa** (night desk) plays a lofi loop generated live by the app.
