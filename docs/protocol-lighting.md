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

## Note
- GET feature report non supportato dal device (solo SET/OUT).
- Prossimo: catturare BREATH/STREAM/RADAR e per-key allo stesso modo,
  sempre e solo dal nostro traffico.
