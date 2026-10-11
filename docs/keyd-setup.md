# keyd — setup live (2026-10-11)

- Sorgente: COPR `fmonteghetti/keyd` (Fedora non lo pacchettizza),
  versione `2.3.1-rc`.
- Config attiva: `/etc/keyd/keyd.conf` generata dal nostro renderer,
  base vuota (`RemapProfile(name='empty')`). Il remap `test1`
  (`capslock = esc`) e' stato verificato funzionante il 2026-10-11 e poi
  rimosso su richiesta: niente remap attivi adesso.
  Bug trovato e fixato: keyd non legge `conf.d`, i test scrivono
  `keyd.conf` con backup/ripristino.
- Procedura per ogni cambio: `tools/keyd_guarded_test.sh` con revert
  automatico a `tools/keyd_rollback.sh` (snapshot in
  `docs/fallback-keyd.md`).
