#!/usr/bin/env bash
# Installer one-command di Drevo Control.
# Uso locale:  bash install.sh [--with-keyd]
# Uso remoto:  curl -sSL https://github.com/lorenzo0932/drevo-linux/raw/main/install.sh | bash -s -- [--with-keyd]
set -u

REPO_URL="${REPO_URL:-https://github.com/lorenzo0932/drevo-linux}"
DEST="$HOME/.local/share/drevo-control"
WITH_KEYD=0
[ "${1:-}" = "--with-keyd" ] && WITH_KEYD=1

fail() { echo "ERRORE: $1" >&2; exit 1; }

command -v python3 >/dev/null || fail "python3 non trovato"
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" \
    || fail "serve Python >= 3.10"

if [ -f ./pyproject.toml ] && [ -d ./src/drevo_control ]; then
    SRC="$(pwd)"
else
    command -v git >/dev/null || fail "git non trovato"
    SRC="${TMPDIR:-/tmp}/drevo-src-$$"
    rm -rf "$SRC"
    git clone --depth 1 "$REPO_URL" "$SRC" || fail "clone fallito"
fi
echo "sorgenti: $SRC"

[ -d "$DEST" ] && { echo "$DEST esiste: rimuovo (installazione pulita)"; rm -rf "$DEST"; }
python3 -m venv "$DEST/venv" || fail "creazione venv fallita"
# shellcheck disable=SC1091
. "$DEST/venv/bin/activate"
pip install -q --upgrade pip
pip install -q "$SRC[gui]" || fail "pip install fallita"

mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
ln -sf "$DEST/venv/bin/drevo-control" "$HOME/.local/bin/drevo-control"
ln -sf "$DEST/venv/bin/drevo-control-gui" "$HOME/.local/bin/drevo-control-gui"
sed "s|^Exec=drevo-control-gui|Exec=$HOME/.local/bin/drevo-control-gui|" \
    "$SRC/drevo-control.desktop" > "$HOME/.local/share/applications/drevo-control.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

if [ ! -f /etc/udev/rules.d/77-drevo-control.rules ]; then
    echo "installo regola udev (richiede sudo una volta sola)"
    sudo install -m 644 "$SRC/udev/77-drevo-control.rules" /etc/udev/rules.d/ \
        || fail "installazione udev fallita"
    sudo udevadm control --reload-rules
    sudo udevadm trigger --subsystem-match=usb --subsystem-match=hidraw
else
    echo "regola udev gia' presente"
fi

if [ "$WITH_KEYD" = 1 ]; then
    echo "installo keyd dai sorgenti (richiede gcc/make/git + sudo)"
    bash "$SRC/src/drevo_control/data/keyd_install_src.sh" \
        || fail "installazione keyd fallita"
fi

echo
echo "OK: lancia 'drevo-control-gui' o cerca Drevo Control nel menu."
echo "nota: assicurati che ~/.local/bin sia nel PATH."
