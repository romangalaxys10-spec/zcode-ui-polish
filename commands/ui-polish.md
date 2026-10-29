---
description: Design-mirror pass that fixes bad AI frontend output (colors, spacing, type, radii, shadows) against a reference site or design tokens.
allowed-tools: Read, Bash, Write, Edit, Grep, Glob
argument-hint: [reference-url-or-tokens-file] [app-url]
---
Invoke the `ui-polish` skill with this input: **$ARGUMENTS**

Args are two parts, either order: the reference (a site URL, a stylesheet
path, or a design-tokens JSON) and the app URL you want polished.

If args are empty:
- ask which screen of which app to polish and what to mirror it onto
  (a URL, a CSS file, or a tokens file);
- if no browser tool is active, ask the user to capture the current state
  as a screenshot and pass the path;
- run the skill's capture / extract / diff / batch-fix / re-capture loop,
  presentation properties only, one logged change at a time.
