# SPDX-License-Identifier: GPL-3.0-or-later
"""Test oslayer: render keyd + roundtrip profili (no hardware)."""

import os
import tempfile

from drevo_control.oslayer import RemapProfile, render_keyd

p = RemapProfile(name="test", remaps={"capslock": "esc"},
                 macros={"f9": ["a", "b"]}, game_mode=True,
                 lighting={"effect": "static"})
cfg = render_keyd(p)
assert "[ids]" in cfg and "0416:a0f8" in cfg
assert "capslock = esc" in cfg
assert "f9 = macro(a 100ms b)" in cfg
assert "f12 = toggle(game)" in cfg
assert "[game]" in cfg and "leftmeta = noop" in cfg

p2 = RemapProfile(name="plain")
assert "toggle(game)" not in render_keyd(p2)

tmp = tempfile.mkdtemp()
os.environ["XDG_CONFIG_HOME"] = tmp
from drevo_control.oslayer import profiles

profiles.save_profile(p)
assert profiles.list_profiles() == ["test"]
assert profiles.load_profile("test") == p

print("oslayer ok")
