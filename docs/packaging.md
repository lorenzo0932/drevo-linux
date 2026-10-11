# Packaging e distribuzione

Formato: pacchetto pip (setuptools) + `install.sh` one-command.
Niente AppImage/Flatpak di proposito: udev, keyd come servizio e voce
menu richiedono comunque passi sull'host; Flatpak blocca l'HID raw.

## Cosa fa l'installer

1. venv isolato in `~/.local/share/drevo-linux`, `pip install .[gui]`;
2. symlink in `~/.local/bin`, `.desktop` nel menu;
3. regola udev (unico sudo) + reload/trigger;
4. opzionale `--with-keyd`: build keyd dai sorgenti.

`uninstall.sh [--purge] [--remove-keyd]`: rimuove app, voce menu e udev;
profili conservati salvo `--purge`. Verificato il giro completo con
profili sopravvissuti.

## Dipendenze

Tutto via wheel PyPI (`hid`, `PySide6`), Python ≥ 3.10, nessuna dipendenza
da package manager di distro (tranne gcc/make/git solo per keyd).
File dati shippati via `package-data`: QSS, regola udev, script e icona
chevron. Entry point: `drevo-control`, `drevo-control-gui`.
