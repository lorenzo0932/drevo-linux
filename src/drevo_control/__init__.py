# SPDX-License-Identifier: GPL-3.0-or-later
"""drevo-control: controllo Linux per tastiere Drevo Winbond (0416:a0f8)."""

__version__ = "0.0.1"

# Tastiera target: Drevo Tyrfing V2 / Calibur V2 TE (controller Winbond).
# Interfaccia di controllo: interface_number 1, usage 0.
VENDOR_ID = 0x0416
PRODUCT_ID = 0xA0F8
CONTROL_INTERFACE = 1
CONTROL_USAGE = 0
