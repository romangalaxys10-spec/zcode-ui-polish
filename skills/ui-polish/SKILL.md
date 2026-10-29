---
name: ui-polish
description: Use when an AI-generated or rushed frontend looks off and needs to be brought up to the level of a real reference site or a design-tokens spec. Captures the current state, extracts the reference design system, diffs, and applies presentation-only fixes in small batches. Do not use for new feature work or refactors; this skill changes looks, not behavior.
---

# ui-polish

Fix a UI that is functionally correct but visually off, by mirroring a reference design.

## Inputs

- `app`: how the current UI is reached. One of:
  - a running URL the agent can open with a browser tool,
  - a user-supplied screenshot of the current UI (path),
  - the user says "use my screenshots" and supplies paths.
- `reference`: one of
  - a live site URL whose CSS is the source of truth,
  - a design-tokens file (JSON/CSS) the user maintains,
  - a reference screenshot from a real product.
- `region`: which screen(s) to polish. Default: the first route of the app.

## Workflow

### 1. Capture the current state

- If a browser tool is available (Playwright, chrome-devtools, or browser-use), open the app URL and capture a screenshot to `ui-polish/current-<ts>.png`.
- If no browser tool is available, stop and instruct the user:
  "No browser tool is active. Take a screenshot of the current UI (full page,
  at 1280px wide if possible) and save it to a path you pass me. I will diff
  against it."
- Read the screenshot. Note what looks wrong in one line each: wrong colors,
  wrong spacing rhythm, inconsistent radii, type scale chaos, flat/no shadows.

### 2. Extract the reference design system

- If the reference is a CSS file or a live site stylesheet:
  ```bash
  python3 scripts/design_tokens.py <path-or-curl-saved-file.css> -o tokens.json
  ```
  The script is stdlib-only and parses hex/rgb/hsl colors, font-size values,
  spacing values, border-radius, and font-family stacks into a token JSON.
- If the reference is the user's design-tokens JSON file, read it directly;
  map its keys to the same shape: `colors`, `font_sizes`, `spacing`,
  `radii`, `shadows`, `font_families`.
- If the reference is a screenshot only, extract tokens by eye and say so:
  color names as hex approximations, a 4-step type scale, a 4-space spacing
  base. Mark every value `[inferred]` in the log.
- Report the token set back to the user before touching code:
  ```
  Reference tokens:
    colors:  primary #2563eb  bg #f8fafc  text #0f172a  muted #64748b
    type:    12 / 14 / 16 / 24 / 32 px
    spacing: 4 / 8 / 16 / 24 / 32 px
    radii:   4 / 8 / 16 px
    shadows: sm 0 1 2, md 0 4 8
  ```

### 3. Diff current UI against the reference

Walk every component file in the region and record, per property, what the
code says versus what the tokens say. Emit a concrete fix list, not prose:

```
1. .card uses border-radius: 0;  reference says 8px.  Fix: border-radius: 8px
2. .btn uses #1d4ed8 14px/1;  reference primary is #2563eb at 16px/1.5.
   Fix: background: #2563eb; font-size: 16px; line-height: 1.5
3. Spacing between .header and .main is 22px (magic number).
   Reference scale: 24px. Fix: margin-top: 24px
```

Rules for the diff:
- Only presentation properties are in scope: color, background, border,
  border-radius, margin, padding, gap, font-size, line-height, font-family,
  font-weight, box-shadow, opacity.
- Anything that changes structure, props, state, or behavior is out of scope.
  If a fix would require touching logic, drop it from the list and say why.

### 4. Apply fixes in small batches

- Batch = at most ~5 files or ~15 property changes per commit-size unit.
- For each change, append one line to `ui-polish/polish-log.md`:
  `file:line property old -> new : reason (token name)`.
- After a batch, re-run step 1 (screenshot) and compare against the previous
  capture. If a batch moved the UI the wrong way, revert that batch and log
  `REVERT reason`.

### 5. Iterate to parity

- Repeat capture / diff / batch until:
  - the screenshot reads as the reference at a glance, or
  - two consecutive loops find zero new fixable diffs, or
  - the user says stop.
- Final message: the polish log summary (n changes, n reverts), the last
  screenshot path, and any diffs you chose not to fix with the reason.

## Guardrails

- Never edit event handlers, hooks, state, data fetching, or routing while
  polishing. Presentation properties only.
- Never delete or rename classes; adjust the declarations inside them so other
  code keeps working.
- Do not invent tokens: every value applied must trace to step 2's set or to
  the user's tokens file. Inferred values carry `[inferred]`.
- Log every change. No silent edits.
- Honest limit: CSS extraction sees what is written, not what the browser
  actually renders after cascade/overrides. The screenshot in step 1 is the
  ground truth; the token JSON is the target. If they disagree, trust the
  screenshot and note the mismatch.
- Honest limit: cross-browser rendering differences (font metrics, subpixel
  rounding) will make "pixel parity" unreachable. The goal is "reads the same".
