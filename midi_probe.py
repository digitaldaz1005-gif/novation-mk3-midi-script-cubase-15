#!/usr/bin/env python3
"""
Small utility to inspect raw MIDI messages from your Launchkey MK3.
Run: python midi_probe.py "Launchkey"
"""
from __future__ import print_function
import sys
import time
import rtmidi

def list_ports(midiin):
    ports = midiin.get_ports()
    if not ports:
        print("No MIDI input ports found.")
    for i, p in enumerate(ports):
        print(f"[{i}] {{p}}")
    return ports

def open_input(midiin, name_substr=None):
    ports = midiin.get_ports()
    if name_substr:
        for i, p in enumerate(ports):
            if name_substr.lower() in p.lower():
                midiin.open_port(i)
                print(f"Opened input port: {{p}}")
                return
    # otherwise open first port
    if ports:
        midiin.open_port(0)
        print(f"Opened input port: {{ports[0]}}")
    else:
        raise SystemExit("No MIDI input ports available")

def midi_callback(message, data):
    msg, delta = message
    t = time.time()
    hex_bytes = ' '.join(f"{{b:02X}}" for b in msg)
    print(f"{{t:.3f}}  delta={{delta:.6f}}  bytes=[{{hex_bytes}}]  msg={{msg}}")

if __name__ == '__main__':
    midiin = rtmidi.MidiIn()
    ports = list_ports(midiin)
    if not ports:
        sys.exit(1)
    name = None
    if len(sys.argv) > 1:
        name = sys.argv[1]
    open_input(midiin, name_substr=name)
    print("Listening for incoming messages. Ctrl-C to exit.")
    midiin.set_callback(midi_callback)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting")
        try:
            midiin.close_port()
        except Exception:
            pass
