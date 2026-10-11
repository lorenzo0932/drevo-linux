#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render offscreen di ogni pagina GUI in PNG per review visiva."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from drevo_control.gui.app import MainWindow

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/opencode/shots"
os.makedirs(OUT, exist_ok=True)

app = QApplication([])
if len(sys.argv) > 2:
    from drevo_control.gui import theme as T
    T.save_mode(sys.argv[2])
win = MainWindow()
win.resize(1080, 700)
win.show()
for row in range(win.nav.count()):
    win.nav.setCurrentRow(row)
    label = win.nav.item(row).text().replace(" ", "_")
    shot = win.grab()
    path = os.path.join(OUT, f"{row:02d}_{label}.png")
    shot.save(path)
    print("salvato", path)
win.close()
