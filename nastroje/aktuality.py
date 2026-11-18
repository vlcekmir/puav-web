#!/usr/bin/env python3
"""Vygeneruje aktuality z obsah/aktuality.json do stránek webu.

- docs/index.html             sekce „Co je nového“: N nejnovějších (N = na_uvodni_strance)
- docs/o-platforme/index.html  sekce „Co se událo“: všechny aktuality

Aktuality se vkládají mezi značky <!-- AKTUALITY:START --> a <!-- AKTUALITY:END -->.
Obsah mezi nimi se při každém spuštění přepíše, proto ho needitujte ručně.

Spuštění (z kořene repozitáře, stačí Python 3 bez dalších balíčků):
    python3 nastroje/aktuality.py
"""
import html
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'obsah', 'aktuality.json')
IMG_DIR = os.path.join(ROOT, 'docs', 'assets', 'img')
PAGES = [
    # soubor, cesta k assets, kolik aktualit (None = všechny)
    ('docs/index.html', '', 'uvod'),
    ('docs/o-platforme/index.html', '../', 'archiv'),
]
START, END = '<!-- AKTUALITY:START -->', '<!-- AKTUALITY:END -->'
FALLBACK_IMAGE = {'soubor': 'puav-logo.png', 'popis': '', 'styl': 'logo', 'pozadi': 'rgb(255, 255, 255)'}


def nbsp(text):
    """Nezlomitelná mezera za jednopísmennými předložkami a spojkami (jako na zbytku webu)."""
    letters = 'aikosuvzAIKOSUVZ'
    parts = text.split(' ')
    out = parts[0]
    for i in range(1, len(parts)):
        prev = parts[i - 1]
        out += ('&nbsp;' if len(prev) == 1 and prev in letters else ' ') + parts[i]
    return out


def esc(text):
    return nbsp(html.escape(text, quote=False))


def image_size(path):
    """Rozměry PNG/JPEG/WebP bez externích knihoven."""
    with open(path, 'rb') as f:
        head = f.read(32)
        if head.startswith(b'\x89PNG'):
            return struct.unpack('>II', head[16:24])
        if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
            f.seek(0)
            data = f.read(64)
            if data[12:16] == b'VP8 ':
                w, h = struct.unpack('<HH', data[26:30])
                return w & 0x3FFF, h & 0x3FFF
            if data[12:16] == b'VP8L':
                b = data[21:25]
                return 1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
            if data[12:16] == b'VP8X':
                return 1 + int.from_bytes(data[24:27], 'little'), 1 + int.from_bytes(data[27:30], 'little')
        if head[:2] == b'\xff\xd8':
            f.seek(2)
            while True:
                marker, length = struct.unpack('>HH', f.read(4))
                if marker in (0xFFC0, 0xFFC1, 0xFFC2):
                    h, w = struct.unpack('>xHH', f.read(5))
                    return w, h
                f.seek(length - 2, 1)
    raise ValueError(f'Neznámý formát obrázku: {path}')


def thumb(o, pre):
    path = os.path.join(IMG_DIR, o['soubor'])
    if not os.path.exists(path):
        sys.exit(f'Chybí obrázek docs/assets/img/{o["soubor"]}')
    w, h = image_size(path)
    src = f'{pre}assets/img/{o["soubor"]}'
    alt = html.escape(o.get('popis', ''))
    img = f'<img src="{src}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{alt}" '
    style = o.get('styl', 'foto')
    if style == 'foto':
        return ('<div style="background: rgb(237, 236, 237); border-right: 1px solid rgb(222, 220, 218); position: relative; overflow: hidden; min-height: 72px;">'
                + img + f'style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: {o.get("pozice", "50% 50%")};"></div>')
    if style == 'logo':
        return (f'<div style="background: {o.get("pozadi", "rgb(255, 255, 255)")}; border-right: 1px solid rgb(222, 220, 218); display: flex; align-items: center; justify-content: center; padding: 8px; min-height: 72px;">'
                + img + 'style="width: 100%; max-width: 110px; height: auto; display: block;"></div>')
    if style == 'dokument':
        return ('<div style="background: rgb(237, 236, 237); border-right: 1px solid rgb(222, 220, 218); display: flex; align-items: center; justify-content: center; padding: 12px 14px; min-height: 72px;">'
                + img + 'style="width: 100%; max-width: 82px; height: auto; display: block; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.18);"></div>')
    sys.exit(f'Neznámý styl obrázku „{style}“ (povoleno: foto, logo, dokument)')


def article(a, pre):
    link = ''
    if a.get('odkaz'):
        url = a['odkaz']['url']
        if url.startswith('/'):  # odkaz v rámci webu, např. /jak-natacet-udrzitelne/#principy
            url = (pre + url[1:]) or './'
        ext = ' target="_blank" rel="noopener"' if url.startswith('http') else ''
        link = f' <a href="{html.escape(url)}"{ext} style="font-weight: 700;">{html.escape(a["odkaz"]["text"], quote=False)}</a>'
    return f'''        <article style="background: rgb(255, 255, 255); display: grid; grid-template-columns: 110px 1fr; gap: 0px; align-items: stretch;" class="r14">
          {thumb(a.get("obrazek") or FALLBACK_IMAGE, pre)}
          <div style="padding: 16px 18px;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;">
              <time datetime="{a["datum"]}" style="font-size: 14px; font-weight: 700; color: rgb(17, 17, 17);">{esc(a["datum_text"])}</time>
              <span style="font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; background: rgb(251, 170, 26); color: rgb(17, 17, 17); padding: 3px 8px;">{esc(a["stitek"])}</span>
            </div>
            <h3 style="font-size: 18px; font-weight: 700; line-height: 1.35; margin-bottom: 8px;">{esc(a["nadpis"])}</h3>
            <p style="font-size: 16px; line-height: 1.65; color: rgb(63, 63, 63);">{esc(a["text"])}{link}</p>
          </div>
        </article>'''


def main():
    data = json.load(open(DATA, encoding='utf-8'))
    items = sorted(data['aktuality'], key=lambda a: a['datum'], reverse=True)
    for a in items:
        for key in ('datum', 'datum_text', 'stitek', 'nadpis', 'text'):
            if not a.get(key):
                sys.exit(f'Aktualitě „{a.get("nadpis", "?")}“ chybí pole „{key}“')
    for rel, pre, kind in PAGES:
        path = os.path.join(ROOT, rel)
        s = open(path, encoding='utf-8').read()
        i, j = s.find(START), s.find(END)
        if i < 0 or j < 0:
            sys.exit(f'V {rel} chybí značky {START} / {END}')
        chosen = items[:data.get('na_uvodni_strance', 3)] if kind == 'uvod' else items
        block = START + '\n' + '\n'.join(article(a, pre) for a in chosen) + '\n        ' + END
        s = s[:i] + block + s[j + len(END):]
        open(path, 'w', encoding='utf-8').write(s)
        print(f'{rel}: {len(chosen)} aktualit')


if __name__ == '__main__':
    main()
