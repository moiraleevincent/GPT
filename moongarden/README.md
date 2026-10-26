# Moongarden

A quiet, moonlit aquarium for sleep and study. Original Canvas 2D illustration and animation: five translucent jellyfish with pulsing bells and flowing tentacles, 28 fish, layered kelp, rounded stones, suspended particles, and slow shafts of light. Silent by design so it can accompany music, a video, or quiet work.

## Open

GitHub Pages (when enabled for main / root): https://moiraleevincent.github.io/GPT/moongarden/

Static preview: https://raw.githack.com/moiraleevincent/GPT/main/moongarden/index.html

No installation or build step. All animation is in index.html; no external libraries, fonts, images, accounts, or network requests are needed once loaded.

## Controls

- **Study / Sleep:** normal illumination or a slower, dimmer scene.
- **Settings:** brightness, motion speed, optional 15/30/60-minute fade-to-black timer, and opt-in screen wake lock where supported.
- **Pause / Space:** freeze or resume. Reduced-motion preferences start the scene paused.
- **Fullscreen / F:** native fullscreen where supported; a helpful fallback appears otherwise.
- Controls disappear after inactivity. Tap or move the pointer to reveal them; keyboard focus keeps controls accessible.
- Brightness, mode and speed are saved locally. Timer and keep-awake are session-only.
- At the timer deadline the scene turns black and animation pauses. Resume or select a mode/change brightness to illuminate the scene again.

## iPhone / iPad

Open the hosted aquarium in Safari → Share → Add to Home Screen, then launch the icon for standalone display. Native fullscreen depends on browser/device support. The scene fits both portrait and landscape without scrolling. No actual iPhone device test was available during development.

## Implementation / validation

Single HTML file with Canvas 2D. Pixel ratio is capped at 1.75; the static background is cached, movement stops in hidden tabs, and frame deltas are bounded on return. A wake lock failure leaves the device's normal timeout in place. Timers use wall-clock time but cannot run while a device/browser is suspended; on return the elapsed deadline is applied.

Validated JavaScript syntax and inspected the rendered desktop scene in the preview browser. Exercised Study/Sleep, settings, pause/resume, and fullscreen fallback. Native fullscreen was blocked by the preview browser. Timer duration, physical iPhone behavior and OS wake-lock persistence were not device-tested.
