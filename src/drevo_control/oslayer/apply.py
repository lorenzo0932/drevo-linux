"""Apply unificato luci+tasti, riusato da CLI e GUI."""

import os
import shutil
import subprocess

from drevo_control.oslayer import RemapProfile, render_keyd
from drevo_control.oslayer.daemon import pause_daemon, resume_daemon
from drevo_control.protocol import commands as C
from drevo_control.protocol.device import write_packet

EFFECT_CMDS = {"static": C.CMD_STATIC, "breath": C.CMD_BREATH,
               "stream": C.CMD_STREAM, "radar": C.CMD_RADAR,
               "mem": C.CMD_MEM}


def lighting_packet(lighting):
    lighting = lighting or {}
    return C.effect_packet(
        EFFECT_CMDS.get(lighting.get("effect", "static"), C.CMD_STATIC),
        tuple(lighting.get("rgb", (255, 255, 255))),
        brightness=lighting.get("bri", 100),
        speed=lighting.get("speed", 100))


def _escalated(*args):
    """Esegue con sudo -n, fallback pkexec se c'e' un display."""
    r = subprocess.run(["sudo", "-n", *args], capture_output=True, text=True)
    if r.returncode == 0:
        return r
    if shutil.which("pkexec") and (os.environ.get("DISPLAY")
                                   or os.environ.get("WAYLAND_DISPLAY")):
        return subprocess.run(["pkexec", *args], capture_output=True,
                              text=True)
    return r


def apply_lighting(lighting, pause=None):
    """Scrive il pacchetto luci (pausa daemon salvo impostazione)."""
    from drevo_control.oslayer.daemon import pause_enabled
    if pause is None:
        pause = pause_enabled()
    if pause:
        pause_daemon()
    try:
        write_packet(lighting_packet(lighting))
    finally:
        if pause:
            resume_daemon()


def install_keyd_conf(profile):
    """Installa la conf keyd del profilo e riavvia keyd. Ritorna (ok, msg).

    keyd non supporta reload: serve restart.
    """
    tmp = "/tmp/opencode/keyd-profile.conf"
    with open(tmp, "w") as f:
        f.write(render_keyd(profile))
    r = _escalated("install", "-m", "644", tmp, "/etc/keyd/keyd.conf")
    if r.returncode != 0:
        return False, (r.stderr or "install fallito").strip()
    r = _escalated("systemctl", "restart", "keyd")
    if r.returncode != 0:
        return False, (r.stderr or "restart keyd fallito").strip()
    return True, "keyd aggiornato"


def apply_profile(profile, pause=True):
    """Profilo completo: luci via HID + tasti via keyd."""
    apply_lighting(profile.lighting, pause=pause)
    return install_keyd_conf(profile)


def keyd_active():
    r = subprocess.run(["systemctl", "is-active", "keyd"],
                       capture_output=True, text=True)
    return r.stdout.strip() == "active"
