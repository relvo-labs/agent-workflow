# Banner assets

`banner-desktop.png` and `banner-mobile.png` are provider/tool-neutral, English-only
renders of the README banner. Editable source and provenance:

- [diagrams/banner.json](../diagrams/banner.json) — editable content (labels, notes,
  skill/record names). Edit this, not the SVG.
- [tools/banner_diagram.py](../tools/banner_diagram.py) — the renderer.
- [diagrams/banner-desktop.svg](../diagrams/banner-desktop.svg) and
  [diagrams/banner-mobile.svg](../diagrams/banner-mobile.svg) — generated SVG,
  never hand-edited.

## Regenerate the SVG

```sh
.venv/bin/python tools/generate_diagram.py --banner
.venv/bin/python tools/generate_diagram.py --banner --check
```

This only touches `diagrams/banner-desktop.svg` and `diagrams/banner-mobile.svg`;
it does not change `diagrams/core.json` or `diagrams/core.svg`.

## Rasterize to PNG (manual, optional)

PNG output is for README rendering compatibility only; the SVG is the source of
truth. Rasterization is a manual, optional step and intentionally is **not** a
pinned project dependency (no headless-browser or raster library is added to
`requirements.in`/`requirements.txt`). Any real browser can do this: open each
generated SVG at its own intrinsic `width`/`height` (read the SVG root element)
and export/screenshot it at that exact pixel size, for example with a headless
Chromium already available on the operator's machine:

```sh
chromium --headless --disable-gpu --hide-scrollbars \
  --window-size=1440,1171 --screenshot=assets/banner-desktop.png \
  diagrams/banner-desktop.svg
chromium --headless --disable-gpu --hide-scrollbars \
  --window-size=560,2270 --screenshot=assets/banner-mobile.png \
  diagrams/banner-mobile.svg
```

Replace the two `--window-size` values with the current `width`/`height`
attributes of each generated SVG if `diagrams/banner.json` changes. This step
is not run automatically here; it requires real browser rendering.
