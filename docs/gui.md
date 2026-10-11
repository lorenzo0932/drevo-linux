# GUI

Qt6 (PySide6), stile Adwaita-like generato (`gui/theme.py`: palette
chiaro/scuro + QPalette applicata per gli sfondi dei viewport).

## Pagine (`gui/page_*.py`)

- **Luci**: effetto, 2 colori, luminosità/velocità, direzione, rainbow.
- **Per-key**: tastiera ISO disegnata e cliccabile (`gui/keyboard_view.py`,
  keymap 1:1 coi nomi, FN disabilitato), assegnazioni + tinta board.
- **Tasti e Macro**: remap, macro con timeout spiegato, game-mode;
  anteprima config e installazione con ripristino.
- **Profili**: salva stato attuale, applica, elimina (con conferma).
- **Impostazioni**: tema auto/chiaro/scuro, pausa daemon, keyd (stato,
  installa da sorgenti, rimuovi), regola udev, info.

## UX applicata

Sezioni piatte stile Impostazioni GNOME (niente box coi titoli),
sottotitoli esplicativi, placeholder nelle combo, empty-state nelle
liste, note ok/error colorate, barra di stato live (Tastiera/keyd),
finestra responsive (minimo 700×500, tastiera con font che scala e nav
che si impila sotto i 700px), dialoghi di conferma per azioni
distruttive, nessun path locale nei testi.

## Verifica visiva

`tools/gui_shots.py [dir] [light|dark]` renderizza ogni pagina offscreen
in PNG; revisione a ogni change. Audit completi in entrambi i temi prima
di ogni milestone GUI. Test: `tests/test_gui.py` (costruzione, navigazione,
apply mockati, tema, stati).
