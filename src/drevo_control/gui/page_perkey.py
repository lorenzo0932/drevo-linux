"""Pagina Per-key: assegna colori ai singoli tasti + tinta unita board."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QListWidget, QPushButton, QVBoxLayout,
                               QWidget)

from drevo_control.oslayer.daemon import pause_daemon, resume_daemon
from drevo_control.protocol import board as B
from drevo_control.protocol.commands import indiv_packet
from drevo_control.protocol.device import open_control
from drevo_control.protocol.keymap import BY_NAME
from drevo_control.lock import hid_writer_lock


class PerKeyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.pending = {}  # nome -> (r, g, b)
        self.color = QColor(255, 0, 0)
        self.status = QLabel("")
        self.status.setObjectName("hint")

        layout = QVBoxLayout(self)
        title = QLabel("Per-key")
        title.setObjectName("title")
        layout.addWidget(title)

        box = QGroupBox("Assegnazioni")
        form = QVBoxLayout(box)
        row = QHBoxLayout()
        self.keysel = QComboBox()
        self.keysel.setEditable(True)
        self.keysel.addItems(sorted(BY_NAME))
        self.swatch = QPushButton("Colore")
        self.swatch.setObjectName("swatch")
        self.swatch.clicked.connect(self._pick)
        add = QPushButton("Aggiungi")
        add.clicked.connect(self._add)
        row.addWidget(self.keysel, 1)
        row.addWidget(self.swatch)
        row.addWidget(add)
        form.addLayout(row)
        self._refresh_swatch()

        self.assigned = QListWidget()
        form.addWidget(self.assigned)
        rm = QPushButton("Rimuovi selezionato")
        rm.clicked.connect(self._remove)
        form.addWidget(rm)
        layout.addWidget(box)

        box2 = QGroupBox("Tutta la tastiera")
        row2 = QHBoxLayout(box2)
        self.board_color_btn = QPushButton("Colore board")
        self.board_color_btn.setObjectName("swatch")
        self.board_color_btn.clicked.connect(self._pick_board)
        self.board_color = QColor(255, 90, 0)
        self._refresh_board()
        apply_board = QPushButton("Applica a tutta la board")
        apply_board.setObjectName("accent")
        apply_board.clicked.connect(self.apply_board)
        row2.addWidget(self.board_color_btn)
        row2.addWidget(apply_board)
        layout.addWidget(box2)

        apply_btn = QPushButton("Applica assegnazioni")
        apply_btn.setObjectName("accent")
        apply_btn.clicked.connect(self.apply)
        layout.addWidget(apply_btn)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def _pick(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self._refresh_swatch()

    def _refresh_swatch(self):
        self.swatch.setStyleSheet(
            f"background: {self.color.name()}; color: white;")

    def _pick_board(self):
        color = QColorDialog.getColor(self.board_color, self)
        if color.isValid():
            self.board_color = color
            self._refresh_board()

    def _refresh_board(self):
        self.board_color_btn.setStyleSheet(
            f"background: {self.board_color.name()}; color: white;")

    def _add(self):
        name = self.keysel.currentText().strip()
        if name not in BY_NAME:
            self.status.setText(f"Tasto sconosciuto: {name}")
            return
        c = self.color
        self.pending[name] = (c.red(), c.green(), c.blue())
        self._reload_list()
        self.status.setText("")

    def _remove(self):
        for item in self.assigned.selectedItems():
            self.pending.pop(item.text().split(" ")[0], None)
        self._reload_list()

    def _reload_list(self):
        self.assigned.clear()
        for name, (r, g, b) in sorted(self.pending.items()):
            self.assigned.addItem(f"{name}  #{r:02x}{g:02x}{b:02x}")

    def _write_all(self, packets):
        from drevo_control.oslayer.daemon import pause_enabled
        paused = pause_enabled()
        if paused:
            pause_daemon()
        try:
            with hid_writer_lock() as locked:
                if not locked:
                    raise RuntimeError("writer HID occupato")
                with open_control() as dev:
                    for pkt in packets:
                        dev.write(pkt)
        finally:
            if paused:
                resume_daemon()

    def apply(self):
        if not self.pending:
            self.status.setText("Niente da applicare.")
            return
        names = list(self.pending)
        packets = []
        for i in range(0, len(names), 5):
            group = names[i:i + 5]
            ids = [BY_NAME[n] for n in group]
            packets.append(indiv_packet(ids, [self.pending[n]
                                              for n in group]))
        self._write_all(packets)
        self.status.setText(f"Applicati {len(names)} tasti.")

    def apply_board(self):
        c = self.board_color
        self._write_all(B.kbd_packets((c.red(), c.green(), c.blue())))
        self.status.setText("Board applicata.")
