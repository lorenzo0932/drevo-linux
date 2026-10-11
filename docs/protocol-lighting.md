# Protocollo lighting — derivazione indipendente (2026-10-11)

Fonte: cattura `usbmon` (bus 5) di UNA scrittura del nostro helper
(`kbd_apply_one.py 10 20 30 100`). Nessun software Drevo coinvolto:
clean-room intatta.

## Comando STATIC (32B, control OUT su EP3 = iface 1)

```
Io:5:004:3 32 = 06 be 15 00 01 01 01 09 06 00 00 00
               0a 14 1e 00 ff 00 00 00 00... (zero padding a 32B)
```

| Byte | Valore | Significato osservato        |
|------|--------|------------------------------|
| 0–6  | `06 be 15 00 01 01 01` | prefisso comando STATIC |
| 7    | `09`   | speed: `round(pct/100*9)` → 100% = 9 |
| 8    | `06`   | brightness: `round(pct/100*6)` → 100% = 6 (6 step HW) |
| 9–11 | `00 00 00` | direction/riservati (static: 0) |
| 12–14| `0a 14 1e` | RGB = (10, 20, 30), l'input dato |
| 15   | `00`   | rainbow flag (0 = off)       |
| 16–18| `ff 00 00` | secondo colore default (rosso) |
| 19–31| zero   | padding                      |

Conferma indipendente del formato gia' usato dal daemon: gli step
brightness 1–6 e speed 0–9 corrispondono ai range osservati qui.

## Altri effetti (stesso layout, CMD diverso)

| CMD  | Effetto | Byte 7 | Byte 9 |
|------|---------|--------|--------|
| `01` | STATIC  | speed 0–9 | direction (0) |
| `02` | BREATH  | speed 0–9 | 0 |
| `03` | STREAM  | speed 0–9 | direction e=0 w=1 s=2 n=3 |
| `10` | RADAR   | speed 0–9 | direction |
| `0D` | MEM     | sempre `00` (speed ignorato) | 0 |

Byte 8 = brightness 0–6; 12–14 colore1; 15 rainbow (solo STATIC, gli
altri osservati a 0); 16–18 colore2. Catture: `cap_breath/stream/radar/
mem.txt` in /tmp/opencode (non committate).

## Per-key (prefisso `06 be 19 00 01 01 0e`)

- 1 tasto: 32B, key-id a byte 7, RGB a 12–14. Key-id = HID usage ID
  standard (es. `a` = `0x04`).
- n tasti (≤5): `12+4n` B, key-id a byte 7–11, poi RGB+`00` per tasto.
  Lunghezze n=2..4 DA VERIFICARE.
- `kbd()`: apertura `06 be 15 00 01 01 0f` (bri a byte 8, `ff` a 12),
  gruppi da 5 (primo con marcatori byte15=`0x53`, byte31=`0x65`),
  chiusura `06 be 15 00 02 01 01 05 09 ... ff ... ff`.

## Implementazione
`src/drevo_control/protocol/` replica questi formati con codice
originale; `tests/test_commands.py` li confronta ai byte catturati;
test hardware 2026-10-11: `cli static 10 20 30` produce byte identici
al riferimento e il device risponde.

## Note
- GET feature report non supportato dal device (solo SET/OUT).
- Prossimo: catturare BREATH/STREAM/RADAR e per-key allo stesso modo,
  sempre e solo dal nostro traffico.
