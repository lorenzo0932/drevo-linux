"""Pagina Impostazioni: tema, keyd, udev, info app."""

import os
import shutil
import subprocess

from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGroupBox,
                               QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

from drevo_control import __version__
from drevo_control.gui import theme as T
from drevo_control.gui.widgets import hint, padded
from drevo_control.oslayer.apply import keyd_active


class SettingsPage(QWidget):
    def __init__(self, window=None):
        super().__init__()
        self.window = window
        self.status = QLabel("")
        self.status.setObjectName("hint")

        layout = padded(QVBoxLayout(self))
        title = QLabel("Impostazioni")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(hint("Tema, coordinamento e componenti di sistema."))

        box = QGroupBox("Aspetto")
        form = QFormLayout(box)
        self.theme = QComboBox()
        self.theme.addItems(["auto", "chiaro", "scuro"])
        self.theme.setCurrentText({"auto": "auto", "light": "chiaro",
                                   "dark": "scuro"}.get(T.saved_mode(),
                                                        "auto"))
        self.theme.currentTextChanged.connect(self._theme_changed)
        form.addRow("Tema:", self.theme)
        layout.addWidget(box)

        box2 = QGroupBox("Coordinamento")
        form2 = QVBoxLayout(box2)
        self.pause = QCheckBox("Metti in pausa l'ambilight durante le "
                              "scritture (consigliato)")
        from PySide6.QtCore import QSettings
        self._settings = QSettings("drevo-control", "drevo-control")
        paused = self._settings.value("daemon/pause", True)
        self.pause.setChecked(paused not in (False, "false", 0, "0"))
        self.pause.toggled.connect(
            lambda v: self._settings.setValue("daemon/pause", bool(v)))
        form2.addWidget(self.pause)
        layout.addWidget(box2)

        box3 = QGroupBox("Sistema")
        form3 = QVBoxLayout(box3)
        self.keyd_label = QLabel()
        row = QHBoxLayout()
        install = QPushButton("Installa keyd (COPR)")
        install.clicked.connect(self._install_keyd)
        remove = QPushButton("Rimuovi keyd")
        remove.clicked.connect(self._remove_keyd)
        row.addWidget(install)
        row.addWidget(remove)
        form3.addWidget(self.keyd_label)
        form3.addLayout(row)
        udev_row = QHBoxLayout()
        self.udev_label = QLabel()
        udev_btn = QPushButton("Installa regola udev")
        udev_btn.clicked.connect(self._install_udev)
        udev_row.addWidget(self.udev_label, 1)
        udev_row.addWidget(udev_btn)
        form3.addLayout(udev_row)
        layout.addWidget(box3)
        self.refresh_system()

        info = QLabel(f"drevo-control {__version__} — GPL-3.0-or-later\n"
                      f"config: {os.path.expanduser('~/.config/drevo-control')}")
        info.setObjectName("hint")
        layout.addWidget(info)
        layout.addWidget(self.status)
        layout.addStretch(1)

    # -- tema ----------------------------------------------------------
    def _theme_changed(self, text):
        mode = {"auto": "auto", "chiaro": "light", "scuro": "dark"}[text]
        T.save_mode(mode)
        if self.window is not None:
            T.apply_theme(self.window, mode)

    # -- sistema -------------------------------------------------------
    def refresh_system(self):
        self.keyd_label.setText(
            "keyd: " + ("attivo" if keyd_active() else "non attivo"))
        dst = "/etc/udev/rules.d/77-drevo-control.rules"
        self.udev_label.setText(
            "udev: " + ("installata" if os.path.isfile(dst) else
                        "non installata"))

    def _run_priv(self, *cmd):
        if shutil.which("pkexec") and (os.environ.get("DISPLAY")
                                       or os.environ.get("WAYLAND_DISPLAY")):
            cmd = ("pkexec", *cmd)
        else:
            cmd = ("sudo", "-n", *cmd)
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=300)

    def _install_keyd(self):
        self.status.setText("Installazione keyd in corso…")
        r = self._run_priv("bash", "-c",
                           "dnf copr enable -y fmonteghetti/keyd && "
                           "dnf install -y keyd")
        self.status.setText("keyd installato." if r.returncode == 0
                            else f"Errore: {(r.stderr or '')[:200]}")
        self.refresh_system()

    def _remove_keyd(self):
        self.status.setText("Rimozione keyd in corso…")
        r = self._run_priv("bash", "-c",
                           "systemctl stop keyd; systemctl disable keyd; "
                           "dnf remove -y keyd; rm -rf /etc/keyd")
        self.status.setText("keyd rimosso." if r.returncode == 0
                            else f"Errore: {(r.stderr or '')[:200]}")
        self.refresh_system()

    def _install_udev(self):
        import importlib.resources
        import tempfile

        data = importlib.resources.read_text(
            "drevo_control.data", "77-drevo-control.rules")
        with tempfile.NamedTemporaryFile("w", suffix=".rules",
                                         delete=False) as f:
            f.write(data)
        r = self._run_priv(
            "bash", "-c",
            f"install -m 644 {f.name} "
            "/etc/udev/rules.d/77-drevo-control.rules && "
            "udevadm control --reload-rules && udevadm trigger")
        os.unlink(f.name)
        self.status.setText("Regola udev installata." if r.returncode == 0
                            else f"Errore: {(r.stderr or '')[:200]}")
        self.refresh_system()
