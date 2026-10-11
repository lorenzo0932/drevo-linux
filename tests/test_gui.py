"""Smoke test GUI offscreen: costruzione, navigazione, apply luci mockato."""

import os
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from drevo_control.gui import app as appmod

qt = QApplication([])
win = appmod.MainWindow()
assert win.nav.count() == 4
for row in range(4):
    win.nav.setCurrentRow(row)
    assert win.stack.currentIndex() == row

lights = win.pages[0][1]
sent = []
import drevo_control.gui.page_lights as pl

with mock.patch.object(pl, "write_packet",
                       side_effect=lambda p: sent.append(p) or True), \
     mock.patch.object(pl, "pause_daemon"), \
     mock.patch.object(pl, "resume_daemon"):
    lights.apply()

assert len(sent) == 1 and sent[0][:7] == [6, 0xBE, 0x15, 0, 1, 1, 1]
assert lights.status.text() == "Applicato."
print("gui ok")
