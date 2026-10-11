# keyd — setup live (2026-10-11)

- Sorgente: COPR `fmonteghetti/keyd` (Fedora non lo pacchettizza),
  versione `2.3.1-rc`.
- Config attiva: `/etc/keyd/keyd.conf` generata dal nostro renderer,
  profilo `test4` (capslock=esc + game-mode su F12), verificato OK
  il 2026-10-11 via `profile apply`.
- Nota: keyd non supporta `reload` → il codice usa restart in fallback.
- Test hardware passati: macro F9, toggle game-mode, keymap enter=rosso,
  apply unificato luci+tasti con pausa daemon.
- Procedura per ogni cambio: `tools/keyd_guarded_test.sh` con revert
  automatico a `tools/keyd_rollback.sh` (snapshot in
  `docs/fallback-keyd.md`).
