"""Pagina Luci: effetto firmware + parametri, scrittura sotto pausa daemon."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QCheckBox, QColorDialog, QComboBox,
                               QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QVBoxLayout, QWidget)

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

        layout = QVBoxLayout(self)
        title = QLabel("Luci")
        title.setObjectName("title")
        layout.addWidget(title)

        box = QGroupBox("Effetto")
        form = QFormLayout(box)
        self.effect = QComboBox()
        for label, _ in EFFECTS:
            self.effect.addItem(label)
        form.addRow("Effetto:", self.effect)

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

        self.bri = self._slider(100)
        form.addRow("Luminosità (%):", self.bri)
        self.speed = self._slider(100)
        form.addRow("Velocità (%):", self.speed)

        self.direction = QComboBox()
        for label, _ in DIRECTIONS:
            self.direction.addItem(label)
        form.addRow("Direzione:", self.direction)
        self.rainbow = QCheckBox("Arcobaleno (solo statico)")
        form.addRow("", self.rainbow)
        layout.addWidget(box)

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
        return s

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
        cmd = EFFECTS[self.effect.currentIndex()][1]
        pkt = C.effect_packet(
            cmd, self._rgb(self.color1),
            color2=self._rgb(self.color2), speed=self.speed.value(),
            brightness=self.bri.value(),
            direction=DIRECTIONS[self.direction.currentIndex()][1],
            rainbow=self.rainbow.isChecked())
        pause_daemon()
        try:
            write_packet(pkt)
        finally:
            resume_daemon()
        self.status.setText("Applicato.")
