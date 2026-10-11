# SPDX-License-Identifier: GPL-3.0-or-later
"""Coordinamento col daemon ambilight (stop/start attorno alle scritture)."""

import subprocess

SERVICE = "ambilight-keyboard.service"


def pause_enabled():
    """False solo se l'utente l'ha disattivato nelle Impostazioni GUI."""
    try:
        from PySide6.QtCore import QSettings
        v = QSettings("drevo-control", "drevo-control").value(
            "daemon/pause", True)
        return v not in (False, "false", 0, "0")
    except Exception:
        return True


def pause_daemon():
    subprocess.run(["systemctl", "--user", "stop", SERVICE], check=False)


def resume_daemon():
    subprocess.run(["systemctl", "--user", "start", SERVICE], check=False)


def daemon_active():
    r = subprocess.run(["systemctl", "--user", "is-active", SERVICE],
                       capture_output=True, text=True)
    return r.stdout.strip() == "active"
