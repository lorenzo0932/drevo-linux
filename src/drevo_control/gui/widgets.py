# SPDX-License-Identifier: GPL-3.0-or-later
"""Widget condivisi: hint, stati vuoti, note di stato, spaziature."""

from PySide6.QtWidgets import QLabel


def padded(layout, margin=16, spacing=10):
    """Respiro uniforme per layout di pagina e gruppi."""
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(spacing)
    return layout


def section(text):
    label = QLabel(text)
    label.setObjectName("section")
    return label


def hint(text):
    label = QLabel(text)
    label.setObjectName("hint")
    label.setWordWrap(True)
    return label


def note(label, text, kind="info"):
    """Messaggio di stato colorato: kind in info/ok/error."""
    label.setText(text)
    label.setProperty("kind", kind)
    label.style().unpolish(label)
    label.style().polish(label)


def toggle_empty(note_label, list_widget, empty_text="Nessun elemento."):
    """Mostra una riga guida quando la lista e' vuota."""
    if list_widget.count() == 0:
        note_label.setText(empty_text)
        note_label.setVisible(True)
    else:
        note_label.setVisible(False)
