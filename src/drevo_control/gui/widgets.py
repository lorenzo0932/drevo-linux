"""Widget condivisi: hint, stati vuoti, note di stato."""

from PySide6.QtWidgets import QLabel


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
