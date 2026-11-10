#!/usr/bin/env python3
"""Fail when crates.io has a crate owned by lilith that this catalog neither lists nor deliberately leaves out.

Usage: python3 tools/check_crates.py [--report PATH]

Listed: every published crate in data/registry.json (written by `tools/build.py --refresh`).
Left out on purpose: the [unlisted] table in catalog.toml, one line per crate with the reason.
Exit 1 and, with --report, write a Markdown list of the crates to add to one place or the other.
Standard library only (Python 3.11+).
"""
import json
import os
import sys
import tomllib

from build import owned_crates

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = 'lilith'


def main():
    report = sys.argv[sys.argv.index('--report') + 1] if '--report' in sys.argv else None
    with open(os.path.join(ROOT, 'catalog.toml'), 'rb') as f:
        unlisted = tomllib.load(f).get('unlisted', {})
    with open(os.path.join(ROOT, 'data/registry.json')) as f:
        listed = {n for n, c in json.load(f)['crates'].items() if c.get('published')}
    owned = owned_crates(OWNER)
    new = sorted(n for n in owned if n not in listed and n not in unlisted)
    stale = sorted(n for n in unlisted if n not in owned)
    print(f'{len(owned)} crates owned by {OWNER} on crates.io; {len(listed)} listed; {len(unlisted)} left out on purpose')
    if stale:
        print('In [unlisted] but no longer owned by ' + OWNER + ': ' + ', '.join(stale))
    if not new:
        print('No new crates.')
        return 0
    lines = [f'crates.io has {len(new)} crate(s) owned by {OWNER} that the catalog does not list:', '']
    for n in new:
        c = owned[n]
        lines.append(f"- [{n}](https://crates.io/crates/{n}) {c.get('max_version')}: {(c.get('description') or '').strip()} "
                     f"(repository: {c.get('repository') or 'none'})")
    lines += ['', 'Add each one to a topic in the stats inventory (it then appears here on the next refresh), '
              'or to the [unlisted] table in catalog.toml with the reason it stays out.']
    text = '\n'.join(lines) + '\n'
    print(text)
    if report:
        with open(report, 'w') as f:
            f.write(text)
    return 1


if __name__ == '__main__':
    sys.exit(main())
