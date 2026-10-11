# keyd — setup live (2026-10-11)

- Sorgente: COPR `fmonteghetti/keyd` (Fedora non lo pacchettizza),
  versione `2.3.1-rc`.
- Config attiva: `/etc/keyd/keyd.conf` generata dal nostro renderer
  (`RemapProfile(name='empty')`): solo `[ids] 0416:a0f8` + `[main]`
  vuota. Test guidato via mouse: digitazione confermata OK.
- Procedura per ogni cambio: `tools/keyd_guarded_test.sh` con revert
  automatico a `tools/keyd_rollback.sh` (snapshot in
  `docs/fallback-keyd.md`).
