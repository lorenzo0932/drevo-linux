"""Pagina Tasti e Macro: remap, macro, game-mode -> config keyd."""

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QSpinBox, QTextEdit, QVBoxLayout,
                               QWidget)

from drevo_control.gui.widgets import hint, note, padded, toggle_empty
from drevo_control.oslayer import RemapProfile
from drevo_control.oslayer.apply import install_keyd_conf, keyd_active

KEYD_KEYS = ([chr(c) for c in range(ord("a"), ord("z") + 1)]
             + [str(d) for d in range(10)]
             + ["esc", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
                "f9", "f10", "f11", "f12", "capslock", "tab", "space",
                "enter", "backspace", "delete", "insert", "home", "end",
                "pageup", "pagedown", "up", "down", "left", "right",
                "leftmeta", "rightmeta", "leftalt", "leftctrl", "leftshift",
                "rightctrl", "print", "scrolllock", "pause"])


def _key_combo():
    combo = QComboBox()
    combo.setEditable(True)
    combo.addItems(KEYD_KEYS)
    combo.lineEdit().setPlaceholderText("tasto…")
    combo.setCurrentText("")
    return combo


class KeysPage(QWidget):
    def __init__(self):
        super().__init__()
        self.status = QLabel("")
        self.status.setObjectName("hint")
        self._backup_conf = None

        layout = padded(QVBoxLayout(self))
        title = QLabel("Tasti e Macro")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(hint("Rimappature e macro via keyd, game-mode con "
                              "toggle. Installa quando hai finito."))

        self.remap_list = QListWidget()
        box = QGroupBox("Rimappature")
        form = padded(QVBoxLayout(box))
        row = QHBoxLayout()
        self.remap_src = _key_combo()
        self.remap_dst = _key_combo()
        add = QPushButton("Aggiungi")
        add.clicked.connect(self._add_remap)
        row.addWidget(self.remap_src, 1)
        row.addWidget(QLabel("→"))
        row.addWidget(self.remap_dst, 1)
        row.addWidget(add)
        form.addLayout(row)
        form.addWidget(self.remap_list)
        self.remap_empty = hint("")
        form.addWidget(self.remap_empty)
        rm = QPushButton("Rimuovi selezionato")
        rm.clicked.connect(lambda: self._remove_sel(self.remap_list,
                                                    self._remaps))
        form.addWidget(rm)
        layout.addWidget(box)
        self._remaps = {}

        self.macro_list = QListWidget()
        box2 = QGroupBox("Macro")
        form2 = padded(QVBoxLayout(box2))
        row2 = QHBoxLayout()
        self.macro_key = _key_combo()
        self.macro_seq = QLineEdit()
        self.macro_seq.setPlaceholderText("sequenza separata da spazi")
        self.macro_timeout = QSpinBox()
        self.macro_timeout.setRange(10, 2000)
        self.macro_timeout.setValue(100)
        self.macro_timeout.setSuffix(" ms")
        add2 = QPushButton("Aggiungi")
        add2.clicked.connect(self._add_macro)
        row2.addWidget(self.macro_key)
        row2.addWidget(self.macro_seq, 1)
        row2.addWidget(self.macro_timeout)
        row2.addWidget(add2)
        form2.addLayout(row2)
        form2.addWidget(self.macro_list)
        self.macro_empty = hint("")
        form2.addWidget(self.macro_empty)
        rm2 = QPushButton("Rimuovi selezionato")
        rm2.clicked.connect(lambda: self._remove_sel(self.macro_list,
                                                     self._macros))
        form2.addWidget(rm2)
        layout.addWidget(box2)
        self._macros = {}

        box3 = QGroupBox("Game mode")
        form3 = padded(QHBoxLayout(box3))
        self.game_on = QCheckBox("Attiva game mode (Win disabilitati)")
        self.game_toggle = _key_combo()
        self.game_toggle.setCurrentText("f12")
        form3.addWidget(self.game_on)
        form3.addWidget(QLabel("Toggle:"))
        form3.addWidget(self.game_toggle)
        layout.addWidget(box3)

        actions = QHBoxLayout()
        preview = QPushButton("Anteprima config")
        preview.clicked.connect(self._preview)
        install = QPushButton("Installa in keyd")
        install.setObjectName("accent")
        install.clicked.connect(self.install)
        self.restore_btn = QPushButton("Ripristina precedente")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self._restore)
        actions.addWidget(preview)
        actions.addWidget(install)
        actions.addWidget(self.restore_btn)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)
        self._reload_lists()

    # -- stato ---------------------------------------------------------
    def get_profile(self, name="bozza"):
        return RemapProfile(
            name=name,
            remaps=dict(self._remaps),
            macros=dict(self._macros),
            macro_timeout_ms=self.macro_timeout.value(),
            game_mode=self.game_on.isChecked(),
            game_toggle_key=self.game_toggle.currentText().strip())

    def load_profile_state(self, profile):
        self._remaps = dict(profile.remaps)
        self._macros = dict(profile.macros)
        self.macro_timeout.setValue(profile.macro_timeout_ms)
        self.game_on.setChecked(profile.game_mode)
        self.game_toggle.setCurrentText(profile.game_toggle_key)
        self._reload_lists()

    def _reload_lists(self):
        self.remap_list.clear()
        for s, d in sorted(self._remaps.items()):
            self.remap_list.addItem(f"{s} → {d}")
        toggle_empty(self.remap_empty, self.remap_list,
                     "Nessuna rimappatura.")
        self.macro_list.clear()
        for k, seq in sorted(self._macros.items()):
            self.macro_list.addItem(f"{k} = {' '.join(seq)}")
        toggle_empty(self.macro_empty, self.macro_list, "Nessuna macro.")

    # -- editing -------------------------------------------------------
    def _add_remap(self):
        s = self.remap_src.currentText().strip()
        d = self.remap_dst.currentText().strip()
        if s and d:
            self._remaps[s] = d
            self._reload_lists()

    def _add_macro(self):
        k = self.macro_key.currentText().strip()
        seq = self.macro_seq.text().split()
        if k and seq:
            self._macros[k] = seq
            self.macro_seq.clear()
            self._reload_lists()

    def _remove_sel(self, widget, store):
        for item in widget.selectedItems():
            store.pop(item.text().split(" ")[0], None)
        self._reload_lists()

    # -- keyd ----------------------------------------------------------
    def _preview(self):
        from drevo_control.oslayer import render_keyd
        dlg = QDialog(self)
        dlg.setWindowTitle("Anteprima keyd.conf")
        dlg.resize(520, 380)
        lay = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(render_keyd(self.get_profile()))
        lay.addWidget(text)
        dlg.exec()

    def install(self):
        import subprocess

        if not keyd_active():
            note(self.status, "keyd non attivo: installalo da Impostazioni.",
                 "error")
            return
        cur = subprocess.run(["sudo", "-n", "cat", "/etc/keyd/keyd.conf"],
                             capture_output=True, text=True)
        self._backup_conf = cur.stdout if cur.returncode == 0 else None
        ok, msg = install_keyd_conf(self.get_profile())
        note(self.status, msg, "ok" if ok else "error")
        self.restore_btn.setEnabled(ok and self._backup_conf is not None)

    def _restore(self):
        import subprocess

        if self._backup_conf is None:
            return
        with open("/tmp/opencode/keyd-restore.conf", "w") as f:
            f.write(self._backup_conf)
        subprocess.run(["sudo", "-n", "install", "-m", "644",
                        "/tmp/opencode/keyd-restore.conf",
                        "/etc/keyd/keyd.conf"])
        subprocess.run(["sudo", "-n", "systemctl", "restart", "keyd"])
        note(self.status, "Config precedente ripristinata.", "ok")
        self.restore_btn.setEnabled(False)
