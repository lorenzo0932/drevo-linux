#!/usr/bin/env bash
# Installa keyd dai sorgenti in locale (~/.local/src/keyd).
# Niente package manager: richiede solo gcc/make/git (verificati prima).
# Uso: keyd_install_src.sh [tag]  (default: ultimo tag stabile remoto)
set -u

SRC="$HOME/.local/src/keyd"
REPO_URL="https://github.com/rvaiya/keyd"

for t in gcc make git; do
    command -v "$t" >/dev/null || {
        echo "manca $t: installalo e riprova" >&2; exit 1; }
done

TAG="${1:-}"
if [ -z "$TAG" ]; then
    TAG=$(git ls-remote --tags --sort=-v:refname "$REPO_URL" \
        | grep -o 'refs/tags/v[0-9.]*$' | head -1 | sed 's|refs/tags/||')
    [ -n "$TAG" ] || { echo "rete non disponibile?" >&2; exit 1; }
fi
echo "keyd tag: $TAG"

if [ -d "$SRC/.git" ]; then
    git -C "$SRC" fetch --tags --depth 1 origin "$TAG" || exit 1
    git -C "$SRC" checkout -q "$TAG" || exit 1
else
    rm -rf "$SRC"
    git clone --depth 1 --branch "$TAG" "$REPO_URL" "$SRC" || exit 1
fi

make -C "$SRC" -j"$(nproc)" || exit 1
sudo make -C "$SRC" install || exit 1
sudo systemctl enable --now keyd
systemctl is-active keyd
