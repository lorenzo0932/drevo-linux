# Testing e sicurezza hardware

## Livelli

1. **Unit** (`tests/`): builder contro byte catturati, render keyd,
   roundtrip profili, GUI offscreen (pagine, tema, apply mockati).
2. **Hardware lighting**: una scrittura alla volta sotto `usbmon`, confronto
   byte-identico, daemon in pausa; default ripristinato dal daemon.
3. **Hardware tasti** (serve utente): `tools/keyd_guarded_test.sh` installa
   la config di test e chiede conferma via mouse con timeout; senza
   conferma torna alla base. Mai due cambi insieme.
4. **Rollback**: `tools/keyd_rollback.sh` idempotente (snapshot in
   `docs/fallback-keyd.md`).

## Regole hardware (controller Winbond fragile)

Mai polling HID, mai scritture concorrenti (lock single-writer), mai
catture senza mettere in pausa il daemon. Ogni pacchetto nuovo deve
prima esistere come cattura del nostro stesso traffico.
