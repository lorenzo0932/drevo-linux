"""Test dei builder contro i byte catturati via usbmon (no hardware)."""

from drevo_control.protocol import commands as C

# STATIC (10,20,30) bri=100 — cap_static
assert C.effect_packet(C.CMD_STATIC, (10, 20, 30))[12:15] == [10, 20, 30]
assert C.effect_packet(C.CMD_STATIC, (10, 20, 30))[7:9] == [9, 6]
assert C.effect_packet(C.CMD_STATIC, (10, 20, 30))[15:19] == [0, 255, 0, 0]

# BREATH (0x11,0x22,0x33)/(0x44,0x55,0x66) bri=80 speed=50
p = C.effect_packet(C.CMD_BREATH, (0x11, 0x22, 0x33),
                    color2=(0x44, 0x55, 0x66), speed=50, brightness=80)
assert p[:12] == [6, 0xBE, 0x15, 0, 1, 1, 2, 4, 5, 0, 0, 0]
assert p[12:19] == [0x11, 0x22, 0x33, 0, 0x44, 0x55, 0x66]

# STREAM bri=70 speed=30 dir=w(1)
p = C.effect_packet(C.CMD_STREAM, (0x71, 0x72, 0x73),
                    color2=(0x74, 0x75, 0x76), speed=30, brightness=70,
                    direction=1)
assert p[:12] == [6, 0xBE, 0x15, 0, 1, 1, 3, 3, 4, 1, 0, 0]
assert p[12:19] == [0x71, 0x72, 0x73, 0, 0x74, 0x75, 0x76]

# RADAR bri=60 speed=40 dir=1
p = C.effect_packet(C.CMD_RADAR, (0xA1, 0xA2, 0xA3),
                    color2=(0xA4, 0xA5, 0xA6), speed=40, brightness=60,
                    direction=1)
assert p[:12] == [6, 0xBE, 0x15, 0, 1, 1, 0x10, 4, 4, 1, 0, 0]

# MEM bri=90: byte7 resta 0x00, byte8=5
p = C.effect_packet(C.CMD_MEM, (0xC1, 0xC2, 0xC3),
                    color2=(0xC4, 0xC5, 0xC6), brightness=90)
assert p[:12] == [6, 0xBE, 0x15, 0, 1, 1, 0x0D, 0, 5, 0, 0, 0]
assert p[12:19] == [0xC1, 0xC2, 0xC3, 0, 0xC4, 0xC5, 0xC6]

# KEY1: tasto 0x04 -> (05,06,07), 32B
p = C.indiv_packet([0x04], [(5, 6, 7)])
assert len(p) == 32
assert p[:12] == [6, 0xBE, 0x19, 0, 1, 1, 0x0E, 4, 0, 0, 0, 0]
assert p[12:15] == [5, 6, 7]

# KEYSET 3 tasti -> 24B
p = C.indiv_packet([0x04, 0x05, 0x06],
                   [(1, 1, 1), (2, 2, 2), (3, 3, 3)])
assert len(p) == 24
assert p[:12] == [6, 0xBE, 0x19, 0, 1, 1, 0x0E, 4, 5, 6, 0, 0]
assert p[12:24] == [1, 1, 1, 0, 2, 2, 2, 0, 3, 3, 3, 0]

# kbd open/close
assert C.kbd_open_packet()[:13] == \
    [6, 0xBE, 0x15, 0, 1, 1, 0x0F, 0, 6, 0, 0, 0, 0xFF]
assert C.kbd_close_packet()[:17] == \
    [6, 0xBE, 0x15, 0, 2, 1, 1, 5, 9, 0, 0, 0, 0xFF, 0, 0, 0, 0xFF]

print("builder ok: tutti i byte corrispondono alle catture")
