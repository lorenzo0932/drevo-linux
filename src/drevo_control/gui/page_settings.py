"""Pagina Impostazioni: tema, keyd, udev, info app."""

import os
import shutil
import subprocess

from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGroupBox,
                               QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

from drevo_control import __version__
from drevo_control.gui import theme as T
from drevo_control.gui.widgets import hint, padded, section
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

        layout.addWidget(section("Aspetto"))
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        form.setContentsMargins(0, 4, 0, 0)
        self.theme = QComboBox()
        self.theme.addItems(["auto", "chiaro", "scuro"])
        self.theme.setCurrentText({"auto": "auto", "light": "chiaro",
                                   "dark": "scuro"}.get(T.saved_mode(),
                                                        "auto"))
        self.theme.currentTextChanged.connect(self._theme_changed)
        form.addRow("Tema:", self.theme)
        form_box = QWidget()
        form_box.setLayout(form)
        layout.addWidget(form_box)

        layout.addWidget(section("Coordinamento"))
        form2 = QVBoxLayout()
        form2.setContentsMargins(0, 4, 0, 0)
        form2.setSpacing(8)
        self.pause = QCheckBox("Metti in pausa l'ambilight durante le "
                              "scritture (consigliato)")
        from PySide6.QtCore import QSettings
        self._settings = QSettings("drevo-control", "drevo-control")
        paused = self._settings.value("daemon/pause", True)
        self.pause.setChecked(paused not in (False, "false", 0, "0"))
        self.pause.toggled.connect(
            lambda v: self._settings.setValue("daemon/pause", bool(v)))
        form2.addWidget(self.pause)
        self.ambilight_info = hint(
            "Ambilight: automazione esterna che segue i colori dello schermo "
            "(~/.local/share/myScript/GameMode/drevo_keyboard_sync.py, "
            "servizio ambilight-keyboard.service). La pausa evita scritture "
            "concorrenti sull'HID.")
        self.ambilight_info.setWordWrap(True)
        form2.addWidget(self.ambilight_info)
        coord_box = QWidget()
        coord_box.setLayout(form2)
        layout.addWidget(coord_box)

        layout.addWidget(section("Sistema"))
        form3 = QVBoxLayout()
        form3.setContentsMargins(0, 4, 0, 0)
        form3.setSpacing(8)
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
        sys_box = QWidget()
        sys_box.setLayout(form3)
        layout.addWidget(sys_box)
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
        installed = self._ambilight_installed()
        for widget in (self.pause, self.ambilight_info):
            widget.setEnabled(installed)
        if not installed:
            self.ambilight_info.setText(
                "Ambilight non rilevato su questo sistema: coordinamento "
                "non necessario.")

    @staticmethod
    def _ambilight_installed():
        import subprocess

        r = subprocess.run(
            ["systemctl", "--user", "list-unit-files",
             "ambilight-keyboard.service"],
            capture_output=True, text=True)
        return "ambilight-keyboard.service" in r.stdout

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
