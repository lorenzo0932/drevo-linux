"""Tastiera ISO disegnata: keycap cliccabili con colore assegnato."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, \
    QVBoxLayout, QWidget

DISPLAY = {
    "backs": "Bksp", "caps": "Caps", "lshift": "Shift", "rshift": "Shift",
    "lctrl": "Ctrl", "rctrl": "Ctrl", "lalt": "Alt", "ralt": "Alt",
    "win": "Win", "space": "Space", "enter": "Enter", "menu": "Menu",
    "grave": "`¬", "minus": "-_", "equal": "=+", "lbrace": "[{",
    "rbrace": "]}", "scolon": ";:", "quote": "'@", "hash": "#~",
    "comma": ",<", "dot": ".>", "slash": "/?", "iso": "\\|",
    "pup": "PgUp", "pdown": "PgDn", "ps": "Stamp",
    "sl": "Bloc", "pb": "Pausa", "ins": "Ins",
}

ROWS = [
    [("esc", 1), ("f1", 1), ("f2", 1), ("f3", 1), ("f4", 1),
     ("f5", 1), ("f6", 1), ("f7", 1), ("f8", 1), ("f9", 1), ("f10", 1),
     ("f11", 1), ("f12", 1), ("ps", 1), ("sl", 1), ("pb", 1)],
    [("grave", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1),
     ("6", 1), ("7", 1), ("8", 1), ("9", 1), ("0", 1), ("minus", 1),
     ("equal", 1), ("backs", 2)],
    [("tab", 1.5), ("q", 1), ("w", 1), ("e", 1), ("r", 1), ("t", 1),
     ("y", 1), ("u", 1), ("i", 1), ("o", 1), ("p", 1), ("lbrace", 1),
     ("rbrace", 1)],
    [("caps", 1.75), ("a", 1), ("s", 1), ("d", 1), ("f", 1), ("g", 1),
     ("h", 1), ("j", 1), ("k", 1), ("l", 1), ("scolon", 1), ("quote", 1),
     ("hash", 1), ("enter", 2.25)],
    [("lshift", 1.25), ("iso", 1), ("z", 1), ("x", 1), ("c", 1),
     ("v", 1), ("b", 1), ("n", 1), ("m", 1), ("comma", 1), ("dot", 1),
     ("slash", 1), ("rshift", 2.75)],
    [("lctrl", 1.25), ("win", 1.25), ("lalt", 1.25), ("space", 6.25),
     ("ralt", 1.25), ("FN", 1), ("menu", 1), ("rctrl", 1)],
]

NAV = [
    [("ins", 1), ("home", 1), ("pup", 1)],
    [("del", 1), ("end", 1), ("pdown", 1)],
    [(None, 1), ("up", 1), (None, 1)],
    [("left", 1), ("down", 1), ("right", 1)],
]


class KeyboardView(QWidget):
    keySelected = Signal(str)

    def __init__(self):
        super().__init__()
        self.caps = {}
        self.selected = None
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)
        main = QVBoxLayout()
        main.setSpacing(5)
        for row in ROWS:
            main.addLayout(self._row(row))
        outer.addLayout(main, 1)
        nav = QVBoxLayout()
        nav.setSpacing(5)
        for row in NAV:
            nav.addLayout(self._row(row))
        nav.addStretch(1)
        outer.addLayout(nav)

    def _row(self, row):
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        for name, units in row:
            if name is None:
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Fixed)
                layout.addWidget(spacer, int(units * 10))
                continue
            btn = QPushButton(DISPLAY.get(name, name.upper()))
            font = btn.font()
            font.setPointSize(9)
            btn.setFont(font)
            btn.setFixedHeight(42)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setProperty("keyname", name)
            if name == "FN":
                btn.setEnabled(False)
                btn.setToolTip("FN: hardware, non assegnabile")
            else:
                btn.clicked.connect(
                    lambda _=False, n=name: self.select(n))
            layout.addWidget(btn, max(1, int(units * 10)))
            self.caps[name] = btn
        return layout

    def select(self, name):
        self.selected = name
        for cap_name, btn in self.caps.items():
            selected = cap_name == name
            btn.setProperty("selected", selected)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.keySelected.emit(name)

    def paint_colors(self, mapping):
        """mapping: nome -> (r, g, b)."""
        for name, btn in self.caps.items():
            if name in mapping:
                r, g, b = mapping[name]
                btn.setStyleSheet(
                    f"background: #{r:02x}{g:02x}{b:02x}; color: white;")
            else:
                btn.setStyleSheet("")
