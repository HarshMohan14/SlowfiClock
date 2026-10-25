# SlowfiClock

D·Focus: a lamplit focus hourglass. Real falling sand settles grain by grain into the Mona Lisa as your session ends. Installable as a web app, works offline, and the sand follows your phone's motion sensor.

Everything in this folder is the app: `index.html`, `manifest.webmanifest`, `sw.js` and `icons/`.
Motion sensors and installing only work over **https**, so put the folder on any static host first.

## Put it online (2 minutes, free)

- **Netlify Drop:** open https://app.netlify.com/drop and drag this whole folder onto the page. You get an https link straight away.
- **GitHub Pages:** push the folder to a repository, then Settings → Pages → deploy from the main branch.
- **Vercel / Cloudflare Pages:** create a project from the folder; no build step is needed.

## Install it on your phone

- **iPhone (Safari):** open the link → Share → **Add to Home Screen**. Open it from the home screen, tap **Start focus**, and allow **Motion & Orientation** when asked.
- **Android (Chrome):** open the link → menu → **Install app** (or the install banner). Motion works without a prompt.

## What the phone controls

- **Tilt:** sand follows real gravity. Lean the phone and the stream bends; turn it on its side and the sand slides away from the neck, so time rests; turn it upside down and the sand (and time) flows back.
- **Lying flat:** by default the hourglass keeps standing when the phone lies on a desk. Turn this off in Settings → Motion for pure physics.
- **Shake:** shake the phone, or flick the hourglass on screen.
- **Finished?** Turn the phone over to start the sand again, like a real hourglass.
- **Screen:** stays awake during a session. On Android the app is locked to portrait; on iPhone, turn on Portrait Orientation Lock so the hourglass stays fixed to the phone.

After the first visit the app works offline.
