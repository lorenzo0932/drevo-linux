# Baseline HID — Drevo 0416:a0f8 (2026-10-11, read-only)

Sorgente: `lsusb -v`, sysfs, `hid.enumerate`. Nessun software Drevo usato.

## USB

- `Bus 005 Device 004: ID 0416:a0f8 Winbond Electronics Corp.`
- iface 0: class HID, subclass boot (1), protocol keyboard (1), EP IN `0x81`
  64B. Legata al kernel (`0003:0416:A0F8.0005`), report descriptor da
  tastiera standard (usage page Generic Desktop + Keyboard + LED).
- iface 1: class HID, subclass boot (1), protocol mouse (2), EP IN `0x82`
  + EP OUT `0x03`, 64B. NON legata al kernel hid → accesso libusb diretto
  senza detach (è l'interfaccia che usa il daemon via `dtv2`).

## Controllo

- `hid.enumerate(0x0416, 0xA0F8)` → `5-4:1.0` e `5-4:1.1`, usage 0.
- GET feature report su iface 1 (ID `0x00`–`0x10`): tutti `read error`.
  Il device NON supporta GET_REPORT: protocollo write-only via
  SET_REPORT feature (coerente con `dtv2`, che usa solo write).
  Nessun effetto sul device (tentativi di lettura falliti).

## Conseguenze

- Letture (GET_REPORT) sicure; scritture solo su evento e mai concorrenti
  (bug Winbond reset-loop documentato nel daemon).
- Macro/remap/game-mode implementati lato OS, non via protocollo device.
