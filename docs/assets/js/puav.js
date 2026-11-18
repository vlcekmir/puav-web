/* PUAV – interaktivní prvky webu (čistý JavaScript, bez knihoven).
   Web funguje i bez JavaScriptu; skript jen přidává:
   1) filtr Principů, 2) rozbalení odborného komentáře, 3) kontaktní formulář, 4) kopírování e-mailu. */
(function () {
  'use strict';

  var MAIL = 'vlcek@puav.cz';
  var NBSP = ' ';

  /* ---------- 1) Principy: „Jen 13 základních“ / „Všech 22 bodů“ ---------- */
  var bZ = document.getElementById('btn-filter-zakladni');
  var bV = document.getElementById('btn-filter-vse');

  function styleButton(btn, active) {
    btn.style.background = active ? '#111111' : '#ffffff';
    btn.style.color = active ? '#ffffff' : '#3f3f3f';
    btn.style.borderColor = active ? '#111111' : '#C0C0C0';
    btn.style.fontWeight = active ? '700' : '400';
  }

  function filterPrincipy(mode) {
    var items = document.querySelectorAll('.principy-item');
    for (var i = 0; i < items.length; i++) {
      var type = items[i].getAttribute('data-type');
      items[i].style.display = (mode === 'vse' || type === 'zakladni') ? '' : 'none';
    }
    styleButton(bZ, mode === 'zakladni');
    styleButton(bV, mode === 'vse');
  }

  if (bZ && bV) {
    bZ.addEventListener('click', function () { filterPrincipy('zakladni'); });
    bV.addEventListener('click', function () { filterPrincipy('vse'); });
  }

  /* ---------- 2) Odborný komentář ---------- */
  var esejBtn = document.getElementById('btn-esej');
  var esejBox = document.getElementById('esej-obsah');
  if (esejBtn && esejBox) {
    esejBtn.addEventListener('click', function () {
      var open = esejBox.style.display !== 'none';
      esejBox.style.display = open ? 'none' : 'block';
      esejBtn.setAttribute('aria-expanded', open ? 'false' : 'true');
      var lbl = document.getElementById('btn-esej-label');
      var plus = document.getElementById('btn-esej-plus');
      if (lbl) lbl.textContent = open ? 'Číst odborný komentář' : 'Skrýt komentář';
      if (plus) plus.style.transform = open ? 'none' : 'rotate(45deg)';
    });
  }

  /* ---------- 3) Kopírování e-mailu ---------- */
  var copyTimer = null;
  function copyMail() {
    if (navigator.clipboard) navigator.clipboard.writeText(MAIL).catch(function () {});
    setCopyLabel('Zkopírováno');
    clearTimeout(copyTimer);
    copyTimer = setTimeout(function () { setCopyLabel('Kopírovat e-mail'); }, 1800);
  }
  function setCopyLabel(text) {
    var labels = document.querySelectorAll('[data-copy-label]');
    for (var i = 0; i < labels.length; i++) labels[i].textContent = text;
  }
  var copyButtons = document.querySelectorAll('[data-copy-mail]');
  for (var c = 0; c < copyButtons.length; c++) copyButtons[c].addEventListener('click', copyMail);

  /* ---------- 4) Kontaktní formulář ---------- */
  // Formulář nic neodesílá na server: otevře e-mailového klienta s předvyplněnou zprávou.
  var dlg = document.getElementById('kontakt-dialog');
  var form = document.getElementById('kontakt-form');
  if (!dlg || !form) return;
  var stateForm = dlg.querySelector('[data-state="form"]');
  var stateSent = dlg.querySelector('[data-state="sent"]');

  function openDialog(topic) {
    if (typeof dlg.showModal !== 'function') {  // velmi staré prohlížeče
      window.location.href = 'mailto:' + MAIL;
      return;
    }
    form.elements.topic.value = topic;
    stateForm.hidden = false;
    stateSent.hidden = true;
    dlg.showModal();
  }

  var openers = document.querySelectorAll('[data-contact]');
  for (var o = 0; o < openers.length; o++) {
    openers[o].addEventListener('click', function () { openDialog(this.getAttribute('data-contact')); });
  }
  var closers = dlg.querySelectorAll('[data-close]');
  for (var k = 0; k < closers.length; k++) closers[k].addEventListener('click', function () { dlg.close(); });
  // klik na ztmavené pozadí zavře dialog
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    var body = [
      'Jméno: ' + f.name.value,
      'E-mail: ' + f.email.value,
      'Organizace: ' + (f.org.value || '—'),
      'Téma: ' + f.topic.value,
      '',
      f.msg.value
    ].join('\n');
    window.location.href = 'mailto:' + MAIL +
      '?subject=' + encodeURIComponent('PUAV — ' + f.topic.value) +
      '&body=' + encodeURIComponent(body);
    dlg.querySelector('[data-sent-text]').textContent =
      'Otevřeli jsme váš e-mailový klient s' + NBSP + 'předplněnou zprávou pro vlcek@puav.cz — stačí ji odeslat. Pokud se nic neotevřelo, napište nám prosím přímo.';
    stateForm.hidden = true;
    stateSent.hidden = false;
  });
})();
