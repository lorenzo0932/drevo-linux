#!/usr/bin/env python3
"""Survey READ-ONLY della Drevo 0416:a0f8: enumera interfacce HID e legge
i report descriptor + feature report. NON scrive nulla sul device."""

import sys

from drevo_control import CONTROL_INTERFACE, PRODUCT_ID, VENDOR_ID


def main():
    import hid

    found = False
    for itf in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        if (itf.get("interface_number") == CONTROL_INTERFACE
                and itf.get("usage") == 0):
            found = True
            print("controllo:", {
                "path": itf.get("path"),
                "manufacturer": itf.get("manufacturer_string"),
                "product": itf.get("product_string"),
                "release": hex(itf.get("release_number") or 0),
            })
            dev = hid.device()
            dev.open_path(itf["path"])
            try:
                for rid in range(0x00, 0x11):
                    try:
                        data = dev.get_feature_report(rid, 64)
                        if data:
                            print(f"feature 0x{rid:02x} len={len(data)}: "
                                  + " ".join(f"{b:02x}" for b in data[:16])
                                  + (" ..." if len(data) > 16 else ""))
                    except OSError as e:
                        print(f"feature 0x{rid:02x}: errore ({e})")
            finally:
                dev.close()
    if not found:
        print("interfaccia di controllo non trovata", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
