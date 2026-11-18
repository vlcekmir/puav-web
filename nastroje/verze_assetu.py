#!/usr/bin/env python3
"""Doplní do odkazů na puav.css a puav.js otisk obsahu (?v=…).

Prohlížeče i GitHub Pages si styly a skripty pamatují (až 10 minut i déle). Když se změní,
nový otisk v adrese zajistí, že návštěvník dostane novou verzi společně s novou stránkou.
Spusťte po každé změně souborů v docs/assets/css nebo docs/assets/js:
    python3 nastroje/verze_assetu.py
"""
import glob
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = ['assets/css/puav.css', 'assets/js/puav.js']

versions = {}
for a in ASSETS:
    data = open(os.path.join(ROOT, 'docs', a), 'rb').read()
    versions[a] = hashlib.sha256(data).hexdigest()[:8]

pages = glob.glob(os.path.join(ROOT, 'docs', '**', '*.html'), recursive=True)
for path in pages:
    s = open(path, encoding='utf-8').read()
    new = s
    for a, v in versions.items():
        new = re.sub(r'((?:\.\./|/)?' + re.escape(a) + r')(\?v=[0-9a-f]+)?"', r'\1?v=' + v + '"', new)
    if new != s:
        open(path, 'w', encoding='utf-8').write(new)
        print('aktualizováno:', os.path.relpath(path, ROOT))
print('verze:', versions)
