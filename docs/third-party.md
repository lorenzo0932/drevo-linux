# Progetti terzi: ringraziamenti e prior art

Questo progetto sta sulle spalle di:

| Progetto | Come lo usiamo | Licenza |
|---|---|---|
| [keyd](https://github.com/rvaiya/keyd) (rvaiya) | remap/macro/game-mode via evdev; compilato dai sorgenti al momento dell'installazione | MIT |
| [hidapi](https://github.com/libusb/hidapi) (libusb) | accesso HID via binding Python `hid` | dual BSD-3-Clause / GPL (varia col pacchetto: wheel PyPI o `python3-hidapi`/`hidapi` di sistema) |
| [PySide6](https://wiki.qt.io/Qt_for_Python) / Qt | GUI | LGPL-3.0 (Qt: dual GPL/LGPL) |
| [dtv2](https://github.com/cobacdavid/dtv2) (David Cobac) | prior art sul protocollo lighting + dipendenza dell'automazione ambilight esterna | CC-BY-NC-SA |
| systemd/udev, kernel evdev/hidraw | servizi, permessi device, input | piattaforma (LGPL/GPL) |

Altri riferimenti utili, senza codice in comune: il software proprietario
[Drevo Power Console](https://www.drevo.net/page/software) (riferimento
funzionale), [dpc_linux](https://github.com/kakaZzz1/dpc_linux) e
[OpenRGB](https://openrgb.org/). Il metodo seguito e' descritto in
[reverse-engineering](reverse-engineering.md).

## Licenza di questo progetto

GPL-3.0-or-later — vedi [LICENSE](../LICENSE). Le dipendenze restano
delle loro licenze; keyd (MIT) e le librerie di sistema non vengono
ridistribuite nei nostri sorgenti (keyd si compila al momento
dell'installazione).
