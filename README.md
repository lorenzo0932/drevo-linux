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

## Installazione (qualunque distro)

Requisiti: Python 3.10+. L'accesso HID usa `hidapi` (le wheel `hid`/`PySide6`
su pip includono i binari; se `import hid` fallisce, installa la libreria
di sistema, es. `hidapi`).

```sh
pip install .[gui]
drevo-control effect static 255 90 0   # CLI
drevo-control-gui                        # GUI
```

La GUI richiede l'extra `gui` (PySide6). Regola udev e voce di menu:

```sh
sudo cp udev/77-drevo-control.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
cp drevo-control.desktop ~/.local/share/applications/
```

keyd (remap/macro/game-mode) si installa da Impostazioni, dai sorgenti
senza package manager. Il firmware si aggiorna solo da Windows.

## Layout

- `src/drevo_control/` — core lib HID + GUI (prossimo)
- `plan/` — piano di feature, mai committato (gitignored)
