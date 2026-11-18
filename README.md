# PUAV – web Platformy udržitelné audiovize

Statický web pro **puav.cz**. Web nemá databázi, administraci ani serverový kód: tvoří ho jen HTML, CSS, obrázky a PDF.

## Co kde je

```
docs/                               ← samotný web (to se publikuje)
  index.html                        Domů
  jak-natacet-udrzitelne/           Jak natáčet udržitelně
  proc-natacet-udrzitelne/          Proč natáčet udržitelně
  druhy-zivot-filmoveho-dreva/      Návod: Druhý život filmového dřeva
  kratkodobe-pripojeni-k-siti/      Návod: Krátkodobé připojení k elektrické síti
  storytelling/                     Storytelling
  o-platforme/                      O Platformě
  404.html                          stránka „nenalezeno“
  ke-stazeni/                       PDF ke stažení
  assets/img/                       obrázky a loga
  assets/css/puav.css               písmo, efekty po najetí myší, mobilní úpravy
  assets/js/puav.js                 filtr Principů, rozbalovací komentář, kontaktní formulář
  sitemap.xml, robots.txt           pro vyhledávače
nastroje/prevod-z-claude-design/    jednorázové skripty, kterými se web převedl z exportu Claude Design
```

Vzhled je většinou zapsaný přímo u prvků (atribut `style`), tak jak vznikl v Claude Design.
Hlavička, patička a kontaktní sekce jsou na každé stránce zvlášť. Při jejich změně je potřeba upravit všech 7 stránek a `404.html`.

## Jak web upravovat

Obsah se upravuje přímo v souborech ve složce `docs/`. Jsou dvě cesty:

1. **S Claude:** otevřete [claude.ai/code](https://claude.ai/code) s tímto repozitářem a popište změnu.
   Claude upraví soubory, ukáže náhled a po vašem schválení změnu uloží (commit + push).
   Do minuty je změna na webu.
2. **Ručně na GitHubu:** otevřete soubor, klikněte na ikonu tužky, upravte a uložte (Commit changes).

Každá změna se ukládá jako verze. Cokoli jde vrátit zpět.

**Pravidla, aby web zůstal v pořádku:**
- Nové obrázky zmenšete na nejvýš dvojnásobek velikosti, ve které se zobrazují (fotky do ~300 kB, JPEG).
- Nové PDF patří do `docs/ke-stazeni/` a odkazuje se na ně běžným odkazem.
- Nová stránka = nová složka s `index.html`, odkaz v navigaci všech stránek a záznam v `sitemap.xml`.

## Nasazení

Web běží na **GitHub Pages** (zdarma, HTTPS automaticky). Nastavení repozitáře: *Settings → Pages → Deploy from a branch → `main` / `docs`*.

### Pro správce domény puav.cz

Aby doména puav.cz ukazovala na web, je potřeba v DNS:

1. **Zrušit současné přesměrování** puav.cz → greenfilming.cz.
2. Pro **puav.cz** nastavit záznamy:

   | Typ  | Hodnota |
   |------|---------|
   | A    | 185.199.108.153 |
   | A    | 185.199.109.153 |
   | A    | 185.199.110.153 |
   | A    | 185.199.111.153 |
   | AAAA | 2606:50c0:8000::153 |
   | AAAA | 2606:50c0:8001::153 |
   | AAAA | 2606:50c0:8002::153 |
   | AAAA | 2606:50c0:8003::153 |

3. Pro **www.puav.cz** nastavit `CNAME` na `vlcekmir.github.io`.
4. **MX a další záznamy pro e-mail (@puav.cz) nechat beze změny.** Mění se jen A/AAAA a www.
5. Doporučeno: ověřit doménu v nastavení GitHub účtu (*Settings → Pages → Add a domain*). GitHub k tomu vygeneruje jeden TXT záznam.
   Ověření chrání doménu proti zneužití.

Pak se v *Settings → Pages* zadá vlastní doména `puav.cz` a zapne *Enforce HTTPS*. Certifikát vydá GitHub automaticky.
Dokumentace: [Managing a custom domain for your GitHub Pages site](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

**greenfilming.cz** (spravuje TV Nova): ideálně trvalé přesměrování (HTTP 301) na `https://puav.cz/`.

## Otevřené body v obsahu

- Galerie „Takhle to vypadá na place“ (Domů) je dočasně skrytá (atribut `hidden` u `<section id="galerie">`). Šest míst pro fotky je v kódu označeno komentářem `<!-- FOTO … -->`.
- Odkaz „Vyplnit Závěrečnou zprávu ↗“ (Jak natáčet udržitelně) vede na `ODKAZ-NA-GOOGLE-FORM`. Chybí adresa Google formuláře.
- Kontaktní formulář otevírá e-mailového klienta (mailto). Odesílání bez e-mailového klienta by vyžadovalo formulářovou službu.
