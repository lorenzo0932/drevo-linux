"""Pagina Luci: effetto firmware + parametri, scrittura sotto pausa daemon."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QCheckBox, QColorDialog, QComboBox,
                               QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QVBoxLayout, QWidget)

from drevo_control.gui.widgets import hint, note, padded, section
from drevo_control.oslayer.daemon import pause_daemon, resume_daemon
from drevo_control.protocol import commands as C
from drevo_control.protocol.device import write_packet

EFFECTS = [("Statico", C.CMD_STATIC), ("Respiro", C.CMD_BREATH),
           ("Scorrimento", C.CMD_STREAM), ("Radar", C.CMD_RADAR),
           ("Memoria", C.CMD_MEM)]
DIRECTIONS = [("Est", 0), ("Ovest", 1), ("Sud", 2), ("Nord", 3)]


class LightsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.color1 = QColor(255, 90, 0)
        self.color2 = QColor(255, 0, 0)
        self.status = QLabel("")
        self.status.setObjectName("hint")

        layout = padded(QVBoxLayout(self))
        title = QLabel("Luci")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(hint("Effetto firmware e parametri: la scrittura "
                              "e' atomica e non disturba la digitazione."))

        layout.addWidget(section("Effetto firmware"))
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.effect = QComboBox()
        for label, _ in EFFECTS:
            self.effect.addItem(label)
        form.addRow("Tipo:", self.effect)

        row = QHBoxLayout()
        self.btn_c1 = QPushButton("Colore 1")
        self.btn_c1.setObjectName("swatch")
        self.btn_c1.clicked.connect(lambda: self._pick(1))
        self.btn_c2 = QPushButton("Colore 2")
        self.btn_c2.setObjectName("swatch")
        self.btn_c2.clicked.connect(lambda: self._pick(2))
        row.addWidget(self.btn_c1)
        row.addWidget(self.btn_c2)
        form.addRow("Colori:", row)
        self._refresh_swatches()

        self.bri, bri_val = self._slider(100)
        form.addRow("Luminosità:", self._labeled(self.bri, bri_val))
        self.speed, speed_val = self._slider(100)
        form.addRow("Velocità:", self._labeled(self.speed, speed_val))

        self.direction = QComboBox()
        for label, _ in DIRECTIONS:
            self.direction.addItem(label)
        form.addRow("Direzione:", self.direction)
        self.rainbow = QCheckBox("Arcobaleno (solo statico)")
        form.addRow("", self.rainbow)
        form_box = QWidget()
        form_box.setLayout(form)
        layout.addWidget(form_box)

        actions = QHBoxLayout()
        apply_btn = QPushButton("Applica")
        apply_btn.setObjectName("accent")
        apply_btn.clicked.connect(self.apply)
        actions.addWidget(apply_btn)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def _slider(self, value):
        from PySide6.QtCore import Qt
        s = QSlider(Qt.Horizontal)
        s.setRange(0, 100)
        s.setValue(value)
        val = QLabel(f"{value}%")
        val.setMinimumWidth(44)
        s.valueChanged.connect(lambda v: val.setText(f"{v}%"))
        return s, val

    @staticmethod
    def _labeled(slider, label):
        row = QHBoxLayout()
        row.addWidget(slider, 1)
        row.addWidget(label)
        box = QWidget()
        box.setLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        return box

    def _pick(self, which):
        color = QColorDialog.getColor(
            self.color1 if which == 1 else self.color2, self)
        if color.isValid():
            if which == 1:
                self.color1 = color
            else:
                self.color2 = color
            self._refresh_swatches()

    def _refresh_swatches(self):
        self.btn_c1.setStyleSheet(
            f"background: {self.color1.name()}; color: white;")
        self.btn_c2.setStyleSheet(
            f"background: {self.color2.name()}; color: white;")

    def _rgb(self, color):
        return (color.red(), color.green(), color.blue())

    def apply(self):
        from drevo_control.oslayer.daemon import pause_enabled
        cmd = EFFECTS[self.effect.currentIndex()][1]
        pkt = C.effect_packet(
            cmd, self._rgb(self.color1),
            color2=self._rgb(self.color2), speed=self.speed.value(),
            brightness=self.bri.value(),
            direction=DIRECTIONS[self.direction.currentIndex()][1],
            rainbow=self.rainbow.isChecked())
        paused = pause_enabled()
        if paused:
            pause_daemon()
        try:
            write_packet(pkt)
        except RuntimeError as e:
            note(self.status, f"Errore: {e}", "error")
            return
        finally:
            if paused:
                resume_daemon()
        note(self.status, "Applicato.", "ok")
