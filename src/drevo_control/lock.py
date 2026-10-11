# SPDX-License-Identifier: GPL-3.0-or-later
"""Lock single-writer per l'HID della tastiera.

Il controller Winbond va in reset-loop con scritture frequenti o
concorrenti: UN SOLO processo alla volta puo' aprire l'interfaccia di
controllo. Anche il daemon ambilight (`drevo_keyboard_sync.py`) deve
passare da qui o restare in pausa durante la configurazione.
"""

import fcntl
import os
import time
from contextlib import contextmanager

LOCK_PATH = "/tmp/drevo_hid_writer.lock"


@contextmanager
def hid_writer_lock(timeout=10.0):
    """Yield a True se il lock e' acquisito, altrimenti False (non blocca)."""
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o644)
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    yield False
                    return
                time.sleep(0.1)
        yield True
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
