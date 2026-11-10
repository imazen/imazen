#!/usr/bin/env python3
"""Build README.md, llms.txt and catalog.json for github.com/imazen/imazen.

Usage:
  python3 tools/build.py --refresh    fetch the inventory and registry facts, then build
  python3 tools/build.py              rebuild from the cached data/ files (offline)
  python3 tools/build.py --full       also write dist/llms-full.txt, every listed README inlined

Writes README.md and llms.txt (committed) and dist/catalog.json (machine-readable, not committed).

Sources, all public:
  - https://stats.lilith.now/data.json: the project inventory (topics, crates, adoption), cached as data/stats.json
    (not committed; 1.3 MB). Its revision is recorded in every output.
  - crates.io and the GitHub API: version, license, docs and default branch per entry, cached as data/registry.json (not committed).
    Set GITHUB_TOKEN for the GitHub calls (60 unauthenticated calls an hour is not enough).
  - catalog.toml: the hand-written half (topic notes, starting points, products, integration guidance).

Standard library only (Python 3.11+ for tomllib). Every number written comes from those files; nothing is estimated.
"""
import datetime
import json
import os
import sys
import time
import tomllib
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_URL = 'https://stats.lilith.now/data.json'
UA = 'imazen-catalog-build (+https://github.com/imazen/imazen)'


def fmt(n):
    return f'{round(n):,}'


def get(url, token=None, raw=False):
    headers = {'User-Agent': UA}
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = f'Bearer {token}'
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                body = r.read()
                return body.decode('utf-8', 'replace') if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == 2:
                raise
        except urllib.error.URLError:
            if attempt == 2:
                raise
        time.sleep(2 + attempt * 3)


def load_json(path):
    with open(os.path.join(ROOT, path)) as f:
        return json.load(f)


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(text)
    print(f'wrote {path} ({len(text.encode()):,} bytes)')


# ---------- the entry list ----------

def entries(d, cat):
    """Every entry the README and llms.txt list, in topic order. An entry is a crate when a crate of that name
    lives in its repository, else the repository itself. Entries the owner hid from README footers stay hidden."""
    proj = {p['repository']: p for p in d['projects']}
    crates = {}
    for p in d['projects']:
        for c in p.get('crates') or []:
            crates.setdefault((p['repository'], c['name']), c)
    adds = cat.get('add', [])
    replaced = {a['replaces'] for a in adds if a.get('replaces')}
    out = []
    for topic in d['guide']['topics']:
        seen = set()
        for it in topic['items']:
            label, repo = it['label'], it.get('repository')
            if label in seen or label in replaced or not repo or repo not in proj or proj[repo].get('readme') is False:
                continue
            seen.add(label)
            c = crates.get((repo, label))
            out.append({
                'topic': topic['label'], 'name': label, 'repository': repo, 'parent': it.get('parent'),
                'kind': 'crate' if c else 'repository',
                'crate_dir': c['id'].split(':')[1] if c else None,
                'description': (c or {}).get('description') or proj[repo].get('description') or '',
            })
        for a in adds:
            if a['topic'] == topic['label'] and a['name'] not in seen:
                seen.add(a['name'])
                out.append({'topic': a['topic'], 'name': a['name'], 'repository': a['repository'], 'parent': None,
                            'kind': 'crate', 'crate_dir': a.get('crate_dir'), 'description': ''})
    return out


def owned_crates(user='lilith'):
    """Every crate.io crate the user owns, by name."""
    uid = get(f'https://crates.io/api/v1/users/{user}')['user']['id']
    out, page = {}, 1
    while True:
        d = get(f'https://crates.io/api/v1/crates?user_id={uid}&per_page=100&page={page}&sort=alpha')
        for c in d['crates']:
            out[c['name']] = c
        if len(d['crates']) < 100:
            return out
        page += 1
        time.sleep(1)  # crates.io asks for at most one request a second


# ---------- registry facts ----------

def cargo_license(repo, branch, crate_dir, token):
    """The license field of an unpublished crate's Cargo.toml, following `license.workspace = true`."""
    base = f'https://raw.githubusercontent.com/{repo}/{branch}/'
    path = 'Cargo.toml' if crate_dir in (None, '.') else f'{crate_dir}/Cargo.toml'
    text = get(base + path, token, raw=True)
    if not text:
        return None
    try:
        pkg = tomllib.loads(text).get('package', {})
    except tomllib.TOMLDecodeError:
        return None
    lic = pkg.get('license')
    if isinstance(lic, dict) and lic.get('workspace'):
        # The workspace root is the nearest ancestor directory whose Cargo.toml has [workspace].
        parts = [] if crate_dir in (None, '.') else crate_dir.split('/')
        lic = None
        for n in range(len(parts), -1, -1):
            text = get(base + '/'.join(parts[:n] + ['Cargo.toml']), token, raw=True)
            try:
                ws = tomllib.loads(text or '').get('workspace')
            except tomllib.TOMLDecodeError:
                ws = None
            if ws is not None:
                lic = ws.get('package', {}).get('license')
                break
    return lic if isinstance(lic, str) else None


def refresh(cat):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        sys.exit('--refresh needs GITHUB_TOKEN (for example GITHUB_TOKEN=$(gh auth token))')
    d = get(STATS_URL)
    write('data/stats.json', json.dumps(d, indent=1, sort_keys=True) + '\n')
    ents = entries(d, cat)
    repos = sorted({e['repository'] for e in ents} | {p['repo'] for p in cat['product']}
                   | {b['repo'] for p in cat['product'] for b in p.get('bindings', [])})
    reg = {'fetched_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           'how': 'python3 tools/build.py --refresh: GET https://api.github.com/repos/<repo>, '
                  '.../releases/latest, .../readme[/<dir>], https://crates.io/api/v1/crates?user_id=<lilith> (published means '
                  'owned by lilith on crates.io), https://crates.io/api/v1/crates/<crate>, and raw Cargo.toml for unpublished crates',
           'repositories': {}, 'crates': {}}
    for repo in repos:
        r = get(f'https://api.github.com/repos/{repo}', token)
        if not r:
            print(f'  missing repository {repo}', file=sys.stderr)
            continue
        rel = get(f'https://api.github.com/repos/{repo}/releases/latest', token)
        reg['repositories'][repo] = {
            'default_branch': r['default_branch'], 'archived': r['archived'], 'private': r['private'],
            'stars': r['stargazers_count'], 'description': r['description'], 'homepage': r['homepage'] or None,
            'license': (r.get('license') or {}).get('spdx_id'),
            'latest_release': {'tag': rel['tag_name'], 'published_at': rel['published_at'][:10]} if rel else None,
        }
    owned = owned_crates()
    reg['owner'] = 'lilith'
    for e in ents:
        if e['kind'] != 'crate' or e['name'] in reg['crates']:
            continue
        if e['name'] in owned:
            time.sleep(1)  # crates.io asks for at most one request a second
            c = get(f"https://crates.io/api/v1/crates/{e['name']}")
            cr = c['crate']
            ver = next((v for v in c['versions'] if v['num'] == cr['max_version']), c['versions'][0])
            reg['crates'][e['name']] = {
                'published': True, 'version': cr['max_stable_version'] or cr['max_version'], 'max_version': cr['max_version'],
                'license': ver.get('license'), 'rust_version': ver.get('rust_version'), 'description': cr.get('description'),
                'downloads': cr['downloads'], 'recent_downloads': cr.get('recent_downloads'),
                'first_published': cr['created_at'][:10], 'updated': cr['updated_at'][:10],
                'repository': cr.get('repository'), 'documentation': cr.get('documentation') or f"https://docs.rs/{e['name']}",
            }
        else:
            branch = reg['repositories'].get(e['repository'], {}).get('default_branch', 'main')
            reg['crates'][e['name']] = {'published': False,
                                        'license': cargo_license(e['repository'], branch, e['crate_dir'], token)}
        print(f"  {e['name']}: {reg['crates'][e['name']]}")
    # The README each entry links to: the crate directory's if it has one, else the repository's.
    reg['readmes'] = {}
    targets = [(p['repo'], None) for p in cat['product']] + [(b['repo'], None) for p in cat['product'] for b in p.get('bindings', [])]
    targets += [(e['repository'], e['crate_dir']) for e in ents]
    for repo, crate_dir in targets:
        key = f"{repo}:{crate_dir or '.'}"
        if key in reg['readmes'] or repo not in reg['repositories']:
            continue
        # GitHub's readme endpoint finds README.md, README.markdown, readme.rst and the rest.
        found = None
        for sub in ([f'/{crate_dir}'] if crate_dir not in (None, '.') else []) + ['']:
            r = get(f'https://api.github.com/repos/{repo}/readme{sub}', token)
            if r and r.get('download_url') and (sub or r['path'].count('/') == 0):
                found = r['download_url']
                break
        reg['readmes'][key] = found
    write('data/registry.json', json.dumps(reg, indent=1, sort_keys=True) + '\n')


# ---------- shared helpers ----------

class Ctx:
    def __init__(self, d, reg, cat):
        self.d, self.reg, self.cat = d, reg, cat
        self.ents = [e for e in entries(d, cat)
                     if not reg['repositories'].get(e['repository'], {}).get('private', False)]
        for e in self.ents:
            if not e['description']:
                e['description'] = reg['crates'].get(e['name'], {}).get('description') or ''
        self.by_name = {}
        for e in self.ents:
            self.by_name.setdefault(e['name'], e)
        self.asof = d['generated_at'][:10]
        self.reg_asof = reg['fetched_at'][:10]

    def repo(self, name):
        return self.reg['repositories'].get(name, {})

    def crate(self, e):
        return self.reg['crates'].get(e['name'], {}) if e['kind'] == 'crate' else {}

    def gh(self, e):
        return f"https://github.com/{e['repository']}"

    def readme_raw(self, repo, crate_dir=None):
        """The README resolved at refresh time; the repository page when it has none."""
        return self.reg.get('readmes', {}).get(f"{repo}:{crate_dir or '.'}") or f'https://github.com/{repo}'

    def license(self, e):
        lic = self.crate(e).get('license') or self.repo(e['repository']).get('license')
        return 'custom (see the repository)' if lic in ('NOASSERTION', 'NONE', 'other') else lic

    def status(self, e):
        c = self.crate(e)
        if e['kind'] == 'crate':
            return f"crates.io {c['version']}" if c.get('published') else 'unreleased (source on GitHub)'
        rel = self.repo(e['repository']).get('latest_release')
        return f"release {rel['tag']} ({rel['published_at']})" if rel else 'source on GitHub'

    def topics(self, secondary):
        sec = set(self.cat.get('secondary_topics', []))
        order = []
        for e in self.ents:
            if e['topic'] not in order and (e['topic'] in sec) == secondary and e['topic'] != 'Products':
                order.append(e['topic'])
        return order

    def in_topic(self, t):
        return [e for e in self.ents if e['topic'] == t]


def spdx_key(lic):
    """One spelling per license expression for counting: `MIT/Apache-2.0` and `Apache-2.0 OR MIT` count as `MIT OR Apache-2.0`."""
    if not lic:
        return 'not declared'
    lic = lic.replace('/', ' OR ')
    if ' AND ' in lic or '(' in lic:
        return lic
    parts = [x.strip() for x in lic.split(' OR ')]
    order = {'MIT': 0, 'Apache-2.0': 1}
    return ' OR '.join(sorted(parts, key=lambda x: (order.get(x, 2), x)))


def desc(text):
    text = ' '.join((text or '').split()).rstrip('.')
    return text[:1].upper() + text[1:] if text else ''


# ---------- llms.txt ----------

def llms(x, full_readmes=None):
    o, cat, u = x.cat['org'], x.cat, x.d['usage']
    L = [f"# {o['name']}", '',
         f"> {o['name']} builds image codecs, image processing and image servers. The current work is an imaging stack "
         'in safe Rust: encoders and decoders for JPEG, WebP, AVIF/AV1, JPEG XL, PNG, GIF, HEIC and more, plus resizing, '
         'color, compositing, quality metrics and a streaming pipeline. Imageflow, Imageflow Server and ImageResizer are '
         'the products built on this work.', '',
         'How to use this file:', '',
         '- Each entry links to a Markdown README. Crates also list their crates.io version, license and docs.rs page; '
         'read the docs for the exact API of the version you install, and do not call an API from memory.',
         '- To serve images on request from a .NET stack, use Imageflow Server. To process images in batch or from Node, Go '
         'or .NET code, use Imageflow and its bindings. To encode or decode inside a Rust program, depend on the codec crate '
         'for each format (the "start with" entry of each topic below).',
         f"- Licensing: many codec and processing crates are `AGPL-3.0-only OR LicenseRef-Imazen-Commercial`. Under the AGPL, software that "
         f"uses them over a network must offer its source; otherwise buy a commercial license at {o['pricing']} "
         f"(a $1 key for open-source projects and for companies with fewer than 5 employees and under $1M revenue). "
         'Shared APIs, pixel types, SIMD and utility crates are permissive, and some ports keep their upstream license. Check each entry\'s license field.',
         '- Images from untrusted sources: the codecs take resource limits (dimensions, pixels, memory) and cooperative '
         'cancellation. Set them for any input you did not produce.',
         '- "Unreleased" entries have source on GitHub but no crates.io release; their APIs change without notice.',
         f"- Questions: {o['support']}. Licensing: {o['sales']}.", '']

    L += ['## Products', '']
    for p in cat['product']:
        r = x.repo(p['repo'])
        rel = r.get('latest_release')
        extra = f"; latest release {rel['tag']} ({rel['published_at']})" if rel else ''
        L.append(f"- [{p['name']}]({x.readme_raw(p['repo'])}): {p['what']} Use it when {p['use_when'][:1].lower() + p['use_when'][1:]} "
                 f"License: {p.get('license') or r.get('license') + ' or commercial'}{extra}. Source: https://github.com/{p['repo']}")
        for b in p.get('bindings', []):
            br = x.repo(b['repo'])
            L.append(f"- [{p['name']} for {b['name']}]({x.readme_raw(b['repo'])}): {desc(br.get('description'))}. "
                     f"License: {br.get('license')} or commercial. Source: https://github.com/{b['repo']}")
    L.append('')

    def entry_line(e):
        c = x.crate(e)
        bits = [x.status(e)]
        bits.append(f"license {x.license(e) or 'not declared'}")
        if c.get('published'):
            bits.append(f"docs {c['documentation']}")
        bits.append(f'source {x.gh(e)}')
        return f"- [{e['name']}]({x.readme_raw(e['repository'], e.get('crate_dir'))}): {desc(e['description'])}. {'; '.join(bits)}"

    for t in x.topics(False):
        note = cat['topic'].get(t, {})
        L += [f'## {t}', '']
        if note.get('note') or note.get('start'):
            L += [' '.join(filter(None, [note.get('note'), f"Start with {note['start']}." if note.get('start') else None])), '']
        L += [entry_line(e) for e in x.in_topic(t)] + ['']

    L += ['## Optional', '']
    for dm in cat.get('demo', []):
        L.append(f"- [{dm['name']}]({dm['url']}): {dm['text']}")
    L.append(f"- [Research dashboard]({o['research']}): the year's work, adoption and measurements, live.")
    for t in x.topics(True):
        for e in x.in_topic(t):
            L.append(entry_line(e) + f' ({t})')
    L += ['', f"Generated {x.asof} (inventory) and {x.reg_asof} (registries) by https://github.com/{o['repo']}.", '']
    text = '\n'.join(L)
    if full_readmes is not None:
        text += full_readmes
    return text


def full_section(x):
    """Every listed README, inlined, for dist/llms-full.txt."""
    out, seen = [], set()
    urls = [(p['name'], x.readme_raw(p['repo'])) for p in x.cat['product']]
    urls += [(e['name'], x.readme_raw(e['repository'], e.get('crate_dir'))) for e in x.ents]
    for name, url in urls:
        if url in seen:
            continue
        seen.add(url)
        body = get(url, raw=True)
        if body:
            out.append(f'\n\n---\n\n# README: {name}\n\nSource: {url}\n\n{body.strip()}\n')
        time.sleep(0.2)
    return ''.join(out)


# ---------- README.md ----------

def readme(x):
    o, cat, d = x.cat['org'], x.cat, x.d
    u, a = d['usage'], d['adoption']
    dep = u['dependents']['repositories']
    raw_llms = f"https://raw.githubusercontent.com/{o['repo']}/main/llms.txt"
    L = [f"# {o['name']}", '',
         f"{o['name']} builds image codecs, image processing and image servers. Our current work is an imaging stack in "
         'safe Rust: encoders and decoders for every major still-image format, the AV1 encoders behind AVIF, resizing, '
         'color management, compositing and perceptual quality metrics, and the pipeline and servers that put them to work.', '',
         f"[Website]({o['site']}) · [Pricing]({o['pricing']}) · [Research dashboard]({o['research']}) · "
         f"[llms.txt](llms.txt)", '']

    L += ['## Products', '', '| Product | What it is | Use it when |', '|:--|:--|:--|']
    for p in cat['product']:
        r = x.repo(p['repo'])
        rel = r.get('latest_release')
        name = f"[{p['name']}](https://github.com/{p['repo']})"
        if p.get('bindings'):
            name += '<br><sub>' + ' · '.join(f"[{b['name']}](https://github.com/{b['repo']})" for b in p['bindings']) + '</sub>'
        what = p['what'] + (f"<br><sub>Latest release {rel['tag']}, {rel['published_at']}</sub>" if rel else '')
        L.append(f"| {name} | {what} | {p['use_when']} |")
    L += ['']

    L += ['## Formats', '',
          'One row per format, with the crates that read and write it. ↔ encode and decode, ← decode only.', '',
          '| Format | | Crates | Status |', '|:--|:-:|:--|:--|']
    for g in d['directive']['codecs']:
        names = list(dict.fromkeys(g.get('encode', []) + g.get('decode', [])))
        public = [n for n in names if n in x.by_name]
        arrow = '↔' if g.get('encode') and g.get('decode') else '→' if g.get('encode') else '←'
        if g.get('href') and not public:
            cell, status = f"[demo]({g['href']})", 'format not frozen yet'
        elif not public:
            continue
        else:
            cell = ' · '.join(f"[{n}]({x.gh(x.by_name[n])})" for n in public)
            pub = [n for n in public if x.crate(x.by_name[n]).get('published')]
            status = 'on crates.io' if pub else 'unreleased'
            if g.get('source') == 'fork':
                status += '; wraps our fork of an existing library'
            elif g.get('source') == 'wrapper':
                status += '; built on existing libraries'
        L.append(f"| {g['label']} | {arrow} | {cell} | {status} |")
    L += ['']

    firsts = [f for f in cat.get('first', []) if f['entry'] in x.by_name]
    if firsts:
        L += ['## Firsts', '', 'As far as we know, these were the first of their kind:', '']
        L += [f"- {f['text'][:1].upper() + f['text'][1:]}: [{f['entry']}]({x.gh(x.by_name[f['entry']])})" for f in firsts]
        L += ['']

    L += ['## Choosing an integration', '',
          '- **On request, from URLs.** [Imageflow Server](https://github.com/imazen/imageflow-server) resizes, crops and '
          're-encodes images as they are requested, and caches the results.',
          '- **Ahead of time.** `imageflow_tool` (in [Imageflow](https://github.com/imazen/imageflow)) and the '
          '[.NET](https://github.com/imazen/imageflow-dotnet), [Node](https://github.com/imazen/imageflow-node) and '
          '[Go](https://github.com/imazen/imageflow-go) bindings process images in build steps and batch jobs.',
          '- **Inside a Rust program.** Depend on the codec crate for each format, or on the processing crates directly. '
          'Every topic in the project list below names the crate to start with.',
          f'- **With a coding agent.** Give it [{raw_llms}]({raw_llms}). It lists every entry with its version, license, '
          'docs and README, plus the rules above for picking one.', '']

    lic = {}
    for name, c in sorted(x.reg['crates'].items()):
        if c.get('published') and name in x.by_name:
            lic.setdefault(spdx_key(c.get('license')), []).append(name)
    L += ['## Licensing', '',
          f"Codec and processing crates are mostly dual-licensed, `AGPL-3.0-only OR LicenseRef-Imazen-Commercial`: use them "
          f"under the AGPL, or buy a commercial license at [imazen.io/pricing]({o['pricing']}). Open-source projects, and "
          f"companies with fewer than 5 employees and under $1M revenue, can get a key for $1. Shared APIs, pixel types, SIMD "
          f"and utility crates are permissive, and some ports keep their upstream's license. Questions: {o['sales']}.", '',
          f"Published crates by license, from crates.io on {x.reg_asof}:", '',
          '| License | Crates |', '|:--|:--|']
    L += [f"| `{k}` | {', '.join(v)} |" for k, v in sorted(lic.items(), key=lambda kv: -len(kv[1]))] + ['']

    L += ['## How it is built', '',
          'Codecs take bytes from strangers, usually on servers that hold other people\'s data, so a decoder bug is a security bug. '
          'Our crates compile with `#![forbid(unsafe_code)]`; SIMD goes through [archmage](https://imazen.github.io/archmage/), '
          'which wraps the intrinsics once. A few older crates still carry unsafe code, and we treat it as debt. '
          'Decoders and encoders take resource limits and cooperative cancellation ([enough](https://crates.io/crates/enough)), '
          'are fuzzed continually, and are tested bit for bit against C references where those exist; where pixels may '
          'differ, perceptual metrics ([zensim](https://github.com/imazen/zensim)) decide whether a person would see it. '
          f"Details, with live figures: [the research dashboard]({o['research']}).", '']

    L += ['## Who depends on it', '',
          f"- {fmt(u['package_downloads_total'])} downloads across crates.io and NuGet "
          f"({fmt(u['crates_downloads_total'])} on crates.io, {fmt(a['nuget']['downloads_total'])} on NuGet).",
          f"- At least {fmt(dep['at_least'])} GitHub repositories depend on "
          f"[{dep['largest']['package']}](https://github.com/{dep['largest']['repository']}/network/dependents).",
          f"- {fmt(u['reverse_dependencies_summed'])} crates.io reverse dependencies across our crates.",
          '', f"<sub>As reported by each registry, captured {u['dependents']['captured']}.</sub>", '']

    def cell(e):
        c = x.crate(e)
        tag = f" <sub>{c['version']}</sub>" if c.get('published') else (' <sub>unreleased</sub>' if e['kind'] == 'crate' else '')
        return f"[{e['name']}]({x.gh(e)}){tag}"

    def table(topics):
        rows = ['| Topic | Projects |', '|:--|:--|']
        for t in topics:
            note = cat['topic'].get(t, {})
            sub = note.get('note', '')
            if note.get('start'):
                sub += f" Start with **{note['start']}**."
            ents = [e for e in x.in_topic(t) if not e['parent']]
            if t == 'Earlier work':
                ents = sorted(ents, key=lambda e: -(x.repo(e['repository']).get('stars') or 0))
            rows.append(f"| **{t}**<br><sub>{sub.strip()}</sub> | {' · '.join(cell(e) for e in ents)} |")
        return rows

    L += ['## Projects', '', 'Version numbers are the latest on crates.io; "unreleased" crates have source but no release yet.', '']
    L += table(x.topics(False)) + ['', '### Also', ''] + table(x.topics(True)) + ['']

    L += ['## Demos', ''] + [f"- [{dm['name']}]({dm['url']}): {dm['text']}" for dm in cat.get('demo', [])] + ['']

    L += ['## Limitations', '',
          '- Most crates are below 1.0 and their APIs still change between minor versions. Pin versions.',
          '- Unreleased crates are listed so you can see where the work is going; do not build products on them yet.',
          '- IMI, our own format, is not frozen; files written today may not decode with a later version.',
          f"- Figures here are snapshots: the inventory from {x.asof}, registry facts from {x.reg_asof}.", '']

    L += ['## About this repository', '',
          '`python3 tools/build.py --refresh` regenerates README.md and llms.txt from the public inventory behind '
          f"the research dashboard ({STATS_URL}), crates.io and GitHub, plus the hand-written [catalog.toml](catalog.toml). "
          'Standard library only. A weekly workflow refreshes both files and fails when crates.io lists a crate we own that '
          'the catalog neither lists nor leaves out on purpose. Corrections are welcome as issues or pull requests against catalog.toml.', '',
          f"*Generated from inventory revision {d['revision'][:12]} ({x.asof}) and registry facts fetched {x.reg_asof}.*", '']
    return '\n'.join(L)


# ---------- catalog.json ----------

def catalog_json(x):
    out = {'generated': {'inventory': x.asof, 'inventory_revision': x.d['revision'], 'registries': x.reg['fetched_at']},
           'org': x.cat['org'], 'products': [], 'entries': []}
    for p in x.cat['product']:
        out['products'].append({**p, **{k: x.repo(p['repo']).get(k) for k in ('license', 'latest_release', 'stars')}})
    for e in x.ents:
        c = x.crate(e)
        out['entries'].append({
            'name': e['name'], 'topic': e['topic'], 'kind': e['kind'], 'repository': f"https://github.com/{e['repository']}",
            'readme': x.readme_raw(e['repository'], e.get('crate_dir')), 'description': desc(e['description']),
            'license': x.license(e), 'published': c.get('published', False) if e['kind'] == 'crate' else None,
            'version': c.get('version'), 'documentation': c.get('documentation'), 'rust_version': c.get('rust_version'),
            'parent': e['parent'],
        })
    return json.dumps(out, indent=1) + '\n'


def main():
    args = sys.argv[1:]
    with open(os.path.join(ROOT, 'catalog.toml'), 'rb') as f:
        cat = tomllib.load(f)
    if '--refresh' in args:
        refresh(cat)
    elif not os.path.exists(os.path.join(ROOT, 'data/stats.json')):
        write('data/stats.json', json.dumps(get(STATS_URL), indent=1, sort_keys=True) + '\n')
    x = Ctx(load_json('data/stats.json'), load_json('data/registry.json'), cat)
    write('README.md', readme(x))
    write('llms.txt', llms(x))
    write('dist/catalog.json', catalog_json(x))
    if '--full' in args:
        write('dist/llms-full.txt', llms(x, full_section(x)))


if __name__ == '__main__':
    main()
