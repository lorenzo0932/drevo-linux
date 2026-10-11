# SPDX-License-Identifier: GPL-3.0-or-later
"""Preferenze GUI (QSettings): tema e coordinamento daemon."""

from PySide6.QtCore import QSettings

ORG = "drevo-control"
APP = "drevo-control"


def pause_enabled():
    """False solo se l'utente l'ha disattivato nelle Impostazioni."""
    v = QSettings(ORG, APP).value("daemon/pause", True)
    return v not in (False, "false", 0, "0")
