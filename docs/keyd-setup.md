# keyd — setup live

- Installazione **dai sorgenti**, senza package manager:
  `src/drevo_control/data/keyd_install_src.sh` (anche da Impostazioni).
  Richiede solo gcc/make/git. Sorgenti in `/usr/local/src/keyd`
  (quelli storici dell'installazione manuale stanno in
  `/root/.local/src/keyd`, il rollback copre entrambi).
- Stato 2026-10-11: keyd **v2.6.0** attivo da sorgenti,
  `/etc/keyd/keyd.conf` = profilo vuoto `bozza` (solo match `0416:a0f8`).
- Procedura per ogni cambio: `tools/keyd_guarded_test.sh` con ritorno
  automatico alla base; rimozione completa con `tools/keyd_rollback.sh`
  (snapshot in `docs/fallback-keyd.md`).
- Nota versioni: i test remap/macro/game-mode sono passati su 2.3.1-rc
  (COPR); la 2.6.0 accetta la stessa sintassi (`toggle()` presente dalla
  2.4). Riverifica con l'utente al primo remap reale su 2.6.0.
