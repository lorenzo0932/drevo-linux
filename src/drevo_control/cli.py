"""CLI: drevo-control <effect|key|kbd> ..."""

import argparse

from drevo_control.protocol import board as B
from drevo_control.protocol import commands as C
from drevo_control.protocol.device import open_control, write_packet
from drevo_control.lock import hid_writer_lock

DIRECTIONS = {"e": 0, "w": 1, "s": 2, "n": 3}


def _rgb(args):
    return (args.r, args.g, args.b)


def _cmd_effect(args):
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


def _cmd_key(args):
    for pkt in B.key_packets(args.key, _rgb(args)):
        write_packet(pkt)
    print("ok")


def _cmd_kbd(args):
    with hid_writer_lock() as locked:
        if not locked:
            raise RuntimeError("writer HID occupato (timeout lock)")
        with open_control() as dev:
            for pkt in B.kbd_packets(_rgb(args), brightness=args.bri):
                dev.write(pkt)
    print("ok")


def _cmd_profile_apply(args):
    import subprocess

    from drevo_control.oslayer import render_keyd
    from drevo_control.oslayer.profiles import load_profile

    profile = load_profile(args.name)
    # 1. pausa daemon ambilight (evita scritture concorrenti)
    subprocess.run(["systemctl", "--user", "stop",
                    "ambilight-keyboard.service"], check=False)
    try:
        # 2. luci via HID (sotto lock)
        lighting = profile.lighting or {}
        effect = lighting.get("effect", "static")
        rgb = tuple(lighting.get("rgb", (255, 255, 255)))
        cmd = {"static": C.CMD_STATIC, "breath": C.CMD_BREATH,
               "stream": C.CMD_STREAM, "radar": C.CMD_RADAR,
               "mem": C.CMD_MEM}[effect]
        pkt = C.effect_packet(cmd, rgb,
                              brightness=lighting.get("bri", 100),
                              speed=lighting.get("speed", 100))
        write_packet(pkt)
        # 3. tasti via keyd
        cfg = render_keyd(profile)
        with open("/tmp/opencode/keyd-profile.conf", "w") as f:
            f.write(cfg)
        subprocess.run(["sudo", "install", "-m", "644",
                        "/tmp/opencode/keyd-profile.conf",
                        "/etc/keyd/keyd.conf"], check=True)
        # keyd non supporta reload: restart se il reload fallisce
        r = subprocess.run(["sudo", "systemctl", "reload", "keyd"])
        if r.returncode != 0:
            subprocess.run(["sudo", "systemctl", "restart", "keyd"],
                           check=True)
    finally:
        # 4. il daemon riparte e riprende le luci (i tasti restano a keyd)
        subprocess.run(["systemctl", "--user", "start",
                        "ambilight-keyboard.service"], check=False)
    print("ok")


def main(argv=None):
    p = argparse.ArgumentParser(prog="drevo-control")
    sub = p.add_subparsers(dest="target", required=True)

    pe = sub.add_parser("effect",
                        help="static|breath|stream|radar|mem R G B")
    pe.add_argument("effect", choices=["static", "breath", "stream",
                                       "radar", "mem"])
    pe.add_argument("r", type=int)
    pe.add_argument("g", type=int)
    pe.add_argument("b", type=int)
    pe.add_argument("--bri", type=int, default=100)
    pe.add_argument("--speed", type=int, default=100)
    pe.add_argument("--direction", choices=DIRECTIONS, default="e")
    pe.add_argument("--rainbow", action="store_true")
    pe.add_argument("--color2", default="255,0,0")
    pe.set_defaults(func=_cmd_effect)

    pk = sub.add_parser("key", help="un tasto: key NOME R G B")
    pk.add_argument("key")
    pk.add_argument("r", type=int)
    pk.add_argument("g", type=int)
    pk.add_argument("b", type=int)
    pk.set_defaults(func=_cmd_key)

    pb = sub.add_parser("kbd", help="tutta la tastiera di un colore")
    pb.add_argument("r", type=int)
    pb.add_argument("g", type=int)
    pb.add_argument("b", type=int)
    pb.add_argument("--bri", type=int, default=100)
    pb.set_defaults(func=_cmd_kbd)

    pp = sub.add_parser("profile", help="profili unificati luci+tasti")
    pp.add_argument("action", choices=["apply"])
    pp.add_argument("name")
    pp.set_defaults(func=_cmd_profile_apply)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
