# UI Polish

Design-mirror pass that fixes bad AI frontend output by mirroring a reference design system.

## Why

AI-generated frontends ship the logic right and the looks wrong: flat colors,
magic-number spacing, inconsistent radii, type scales that do not add up.
Hand-tweaking that is slow and easy to forget. UI Polish makes the fix
mechanical: capture the current UI, extract the reference token set, diff,
apply presentation-only fixes in small logged batches, re-capture, repeat.
Functionality is never touched.

## How it works

1. Capture the current state: browser tool screenshot, or user-supplied screenshot.
2. Extract reference tokens: `design_tokens.py` parses a CSS file (or a
   design-tokens JSON is read directly) into colors, font sizes, spacing,
   radii, shadows, font families.
3. Diff: a concrete fix list of exact property changes, one line each.
4. Apply in small batches, each change logged to `ui-polish/polish-log.md`.
5. Re-capture and iterate until the UI reads like the reference or the user stops it.

## Install

Option A: self-installable marketplace.

- Clone or download this repo.
- ZCode: Plugin Marketplace -> Add -> Add Plugin Marketplace.
- Paste the folder path to this repo.
- Install the `ui-polish` plugin from the list.

Option B: manual copy.

- Copy this folder into your workspace `plugins/` directory
  (e.g. `~/.zcode/workspace/<name>/plugins/ui-polish` or the repo-local
  `plugins/ui-polish`).
- Restart the session so the skill loads.

## Try it

```
/ui-polish https://linear.app myapp.local
```

Expected: the current state of `myapp.local` is captured, Linear's stylesheet
tokens are extracted, and a numbered fix list of exact CSS changes is emitted
before anything is edited. Batches of 5 files or less are applied, logged,
and re-captured until the screen reads like the reference.

## Requirements

- Python 3 standard library only (no pip installs).
- A CSS file, a design-tokens JSON, or a live reference URL.
- For automatic capture: an active browser tool. Without one, the skill
  instructs the user how to supply screenshots manually.

---

<p align="center">
  <a href="https://z.ai/subscribe?ic=R0K78RJKNW"><img alt="z.ai coding plans - 10% OFF coupon" src="https://img.shields.io/badge/z.ai%20coding%20plans-10%25%20OFF%20coupon-blueviolet" /></a>
  <a href="https://zcode.z.ai/invite/ALWM9JUA"><img alt="Try ZCode free" src="https://img.shields.io/badge/Try%20ZCode-free%20invite-0969da" /></a>
</p>

## License

MIT.
