#!/usr/bin/env bash
# Test guidato di una config keyd con revert automatico.
# Uso: keyd_guarded_test.sh <file.conf> [secondi]
# Installa la config, ricarica keyd, chiede conferma VIA MOUSE (zenity).
# Allo scadere del timeout o su risposta negativa: rollback automatico.
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
    --text="Prova a scrivere con la tastiera Drevo.\n\nOK = funziona, tengo la config.\nScadenza tra ${TIMEOUT}s = rollback automatico." \
    --ok-label="Funziona, tieni" --cancel-label="Ripristina subito" 2>/dev/null; then
    echo "confermato via mouse: tengo la config"
    sudo rm -f /etc/keyd/conf.d/00-test.conf
else
    echo "nessuna conferma: ROLLBACK AUTOMATICO"
    bash "$REPO/tools/keyd_rollback.sh"
fi
