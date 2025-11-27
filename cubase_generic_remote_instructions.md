# Cubase 15 — Generic Remote setup instructions (Windows)

1. Install loopMIDI (https://www.tobias-erichsen.de/software/loopmidi.html) and create a new MIDI port named exactly: `MK3 to Cubase` (or choose your own name and use it when launching translator.py with `--out`).
2. Start the translator:
   ```
   python translator.py --in "Launchkey" --out "MK3 to Cubase"
   ```
3. Open Cubase 15.
4. Go to Studio > Studio Setup... > MIDI Port Setup and confirm the loopMIDI port appears.
5. In Studio Setup, click the "+" button → Remote → Generic Remote.
6. In the Generic Remote panel, set the MIDI Input to the loopMIDI port (`MK3 to Cubase`) and use the Learn feature to assign incoming CC/note messages to functions (Fader 1..8, Pan 1..8, Transport Play/Stop/Record, Device Control 1..8, etc.).
   - Use `midi_probe.py` to confirm what messages your Launchkey or the translator is sending when you move controls.
7. Save the Generic Remote preset for re-use.

Tips
- If Cubase receives duplicate messages, make sure only the translator (loopMIDI) port is enabled in Generic Remote and disable direct device input if necessary.
- For bank switching: either create separate Generic Remote presets or implement bank offset logic in `translator.py` to shift CC numbers before they reach Cubase.
- To map plugin parameters, use Cubase's Quick Controls / Device parameters and map incoming CCs to plugin parameters.
