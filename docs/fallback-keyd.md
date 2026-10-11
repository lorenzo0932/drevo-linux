# Fallback pre-keyd — snapshot 2026-10-11

Stato attuale (da ripristinare in caso di problemi):

- `keyd`: pacchetto NON installato, servizio inesistente, `/etc/keyd`
  inesistente.
- `ambilight-keyboard.service` (user): active.
- Repo `drevo-linux`: tutto committato su `feature/drevo-linux-parity`
  (base `bc03afb`), worktree pulito.

## Rollback

Eseguire `tools/keyd_rollback.sh`: stop/disable keyd, rimozione pacchetto
e config, reload udev, restart daemon ambilight, verifica digitazione.

Il rollback NON tocca: repo, daemon ambilight, regola udev
`77-drevo-control.rules` (non ancora installata), profili app.
