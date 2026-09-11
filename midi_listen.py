import mido
""""
print(mido.get_input_names())
"""
PORT = 'LPD8:LPD8 MIDI 1 20:0'

with mido.open_input(PORT) as inport:
    print(f"Listening on {PORT} — press Ctrl+C to stop")
    for msg in inport:
        print(msg)
