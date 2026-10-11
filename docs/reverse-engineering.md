# Reverse engineering: metodo e confini

Metodo consentito qui: **solo black-box sul proprio hardware**.

- `usbmon` sul traffico del nostro stesso software (daemon, helper);
- descrittori USB/HID pubblici e standard HID per i key-id;
- reimplementazione originale dei formati osservati.

Vietato: decompilare/disassemblare DPC o `dtv2`, copiare loro codice,
asset, firmware o installer, redistribuire firmware/binari Drevo.
Le costanti di protocollo osservate sono fatti interoperativi; il codice
che le usa e' originale (licenza repo: GPL-3.0-or-later). In caso di
dubbio legale, fermarsi e chiedere.
