#!/usr/bin/env bash
# Test guidato di una config keyd con ritorno automatico alla base.
# Uso: keyd_guarded_test.sh <file.conf> [secondi]
# Installa la config di test, ricarica keyd, chiede conferma VIA MOUSE.
# Allo scadere del timeout o su risposta negativa: torna alla config base
# (keyd resta installato). La rimozione completa resta in keyd_rollback.sh.
# Pensato per il caso peggiore (tastiera muta): non serve digitare nulla.
set -u

CONF="${1:?uso: $0 <file.conf> [secondi] [descrizione test]}"
TIMEOUT="${2:-45}"
WHAT="${3:-Prova la modifica.}"
MAIN_CONF="/etc/keyd/keyd.conf"
BACKUP="/tmp/opencode/keyd-base.conf"

echo "backup base e installo config di test come $MAIN_CONF"
cp "$MAIN_CONF" "$BACKUP"
sudo install -D -m 644 "$CONF" "$MAIN_CONF"
sudo systemctl reload keyd 2>/dev/null || sudo systemctl restart keyd
sleep 1

if timeout "$TIMEOUT" zenity --question \
    --text="TEST: ${WHAT}\n\nOK = funziona, tengo la modifica.\nScadenza tra ${TIMEOUT}s = ritorno alla config base." \
    --ok-label="Funziona, tieni" --cancel-label="Torna alla base" 2>/dev/null; then
    echo "confermato via mouse: tengo la nuova config (gia' in keyd.conf)"
else
    echo "nessuna conferma: torno alla config base (keyd resta installato)"
    sudo install -m 644 "$BACKUP" "$MAIN_CONF"
    sudo rm -f /etc/keyd/conf.d/00-test.conf
    sudo systemctl reload keyd 2>/dev/null || sudo systemctl restart keyd
    systemctl is-active keyd
fi
