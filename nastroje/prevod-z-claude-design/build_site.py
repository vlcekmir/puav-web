"""Build a static PUAV website from the pages rendered out of the Claude Design bundle.

Inputs:  extract/ (assets unpacked from the bundle), build/ (rendered page parts)
Output:  site/ (deployable static website)
Texts are taken verbatim from the rendered pages.
"""
import base64
import hashlib
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = sys.argv[1]  # scratchpad dir
EX = os.path.join(ROOT, 'extract')
BU = os.path.join(ROOT, 'build')
OUT = os.path.join(ROOT, 'site')
BASE_URL = 'https://puav.cz/'

PAGES = [
    # key, slug, original file name in the bundle, title, description
    ('platforma', '', 'PUAV%20Platforma.dc.html',
     'PUAV – Platforma udržitelné audiovize',
     'PUAV: Platforma udržitelné audiovize. Know-how, Principy udržitelného natáčení a praktické nástroje pro českou audiovizi.'),
    ('praxe', 'jak-natacet-udrzitelne/', 'PUAV%20Praxe.dc.html',
     'Jak natáčet udržitelně - Návod krok za krokem | PUAV',
     'Kompletní Principy udržitelného natáčení, návod krok za krokem a praktické návody pro konkrétní situace na place.'),
    ('kontext', 'proc-natacet-udrzitelne/', 'PUAV%20Kontext.dc.html',
     'Proč natáčet udržitelně | PUAV',
     'Data o dopadu audiovizuální výroby, odpovědi na nejčastější námitky z praxe a to, co s tématem umí udělat samotný obsah.'),
    ('drevo', 'druhy-zivot-filmoveho-dreva/', 'PUAV%20N%C3%A1vod%20D%C5%99evo.dc.html',
     'Druhý život filmového dřeva - návod na recyklaci kulis | PUAV',
     'Když kulisy dosslouží, jejich příběh nemusí skončit na skládce. Návod od kontroly materiálu po potvrzení využitelné v závěrečné zprávě.'),
    ('pripojky', 'kratkodobe-pripojeni-k-siti/', 'PUAV%20N%C3%A1vod%20P%C5%99%C3%ADpojky.dc.html',
     'Krátkodobé připojení k elektrické síti - návod pro filmaře | PUAV',
     'Průvodce pro filmaře: jak se na lokaci připojit do sítě místo agregátu. Postup, ceny a lhůty u PRE, ČEZ i EG.D.'),
    ('storytelling', 'storytelling/', 'PUAV%20Klimatick%C3%BD%20Storytelling.dc.html',
     'Storytelling – klimatické vyprávění | PUAV',
     'Klimatické vyprávění je tvůrčí optika, která napříč žánry pomáhá přirozeně zachytit měnící se svět. Tipy, data a příležitosti pro tvůrce.'),
    ('oplatforme', 'o-platforme/', 'PUAV%20O%20Platform%C4%9B.dc.html',
     'O Platformě | PUAV',
     'PUAV je otevřená oborová platforma propojující producenty, režiséry, vysílatele, profesní asociace, filmové školy a odborníky na udržitelnost.'),
]
FILE2SLUG = {p[2]: p[1] for p in PAGES}

# PDFs: href in the page -> (bundle asset, download file name used by the original site)
PDFS = {
    'principy-udrzitelneho-nataceni-cz.pdf': (None, 'Principy udrzitelneho nataceni CZ.pdf'),
    'climate-spring-climate-stories.pdf': ('a2c3a1b6-cc6d-4292-a4b0-c006ade504f1', 'The Climate Stories We Need - Climate Spring.pdf'),
    'pribehy-zmeny.pdf': ('7ff3064b-7baa-4283-a1ff-81a4704c99e2', 'Pribehy zmeny - Pruvodce klimatickym vypravenim.pdf'),
    'ecoprod-screenwriting-guide.pdf': ('d99714e2-674a-46fd-bad2-4cf4f52bfa69', 'Ecoprod - Sustainability guide for screenwriting professionals.pdf'),
    'green-storytelling-checklist.pdf': ('6602c619-7508-4c9d-935f-ffd4ed004b80', 'Green Storytelling Checklist.pdf'),
    'memorandum-cz.pdf': ('b8ecab71-b3dc-4106-bc46-702218acd3c2', 'Memorandum o zalozeni Ceske platformy pro udrzitelnou audiovizi CZ.pdf'),
    'memorandum-en.pdf': ('8558b5a5-59c8-4771-beee-e635e12c27e8', 'Memorandum on the Establishment of the Czech Platform for Sustainable Audiovisual Production EN.pdf'),
}

# images: bundle asset -> (output name, resize rule)  rule: ('w', px) | ('h', px) | None
IMAGES = {
    'cf1d6af4-67b2-45f1-bbde-2e37902084c0': ('puav-logo.png', ('w', 360)),
    '49909086-1099-46a8-8999-a80df51e647b': ('puav-logo-paticka.png', ('w', 300)),
    '54e23a8f-f4c7-4ee6-a481-97b63b068892': ('foto-stab-pri-nataceni.jpg', None),
    'a5528d8d-c844-4cb3-9242-dd22ebd8e15d': ('hero-jak-natacet.jpg', None),
    'f4593a45-e638-4aee-bad9-d375dda7bd6a': ('hero-proc-natacet.jpg', None),
    '1c001afb-c61e-43fd-abad-13b919bbcb9f': ('foto-filmove-drevo.jpg', None),
    '042e5034-9ece-467e-8665-50f994292cfd': ('hero-storytelling.jpg', None),
    '8592d3f4-2f77-45ef-868a-09ed4841c2ec': ('hero-o-platforme.jpg', None),
    'e6b1d986-6957-4c1c-ab0b-d1d5e6411cb0': ('mapa-uk.png', None),
    '070cd51a-836d-4328-8965-104e1597d2f3': ('mapa-francie.png', None),
    'e17ee9e8-4d96-4f37-ab70-275fcde52d48': ('mapa-cr.png', None),
    '09d7c97b-d411-404a-bf9f-b015726d2769': ('logo-planet-a-collective.png', ('w', 300)),
    '29748f5a-a7ed-4145-bb15-fc65de5725a9': ('nahled-pribehy-zmeny.jpg', ('w', 660)),
    'd02d7582-68e9-4944-8b80-0c6d62128276': ('nahled-climate-stories.jpg', ('w', 660)),
    'ef2db45e-5058-4306-b812-8f165ec41861': ('nahled-ecoprod-screenwriting.jpg', ('w', 660)),
    'fe17c5b1-b0b8-4c9c-82b2-05b5fb3f5887': ('nahled-green-storytelling-checklist.jpg', ('w', 660)),
    'c5daa84f-a840-43b0-b5ad-7cd2d05ccb33': ('foto-clenove-platformy.jpg', None),
    '3bc8085e-fc24-45bd-8172-5ce2e697eeb0': ('logo-apa.jpg', ('h', 162)),
    'e6dc930d-1f20-4124-8075-52f56c68a21b': ('logo-aras.jpg', ('h', 162)),
    '20c7477b-e92c-402e-bd06-edaaa8f64ba3': ('logo-ceska-televize.png', ('h', 150)),
    '1729797c-1a23-4149-bdf9-37a50c88589b': ('logo-famu.jpg', None),
    '7b2a2f8a-0d6a-4fc3-b8e6-6aacea974e02': ('logo-tv-nova.png', ('h', 90)),
    '690c4b3f-d795-412b-8ef7-e6c8b4976956': ('logo-ftv-prima.png', ('h', 114)),
    '5db94cf0-ba10-4405-a1d4-42b972e8374c': ('foto-podpis-memoranda.jpg', ('w', 1240)),
    '427762a4-b678-440c-b249-130763ee33f2': ('favicon-32.png', None),
    'a042070b-ab26-4f66-84a9-faed3876b088': ('apple-touch-icon.png', None),
}
# images that are visible on first screen: no lazy loading
IMG_SIZES = {}
EAGER = {'puav-logo.png', 'foto-stab-pri-nataceni.jpg', 'hero-jak-natacet.jpg', 'hero-proc-natacet.jpg',
         'foto-filmove-drevo.jpg', 'hero-storytelling.jpg', 'hero-o-platforme.jpg'}

# contrast fixes (WCAG 2.x AA, 4.5:1 for normal text) — colour shifts only, texts untouched
CONTRAST = [
    ('color: rgb(107, 81, 7)', 'color: rgb(87, 65, 5)'),      # #6b5107 -> #574105 on yellow (3.87 -> 5.02)
    ('color: rgb(150, 96, 10)', 'color: rgb(138, 90, 0)'),    # #96600a -> #8a5a00 on #edeced (4.48 -> 5.03)
]

HOVER_RENAME = {
    'scp0': 'hv-text-yellow', 'scp1': 'hv-bg-dark', 'scp2': 'hv-text-black', 'scp3': 'hv-social',
    'scp4': 'hv-chip', 'scp5': 'hv-yellow', 'scp6': 'fx-field', 'scp7': 'hv-invert', 'scp8': 'hv-bg-yellow',
}


def nbsp_cz(text):
    """Same rule as the original typography script: no line break after single-letter Czech prepositions."""
    letters = 'aikosuvzAIKOSUVZ'
    parts = text.split(' ')
    out = parts[0]
    for i in range(1, len(parts)):
        prev = parts[i - 1]
        out += (' ' if len(prev) == 1 and prev in letters else ' ') + parts[i]
    return out


def nbsp_html(html):
    pieces = re.split(r'(<[^>]+>)', html)
    return ''.join(p if p.startswith('<') else nbsp_cz(p) for p in pieces)


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def asset_file(uuid):
    for f in os.listdir(EX):
        if f.startswith(uuid):
            return os.path.join(EX, f)
    raise FileNotFoundError(uuid)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    report = []

    # ---------- images ----------
    for uuid, (name, rule) in IMAGES.items():
        src = asset_file(uuid)
        dst = ensure(os.path.join(OUT, 'assets', 'img', name))
        im = Image.open(src)
        if rule:
            w, h = im.size
            if rule[0] == 'w' and w > rule[1]:
                im = im.resize((rule[1], round(h * rule[1] / w)), Image.LANCZOS)
            elif rule[0] == 'h' and h > rule[1]:
                im = im.resize((round(w * rule[1] / h), rule[1]), Image.LANCZOS)
        if name.endswith('.jpg'):
            im.convert('RGB').save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
        else:
            im.save(dst, 'PNG', optimize=True)
        report.append((name, os.path.getsize(src), os.path.getsize(dst), im.size))
        IMG_SIZES[name] = im.size
    # full-size logo for structured data / search engines
    shutil.copy(asset_file('cf1d6af4-67b2-45f1-bbde-2e37902084c0'), os.path.join(OUT, 'assets', 'img', 'puav-logo-1200.png'))

    # ---------- PDFs ----------
    tpl = open(os.path.join(EX, 'template.html'), encoding='utf-8').read()
    m = re.search(r'data:application/pdf;base64,([A-Za-z0-9+/=]+)', tpl)
    for fname, (uuid, _) in PDFS.items():
        dst = ensure(os.path.join(OUT, 'ke-stazeni', fname))
        if uuid is None:
            open(dst, 'wb').write(base64.b64decode(m.group(1)))
        else:
            shutil.copy(asset_file(uuid), dst)

    # ---------- fonts ----------
    head = tpl[:tpl.find('<body')]
    font_css = []
    for comment, block in re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face \{.*?\})', head, re.S):
        style = re.search(r'font-style: (\w+)', block).group(1)
        uuid = re.search(r'url\("([0-9a-f-]{36})"\)', block).group(1)
        name = f'open-sans-{style}-{comment}.woff2'
        shutil.copy(asset_file(uuid), ensure(os.path.join(OUT, 'assets', 'fonts', name)))
        font_css.append(f'/* {comment} */\n' + block.replace(f'url("{uuid}")', f'url("../fonts/{name}")'))

    # ---------- CSS ----------
    css = json.load(open(os.path.join(BU, 'css.json')))
    hover = []
    for rule in css['hover']:
        for old, new in HOVER_RENAME.items():
            rule = re.sub(r'\.' + old + r'(?=:)', '.' + new, rule)
        hover.append(rule)
    resp = [f'  .r{i} {{ {r["body"]} }}' for i, r in enumerate(css['resp'])]
    site_css = '\n'.join([
        '/* PUAV – styly webu. Většina vzhledu je přímo v atributech style jednotlivých prvků. */',
        '',
        '/* ---------- Písmo Open Sans (uloženo lokálně, bez Google Fonts) ---------- */',
        '\n'.join(font_css),
        '',
        '/* ---------- Základ ---------- */',
        '*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }',
        "body { font-family: 'Open Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #ffffff; color: #111111; -webkit-font-smoothing: antialiased; }",
        'a { color: #111111; }',
        'a:hover { color: #8a5a00; }',
        'summary { list-style: none; cursor: pointer; }',
        'summary::-webkit-details-marker { display: none; }',
        'details[open] > summary .om-plus { transform: rotate(45deg); }',
        'details[open] > summary .om-label-more::after { content: "Sbalit článek"; }',
        'details[open] > summary .om-label-more { font-size: 0; }',
        'details[open] > summary .om-label-more::after { font-size: 16px; }',
        'ul, ol { list-style: none; }',
        'html { scroll-behavior: smooth; }',
        '@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }',
        '[id] { scroll-margin-top: 16px; }',
        '',
        '/* ---------- Odkaz „Přeskočit na hlavní obsah“ ---------- */',
        '.skip-link { position: absolute; left: -9999px; top: 0; background: #fbaa1a; color: #111111; padding: 10px 16px; font-weight: 700; z-index: 9999; }',
        '.skip-link:focus { left: 0; }',
        '',
        '/* ---------- Efekty při najetí myší / zaměření ---------- */',
        '\n'.join(hover),
        '',
        '/* ---------- Kontaktní formulář (dialog) ---------- */',
        '.contact-dialog { border: none; padding: 34px 32px; width: calc(100% - 40px); max-width: 540px; max-height: 90vh; overflow-y: auto; background: #ffffff; color: #111111; margin: auto; }',
        '.contact-dialog::backdrop { background: rgba(0, 0, 0, 0.6); }',
        '',
        '/* ---------- Mobilní zobrazení ---------- */',
        '@media (max-width: 640px) {',
        '\n'.join(resp),
        '}',
        '',
    ])
    open(ensure(os.path.join(OUT, 'assets', 'css', 'puav.css')), 'w', encoding='utf-8').write(site_css)

    # ---------- JS ----------
    shutil.copy(os.path.join(ROOT, 'scripts', 'puav.js'), ensure(os.path.join(OUT, 'assets', 'js', 'puav.js')))

    # ---------- pages ----------
    blob2file = json.load(open(os.path.join(BU, 'blob2file.json')))
    dialog_html = nbsp_html(open(os.path.join(ROOT, 'scripts', 'dialog.html'), encoding='utf-8').read())
    sitemap = []
    for key, slug, orig, title, desc in PAGES:
        d = json.load(open(os.path.join(BU, f'raw-{key}.json')))
        pre = '../' * slug.count('/')
        body_parts = [d['header'], '<main id="main-content">'] + d['sections'] + ['</main>', d['footer']]
        html = '\n'.join(body_parts)

        # images: blob -> file
        def img_src(m):
            f = blob2file[m.group(1)]
            name = IMAGES[f.split('.')[0]][0]
            return f'{pre}assets/img/{name}'
        html = re.sub(r'(blob:null/[0-9a-f-]{36})', lambda m: img_src(m), html)

        # intrinsic size (prevents layout shift) + lazy loading below the fold
        def lazy(m):
            tag = m.group(0)
            src = re.search(r'src="([^"]+)"', tag).group(1)
            w, h = IMG_SIZES[os.path.basename(src)]
            if 'width=' not in tag:
                tag = tag.replace('<img ', f'<img width="{w}" height="{h}" ', 1)
            if os.path.basename(src) in EAGER or 'loading=' in tag:
                return tag
            return tag.replace('<img ', '<img loading="lazy" decoding="async" ', 1)
        html = re.sub(r'<img [^>]*>', lazy, html)

        # links
        def link(m):
            href = m.group(1)
            path, _, frag = href.partition('#')
            if path in FILE2SLUG:
                target = FILE2SLUG[path]
                new = (pre + target) if (pre + target) else './'
                if target == slug and frag:
                    new = ''
                return f'href="{new}{"#" + frag if frag else ""}"'
            if path.startswith('ke-stazeni/'):
                fname = path.split('/', 1)[1]
                dl = PDFS[fname][1]
                return f'href="{pre}{path}" download="{dl}"'
            return m.group(0)
        html = re.sub(r'href="([^"]*)"', link, html)

        # active item in main navigation + nav labels
        navs = list(re.finditer(r'<nav ', html))
        if navs:
            html = html.replace('<nav ', '<nav aria-label="Hlavní navigace" ', 1)
            html = html.replace('<nav style="display: flex; gap: 22px;', '<nav aria-label="Obsah stránky" style="display: flex; gap: 22px;')
        hdr_end = html.find('</header>')
        hdr = html[:hdr_end]
        own = f'href="{(pre + slug) if (pre + slug) else "./"}"'
        nav_start = hdr.find('<nav ')
        idx = hdr.find(own, nav_start)
        if idx > 0:
            hdr = hdr[:idx] + 'aria-current="page" ' + hdr[idx:]
        html = hdr + html[hdr_end:]

        # hover classes
        for old, new in HOVER_RENAME.items():
            html = re.sub(r'\b' + old + r'\b', new, html)

        # contrast fixes
        for old, new in CONTRAST:
            html = html.replace(old, new)
        # "Foto" placeholders on grey: #6e6e6e -> #666666 (4.33 -> 4.87)
        html = html.replace('color: rgb(110, 110, 110); text-align: center; line-height: 1.4;">Foto',
                            'color: rgb(102, 102, 102); text-align: center; line-height: 1.4;">Foto')
        # greyed "(brzy)" cards: opacity 0.5 made the text unreadable (2.3:1); keep the muted look with compliant greys
        def dim_card(m):
            card = m.group(0).replace(' opacity: 0.5;', '')
            card = card.replace('color: rgb(92, 92, 92);', 'color: rgb(118, 118, 118);')
            card = card.replace('color: rgb(17, 17, 17);', 'color: rgb(110, 110, 110);')
            return card
        html = re.sub(r'<div style="[^"]*opacity: 0\.5;">.*?</div>', dim_card, html, flags=re.S)

        # gallery photo slots (photos were not part of the export)
        html = re.sub(r'<image-slot id="([^"]+)"[^>]*placeholder="([^"]*)"[^>]*></image-slot>',
                      r'<!-- FOTO \1: \2 -->', html)

        # contact buttons
        html = html.replace('<span class="sc-interp">Kopírovat e-mail</span>', '<span data-copy-label>Kopírovat e-mail</span>')
        html = re.sub(r'<button type="button"([^>]*)>Chci se přidat</button>',
                      r'<button type="button" data-contact="Členství v PUAV" aria-haspopup="dialog"\1>Chci se přidat</button>', html)
        html = re.sub(r'<button type="button"([^>]*)>Napsat nám</button>',
                      r'<button type="button" data-contact="Konzultace, přednáška nebo školení" aria-haspopup="dialog"\1>Napsat nám</button>', html)
        html = re.sub(r'<button type="button"([^>]*)>(<span data-copy-label>)', r'<button type="button" data-copy-mail\1>\2', html)
        # esej toggle a11y
        html = html.replace('<button type="button" id="btn-esej"', '<button type="button" id="btn-esej" aria-expanded="false" aria-controls="esej-obsah"')

        canonical = BASE_URL + slug
        sitemap.append(canonical)
        jsonld = ''
        if key == 'platforma':
            jsonld = ('<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "Organization",
                "name": "PUAV – Platforma udržitelné audiovize", "alternateName": "PUAV",
                "url": BASE_URL, "logo": BASE_URL + "assets/img/puav-logo-1200.png",
                "email": "vlcek@puav.cz",
                "description": "Oborová platforma, která propojuje producenty, režiséry, vysílatele, profesní asociace, filmové školy a odborníky na udržitelnost v české audiovizi.",
                "foundingDate": "2024-09", "areaServed": "CZ"}, ensure_ascii=False) + '</script>\n')
        page = f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="PUAV – Platforma udržitelné audiovize">
<meta property="og:locale" content="cs_CZ">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="{pre}assets/img/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="{pre}assets/img/apple-touch-icon.png">
<link rel="preload" href="{pre}assets/fonts/open-sans-normal-latin-ext.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{pre}assets/fonts/open-sans-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/css/puav.css">
<script src="{pre}assets/js/puav.js" defer></script>
{jsonld}</head>
<body>
<a href="#main-content" class="skip-link">Přeskočit na hlavní obsah</a>
<div style="{d['wrapStyle']}">
{html}
</div>
{dialog_html}
</body>
</html>
'''
        dst = ensure(os.path.join(OUT, slug, 'index.html'))
        open(dst, 'w', encoding='utf-8').write(page)

    # ---------- social preview image (generated from the homepage hero by ogimage.js) ----------
    og = os.path.join(ROOT, 'og-image.jpg')
    if os.path.exists(og):
        shutil.copy(og, os.path.join(OUT, 'assets', 'img', 'og-image.jpg'))

    # ---------- 404 page (root-absolute paths: it is served for any missing URL) ----------
    home = open(os.path.join(OUT, 'index.html'), encoding='utf-8').read()
    head404 = home[:home.find('</head>')]
    head404 = re.sub(r'<link rel="canonical"[^>]*>\n', '', head404)
    head404 = re.sub(r'<meta property="og:[^>]*>\n|<meta name="twitter[^>]*>\n', '', head404)
    head404 = re.sub(r'<script type="application/ld\+json">.*?</script>\n', '', head404, flags=re.S)
    head404 = head404.replace('<title>PUAV – Platforma udržitelné audiovize</title>', '<title>Stránka nenalezena | PUAV</title>')
    head404 = re.sub(r'<meta name="description"[^>]*>', '<meta name="robots" content="noindex">', head404)
    header = home[home.find('<header'):home.find('</header>') + 9].replace('aria-current="page" ', '')
    footer = home[home.find('<footer'):home.find('</footer>') + 9]

    def absolutize(s):
        s = s.replace('href="#kontakt"', 'href="/#kontakt"')
        s = re.sub(r'(href|src)="\./"', r'\1="/"', s)
        return re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]*)"', r'\1="/\2"', s)
    body404 = f'''<section style="background: #000000; color: #ffffff;">
  <div style="max-width: 1160px; margin: 0 auto; padding: 120px 32px;">
    <span style="display: block; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; color: #d9d9d9; margin-bottom: 26px;">Chyba 404</span>
    <h1 style="font-size: clamp(36px, 4.6vw, 60px); font-weight: 800; line-height: 1.08; letter-spacing: -0.025em;">Stránka nenalezena</h1>
    <div style="width: 64px; height: 6px; background: #fbaa1a; margin: 26px 0 24px;"></div>
    <p style="font-size: 18px; line-height: 1.65; color: #e6e6e6; max-width: 46ch;">{nbsp_cz("Tato stránka neexistuje nebo byla přesunuta.")}</p>
    <div style="margin-top: 34px;"><a href="/" style="font-size: 16px; font-weight: 700; text-decoration: none; color: #111111; background: #fbaa1a; padding: 14px 22px; display: inline-block;">{nbsp_cz("Zpět na úvodní stránku")}</a></div>
  </div>
</section>'''
    page404 = (absolutize(head404).replace('<script src="/assets/js/puav.js" defer></script>\n', '') + '</head>\n<body>\n'
               + '<div style="max-width: 100%; overflow-x: hidden;">\n' + absolutize(header)
               + '\n<main id="main-content">\n' + body404 + '\n</main>\n' + absolutize(footer) + '\n</div>\n</body>\n</html>\n')
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(page404)

    # ---------- sitemap, robots, misc ----------
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in sitemap) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')

    for name, a, b, size in report:
        print(f'{name:42s} {a/1024:8.0f} KB -> {b/1024:6.0f} KB  {size}')


if __name__ == '__main__':
    main()
