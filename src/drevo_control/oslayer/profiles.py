# SPDX-License-Identifier: GPL-3.0-or-later
"""Profili app: lighting (device) + tasti (keyd) in un JSON."""

import json
import os

from drevo_control.oslayer import RemapProfile

APP_DIR = os.path.join(os.environ.get("XDG_CONFIG_HOME",
                                       os.path.expanduser("~/.config")),
                       "drevo-control", "profiles")


def profile_path(name):
    return os.path.join(APP_DIR, f"{name}.json")


def save_profile(profile):
    os.makedirs(APP_DIR, exist_ok=True)
    data = {"name": profile.name, "remaps": profile.remaps,
            "macros": profile.macros,
            "macro_timeout_ms": profile.macro_timeout_ms,
            "game_mode": profile.game_mode,
            "game_toggle_key": profile.game_toggle_key,
            "lighting": profile.lighting}
    with open(profile_path(profile.name), "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def load_profile(name):
    with open(profile_path(name)) as f:
        data = json.load(f)
    return RemapProfile(**data)


def list_profiles():
    if not os.path.isdir(APP_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(APP_DIR) if f.endswith(".json"))
