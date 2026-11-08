"""Builds zones/<zone>.json and zones/index.json from the LSB nodes.yaml files (the xi-visualizer pathing node export).

python tools/build_zones.py <LSB checkout> [git ref, default retail-pathing-nodes]
Each zone file: {"nodes": [[x, z, y, radius, source], ...], "ids": [...], "links": [[i, j], ...]} with source 0 = extracted
from retail roam data, 1 = generated on recorded ground, 2 = generated on navmesh-only ground; links are node indexes,
listed once.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'zones')
SOURCES = {'extracted': 0, 'recorded': 1, 'navmesh': 2}
LINE = re.compile(r'\s+(\d+):\s+\{at: \[([-\d.]+), ([-\d.]+), ([-\d.]+)\], radius: ([-\d.]+), source: (\w+), links: \[([\d, ]*)\]')


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), check=True, capture_output=True, text=True, encoding='utf-8').stdout


def parse(text):
    rows = []
    for line in text.splitlines():
        m = LINE.match(line)
        if m:
            links = [int(v) for v in m.group(7).split(',') if v.strip()]
            rows.append((int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), SOURCES[m.group(6)], links))
    rows.sort()
    index = {r[0]: i for i, r in enumerate(rows)}
    nodes = [[round(x, 2), round(z, 2), round(y, 2), round(r, 2), s] for _, x, y, z, r, s, _ in rows]
    pairs = set()
    for nid, *_, links in rows:
        a = index[nid]
        for l in links:
            b = index.get(l)
            if b is not None and a != b:
                pairs.add((min(a, b), max(a, b)))
    return {'nodes': nodes, 'ids': [r[0] for r in rows], 'links': sorted(pairs)}


def title(folder):
    return ' '.join(w if w in ('of', 'the', 'and', 'de') else w.capitalize() for w in folder.split('_'))


def main():
    repo = sys.argv[1]
    ref = sys.argv[2] if len(sys.argv) > 2 else 'retail-pathing-nodes'
    files = [f for f in git(repo, 'ls-tree', '-r', '--name-only', ref, 'data/zones').splitlines() if f.endswith('/nodes.yaml')]
    os.makedirs(OUT, exist_ok=True)
    zones = []
    for f in files:
        folder = f.split('/')[-2]
        data = parse(git(repo, 'show', '%s:%s' % (ref, f)))
        if not data['nodes']:
            continue
        with open(os.path.join(OUT, folder + '.json'), 'w', encoding='utf-8', newline='\n') as out:
            json.dump(data, out, separators=(',', ':'))
        counts = [sum(1 for n in data['nodes'] if n[4] == s) for s in range(3)]
        zones.append({'zone': folder, 'name': title(folder), 'nodes': counts, 'links': len(data['links'])})
    zones.sort(key=lambda z: z['name'])
    with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8', newline='\n') as out:
        json.dump(zones, out, separators=(',', ':'))
    print(len(zones), 'zones')


if __name__ == '__main__':
    main()
