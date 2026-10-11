# SPDX-License-Identifier: GPL-3.0-or-later
"""Pagina Profili: salva/applica/elimina profili luci+tasti."""

from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QVBoxLayout, QWidget)

from drevo_control.gui.widgets import hint, note, padded
from drevo_control.oslayer import profiles as store
from drevo_control.oslayer.apply import apply_profile


class ProfilesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lights = None
        self.keys = None
        self.status = QLabel("I profili applicano luci e tasti insieme.")
        self.status.setObjectName("hint")

        layout = padded(QVBoxLayout(self))
        title = QLabel("Profili")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(hint("Salva e riapplica configurazioni complete "
                              "di luci e tasti."))

        row = QHBoxLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("nome profilo")
        save = QPushButton("Salva stato attuale")
        save.setObjectName("accent")
        save.clicked.connect(self.save_current)
        row.addWidget(self.name, 1)
        row.addWidget(save)
        layout.addLayout(row)

        self.plist = QListWidget()
        layout.addWidget(self.plist, 1)

        row2 = QHBoxLayout()
        apply_btn = QPushButton("Applica selezionato")
        apply_btn.setObjectName("accent")
        apply_btn.clicked.connect(self.apply_selected)
        delete = QPushButton("Elimina")
        delete.clicked.connect(self.delete_selected)
        row2.addWidget(apply_btn)
        row2.addWidget(delete)
        layout.addLayout(row2)
        layout.addWidget(self.status)
        self.reload()

    def set_sources(self, lights, keys):
        self.lights = lights
        self.keys = keys

    def reload(self):
        self.plist.clear()
        self.plist.addItems(store.list_profiles())

    def _lighting_state(self):
        if self.lights is None:
            return {}
        return {"effect": ["static", "breath", "stream", "radar", "mem"][
                    self.lights.effect.currentIndex()],
                "rgb": [self.lights.color1.red(), self.lights.color1.green(),
                        self.lights.color1.blue()],
                "bri": self.lights.bri.value(),
                "speed": self.lights.speed.value()}

    def save_current(self):
        name = self.name.text().strip()
        if not name or self.keys is None:
            note(self.status, "Dai un nome al profilo.", "error")
            return
        profile = self.keys.get_profile(name)
        profile.lighting = self._lighting_state()
        store.save_profile(profile)
        self.name.clear()
        self.reload()
        note(self.status, f"Profilo '{profile.name}' salvato.", "ok")

    def apply_selected(self):
        items = self.plist.selectedItems()
        if not items:
            return
        try:
            ok, msg = apply_profile(store.load_profile(items[0].text()))
        except RuntimeError as e:
            note(self.status, f"Errore: {e}", "error")
            return
        note(self.status, msg if ok else f"Errore: {msg}",
             "ok" if ok else "error")

    def delete_selected(self):
        import os

        from PySide6.QtWidgets import QMessageBox
        items = self.plist.selectedItems()
        if not items:
            return
        answer = QMessageBox.question(
            self, "Elimina profilo",
            f"Eliminare '{items[0].text()}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        for item in items:
            try:
                os.remove(store.profile_path(item.text()))
            except OSError:
                pass
        self.reload()
