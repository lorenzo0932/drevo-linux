"""Finestra principale: navigazione laterale + pagine."""

from PySide6.QtWidgets import (QHBoxLayout, QListWidget, QMainWindow,
                               QStackedWidget, QWidget)

from drevo_control.gui import theme as T
from drevo_control.gui.page_keys import KeysPage
from drevo_control.gui.page_lights import LightsPage
from drevo_control.gui.page_perkey import PerKeyPage
from drevo_control.gui.page_profiles import ProfilesPage
from drevo_control.gui.page_settings import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drevo Control")
        self.resize(900, 640)
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
        self.nav.setFixedWidth(180)
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
            self.nav.addItem(label)
            self.stack.addWidget(page)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)


def main():
    import sys

    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
