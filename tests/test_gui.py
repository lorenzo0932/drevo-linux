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

# per-key: aggiunta + apply con device mockato
perkey = win.pages[1][1]
perkey.keysel.setCurrentText("enter")
perkey._add()
perkey.keysel.setCurrentText("a")
perkey._add()
assert len(perkey.pending) == 2


class FakeDev:
    def __init__(self):
        self.written = []

    def write(self, pkt):
        self.written.append(pkt)
        return len(pkt)

    def close(self):
        pass


import contextlib

fake = FakeDev()


@contextlib.contextmanager
def fake_open():
    yield fake


with mock.patch.object(pl, "pause_daemon"), \
     mock.patch.object(pl, "resume_daemon"):
    import drevo_control.gui.page_perkey as pp
    with mock.patch.object(pp, "open_control", return_value=fake_open()), \
         mock.patch.object(pp, "hid_writer_lock") as lock:
        lock.return_value.__enter__.return_value = True
        perkey.apply()

assert len(fake.written) == 1 and fake.written[0][7] == 0x28
assert "2 tasti" in perkey.status.text()
print("gui ok")
