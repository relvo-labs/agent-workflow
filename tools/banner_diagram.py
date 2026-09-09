"""Provider/tool-neutral README banner renderer, generated only from diagrams/banner.json.

Two deterministic SVG layouts share one content source:
- desktop: a wide multilane engineering composition (diagrams/banner-desktop.svg)
- mobile: a single-column composition, not a scaled-down desktop copy and not a
  serialization of the alternative execution modes (diagrams/banner-mobile.svg)

Color semantics are consistent across both layouts: cyan = route/execution,
emerald = evidence, purple (dashed) = controls, amber (dashed) = optional
development lifecycle, red = blocked. A small legend under the header names
these once so individual arrows can stay unlabeled.

Never hand-edit the generated SVG files; edit diagrams/banner.json or this
module and regenerate with `tools/generate_diagram.py --banner`.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Dark navy engineering palette. Accent colors are semantic (route/evidence/
# control/lifecycle), never provider brand colors or logos.
BG = '#0a0f1e'
GRID = '#1b2740'
PANEL = '#101a30'
PANEL_ALT = '#0d1526'
BORDER = '#2c3b5c'
TEXT = '#f4f7fb'
MUTED = '#a9b4c9'
CYAN = '#22d3ee'
EMERALD = '#34d399'
PURPLE = '#a685fa'
AMBER = '#f5a524'
BLOCKED = '#fb7185'

COLOR_MAP = {'cyan': CYAN, 'emerald': EMERALD, 'purple': PURPLE, 'amber': AMBER, 'blocked': BLOCKED}


def esc(value) -> str:
    return escape(str(value), quote=True)


def wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ''
    for word in words:
        trial = f'{current} {word}'.strip()
        if len(trial) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or ['']


def max_chars_for(width: float, size: float, pad: float = 22) -> int:
    return max(6, int((width - 2 * pad) / (size * 0.56)))


def text_lines(x, y, lines, size, color, weight='400', line_height=None, anchor='start', family='sans-serif'):
    lh = line_height or size + 7
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x:g}" y="{y + i * lh:g}" font-family="{family}" font-size="{size:g}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{esc(line)}</text>'
        )
    return out


def rect(x, y, w, h, fill, stroke=None, stroke_width=2, dash=None, rx=14):
    stroke_attr = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ''
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}"{stroke_attr}{dash_attr}/>'


def grid(width, height, spacing=44):
    out = [f'<rect width="{width:g}" height="{height:g}" fill="{BG}"/>']
    x = spacing
    while x < width:
        out.append(f'<line x1="{x:g}" y1="0" x2="{x:g}" y2="{height:g}" stroke="{GRID}" stroke-width="1" opacity="0.35"/>')
        x += spacing
    y = spacing
    while y < height:
        out.append(f'<line x1="0" y1="{y:g}" x2="{width:g}" y2="{y:g}" stroke="{GRID}" stroke-width="1" opacity="0.35"/>')
        y += spacing
    return out


def markers():
    def marker(id_, color):
        return (
            f'<marker id="{id_}" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto">'
            f'<path d="M0,0 L7,3.5 L0,7 Z" fill="{color}"/></marker>'
        )
    return '<defs>' + marker('arrow-cyan', CYAN) + marker('arrow-emerald', EMERALD) + marker('arrow-muted', MUTED) + marker('arrow-blocked', BLOCKED) + '</defs>'


def edge(path_d, color, marker_id, width=3, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="{width}" marker-end="url(#{marker_id})"{dash_attr}/>'


def card(x, y, w, h, title, note, accent, fill=PANEL, title_size=19, note_size=14.5,
         dash=None, title_dy=30, note_dy=None, note_gap=8, note_color=MUTED, title_color=TEXT):
    out = [rect(x, y, w, h, fill, accent, 2, dash)]
    title_lines = wrap(title, max_chars_for(w, title_size))
    out += text_lines(x + 20, y + title_dy, title_lines, title_size, title_color, weight='600')
    if note:
        note_lines = wrap(note, max_chars_for(w, note_size))
        start_y = note_dy if note_dy is not None else y + title_dy + len(title_lines) * (title_size + 7) - (title_size + 7) + note_gap + note_size
        out += text_lines(x + 20, start_y, note_lines, note_size, note_color)
    return out


def load_banner():
    import json
    return json.loads((ROOT / 'diagrams/banner.json').read_text(encoding='utf-8'))


def render_header(data, x0, width, heading_size, subtitle_size, legend_size, top):
    """Visible heading + subtitle + a compact color legend. Wraps the legend
    onto additional rows if it would overflow the available width, so this
    works for both the wide desktop canvas and the narrow mobile column.
    Returns (svg_elements, bottom_y)."""
    out = []
    y = top + heading_size
    out += text_lines(x0, y, [data['heading']], heading_size, TEXT, weight='700')
    y += subtitle_size + 10
    out += text_lines(x0, y, [data['subtitle']], subtitle_size, MUTED, weight='500')
    y += legend_size + 18

    max_x = x0 + width
    dot_r = max(3, legend_size * 0.34)
    lx = x0
    row_y = y
    for item in data['legend']:
        label = item['label']
        entry_w = dot_r * 2 + 8 + len(label) * legend_size * 0.6 + 26
        if lx + entry_w > max_x and lx > x0:
            lx = x0
            row_y += legend_size + 12
        color = COLOR_MAP[item['color']]
        out.append(f'<circle cx="{lx + dot_r:g}" cy="{row_y - legend_size * 0.32:g}" r="{dot_r:g}" fill="{color}"/>')
        out += text_lines(lx + dot_r * 2 + 8, row_y, [label], legend_size, MUTED, weight='500')
        lx += entry_w
    bottom = row_y + 14
    return out, bottom


def skills_panel_content(x, top, w, sp_):
    """Draw the shared skills/contracts panel body starting at (x, top) with
    width w. Returns (svg_elements, natural_height) so callers may either use
    a fixed surrounding box (desktop sidebar) or size the box to content
    (mobile panel)."""
    heading_lines = wrap(sp_['heading'], max_chars_for(w, 17))
    layer_lines = wrap(sp_['layer_note'], max_chars_for(w, 12.5))
    records_note_lines = wrap(sp_['records_note'], max_chars_for(w, 12))

    out = []
    ty = top + 30
    out += text_lines(x + 20, ty, heading_lines, 17, TEXT, weight='700')
    ty += (len(heading_lines) - 1) * 22 + 24
    out += text_lines(x + 20, ty, [sp_['version_label']], 12.5, CYAN, weight='600')
    ty += 22
    out += text_lines(x + 20, ty, layer_lines, 12.5, MUTED)
    ty += len(layer_lines) * 17 + 18
    out += text_lines(x + 20, ty, [sp_['skills_heading']], 13.5, TEXT, weight='600')
    ty += 16
    for name in sp_['skills']:
        ty += 30
        out.append(rect(x + 20, ty - 20, w - 40, 26, PANEL, CYAN, 1, rx=8))
        out += text_lines(x + 32, ty - 2, [name], 12.5, TEXT)
    ty += 34
    out += text_lines(x + 20, ty, [sp_['records_heading']], 13.5, TEXT, weight='600')
    ty += 16
    for name in sp_['records']:
        ty += 30
        out.append(rect(x + 20, ty - 20, w - 40, 26, PANEL, PURPLE, 1, rx=8))
        out += text_lines(x + 32, ty - 2, [name], 12.5, TEXT)
    ty += 30
    out += text_lines(x + 20, ty, records_note_lines, 12, MUTED)
    content_bottom = ty + max(0, len(records_note_lines) - 1) * 19 + 24
    return out, content_bottom - top


def skills_panel_height(sp_, w):
    _, height = skills_panel_content(0, 0, w, sp_)
    return height


# ---------------------------------------------------------------------------
# Desktop: wide multilane composition with a dedicated skills/contracts sidebar
# ---------------------------------------------------------------------------

def render_desktop(data) -> str:
    W = 1440
    main_w = 1140
    sidebar_x = main_w + 40
    sidebar_w = W - sidebar_x - 40
    margin_x = 40

    body = []  # everything except the outer svg/defs/background, so H can be computed first

    # Header: visible heading + subtitle + legend (fixes: banner had no
    # visible title before; only the SVG <title> existed for accessibility).
    header_elems, y0 = render_header(data, margin_x, W - 2 * margin_x,
                                      heading_size=27, subtitle_size=14, legend_size=12, top=18)
    body += header_elems
    y0 += 12

    # Row 1: intake -> coordinator. The fan-out below must start at the
    # coordinator's own bottom border, not the (taller) intake card's border.
    intake = data['intake']
    coord = data['coordinator']
    ix, iy, iw, ih = margin_x, y0, 260, 118
    cx, cy, cw, ch = 360, y0, 740, 104
    body += card(ix, iy, iw, ih, intake['label'], intake['note'], BORDER, title_size=20)
    body += card(cx, cy, cw, ch, coord['label'], coord['note'], CYAN, title_size=21)
    body.append(edge(f'M{ix+iw:g},{iy+ih/2:g} L{cx:g},{iy+ih/2:g}', CYAN, 'arrow-cyan'))
    coord_bottom = cy + ch
    row1_bottom = max(iy + ih, coord_bottom)

    # Alternatives heading, with generous clearance from the fan-out elbow
    # below it so the label is never crowded against a line.
    heading_y = row1_bottom + 34
    body += text_lines(margin_x, heading_y, [data['alternatives_heading']], 16, MUTED, weight='600')

    # Row 2: three alternative lanes, fed by a cyan fan-out from the
    # coordinator's actual bottom border.
    lane_y = heading_y + 54
    lane_h = 124
    lane_w = 360
    gaps = 20
    lane_xs = [margin_x, margin_x + lane_w + gaps, margin_x + 2 * (lane_w + gaps)]
    for lx, alt in zip(lane_xs, data['alternatives']):
        body += card(lx, lane_y, lane_w, lane_h, alt['label'], alt['note'], BORDER)
        coord_cx = cx + cw / 2
        lane_cx = lx + lane_w / 2
        elbow_y = lane_y - 18
        body.append(edge(f'M{coord_cx:g},{coord_bottom:g} L{coord_cx:g},{elbow_y:g} L{lane_cx:g},{elbow_y:g} L{lane_cx:g},{lane_y:g}',
                          CYAN, 'arrow-cyan'))
    lane_bottom = lane_y + lane_h

    # Purple dashed control strip. Fix: arrows used to fan straight through
    # this strip and overprint its title/note. Now three cyan arrows stop
    # exactly at the strip's top border (controls receive the execution
    # signal) and a single emerald arrow leaves its bottom border toward
    # Result (evidence emerges once controls have applied) -- no line ever
    # enters the strip's text area.
    strip_y = lane_bottom + 34
    strip_h = 92
    strip_w = main_w
    for lx in lane_xs:
        lane_cx = lx + lane_w / 2
        body.append(edge(f'M{lane_cx:g},{lane_bottom:g} L{lane_cx:g},{strip_y:g}', CYAN, 'arrow-cyan'))
    body += card(margin_x, strip_y, strip_w, strip_h, data['control_strip']['label'], data['control_strip']['note'],
                 PURPLE, fill=PANEL_ALT, title_size=17, dash='10,6')
    strip_bottom = strip_y + strip_h
    strip_cx = margin_x + strip_w / 2

    # Single emerald evidence arrow, strip -> Result (aligned so it is a
    # straight vertical line, not a diagonal that could graze the strip text).
    ev = data['evidence']
    ev_w, ev_h = 610, 96
    ev_x = strip_cx - ev_w / 2
    ev_y = strip_bottom + 30
    body.append(edge(f'M{strip_cx:g},{strip_bottom:g} L{strip_cx:g},{ev_y:g}', EMERALD, 'arrow-emerald'))
    body += card(ev_x, ev_y, ev_w, ev_h, ev['label'], ev['note'], EMERALD, title_size=20)
    ev_bottom = ev_y + ev_h
    ev_cx = strip_cx

    # Evidence review: this is still evidence flow, so use the emerald
    # accent (previously cyan, which is reserved for route/execution).
    rv = data['review']
    rv_w, rv_h = 370, 92
    rv_x = ev_cx - rv_w / 2
    rv_y = ev_bottom + 30
    body.append(edge(f'M{ev_cx:g},{ev_bottom:g} L{ev_cx:g},{rv_y:g}', EMERALD, 'arrow-emerald'))
    body += card(rv_x, rv_y, rv_w, rv_h, rv['label'], rv['note'], EMERALD, title_size=20)
    rv_bottom = rv_y + rv_h
    rv_cx = ev_cx
    rv_right = rv_x + rv_w

    # Closure row: deliver / repair / blocked. Extra vertical gap above this
    # row leaves room for short condition labels (Pass / Repair budget /
    # Unresolved) so the three outcomes read as alternatives, not a sequence
    # that happens all at once.
    close_y = rv_bottom + 56
    close_h = 96
    close_w = 360
    close_xs = [margin_x, margin_x + close_w + gaps, margin_x + 2 * (close_w + gaps)]
    close_colors = {'deliver': EMERALD, 'repair': BORDER, 'blocked': BLOCKED}
    close_markers = {'deliver': 'arrow-emerald', 'repair': 'arrow-muted', 'blocked': 'arrow-blocked'}
    close_line_colors = {'deliver': EMERALD, 'repair': MUTED, 'blocked': BLOCKED}
    elbow_y = close_y - 20
    # Condition labels sit just above each branch's final vertical drop, but
    # offset to the side of that line (not centered on it) -- three branches
    # share one trunk immediately below Evidence review before diverging, so
    # a centered label there would sit on top of the line itself.
    condition_label_y = elbow_y - 8
    repair_box = None
    for cxi, item in zip(close_xs, data['closure']):
        item_cx = cxi + close_w / 2
        line_color = close_line_colors[item['id']]
        body.append(edge(f'M{rv_cx:g},{rv_bottom:g} L{rv_cx:g},{elbow_y:g} L{item_cx:g},{elbow_y:g} L{item_cx:g},{close_y:g}',
                          line_color, close_markers[item['id']]))
        body += text_lines(item_cx + 18, condition_label_y, [item['condition']], 11.5, line_color, weight='600', anchor='start')
        body += card(cxi, close_y, close_w, close_h, item['label'], item['note'], close_colors[item['id']])
        if item['id'] == 'repair':
            repair_box = (cxi, close_y, close_w, close_h)
    close_bottom = close_y + close_h

    # Bounded repair recheck: routed as an orthogonal dashed line through the
    # empty gap to the right of the repair card, then across open space to
    # the right of the review card (never crossing the outcome-split lines
    # or any card interior), with its label placed in that same open area.
    rp_x, rp_y, rp_w, rp_h = repair_box
    rp_right = rp_x + rp_w
    gap_x = rp_right + (gaps / 2)
    open_x = rv_right + 210
    p1 = (rp_right, rp_y + 22)
    p2 = (gap_x, rp_y + 22)
    p3 = (gap_x, rv_bottom + 10)
    p4 = (open_x, rv_bottom + 10)
    p5 = (open_x, rv_y + rv_h / 2)
    p6 = (rv_right, rv_y + rv_h / 2)
    path = f'M{p1[0]:g},{p1[1]:g} L{p2[0]:g},{p2[1]:g} L{p3[0]:g},{p3[1]:g} L{p4[0]:g},{p4[1]:g} L{p5[0]:g},{p5[1]:g} L{p6[0]:g},{p6[1]:g}'
    body.append(edge(path, CYAN, 'arrow-cyan', width=2.25, dash='2,7'))
    body += text_lines(open_x + 8, (p4[1] + p5[1]) / 2, [data['repair_edge_label']], 12, CYAN, weight='600')

    # Development-only optional strip
    dev_y = close_bottom + 30
    dev_h = 74
    body += card(margin_x, dev_y, main_w, dev_h, data['dev_strip']['label'], data['dev_strip']['note'],
                 AMBER, fill=PANEL_ALT, title_size=16, dash='10,6')
    dev_bottom = dev_y + dev_h

    # Footer
    footer_y = dev_bottom + 32
    footer_lines = wrap(data['footer'], max_chars_for(main_w, 13))
    body += text_lines(margin_x, footer_y, footer_lines, 13, MUTED)
    content_bottom = footer_y + (len(footer_lines) - 1) * 20 + 24

    # Sidebar: shared skills & contracts layer, spanning the full content
    # column height so it reads as a distinct, always-present layer.
    sp = data['skills_panel']
    sidebar_top = y0
    sidebar_content, sidebar_natural_h = skills_panel_content(sidebar_x, sidebar_top, sidebar_w, sp)
    sidebar_bottom = sidebar_top + sidebar_natural_h + 20

    H = int(max(content_bottom, sidebar_bottom) + 30)
    body.append(rect(sidebar_x, sidebar_top, sidebar_w, H - sidebar_top - 30, PANEL_ALT, BORDER, 2))
    body += sidebar_content

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="title desc">',
           f'<title id="title">{esc(data["heading"])}: {esc(data["title"])}</title>',
           '<desc id="desc">Neutral engineering banner: goal and authority into a coordinator that chooses '
           'direct tools, a single agent or optional multi-agent lanes; questions and checkpoints apply '
           'during execution; evidence fans in for correlated review, one bounded repair, delivery or a '
           'blocked stop; an optional development lifecycle sits below; a shared skills and contracts '
           'layer is shown separately from provider adapters.</desc>']
    out += grid(W, H)
    out.append(markers())
    out += body
    out.append('</svg>\n')
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Mobile: single-column composition. The three alternatives are grouped in one
# bordered block with "or" separators (not stacked as sequential steps), so
# this is not a serialization of the alternative execution modes.
# ---------------------------------------------------------------------------

def render_mobile(data) -> str:
    W = 560
    pad = 24
    card_w = W - 2 * pad

    intake = data['intake']
    coord = data['coordinator']
    alts = data['alternatives']
    strip = data['control_strip']
    ev = data['evidence']
    rv = data['review']
    closure = data['closure']
    dev = data['dev_strip']
    sp = data['skills_panel']

    blocks = []  # list of (kind, payload) describing draw ops, in order

    header_elems, y = render_header(data, pad, card_w, heading_size=21, subtitle_size=12.5, legend_size=10.5, top=16)
    blocks.append(('raw', header_elems))
    y += 14

    def add_card(title, note, accent, h, fill=PANEL, dash=None, title_size=18, note_size=13.5):
        nonlocal y
        blocks.append(('card', (pad, y, card_w, h, title, note, accent, fill, dash, title_size, note_size)))
        top = y
        y += h
        return top, h

    def add_gap_arrow(color, marker_id, gap=34, dash=None, x=None):
        nonlocal y
        cx = x if x is not None else pad + card_w / 2
        blocks.append(('edge', (f'M{cx:g},{y:g} L{cx:g},{y+gap:g}', color, marker_id, dash)))
        y += gap

    # 1. intake
    add_card(intake['label'], intake['note'], BORDER, 92)
    add_gap_arrow(CYAN, 'arrow-cyan')

    # 2. coordinator
    coord_top, coord_h = add_card(coord['label'], coord['note'], CYAN, 114, title_size=19)
    coord_bottom = coord_top + coord_h

    # 3. Heading label confined to the left ~55% of the width, so the
    # coordinator -> alternatives arrow (kept centered) can run straight
    # down beside it without crossing the text, then reach the group's
    # actual top border (fix: arrow used to stop at the label instead).
    heading_gap = 74
    heading_lines = wrap(data['alternatives_heading'], max_chars_for(card_w * 0.56, 13))
    heading_top = coord_bottom + 20
    blocks.append(('text', (pad, heading_top, heading_lines, 13, MUTED, '600', 'start')))
    group_top = coord_bottom + heading_gap
    blocks.append(('edge', (f'M{pad+card_w/2:g},{coord_bottom:g} L{pad+card_w/2:g},{group_top:g}', CYAN, 'arrow-cyan', None)))
    y = group_top

    # grouped alternatives block (single bordered group, "or" separators --
    # not sequential steps)
    inner_pad = 16
    row_h = 74
    sep_h = 22
    n = len(alts)
    group_h = inner_pad * 2 + n * row_h + (n - 1) * sep_h
    blocks.append(('rect', (pad, group_top, card_w, group_h, PANEL_ALT, BORDER, None)))
    ry = group_top + inner_pad
    for i, alt in enumerate(alts):
        blocks.append(('inner_card_text', (pad + inner_pad, ry, card_w - 2 * inner_pad, row_h, alt['label'], alt['note'])))
        ry += row_h
        if i != n - 1:
            blocks.append(('or_sep', (pad + card_w / 2, ry + sep_h / 2)))
            ry += sep_h
    y = group_top + group_h
    add_gap_arrow(CYAN, 'arrow-cyan')

    # 4. control strip (purple dashed) -> single emerald arrow into evidence,
    # matching the desktop semantics (controls apply during execution; the
    # arrow into it and the arrow out of it never cross its text).
    add_card(strip['label'], strip['note'], PURPLE, 120, fill=PANEL_ALT, dash='10,6', title_size=15.5, note_size=12.5)
    add_gap_arrow(EMERALD, 'arrow-emerald')

    # 5. evidence (fan-in target) -- emerald throughout the evidence segment
    add_card(ev['label'], ev['note'], EMERALD, 92, title_size=18)
    add_gap_arrow(EMERALD, 'arrow-emerald')

    # 6. evidence review (emerald accent: still evidence flow, not route)
    add_card(rv['label'], rv['note'], EMERALD, 92, title_size=18)
    add_gap_arrow(CYAN, 'arrow-cyan')

    # 7. grouped closure block (deliver / one bounded repair / blocked): "or"
    # separators (same style as the alternatives group) instead of plain
    # dividers, so the three outcomes read as conditional alternatives, not
    # sequential required steps. Each row carries a short condition label
    # (Pass / Repair budget / Unresolved); the repair row's condition also
    # names the canonical repair_edge_label so mobile states the same
    # bounded-repair fact as desktop without needing a routed connector in
    # this narrow column (there is no free margin to route one without
    # crossing text or clipping off-canvas).
    close_top = y
    close_row_h = 78
    close_sep = 22
    close_h = inner_pad * 2 + 3 * close_row_h + 2 * close_sep
    blocks.append(('rect', (pad, close_top, card_w, close_h, PANEL_ALT, BORDER, None)))
    cy = close_top + inner_pad
    close_colors = {'deliver': EMERALD, 'repair': MUTED, 'blocked': BLOCKED}
    for i, item in enumerate(closure):
        condition = item['condition']
        if item['id'] == 'repair':
            condition = f"{condition} · {data['repair_edge_label']}"
        blocks.append(('inner_card_text', (pad + inner_pad, cy, card_w - 2 * inner_pad, close_row_h,
                                            item['label'], item['note'], close_colors[item['id']], condition)))
        cy += close_row_h
        if i != len(closure) - 1:
            blocks.append(('or_sep', (pad + card_w / 2, cy + close_sep / 2)))
            cy += close_sep
    close_bottom = close_top + close_h
    y = close_bottom

    # The optional development strip is a separate annotation, not a
    # transition that follows "blocked" -- so no arrow connects them; a
    # small gap and its own dashed amber border make that visually clear.
    y += 30

    # 8. dev-only strip
    dev_note_lines = wrap(dev['note'], max_chars_for(card_w, 12.5))
    add_card(dev['label'], dev['note'], AMBER, 56 + len(dev_note_lines) * 18, fill=PANEL_ALT, dash='10,6',
             title_size=15, note_size=12.5)

    y += 30
    # 9. shared skills & contracts panel
    panel_h = skills_panel_height(sp, card_w)
    blocks.append(('skills_panel', (pad, y, card_w, panel_h, sp)))
    y += panel_h + 26

    footer_lines = wrap(data['footer'], max_chars_for(card_w, 12.5))
    blocks.append(('text', (pad, y, footer_lines, 12.5, MUTED, '400', 'start')))
    y += len(footer_lines) * 18 + 30

    H = int(y)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-labelledby="title desc">',
           f'<title id="title">{esc(data["heading"])}: {esc(data["title"])}</title>',
           '<desc id="desc">Neutral single-column banner: goal and authority into a coordinator, one '
           'grouped choice of direct tools, single agent or optional multi-agent execution, questions '
           'and checkpoints during execution, evidence fan-in for correlated review, one bounded repair, '
           'delivery or a blocked stop, an optional development lifecycle shown as a separate annotation, '
           'and a shared skills and contracts layer.</desc>']
    out += grid(W, H, spacing=36)
    out.append(markers())

    for kind, payload in blocks:
        if kind == 'raw':
            out += payload
        elif kind == 'card':
            x, by, w, h, title, note, accent, fill, dash, title_size, note_size = payload
            out += card(x, by, w, h, title, note, accent, fill=fill, dash=dash, title_size=title_size, note_size=note_size)
        elif kind == 'rect':
            x, by, w, h, fill, stroke, dash = payload
            out.append(rect(x, by, w, h, fill, stroke, 2, dash))
        elif kind == 'inner_card_text':
            if len(payload) == 6:
                x, by, w, h, title, note = payload
                accent_color = TEXT
                condition = None
            else:
                x, by, w, h, title, note, accent_color, condition = payload
            if condition:
                out += text_lines(x + w, by + 16, [condition], 11, accent_color, weight='600', anchor='end')
            title_lines = wrap(title, max_chars_for(w, 16))
            out += text_lines(x, by + 20, title_lines, 16, TEXT, weight='600')
            note_lines = wrap(note, max_chars_for(w, 12.5))
            out += text_lines(x, by + 20 + len(title_lines) * 20 + 4, note_lines, 12.5, MUTED)
        elif kind == 'or_sep':
            cx, cyy = payload
            out.append(f'<line x1="{pad+20:g}" y1="{cyy:g}" x2="{cx-24:g}" y2="{cyy:g}" stroke="{BORDER}" stroke-width="1"/>')
            out.append(f'<line x1="{cx+24:g}" y1="{cyy:g}" x2="{pad+card_w-20:g}" y2="{cyy:g}" stroke="{BORDER}" stroke-width="1"/>')
            out += text_lines(cx, cyy + 4, ['or'], 12, MUTED, anchor='middle', weight='600')
        elif kind == 'sep':
            cx, cyy = payload
            out.append(f'<line x1="{pad+20:g}" y1="{cyy:g}" x2="{pad+card_w-20:g}" y2="{cyy:g}" stroke="{BORDER}" stroke-width="1"/>')
        elif kind == 'loop_label':
            lx, ly, label = payload
            out += text_lines(lx, ly, [label], 11, CYAN, anchor='start', weight='600')
        elif kind == 'edge':
            path_d, color, marker_id, dash = payload
            out.append(edge(path_d, color, marker_id, width=2.5, dash=dash))
        elif kind == 'text':
            x, ty, lines, size, color, weight, anchor = payload
            out += text_lines(x, ty, lines, size, color, weight=weight, anchor=anchor)
        elif kind == 'skills_panel':
            x, by, w, h, sp_ = payload
            out.append(rect(x, by, w, h, PANEL_ALT, BORDER, 2))
            content, _ = skills_panel_content(x, by, w, sp_)
            out += content

    out.append('</svg>\n')
    return '\n'.join(out)


OUTPUTS = {
    'desktop': (render_desktop, ROOT / 'diagrams/banner-desktop.svg'),
    'mobile': (render_mobile, ROOT / 'diagrams/banner-mobile.svg'),
}


def generate(check: bool = False) -> int:
    data = load_banner()
    stale = []
    for name, (renderer, target) in OUTPUTS.items():
        output = renderer(data)
        if check:
            if not target.exists() or target.read_text(encoding='utf-8') != output:
                stale.append(name)
        else:
            target.write_text(output, encoding='utf-8')
    if check:
        if stale:
            import sys
            print(f'banner diagram(s) stale: {", ".join(stale)}', file=sys.stderr)
            return 1
        print('Banner diagrams match source')
        return 0
    print('Generated diagrams/banner-desktop.svg and diagrams/banner-mobile.svg')
    return 0
