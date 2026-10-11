# OS layer: keyd (remap, macro, game-mode)

Remap/macro/game-mode vivono a livello OS, non nel protocollo device:
piu' sicuro, Wayland-safe, indipendente dal firmware.

## Generazione (`oslayer/keyd.py`)

`RemapProfile` → testo keyd con sezione `[ids] 0416:a0f8` (solo la Drevo),
layer `[main]` (remap `a = b`, macro `f9 = macro(c 100ms i 100ms a)`) e
layer `[game]` (`leftmeta/rightmeta = noop`) con `toggle(game)`.

## Note di versione e quirks verificati

- keyd **non legge `conf.d`**: scrivere sempre `/etc/keyd/keyd.conf`.
- keyd **non supporta `reload`**: dopo ogni installazione serve `restart`.
- `toggle()` presente dalla 2.4 (verificato su 2.3.1 con esito positivo
  nei test storici e su 2.6.0 da sorgenti per sintassi).
- keyd tocca solo tastiere evdev; mouse e HID di controllo non confliggono.

## Installazione

Dai sorgenti, senza package manager (`data/keyd_install_src.sh`,
richiede gcc/make/git + rete per il clone): sorgenti in
`/usr/local/src/keyd`, binari in `/usr/local/bin`, unit di sistema.
Rimozione: `tools/keyd_rollback.sh` (copre installazioni rpm e sorgenti).
