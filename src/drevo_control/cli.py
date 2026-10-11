"""CLI: drevo-control static|breath|stream|radar|mem R G B [opzioni]."""

import argparse

from drevo_control.protocol import commands as C
from drevo_control.protocol.device import write_packet

DIRECTIONS = {"e": 0, "w": 1, "s": 2, "n": 3}


def _rgb(args):
    return (args.r, args.g, args.b)


def main(argv=None):
    p = argparse.ArgumentParser(prog="drevo-control")
    p.add_argument("effect", choices=["static", "breath", "stream",
                                      "radar", "mem"])
    p.add_argument("r", type=int)
    p.add_argument("g", type=int)
    p.add_argument("b", type=int)
    p.add_argument("--bri", type=int, default=100)
    p.add_argument("--speed", type=int, default=100)
    p.add_argument("--direction", choices=DIRECTIONS, default="e")
    p.add_argument("--rainbow", action="store_true")
    p.add_argument("--color2", default="255,0,0")
    args = p.parse_args(argv)

    color2 = tuple(int(x) for x in args.color2.split(","))
    cmd = {"static": C.CMD_STATIC, "breath": C.CMD_BREATH,
           "stream": C.CMD_STREAM, "radar": C.CMD_RADAR,
           "mem": C.CMD_MEM}[args.effect]
    pkt = C.effect_packet(cmd, _rgb(args), color2=color2, speed=args.speed,
                          brightness=args.bri,
                          direction=DIRECTIONS[args.direction],
                          rainbow=args.rainbow)
    write_packet(pkt)
    print("ok")


if __name__ == "__main__":
    main()
