# Keymap UK-ISO (87 tasti)

`protocol/keymap.py`: nome → HID usage ID dallo standard USB HID
(es. `a` = `0x04`, `enter` = `0x28`, `space` = `0x2C`).
87 usage unici; FN e' hardware-only (senza usage, mostrato disabilitato).

Verifica: spot-check hardware (`enter` rosso) + suite. Scritture verso
key-id inesistenti sono ignorate dal device (innocue).
