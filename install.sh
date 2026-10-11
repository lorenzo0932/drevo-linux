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

have() { command -v "$1" >/dev/null; }

# Rileva package manager: stampa "dnf|apt|pacman|zypper|none"
detect_pm() {
    if have dnf; then echo dnf
    elif have apt-get; then echo apt
    elif have pacman; then echo pacman
    elif have zypper; then echo zypper
    else echo none
    fi
}

# Installa pacchetti di sistema col PM rilevato (una sola richiesta sudo)
sys_install() {
    [ $# -eq 0 ] && return 0
    case "$(detect_pm)" in
        dnf) sudo dnf install -y "$@" ;;
        apt) sudo apt-get update -qq && sudo apt-get install -y "$@" ;;
        pacman) sudo pacman -S --needed --noconfirm "$@" ;;
        zypper) sudo zypper -n install "$@" ;;
        none) fail "installa manualmente: $*" ;;
    esac
}

# Nomi pacchetto per distro: python3 venv-capable, git, hidapi, build tools
need_python() {
    python3 -c "import sys, venv; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null
}
ensure_reqs() {
    need_python || case "$(detect_pm)" in
        dnf) sys_install python3 ;;
        apt) sys_install python3 python3-venv ;;
        pacman) sys_install python ;;
        zypper) sys_install python3 ;;
        none) fail "serve Python >= 3.10" ;;
    esac
    need_python || fail "serve Python >= 3.10"
    # git solo se serve clonare (uso remoto)
    if ! { [ -f ./pyproject.toml ] && [ -d ./src/drevo_control ]; }; then
        have git || case "$(detect_pm)" in
            dnf) sys_install git ;;
            apt) sys_install git ;;
            pacman) sys_install git ;;
            zypper) sys_install git ;;
            none) fail "serve git" ;;
        esac
    fi
    # lib hid di sistema (fallback se la wheel non basta)
    python3 -c "import hid" 2>/dev/null || case "$(detect_pm)" in
        dnf) sys_install hidapi ;;
        apt) sys_install libhidapi-hidraw0 ;;
        pacman) sys_install hidapi ;;
        zypper) sys_install libhidapi-hidraw0 ;;
        none) echo "avviso: impossibile verificare hidapi di sistema" ;;
    esac
    if [ "$WITH_KEYD" = 1 ]; then
        for t in gcc make; do
            have "$t" && continue
            case "$(detect_pm)" in
                dnf) sys_install gcc make ;;
                apt) sys_install build-essential ;;
                pacman) sys_install base-devel ;;
                zypper) sys_install gcc make ;;
                none) fail "servono gcc e make per keyd" ;;
            esac
            break
        done
    fi
}

ensure_reqs
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
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    if ! grep -q 'drevo-control PATH' "$HOME/.bashrc" 2>/dev/null; then
        { echo ''; echo '# drevo-control PATH'; echo 'export PATH="$HOME/.local/bin:$PATH"'; } >> "$HOME/.bashrc"
        echo "aggiunto ~/.local/bin al PATH in ~/.bashrc (riapri il terminale)"
    fi
fi
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
