# drevo-linux

Controllo Linux con GUI per tastiere Drevo su controller Winbond
(`0416:a0f8` — Tyrfing V2 / Calibur V2 TE), a parita' funzionale di
Drevo Power Console per le funzioni device-local.

Stato: scaffold iniziale, nessun protocollo implementato.

## Scope

IN: layout, programmazione tasti/macro, RGB, game mode, profili locali +
salvataggio onboard. FUORI: cloud sync, firmware flashing (solo lettura
versione).

## Vincoli

Solo userspace + udev, un solo writer HID alla volta, scritture solo su
evento (il controller Winbond va in reset-loop con scritture frequenti).
Reverse solo black-box da DPC in VM; niente decompilazione.

## Layout

- `src/drevo_control/` — core lib HID + GUI (prossimo)
- `plan/` — piano di feature, mai committato (gitignored)
