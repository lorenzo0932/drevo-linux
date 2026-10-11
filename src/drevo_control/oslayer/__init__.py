# SPDX-License-Identifier: GPL-3.0-or-later
"""Generazione config keyd per 0416:a0f8 (remap, macro, game-mode).

keyd e' system-wide e Wayland-safe. Questo modulo genera solo testo:
installazione/attivazione keyd restano fuori (servizio di sistema).
"""

from dataclasses import dataclass, field

DEVICE_ID = "0416:a0f8"


@dataclass
class RemapProfile:
    """Profilo tasti lato OS. lighting: dict per il driver (effect, rgb...)."""

    name: str = "default"
    remaps: dict = field(default_factory=dict)  # es. {"capslock": "esc"}
    macros: dict = field(default_factory=dict)  # es. {"f9": ["a", "b"]}
    macro_timeout_ms: int = 100
    game_mode: bool = False
    game_toggle_key: str = "f12"
    lighting: dict = field(default_factory=dict)


def _macro_call(keys, timeout_ms):
    seq = f" {timeout_ms}ms ".join(keys)
    return f"macro({seq})"


def render_keyd(profile):
    """Rende una config keyd completa per il profilo."""
    lines = [f"# generato da drevo-control: profilo '{profile.name}'",
             "[ids]", "", DEVICE_ID, "", "[main]"]
    for src, dst in profile.remaps.items():
        lines.append(f"{src} = {dst}")
    for key, keys in profile.macros.items():
        lines.append(f"{key} = {_macro_call(keys, profile.macro_timeout_ms)}")
    if profile.game_mode:
        lines.append(f"{profile.game_toggle_key} = toggle(game)")
        lines += ["", "[game]", "leftmeta = noop", "rightmeta = noop"]
    return "\n".join(lines) + "\n"
