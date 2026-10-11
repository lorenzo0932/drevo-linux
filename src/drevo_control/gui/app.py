"""Finestra principale: navigazione laterale + pagine."""

import importlib.resources

from PySide6.QtWidgets import (QHBoxLayout, QListWidget, QMainWindow,
                               QStackedWidget, QWidget)

from drevo_control.gui.page_lights import LightsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drevo Control")
        self.resize(860, 600)

        try:
            qss = importlib.resources.read_text("drevo_control.gui",
                                                "style.qss")
            self.setStyleSheet(qss)
        except (FileNotFoundError, ModuleNotFoundError):
            pass

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.nav = QListWidget()
        self.nav.setObjectName("nav")
        self.nav.setFixedWidth(180)
        self.stack = QStackedWidget()

        self.pages = [("Luci", LightsPage()),
                      ("Per-key", QWidget()),
                      ("Tasti e Macro", QWidget()),
                      ("Profili", QWidget())]
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
