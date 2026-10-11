"""Apertura/scrittura HID dell'interfaccia di controllo, single-writer."""

from contextlib import contextmanager

from drevo_control import CONTROL_INTERFACE, PRODUCT_ID, VENDOR_ID
from drevo_control.lock import hid_writer_lock


@contextmanager
def open_control():
    """Apre iface 1/usage 0 in scrittura. Solleva RuntimeError se assente."""
    import hid

    path = None
    for itf in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        if (itf.get("interface_number") == CONTROL_INTERFACE
                and itf.get("usage") == 0):
            path = itf["path"]
            break
    if path is None:
        raise RuntimeError("tastiera non trovata o interfaccia assente")
    dev = hid.device()
    dev.open_path(path)
    try:
        yield dev
    finally:
        dev.close()


def write_packet(packet, timeout=10.0):
    """Scrive un pacchetto sotto lock single-writer. Ritorna True/False."""
    with hid_writer_lock(timeout=timeout) as locked:
        if not locked:
            raise RuntimeError("writer HID occupato (timeout lock)")
        with open_control() as dev:
            return dev.write(packet) >= 0
