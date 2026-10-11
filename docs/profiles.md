# Profili unificati

Un profilo JSON (`~/.config/drevo-control/profiles/*.json`) unisce:

- `lighting`: `{effect, rgb, bri, speed}` → pacchetto HID;
- `remaps` / `macros` / `game_mode` → config keyd.

Codice: `oslayer/profiles.py` (save/load/list), apply in
`oslayer/apply.py::apply_profile`: pausa daemon → scrittura HID sotto
lock → install keyd + restart → ripresa daemon. Il daemon resta
proprietario delle luci nel tempo (le riapplica ai suoi eventi); i tasti
restano a keyd.
