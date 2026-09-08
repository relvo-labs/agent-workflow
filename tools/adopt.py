"""Explicit full-checkout adoption, never a global provider installer."""
import argparse
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def content():
    command = ' '.join(shlex.quote(str(p)) for p in
                       (Path(sys.executable).absolute(), ROOT / 'tools/validate.py',
                        ROOT / 'examples/happy-path.json'))
    catalog = '\n'.join(f'- {p.parent.name}: `{p}`' for p in sorted((ROOT / 'skills').glob('*/SKILL.md')))
    return (f'# Local toolkit adoption\n\nToolkit root: `{ROOT}`\n\n'
            'Keep this entire checkout present. Explicitly give your agent this file and the\n'
            'selected skill path. No native auto-discovery or provider probe is claimed.\n'
            'This file contains local paths; do not publish it.\n\n' + catalog +
            '\n\nRun from any directory (POSIX shell; replace final path for your bundle):\n\n'
            f'```sh\n{command}\n```\n\n'
            'No global profile changes. Rerun adoption after relocating the checkout.\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--probe', action='store_true')
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        p.error('target must be an existing directory')
    folder = target / '.agent-workflow'
    dest = folder / 'ADOPTION.md'
    if folder.is_symlink() or dest.is_symlink():
        p.error('refusing a symlink adoption destination')
    text = content()
    if args.check:
        if not dest.is_file() or dest.read_text() != text:
            p.error('adoption binding does not match this checkout/interpreter')
    else:
        folder.mkdir(exist_ok=True)
        try:
            with dest.open('x', encoding='utf-8') as f:
                f.write(text)
        except FileExistsError:
            p.error('adoption already exists; use --check or consciously remove it')
        if dest.read_text(encoding='utf-8') != text:
            p.error('adoption readback mismatch')
    if args.probe:
        completed = subprocess.run([sys.executable, str(ROOT / 'tools/validate.py'),
                                    str(ROOT / 'examples/happy-path.json')], cwd=target,
                                   check=False)
        if completed.returncode:
            return completed.returncode
    print('ADOPTED: explicit full-checkout binding verified; no provider integration claimed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
