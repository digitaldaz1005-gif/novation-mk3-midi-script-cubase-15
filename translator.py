#!/usr/bin/env python3
"""
Launchkey MK3 (25) -> Cubase translator daemon (Windows-friendly).

Usage:
    python translator.py --in "Launchkey" --out "MK3 to Cubase"

Notes:
 - Run midi_probe.py first and update DEFAULT_MAPPING to match your Launchkey's reported CC/note numbers.
 - On Windows, create a loopMIDI port named "MK3 to Cubase" (or use any name and pass it to --out).
"""
from __future__ import print_function
import sys
import time
import argparse
import rtmidi
from copy import deepcopy

def identity(v):
    return v

# DEFAULT_MAPPING example: map incoming (type, channel, number) -> (out_type, out_channel, out_number, transform)
# Types: 'cc', 'note_on', 'note_off'
# Channels are 0-based here (MIDI channel 1 == 0)
DEFAULT_MAPPING = {
    # NOTE: These numbers are examples. Run midi_probe.py and replace the keys with the CC/note numbers your Launchkey reports.

    # Faders -> CC 7 (main volume) on successive MIDI channels (example)
    ('cc', 0, 21): ('cc', 0, 7, identity),  # Fader 1 -> CC7 ch1 (volume)
    ('cc', 0, 22): ('cc', 1, 7, identity),  # Fader 2 -> CC7 ch2
    ('cc', 0, 23): ('cc', 2, 7, identity),
    ('cc', 0, 24): ('cc', 3, 7, identity),
    ('cc', 0, 25): ('cc', 4, 7, identity),
    ('cc', 0, 26): ('cc', 5, 7, identity),
    ('cc', 0, 27): ('cc', 6, 7, identity),
    ('cc', 0, 28): ('cc', 7, 7, identity),

    # Pans -> map to CC 10 (pan) on respective channels (example)
    ('cc', 0, 41): ('cc', 0, 10, identity),  # Pan 1 -> CC10 ch1
    ('cc', 0, 42): ('cc', 1, 10, identity),

    # Knobs -> device parameters (example mapping to CC 20..27 on channel 0)
    ('cc', 0, 11): ('cc', 0, 20, identity),
    ('cc', 0, 12): ('cc', 0, 21, identity),
    ('cc', 0, 13): ('cc', 0, 22, identity),
    ('cc', 0, 14): ('cc', 0, 23, identity),
    ('cc', 0, 15): ('cc', 0, 24, identity),
    ('cc', 0, 16): ('cc', 0, 25, identity),
    ('cc', 0, 17): ('cc', 0, 26, identity),
    ('cc', 0, 18): ('cc', 0, 27, identity),

    # Pads (notes) passthrough or translate to CC for transport mapping via Generic Remote
    # Replace note numbers with values found from midi_probe.py
    ('note_on', 9, 36): ('note_on', 9, 36, identity),
    ('note_off', 9, 36): ('note_off', 9, 36, identity),

    # Transport example: map pad note_on to CC (so Generic Remote can learn it as a button)
    ('note_on', 9, 48): ('cc', 0, 100, lambda v: 127),  # Play
    ('note_on', 9, 49): ('cc', 0, 101, lambda v: 127),  # Stop
    ('note_on', 9, 50): ('cc', 0, 102, lambda v: 127),  # Record
}

# Bank switching: naive example where banks adjust target offsets; extend as needed.
BANKS = {
    0: { 'name': 'Tracks 1-8', 'fader_offset': 0, 'device_offset': 0 },
    1: { 'name': 'Tracks 9-16', 'fader_offset': 8, 'device_offset': 8 },
}

CURRENT_BANK = 0

def find_port(midiin, substr=None):
    ports = midiin.get_ports()
    if substr:
        for i,p in enumerate(ports):
            if substr.lower() in p.lower():
                return i, p
    if ports:
        return 0, ports[0]
    return None, None

def send_message(midiout, out_type, channel, number, value):
    if out_type == 'cc':
        status = 0xB0 | (channel & 0x0F)
        msg = [status, number & 0x7F, value & 0x7F]
    elif out_type == 'note_on':
        status = 0x90 | (channel & 0x0F)
        msg = [status, number & 0x7F, value & 0x7F]
    elif out_type == 'note_off':
        status = 0x80 | (channel & 0x0F)
        msg = [status, number & 0x7F, value & 0x7F]
    else:
        return
    midiout.send_message(msg)

def on_midi(in_msg, data):
    global CURRENT_BANK
    msg, delta = in_msg
    if not msg:
        return
    status = msg[0]
    typ = status & 0xF0
    ch = status & 0x0F

    if typ == 0xB0 and len(msg) >= 3:
        kind = 'cc'
        num = msg[1]
        val = msg[2]
        key = (kind, ch, num)
    elif typ == 0x90 and len(msg) >= 3 and msg[2] != 0:
        kind = 'note_on'
        num = msg[1]
        val = msg[2]
        key = (kind, ch, num)
    elif (typ == 0x80 and len(msg) >= 3) or (typ == 0x90 and len(msg) >= 3 and msg[2] == 0):
        kind = 'note_off'
        num = msg[1]
        val = msg[2]
        key = (kind, ch, num)
    else:
        # ignore other message types for now
        return

    mapping = data['mapping']
    midiout = data['midiout']

    # If mapping exists, translate. Otherwise, passthrough to output port.
    if key in mapping:
        out_type, out_ch, out_num, transform = mapping[key]
        out_val = transform(val)
        # Bank handling: you can programmatically apply offsets here based on CURRENT_BANK and BANKS
        send_message(midiout, out_type, out_ch, out_num, out_val)
        print(f"Translated {{key}} -> {{(out_type,out_ch,out_num,out_val)}}")
    else:
        # Passthrough unmapped message (so device still functions in note mode etc.)
        try:
            midiout.send_message(msg)
            print(f"Passthrough {{msg}}")
        except Exception as e:
            print("Failed to passthrough:", e)


def main():
    parser = argparse.ArgumentParser(description='Launchkey MK3 -> Cubase translator')
    parser.add_argument('--in', dest='in_port', help='Input port substring (e.g. "Launchkey")')
    parser.add_argument('--out', dest='out_port', help='Output port name (virtual port or loopMIDI port, e.g. "MK3 to Cubase")')
    args = parser.parse_args()

    midiin = rtmidi.MidiIn()
    midiout = rtmidi.MidiOut()

    in_idx, in_name = find_port(midiin, args.in_port)
    if in_idx is None:
        print('No input ports available. Run midi_probe.py to list ports.')
        return
    midiin.open_port(in_idx)
    print(f'Opened input: {{in_name}}')

    # open existing output port if present else create a virtual output
    out_idx = None
    if args.out_port:
        ports = midiout.get_ports()
        for i,p in enumerate(ports):
            if args.out_port.lower() in p.lower():
                out_idx = i
                break
        if out_idx is not None:
            midiout.open_port(out_idx)
            print(f'Opened output port: {{ports[out_idx]}}')
        else:
            try:
                midiout.open_virtual_port(args.out_port)
                print(f'Created virtual output port: {{args.out_port}}')
            except Exception as e:
                print('Failed to open or create output port:', e)
                print('Create a loopMIDI port named', args.out_port, 'and re-run.')
                return
    else:
        midiout.open_virtual_port('MK3 to Cubase')
        print('Created virtual output port: MK3 to Cubase')

    data = {'mapping': deepcopy(DEFAULT_MAPPING), 'midiout': midiout}
    midiin.set_callback(on_midi, data)

    print('Translator running. Ctrl-C to quit.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting')
        try:
            midiin.close_port()
        except Exception:
            pass
        try:
            midiout.close_port()
        except Exception:
            pass

if __name__ == '__main__':
    main()