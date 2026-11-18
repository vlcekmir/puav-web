# Převod z Claude Design (jednorázový)

Těmito skripty vznikl obsah složky `docs/` z offline exportu Claude Design (jeden 21MB HTML soubor).
Pro běžné úpravy webu je **nepotřebujete**. Hlavní verzí webu je teď složka `docs/`.

Postup, kdyby bylo potřeba převod zopakovat (vyžaduje Python 3 + Pillow, Node.js + Playwright):

1. `unbundle.py <export.html> extract/`: rozbalí obrázky, PDF, fonty a šablonu z exportu.
2. `extract_pages.js <export.html> build/`: vykreslí každou ze 7 stránek v prohlížeči a uloží jejich HTML.
3. `ogimage.js <url webu> og-image.jpg`: vytvoří náhledový obrázek pro sociální sítě.
4. `build_site.py <pracovní složka>`: složí stránky, zmenší obrázky, opraví kontrast a odkazy a vytvoří sitemap.
   Očekává podsložky `extract/`, `build/` a `scripts/` s `dialog.html` a `puav.js`.

Pozor: opakovaný převod přepíše všechny ruční úpravy provedené ve `docs/`.
