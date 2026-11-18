# Pokyny pro Claude (web PUAV)

- Web je statický, publikuje se složka `docs/` přes GitHub Pages (větev `main`). Každý push na `main` je do minuty na webu: commit a push dělej až po schválení uživatelem.
- **Texty na webu neměň**, pokud o to uživatel výslovně nepožádá. Při převzetí textu od uživatele ho použij doslova. Pravopisné připomínky jen navrhni.
- Typografie: za jednopísmennými předložkami a spojkami (a, i, k, o, s, u, v, z, velká i malá) patří `&nbsp;` místo mezery.
- Hlavička (včetně tlačítka mobilního menu), kontaktní sekce (`#kontakt`) a patička jsou zkopírované v každé ze 7 stránek, hlavička a patička i v `404.html`. Změnu proveď všude.
- **Aktuality** se upravují jen v `obsah/aktuality.json`, potom spusť `python3 nastroje/aktuality.py`. HTML mezi `<!-- AKTUALITY:START/END -->` needituj.
- Odkazy uvnitř webu jsou relativní (`../o-platforme/`), aby web fungoval i na zkušební adrese vlcekmir.github.io/puav-web/. Výjimka: `404.html` používá adresy od kořene (`/…`).
- Nové obrázky zmenši (nejvýš 2× zobrazená velikost, JPEG kvalita ~80) a dej jim `width`/`height` a u obrázků pod první obrazovkou `loading="lazy"`.
- Po úpravě ověř v prohlížeči (Playwright): snímek dotčené části na počítači (1366 px) i mobilu (390 px), žádné chyby v konzoli, test přístupnosti (axe-core, WCAG 2.2 AA) bez chyb.
- Komunikace s uživatelem česky.
