# Progetti terzi integrati e riferimenti

## Integrati (runtime/dipendenze)

| Progetto | Uso | Licenza |
|---|---|---|
| [keyd](https://github.com/rvaiya/keyd) (rvaiya) | remap/macro/game-mode via evdev; compilato dai sorgenti, non bundlato | MIT |
| [hidapi](https://github.com/libusb/hidapi) (libusb) | accesso HID via binding Python `hid` | dual BSD-3-Clause / GPL (a seconda del pacchetto: wheel PyPI o `python3-hidapi`/`hidapi` di sistema) |
| [PySide6](https://wiki.qt.io/Qt_for_Python) / Qt | GUI | LGPL-3.0 (Qt: dual GPL/LGPL) |
| [dtv2](https://github.com/cobacdavid/dtv2) (David Cobac) | automazione ambilight esistente + generatore di traffico di riferimento per le catture; **codice non copiato nel repo** | CC-BY-NC-SA |
| systemd/udev, kernel evdev/hidraw | servizi, permessi device, input | piattaforma (LGPL/GPL) |

## Riferimenti (nessun codice riusato)

- [Drevo Power Console](https://www.drevo.net/page/software) (Drevo):
  software proprietario di riferimento per funzioni e flussi; osservato
  solo come comportamento su hardware proprio, mai decompilato.
- [dpc_linux](https://github.com/kakaZzz1/dpc_linux): clone DPC per
  BladeMaster (`1a2c`), non compatibile col nostro `0416:a0f8`; non riusato
  (blob `libhidkeyboard.a` senza sorgenti).
- [OpenRGB](https://openrgb.org/): solo RGB, senza supporto V2 TE
  (richiesta #718); non riusato.

## Licenza di questo progetto

GPL-3.0-or-later — vedi [LICENSE](../LICENSE). Le dipendenze restano
delle loro licenze; keyd (MIT) e le librerie di sistema non vengono
ridistribuite nei nostri sorgenti (keyd si compila al momento
dell'installazione).
