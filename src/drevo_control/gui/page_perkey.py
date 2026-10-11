# SPDX-License-Identifier: GPL-3.0-or-later
"""Pagina Per-key: assegna colori ai singoli tasti + tinta unita board."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QGroupBox, QHBoxLayout,
                               QLabel, QListWidget, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from drevo_control.gui.keyboard_view import KeyboardView
from drevo_control.gui.widgets import hint, note, padded, section, \
    toggle_empty
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

        layout = padded(QVBoxLayout(self))
        title = QLabel("Per-key")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(hint("Colora singoli tasti o l'intera board. "
                              "I tasti non elencati restano come sono."))

        self.view = KeyboardView()
        self.view.keySelected.connect(self._from_view)
        view_scroll = QScrollArea()
        view_scroll.setWidgetResizable(True)
        view_scroll.setFrameShape(QScrollArea.NoFrame)
        view_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view_scroll.setWidget(self.view)
        view_scroll.setSizeAdjustPolicy(
            QScrollArea.AdjustToContentsOnFirstShow)
        layout.addWidget(view_scroll)

        layout.addWidget(section("Assegnazioni"))
        form = QVBoxLayout()
        form.setContentsMargins(0, 4, 0, 0)
        form.setSpacing(8)
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
        self.keysel.lineEdit().setPlaceholderText("cerca tasto…")
        self.keysel.setCurrentText("")
        row.addWidget(self.swatch)
        row.addWidget(add)
        form.addLayout(row)
        self._refresh_swatch()

        self.assigned = QListWidget()
        form.addWidget(self.assigned)
        self.empty_note = hint("")
        form.addWidget(self.empty_note)
        rm = QPushButton("Rimuovi selezionato")
        rm.clicked.connect(self._remove)
        form.addWidget(rm)
        form_box = QWidget()
        form_box.setLayout(form)
        layout.addWidget(form_box)

        layout.addWidget(section("Tutta la tastiera"))
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 4, 0, 0)
        row2.setSpacing(8)
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
        row2_box = QWidget()
        row2_box.setLayout(row2)
        layout.addWidget(row2_box)

        apply_btn = QPushButton("Applica assegnazioni")
        apply_btn.setObjectName("accent")
        apply_btn.clicked.connect(self.apply)
        layout.addWidget(apply_btn)
        layout.addWidget(self.status)
        self._reload_list()
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

    def _from_view(self, name):
        self.keysel.setCurrentText(name)

    def _add(self):
        name = self.keysel.currentText().strip()
        if name not in BY_NAME:
            note(self.status, f"Tasto sconosciuto: {name}", "error")
            return
        c = self.color
        self.pending[name] = (c.red(), c.green(), c.blue())
        self._reload_list()
        note(self.status, "")

    def _remove(self):
        for item in self.assigned.selectedItems():
            self.pending.pop(item.text().split(" ")[0], None)
        self._reload_list()

    def _reload_list(self):
        self.assigned.clear()
        for name, (r, g, b) in sorted(self.pending.items()):
            self.assigned.addItem(f"{name}  #{r:02x}{g:02x}{b:02x}")
        toggle_empty(self.empty_note, self.assigned,
                     "Nessun tasto: cliccane uno sopra e premi Aggiungi.")
        self.view.paint_colors(self.pending)

    def _write_all(self, packets):
        from drevo_control.oslayer.daemon import pause_enabled
        paused = pause_enabled()
        if paused:
            pause_daemon()
        try:
            with hid_writer_lock() as locked:
                if not locked:
                    note(self.status, "Writer HID occupato.", "error")
                    return False
                with open_control() as dev:
                    for pkt in packets:
                        dev.write(pkt)
        except RuntimeError as e:
            note(self.status, f"Errore: {e}", "error")
            return False
        finally:
            if paused:
                resume_daemon()
        return True

    def apply(self):
        if not self.pending:
            note(self.status, "Niente da applicare.")
            return
        names = list(self.pending)
        packets = []
        for i in range(0, len(names), 5):
            group = names[i:i + 5]
            ids = [BY_NAME[n] for n in group]
            packets.append(indiv_packet(ids, [self.pending[n]
                                              for n in group]))
        if self._write_all(packets):
            note(self.status, f"Applicati {len(names)} tasti.", "ok")

    def apply_board(self):
        c = self.board_color
        if self._write_all(B.kbd_packets((c.red(), c.green(), c.blue()))):
            note(self.status, "Board applicata.", "ok")

    def showEvent(self, event):  # noqa: N802 (API Qt)
        self._reload_list()
        super().showEvent(event)
