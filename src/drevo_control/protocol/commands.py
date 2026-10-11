"""Costruttori di pacchetti per 0416:a0f8, da osservazione usbmon propria.

Formati osservati (control OUT 32B max su iface 1, EP3):
- effetti:  prefisso [06 be 15 00 01 01 CMD] + speed + bri + dir + colori
- per-key: prefisso [06 be 19 00 01 01 0e] + fino a 5 key-id + RGB+00 a tasto
"""

CMD_STATIC = 0x01
CMD_BREATH = 0x02
CMD_STREAM = 0x03
CMD_MEM = 0x0D
CMD_RADAR = 0x10
CMD_INDIV = 0x0E
CMD_CUSTOM_MODE = 0x0F  # pacchetto di apertura modalita' per-key (kbd)

EFFECT_PREFIX = [0x06, 0xBE, 0x15, 0x00, 0x01, 0x01]
INDIV_PREFIX = [0x06, 0xBE, 0x19, 0x00, 0x01, 0x01, CMD_INDIV]


def _scale_speed(pct):
    return int(round(pct / 100 * 9))


def _scale_brightness(pct):
    return int(round(pct / 100 * 6))


def effect_packet(cmd, color1, color2=(0xFF, 0, 0), speed=100,
                  brightness=100, direction=0, rainbow=False):
    """Pacchetto effetto 32B. CMD_STATIC ignora direction; CMD_MEM ignora
    speed (byte 7 resta 0x00) e rainbow."""
    pkt = [0] * 32
    pkt[:7] = EFFECT_PREFIX + [cmd]
    pkt[8] = _scale_brightness(brightness)
    pkt[12:15] = list(color1)
    pkt[16:19] = list(color2)
    if cmd == CMD_MEM:
        return pkt
    pkt[7] = _scale_speed(speed)
    pkt[9] = direction
    pkt[15] = 1 if rainbow else 0
    return pkt


def indiv_packet(key_ids, colors):
    """Pacchetto per-key, 1-5 tasti. key_ids: HID usage ID.

    Lunghezze OSSERVATE su usbmon (stabili tra run, meccanismo lato
    hidraw non indagato): {1: 32, 2: 28, 3: 24, 4: 28, 5: 32}."""
    if not 1 <= len(key_ids) <= 5 or len(key_ids) != len(colors):
        raise ValueError("1-5 tasti con altrettanti colori")
    n = len(key_ids)
    pkt = [0] * {1: 32, 2: 28, 3: 24, 4: 28, 5: 32}[n]
    pkt[:7] = INDIV_PREFIX
    pkt[7:7 + 5] = list(key_ids) + [0] * (5 - n)
    for i, color in enumerate(colors):
        pkt[12 + 4 * i:12 + 4 * i + 3] = list(color)
    return pkt


def kbd_open_packet(brightness=100):
    pkt = [0] * 32
    pkt[:7] = EFFECT_PREFIX + [CMD_CUSTOM_MODE]
    pkt[8] = _scale_brightness(brightness)
    pkt[12] = 0xFF
    return pkt


def kbd_close_packet():
    pkt = [0] * 32
    pkt[:7] = [0x06, 0xBE, 0x15, 0x00, 0x02, 0x01, 0x01]
    pkt[7] = 0x05
    pkt[8] = 0x09
    pkt[12] = 0xFF
    pkt[16] = 0xFF
    return pkt
