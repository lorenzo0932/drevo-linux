#!/usr/bin/env bash
# Disinstalla Drevo Control. Uso: bash uninstall.sh [--purge] [--remove-keyd]
# --purge: rimuove anche profili e impostazioni utente.
# --remove-keyd: disinstalla anche keyd (default: lo lascia).
set -u

DEST="$HOME/.local/share/drevo-linux"
PURGE=0
REMOVE_KEYD=0
for a in "$@"; do
    [ "$a" = "--purge" ] && PURGE=1
    [ "$a" = "--remove-keyd" ] && REMOVE_KEYD=1
done

rm -rf "$DEST"
rm -f "$HOME/.local/bin/drevo-control" "$HOME/.local/bin/drevo-control-gui"
rm -f "$HOME/.local/share/applications/drevo-control.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

if [ -f /etc/udev/rules.d/77-drevo-control.rules ]; then
    sudo rm -f /etc/udev/rules.d/77-drevo-control.rules
    sudo udevadm control --reload-rules
fi

if [ "$REMOVE_KEYD" = 1 ] && [ -f ./tools/keyd_rollback.sh ]; then
    bash ./tools/keyd_rollback.sh
fi

if [ "$PURGE" = 1 ]; then
    rm -rf "$HOME/.config/drevo-control"
    echo "purge: profili e impostazioni rimossi"
else
    echo "nota: profili e impostazioni conservati in ~/.config/drevo-control"
fi

echo "OK: Drevo Control disinstallato"
