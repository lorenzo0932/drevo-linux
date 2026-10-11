#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Genera UNA scrittura di riferimento sul device (per catture usbmon).

Uso: capture_ref.py breath|stream|radar|key1|keyset
Dipende dal pacchetto `dtv2` installato: serve solo a produrre traffico
osservabile, non viene copiato nel repo.
"""

import sys

from dtv2 import dtv2


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    kbd = dtv2()
    if which == "breath":
        kbd.breath((0x11, 0x22, 0x33), color2=(0x44, 0x55, 0x66),
                   brightness=80, speed=50)
    elif which == "stream":
        kbd.stream((0x71, 0x72, 0x73), color2=(0x74, 0x75, 0x76),
                   brightness=70, speed=30, direction="w")
    elif which == "radar":
        kbd.radar((0xA1, 0xA2, 0xA3), color2=(0xA4, 0xA5, 0xA6),
                  brightness=60, speed=40, direction=1)
    elif which == "key1":
        kbd.key("a", (0x05, 0x06, 0x07))
    elif which == "keyset":
        kbd.key_set(["a", "b", "c"], [(0x01, 0x01, 0x01),
                                      (0x02, 0x02, 0x02),
                                      (0x03, 0x03, 0x03)])
    elif which == "mem":
        kbd.mem_effect((0xC1, 0xC2, 0xC3), color2=(0xC4, 0xC5, 0xC6),
                       brightness=90)
    elif which == "kbd":
        kbd.kbd((0xD1, 0xD2, 0xD3))
    else:
        sys.stderr.write(
            "uso: capture_ref.py breath|stream|radar|key1|keyset|mem|kbd\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
