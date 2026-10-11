# SPDX-License-Identifier: GPL-3.0-or-later
"""Test GUI offscreen: pagine, tema, chiavi, profili (no hardware)."""

import contextlib
import os
import tempfile
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()

from PySide6.QtWidgets import QApplication

import drevo_control.gui.page_lights as pl
import drevo_control.gui.page_perkey as pp
from drevo_control.gui import app as appmod
from drevo_control.gui import theme as T

qt = QApplication([])
win = appmod.MainWindow()
assert win.nav.count() == 5
for row in range(5):
    win.nav.setCurrentRow(row)
    assert win.stack.currentIndex() == row

# tema chiaro/scuro/auto
T.apply_theme(win)
T.apply_theme(win, "dark")
assert "242424" in win.styleSheet()
T.apply_theme(win, "light")
assert "fafafa" in win.styleSheet()
T.save_mode("auto")
assert T.saved_mode() == "auto"

# luci: apply mockato
lights = win.pages[0][1]
sent = []
with mock.patch.object(pl, "write_packet",
                       side_effect=lambda p: sent.append(p) or True), \
     mock.patch.object(pl, "pause_daemon"), \
     mock.patch.object(pl, "resume_daemon"):
    lights.apply()
assert len(sent) == 1 and sent[0][:7] == [6, 0xBE, 0x15, 0, 1, 1, 1]
assert lights.status.text() == "Applicato."
assert lights.bri.value() == 100

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


@contextlib.contextmanager
def fake_open():
    yield FakeDev()


fake_holder = {}


@contextlib.contextmanager
def fake_open2():
    dev = FakeDev()
    fake_holder["dev"] = dev
    yield dev


with mock.patch.object(pp, "open_control", return_value=fake_open2()), \
     mock.patch.object(pp, "hid_writer_lock") as lock, \
     mock.patch.object(pp, "pause_daemon"), \
     mock.patch.object(pp, "resume_daemon"):
    lock.return_value.__enter__.return_value = True
    perkey.apply()

dev = fake_holder["dev"]
assert len(dev.written) == 1 and dev.written[0][7] == 0x28
assert "2 tasti" in perkey.status.text()

# tasti/macro: stato profilo
keys = win.pages[2][1]
keys.remap_src.setCurrentText("capslock")
keys.remap_dst.setCurrentText("esc")
keys._add_remap()
keys.macro_key.setCurrentText("f9")
keys.macro_seq.setText("c i a o")
keys._add_macro()
keys.game_on.setChecked(True)
prof = keys.get_profile("t")
assert prof.remaps == {"capslock": "esc"}
assert prof.macros == {"f9": ["c", "i", "a", "o"]}
assert prof.game_mode and prof.game_toggle_key == "f12"
keys2 = win.pages[2][1].__class__()
keys2.load_profile_state(prof)
assert keys2.get_profile("x").remaps == {"capslock": "esc"}

# profili: salva/applica mockato
profiles = win.pages[3][1]
profiles.name.setText("guitest")
profiles.save_current()
from drevo_control.oslayer import profiles as store

assert "guitest" in store.list_profiles()
profiles.plist.setCurrentRow(0)
applied = {}


def fake_apply(profile, pause=True):
    applied["p"] = profile
    return True, "ok"


import drevo_control.gui.page_profiles as pg

with mock.patch.object(pg, "apply_profile", side_effect=fake_apply):
    profiles.apply_selected()
assert applied["p"].name == "guitest"
assert "ok" in profiles.status.text()

# impostazioni: cambio tema persiste, niente path locali in UI
settings = win.pages[4][1]
settings.theme.setCurrentText("scuro")
assert T.saved_mode() == "dark"
settings.theme.setCurrentText("auto")
labels = settings.findChildren(type(settings.status))
for lab in labels:
    assert "/home/" not in lab.text() and "/tmp/" not in lab.text(), lab.text()
print("gui ok")
