# SPDX-License-Identifier: GPL-3.0-or-later
"""Tema chiaro/scuro con follow di sistema e override manuale."""

from PySide6.QtCore import QSettings

ORG, APP = "drevo-control", "drevo-control"

LIGHT = {
    "bg": "#fafafa", "fg": "#2e3436", "muted": "#5e5c64",
    "card": "#ffffff", "nav": "#ebebeb", "sel": "#dce7f5",
    "sel_fg": "#1a5fb4", "border": "#c9c9c9", "track": "#d5d5d5",
    "accent": "#3584e4", "accent_h": "#1c71d8",
}
DARK = {
    "bg": "#242424", "fg": "#eeeeec", "muted": "#9a9996",
    "card": "#2e2e2e", "nav": "#303030", "sel": "#1c71d8",
    "sel_fg": "#ffffff", "border": "#4a4a4a", "track": "#4a4a4a",
    "accent": "#3584e4", "accent_h": "#62a0ea",
}


def build_qss(p):
    try:
        import importlib.resources
        chevron = importlib.resources.files("drevo_control.data").joinpath(
            "chevron-down.svg")
    except (ImportError, ModuleNotFoundError):
        chevron = "chevron-down.svg"
    return f"""
QMainWindow, QWidget#page {{ background: {p['bg']}; color: {p['fg']}; }}
QListWidget#nav {{ background: {p['nav']}; border: none; font-size: 15px; }}
QListWidget#nav::item {{ padding: 10px 14px; border-radius: 8px; }}
QListWidget#nav::item:selected {{ background: {p['sel']}; color: {p['sel_fg']}; }}
QLabel#title {{ font-size: 24px; font-weight: 800; }}
QLabel#section {{ font-size: 15px; font-weight: 700;
    margin-top: 10px; }}
QLabel#hint {{ color: {p['muted']}; }}
QLabel[kind="ok"] {{ color: #26a269; font-weight: 700; }}
QLabel[kind="error"] {{ color: #c01c28; font-weight: 700; }}
QStatusBar {{ background: {p['nav']}; color: {p['muted']}; }}
QStatusBar::item {{ border: none; }}
QPushButton {{ background: {p['card']}; color: {p['fg']};
    border: 1px solid {p['border']}; border-radius: 8px; padding: 8px 16px; }}
QPushButton:hover {{ background: {p['nav']}; }}
QPushButton#accent {{ background: {p['accent']}; color: white; border: none;
    font-weight: 700; }}
QPushButton#accent:hover {{ background: {p['accent_h']}; }}
QPushButton#swatch {{ border-radius: 8px; padding: 6px 12px; }}
QPushButton#cap {{ padding: 2px 1px; }}
QPushButton[selected="true"] {{ border: 2px solid {p['accent']}; }}
QPushButton:disabled {{ color: {p['muted']}; }}
QComboBox {{ background: {p['card']}; color: {p['fg']};
    border: 1px solid {p['border']}; border-radius: 8px;
    padding: 6px 28px 6px 10px; min-height: 20px; }}
QComboBox::drop-down {{ border: none; border-left: 1px solid {p['border']};
    background: {p['nav']}; width: 30px;
    border-top-right-radius: 8px; border-bottom-right-radius: 8px; }}
QComboBox::down-arrow {{ image: url({chevron}); width: 12px; height: 12px; }}
QSpinBox, QLineEdit, QTextEdit, QListWidget {{
    background: {p['card']}; color: {p['fg']};
    border: 1px solid {p['border']}; border-radius: 8px; padding: 6px 10px; }}
QListWidget {{ padding: 4px; }}
QSlider::groove:horizontal {{ height: 4px; background: {p['track']};
    border-radius: 2px; }}
QSlider::handle:horizontal {{ width: 18px; height: 18px;
    background: {p['card']}; border: 1px solid {p['border']};
    border-radius: 9px; margin: -7px 0; }}
QGroupBox {{ border: 1px solid {p['track']}; border-radius: 12px;
    margin-top: 18px; padding-top: 10px;
    background: {p['card']}; color: {p['fg']}; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px;
    color: {p['muted']}; }}
QCheckBox {{ color: {p['fg']}; spacing: 8px; }}
"""


def system_scheme():
    """'dark'/'light' dal portale FreeDesktop, fallback styleHints."""
    try:
        from PySide6.QtDBus import QDBusConnection, QDBusInterface
        bus = QDBusConnection.sessionBus()
        iface = QDBusInterface("org.freedesktop.portal.Desktop",
                               "/org/freedesktop/portal/desktop",
                               "org.freedesktop.portal.Settings", bus)
        reply = iface.call("Read", "org.freedesktop.appearance",
                           "color-scheme")
        if reply.errorName() == "":
            return "dark" if int(reply.arguments()[0]) == 1 else "light"
    except Exception:
        pass
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        hints = QApplication.instance().styleHints()
        scheme = hints.colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
        if scheme == Qt.ColorScheme.Light:
            return "light"
    except Exception:
        pass
    return "light"


def saved_mode():
    return QSettings(ORG, APP).value("theme/mode", "auto")


def save_mode(mode):
    QSettings(ORG, APP).setValue("theme/mode", mode)


def resolve(mode=None):
    mode = mode or saved_mode()
    if mode == "auto":
        return system_scheme()
    return mode


def apply_theme(window, mode=None):
    from PySide6.QtGui import QColor, QPalette

    pal = DARK if resolve(mode) == "dark" else LIGHT
    window.setStyleSheet(build_qss(pal))
    palette = window.palette()
    palette.setColor(QPalette.Window, QColor(pal["bg"]))
    palette.setColor(QPalette.Base, QColor(pal["card"]))
    palette.setColor(QPalette.AlternateBase, QColor(pal["nav"]))
    palette.setColor(QPalette.Text, QColor(pal["fg"]))
    palette.setColor(QPalette.WindowText, QColor(pal["fg"]))
    palette.setColor(QPalette.Button, QColor(pal["card"]))
    palette.setColor(QPalette.ButtonText, QColor(pal["fg"]))
    palette.setColor(QPalette.Highlight, QColor(pal["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor("white"))
    window.setPalette(palette)
    try:
        from PySide6.QtWidgets import QApplication
        inst = QApplication.instance()
        if inst is not None:
            inst.setPalette(palette)
    except Exception:
        pass
