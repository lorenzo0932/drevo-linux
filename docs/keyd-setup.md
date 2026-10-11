# keyd — setup live (2026-10-11)

- Sorgente: COPR `fmonteghetti/keyd` (Fedora non lo pacchettizza),
  versione `2.3.1-rc`.
- Config attiva: `/etc/keyd/keyd.conf` generata dal nostro renderer.
  Base confermata: `test1` (`capslock = esc`), test guidato via mouse OK
  (2026-10-11). Bug trovato e fixato: keyd non legge `conf.d`, i test
  scrivono `keyd.conf` con backup/ripristino.
- Procedura per ogni cambio: `tools/keyd_guarded_test.sh` con revert
  automatico a `tools/keyd_rollback.sh` (snapshot in
  `docs/fallback-keyd.md`).
