#!/usr/bin/env bash
# Rollback keyd -> situazione pre-installazione. Idempotente e sicuro da
# rieseguire: ogni passo tollera l'assenza del componente.
set -u

echo '[1/4] stop+disable keyd (se presente)'
sudo systemctl stop keyd 2>/dev/null || true
sudo systemctl disable keyd 2>/dev/null || true

echo '[2/4] rimozione keyd (pacchetto o sorgenti)'
if rpm -q keyd >/dev/null 2>&1; then
    sudo dnf remove -y keyd
elif [ -x /usr/local/bin/keyd ]; then
    for src in /usr/local/src/keyd "$HOME/.local/src/keyd" \
               /root/.local/src/keyd; do
        if [ -f "$src/Makefile" ]; then
            sudo make -C "$src" uninstall || true
            break
        fi
    done
    sudo rm -f /usr/local/bin/keyd /usr/local/bin/keyd-application-mapper \
        /usr/local/lib/systemd/system/keyd.service \
        /usr/lib/systemd/system/keyd.service \
        /etc/systemd/system/*keyd* /etc/systemd/user/*keyd*
    sudo systemctl daemon-reload
else
    echo 'keyd non installato, salto'
fi

echo '[3/4] rimozione config e udev di keyd (se presenti)'
sudo rm -rf /etc/keyd
sudo rm -f /etc/udev/rules.d/99-keyd.rules
sudo udevadm control --reload-rules 2>/dev/null || true

echo '[4/4] riavvio daemon ambilight e verifica'
systemctl --user restart ambilight-keyboard.service
systemctl --user is-active ambilight-keyboard.service
rpm -q keyd 2>&1 || true
echo 'ROLLBACK OK: verifica digitazione su tastiera Drevo'
