"""Deterministic SVG generated only from diagrams/core.json."""
import argparse
from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.validate import ROOT, load


def render(data):
    nodes, edges = data['nodes'], data['edges']
    index = {n['id']: i for i, n in enumerate(nodes)}
    if len(index) != len(nodes) or any(a not in index or b not in index for a, b in edges):
        raise ValueError('diagram graph')
    height = len(nodes) * 110 + 30
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{height}" viewBox="0 0 760 {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Relvo workflow core</title>',
           '<desc id="desc">Authority through evidence review and bounded repair to delivery or blocked closure.</desc>',
           '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#52647a"/></marker></defs>',
           '<rect width="100%" height="100%" fill="#f7f9fc"/>']
    for a, b in edges:
        ai, bi = index[a], index[b]
        if bi > ai:
            d = f'M340,{20 + ai * 110 + 78} L340,{20 + bi * 110}'
        else:
            d = f'M630,{59 + ai * 110} L700,{59 + ai * 110} L700,{59 + bi * 110} L630,{59 + bi * 110}'
        out.append(f'<path data-edge="{escape(a)}:{escape(b)}" d="{d}" fill="none" stroke="#52647a" stroke-width="2" marker-end="url(#arrow)"/>')
    for i, n in enumerate(nodes):
        y = 20 + i * 110
        out.extend([f'<g id="{escape(n["id"])}">',
                    f'<rect x="50" y="{y}" width="580" height="78" rx="12" fill="white" stroke="#52647a"/>',
                    f'<text x="70" y="{y+29}" font-family="sans-serif" font-size="19" fill="#172a43">{i+1}. {escape(n["title"])}</text>',
                    f'<text x="70" y="{y+55}" font-family="sans-serif" font-size="14" fill="#354b66">{escape(n["note"])}</text>', '</g>'])
    return '\n'.join(out) + '\n</svg>\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--banner', action='store_true',
                    help='Generate the README banner desktop/mobile SVGs from diagrams/banner.json '
                         'instead of the core workflow diagram (see tools/banner_diagram.py).')
    args = p.parse_args()
    if args.banner:
        from tools.banner_diagram import generate as generate_banner
        return generate_banner(check=args.check)
    output = render(load(ROOT / 'diagrams/core.json'))
    target = ROOT / 'diagrams/core.svg'
    if args.check:
        if not target.exists() or target.read_text() != output:
            print('diagram is stale', file=sys.stderr)
            return 1
        print('Diagram matches source')
    else:
        target.write_text(output, encoding='utf-8')
        print('Generated diagrams/core.svg')
    return 0


if __name__ == '__main__':
    sys.exit(main())
