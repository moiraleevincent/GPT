# Stillwater — bedtime aquarium

A quiet, entirely hand-drawn animated aquarium that runs in a web browser. No video, account, external assets, packages, build step, or internet access after loading are required.

**Open:** [Stillwater aquarium](./index.html)

## What lives here
- Seventeen slow-swimming fish in pearlescent colors and a little school of distant fish
- Three translucent, softly pulsing jellyfish
- Rising bubbles, floating particles, drifting light, kelp, anemones, rocks, coral and a tiny snail
- A dimmer for late-night watching
- Pause/resume, fullscreen, and touch ripples

## Fullscreen
Tap the **expand** icon. Desktop browsers and most Android browsers support the fullscreen button.

**iPhone Safari:** Apple does not expose the same fullscreen API to ordinary web pages. To remove browser chrome, open the page in Safari, choose **Share → Add to Home Screen**, and then open Stillwater from its new Home Screen icon. The app is set up for standalone display. The page also fills the available browser viewport without scrolling.

## Hosting from GitHub
If GitHub Pages is enabled with **Deploy from a branch → main → /(root)**, the aquarium URL is:

https://moiraleevincent.github.io/GPT/stillwater/

If Pages is not yet enabled: repository **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save**. This leaves other projects in the repository untouched.

For a quick static preview without Pages, use:
https://raw.githack.com/moiraleevincent/GPT/main/stillwater/index.html

## Files
- index.html — all illustrations, movement and controls, in one HTML file
- manifest.webmanifest — home-screen/standalone settings
- icon.svg — jellyfish home-screen icon

Everything is offline-friendly after it has loaded, but offline reopening requires the browser to have cached the page. For a guaranteed offline copy, download index.html and open it locally on a computer.
