# Protocollo HID 0416:a0f8

Device: Winbond, iface 1 (EP OUT `0x03`, 64B), non legata al kernel.
Tutto write-only via SET_REPORT/feature OUT; GET_REPORT non supportato
(verificato: `tools/hid_survey.py`).

Derivazione: catture `usbmon` del nostro stesso traffico + confronto
byte a byte in `tests/test_commands.py`. Dettaglio completo con tabelle
in [protocol-lighting](protocol-lighting.md) (documento di lavoro delle
catture).

## Effetti (prefisso `06 be 15 00 01 01 CMD`, 32B)

| CMD | Effetto | byte7 | byte9 |
|---|---|---|---|
| `01` | STATIC | speed 0–9 | direction |
| `02` | BREATH | speed 0–9 | 0 |
| `03` | STREAM | speed 0–9 | e=0 w=1 s=2 n=3 |
| `10` | RADAR | speed 0–9 | direction |
| `0D` | MEM | sempre `00` | 0 |

byte8 = brightness 0–6 (6 step HW); 12–14 colore1; 15 rainbow (static);
16–18 colore2. Codice: `protocol/commands.py::effect_packet`.

## Per-key (prefisso `06 be 19 00 01 01 0e`)

Key-id = HID usage ID standard. Fino a 5 tasti per pacchetto, colori
come RGB+`00`. Lunghezze osservate e re-verificate:
`{1: 32, 2: 28, 3: 24, 4: 28, 5: 32}` B (meccanismo lato hidraw non
indagato, tabella empirica stabile).

`kbd()`: apertura `...0f` + 18 gruppi (primo con marcatori `0x53`/`0x65`)
+ chiusura `06 be 15 00 02 01 01 ...`. Codice: `protocol/board.py`.
