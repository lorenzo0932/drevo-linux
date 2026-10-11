"""Finestra principale: navigazione laterale + pagine."""

import subprocess

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QMainWindow,
                               QScrollArea, QStackedWidget, QStatusBar,
                               QWidget)

from drevo_control.gui import theme as T
from drevo_control.gui.page_keys import KeysPage
from drevo_control.gui.page_lights import LightsPage
from drevo_control.gui.page_perkey import PerKeyPage
from drevo_control.gui.page_profiles import ProfilesPage
from drevo_control.gui.page_settings import SettingsPage


def _is_active(unit, user=False):
    cmd = (["systemctl", "--user", "is-active", unit] if user
           else ["systemctl", "is-active", unit])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip() == "active"


def _device_present():
    import glob
    return bool(glob.glob("/dev/input/by-id/*Drevo*"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drevo Control")
        self.resize(1080, 680)
        self.setMinimumSize(700, 500)
        T.apply_theme(self)

        try:
            self.styleHints().colorSchemeChanged.connect(
                lambda: T.apply_theme(self)
                if T.saved_mode() == "auto" else None)
        except (AttributeError, RuntimeError):
            pass

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.nav = QListWidget()
        self.nav.setObjectName("nav")
        self.nav.setFixedWidth(170)
        self.stack = QStackedWidget()

        lights = LightsPage()
        keys = KeysPage()
        profiles = ProfilesPage()
        profiles.set_sources(lights, keys)
        settings = SettingsPage(self)
        self.pages = [("Luci", lights),
                      ("Per-key", PerKeyPage()),
                      ("Tasti e Macro", keys),
                      ("Profili", profiles),
                      ("Impostazioni", settings)]
        for label, page in self.pages:
            page.setObjectName("page")
            page.setAutoFillBackground(True)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.NoFrame)
            scroll.setWidget(page)
            self.nav.addItem(label)
            self.stack.addWidget(scroll)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        bar = QStatusBar()
        self.setStatusBar(bar)
        self.dot_device = QLabel()
        self.dot_daemon = QLabel()
        self.dot_keyd = QLabel()
        for dot in (self.dot_device, self.dot_daemon, self.dot_keyd):
            dot.setContentsMargins(12, 0, 0, 0)
            bar.addPermanentWidget(dot)
        self.refresh_status()
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_status)
        timer.start(5000)

    def refresh_status(self):
        dev = _device_present()
        dam = _is_active("ambilight-keyboard.service", user=True)
        keyd = _is_active("keyd.service")
        green, gray = "#26a269", "#9a9996"
        self.dot_device.setText(
            f"<font color='{green if dev else gray}'>●</font> Tastiera")
        self.dot_daemon.setText(
            f"<font color='{green if dam else gray}'>●</font> Ambilight")
        self.dot_keyd.setText(
            f"<font color='{green if keyd else gray}'>●</font> keyd")


def main():
    import sys

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
