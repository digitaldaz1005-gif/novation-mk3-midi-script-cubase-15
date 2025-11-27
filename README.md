# Novation Launchkey MK3 (25) — Cubase 15 MIDI translation daemon

This repository contains a Python translation daemon that listens to a Novation Launchkey MK3 (25) MIDI input and translates its messages into a consistent set of MIDI messages for use with Cubase 15 (Windows). The goal is to make the Launchkey act as a flexible controller for:

- Channel faders and pans
- Transport (play/stop/record/loop/rewind/forward)
- Device / instrument parameters (knobs)
- Pad note mode and pad-to-transport mapping
- Bank switching to control multiple tracks/plugins
- Plugin parameter mapping via banks

What’s included
- `midi_probe.py` — small utility to inspect raw MIDI messages from your Launchkey MK3 so you can discover CC/note numbers.
- `translator.py` — the translation daemon. Edit `DEFAULT_MAPPING` and `BANKS` inside to tune mappings to your system.
- `requirements.txt` — Python dependency list (`python-rtmidi`).
- `cubase_generic_remote_instructions.md` — step-by-step instructions for connecting the virtual port and configuring Cubase 15 to receive the translated messages.

Prerequisites (Windows)
1. Python 3.8+ installed (https://www.python.org).
2. pip available. Install dependencies: `pip install -r requirements.txt`.
3. loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html) — create a virtual MIDI port named `MK3 to Cubase` (or a name of your choice) and use that as Cubase input.
4. Connect your Launchkey MK3 physically via USB.

Quick start
1. Run `python midi_probe.py` and press pads/turn knobs/slide the faders to see raw MIDI messages. Note CC/note numbers your device uses.
2. Edit `translator.py` and adjust `DEFAULT_MAPPING` to match the CC/note numbers discovered.
3. Start loopMIDI and create a port called `MK3 to Cubase`.
4. Run the translator: `python translator.py --in "Launchkey" --out "MK3 to Cubase"` (you can use substrings to auto-select ports).
5. In Cubase 15: Studio > Studio Setup > MIDI Port Setup / Remote Devices. Add/import mappings (see `cubase_generic_remote_instructions.md`).

Notes
- This translator is intentionally configurable: if your Launchkey reports different CC numbers, update the mapping dictionary (or extend the script to load JSON mappings).
- The translator outputs standard CC/Note messages; use Cubase Generic Remote to bind those messages to functions.
- For more advanced MCU/Mackie emulation, a full MCU implementation is required (out of scope for this starter).

License: MIT
