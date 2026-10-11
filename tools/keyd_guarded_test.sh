#!/usr/bin/env bash
# Test guidato di una config keyd con ritorno automatico alla base.
# Uso: keyd_guarded_test.sh <file.conf> [secondi]
# Installa la config di test, ricarica keyd, chiede conferma VIA MOUSE.
# Allo scadere del timeout o su risposta negativa: torna alla config base
# (keyd resta installato). La rimozione completa resta in keyd_rollback.sh.
# Pensato per il caso peggiore (tastiera muta): non serve digitare nulla.
set -u

CONF="${1:?uso: $0 <file.conf> [secondi]}"
TIMEOUT="${2:-45}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

echo "installo config di test: $CONF"
sudo install -D -m 644 "$CONF" /etc/keyd/conf.d/00-test.conf
sudo systemctl reload keyd 2>/dev/null || sudo systemctl restart keyd
sleep 1

if timeout "$TIMEOUT" zenity --question \
    --text="Prova la modifica (es. BLOC MAIUSC ora e' ESC).\n\nOK = funziona, tengo la modifica.\nScadenza tra ${TIMEOUT}s = ritorno alla config base." \
    --ok-label="Funziona, tieni" --cancel-label="Torna alla base" 2>/dev/null; then
    echo "confermato via mouse: tengo la config di test come base"
    sudo mv /etc/keyd/conf.d/00-test.conf /etc/keyd/conf.d/10-drevo.conf
    sudo systemctl reload keyd 2>/dev/null || sudo systemctl restart keyd
else
    echo "nessuna conferma: torno alla config base (keyd resta installato)"
    sudo rm -f /etc/keyd/conf.d/00-test.conf
    sudo systemctl reload keyd 2>/dev/null || sudo systemctl restart keyd
    systemctl is-active keyd
fi
