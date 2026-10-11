"""Mappa nome -> HID usage ID per ISO-UK 87 tasti (TKL).

Usage ID dallo standard USB HID (tastiera): es. `a` = 0x04. Il tasto FN
e' gestito in hardware e non ha usage. Verificabile con evtest.
"""

# (nome, usage)
KEYS = [
    # riga funzione + sys
    ("esc", 0x29), ("f1", 0x3A), ("f2", 0x3B), ("f3", 0x3C),
    ("f4", 0x3D), ("f5", 0x3E), ("f6", 0x3F), ("f7", 0x40),
    ("f8", 0x41), ("f9", 0x42), ("f10", 0x43), ("f11", 0x44),
    ("f12", 0x45), ("ps", 0x46), ("sl", 0x47), ("pb", 0x48),
    # riga cifre
    ("grave", 0x35), ("1", 0x1E), ("2", 0x1F), ("3", 0x20),
    ("4", 0x21), ("5", 0x22), ("6", 0x23), ("7", 0x24),
    ("8", 0x25), ("9", 0x26), ("0", 0x27), ("minus", 0x2D),
    ("equal", 0x2E), ("backs", 0x2A),
    # riga QWERTY
    ("tab", 0x2B), ("q", 0x14), ("w", 0x1A), ("e", 0x08),
    ("r", 0x15), ("t", 0x17), ("y", 0x1C), ("u", 0x18),
    ("i", 0x0C), ("o", 0x12), ("p", 0x13), ("lbrace", 0x2F),
    ("rbrace", 0x30),
    # riga ASDF (UK: '@' su 0x34, '#~' ISO su 0x32)
    ("caps", 0x39), ("a", 0x04), ("s", 0x16), ("d", 0x07),
    ("f", 0x09), ("g", 0x0A), ("h", 0x0B), ("j", 0x0D),
    ("k", 0x0E), ("l", 0x0F), ("scolon", 0x33), ("quote", 0x34),
    ("hash", 0x32), ("enter", 0x28),
    # riga ZXCV (UK: tasto ISO 0x64 a sinistra di Z)
    ("lshift", 0xE1), ("iso", 0x64), ("z", 0x1D), ("x", 0x1B),
    ("c", 0x06), ("v", 0x19), ("b", 0x05), ("n", 0x11),
    ("m", 0x10), ("comma", 0x36), ("dot", 0x37), ("slash", 0x38),
    ("rshift", 0xE5),
    # riga spazio (FN = hardware, senza usage)
    ("lctrl", 0xE0), ("win", 0xE3), ("lalt", 0xE2), ("space", 0x2C),
    ("ralt", 0xE6), ("menu", 0x65), ("rctrl", 0xE4),
    # navigazione + frecce
    ("ins", 0x49), ("home", 0x4A), ("pup", 0x4B), ("del", 0x4C),
    ("end", 0x4D), ("pdown", 0x4E),
    ("up", 0x52), ("left", 0x50), ("down", 0x51), ("right", 0x4F),
]

BY_NAME = dict(KEYS)
ALL_IDS = [usage for _, usage in KEYS]

# 87 usage unici da standard HID; FN e' hardware-only (senza usage).
# Scritture a key-id inesistenti sono ignorate dal device.
assert len(ALL_IDS) == 87, len(ALL_IDS)
assert len(set(ALL_IDS)) == len(ALL_IDS)
