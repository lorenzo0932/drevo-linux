# SPDX-License-Identifier: GPL-3.0-or-later
"""Comandi multi-tasto: per-key singolo e colorazione intera tastiera."""

from drevo_control.protocol import commands as C
from drevo_control.protocol.keymap import ALL_IDS, BY_NAME


def key_packets(name_or_id, rgb):
    """Un tasto per nome (UK-ISO) o usage ID diretto."""
    usage = BY_NAME[name_or_id] if isinstance(name_or_id, str) else name_or_id
    return [C.indiv_packet([usage], [tuple(rgb)])]


def kbd_packets(rgb, brightness=100):
    """Tutta la tastiera di un colore: open + gruppi da 5 + close.

    87 tasti -> 18 gruppi (17x5+2), 20 pacchetti totali.
    Il primo gruppo porta i marcatori osservati (byte15=0x53, byte31=0x65).
    """
    rgb = tuple(rgb)
    packets = [C.kbd_open_packet(brightness=brightness)]
    groups = [ALL_IDS[i:i + 5] for i in range(0, len(ALL_IDS), 5)]
    for gi, group in enumerate(groups):
        pkt = C.indiv_packet(group, [rgb] * len(group))
        if gi == 0:
            pkt[15] = 0x53
            pkt[31] = 0x65
        packets.append(pkt)
    packets.append(C.kbd_close_packet())
    return packets
