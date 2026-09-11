# LPD8 Media & Desktop Controller

A Python-based MIDI controller mapper for the **Akai LPD8**, designed to turn its pads and knobs into a physical control surface for **MPV**, **VLC**, system audio, OBS, screenshots, and monitor power control.

The script listens for MIDI messages from the LPD8 and translates them into application commands, keyboard shortcuts, or system actions.

## Features

* 🎵 **MPV control**

  * Play/pause
  * Next/previous track
  * Quit MPV
  * Speed-sensitive scrubbing
  * Fine-grained 1-second scrubbing

* 🎬 **VLC control**

  * Play/pause
  * Subtitle toggle
  * Absolute seeking
  * Jog/shuttle control
  * Frame-by-frame stepping
  * Save playback position and quit
  * Resume playback position on next launch

* 🔊 **System audio**

  * Volume control
  * Mute toggle

* 🖥️ **Desktop control**

  * Toggle secondary monitors using DPMS
  * Take screenshots using Spectacle

* 🎥 **OBS**

  * Restart OBS through a user-provided script

---

## Hardware Layout

The LPD8 is configured as two rows of four pads followed by four knobs:

```text
Top:       P5  P6  P7  P8   | K1  K2  K3  K4
Bottom:    P1  P2  P3  P4   | K5  K6  K7  K8
```

The device has three relevant operating modes:

* **PAD** — note messages
* **PROG CHNG** — program-change messages
* **CC** — control-change messages

Switch between these modes using the corresponding buttons on the LPD8.

---

# Installation

## Requirements

This project assumes a Linux desktop environment with the following available:

* Python 3
* An Akai LPD8 connected over USB
* `mpv`
* `vlc`
* `pactl`
* `spectacle`
* `kscreen-doctor`
* An OBS restart script
* Python packages:

  * `mido`
  * `pynput`

The script also assumes that VLC is running with its RC interface enabled when being controlled.

## Python dependencies

Install the Python dependencies with:

```bash
python3 -m pip install mido pynput
```

Depending on your MIDI backend, you may also need a backend such as `python-rtmidi`:

```bash
python3 -m pip install python-rtmidi
```

For Debian/Ubuntu-based systems, the system package may be preferable:

```bash
sudo apt install python3-mido python3-pynput python3-rtmidi
```

---

# Configuration

Several paths and settings are hard-coded near the top of the script.

```python
MPV_SOCKET_PATH = "/tmp/mpvsocket"
MPV_PLAYLIST = "/home/davix/Documents/allmusic.m3u"

VLC_HOST = "127.0.0.1"
VLC_PORT = 4212
VLC_PLAYLIST = "/home/davix/Documents/video.m3u"
VLC_RESUME_FILE = "/home/davix/.vlc_resume_position"

SCREENSHOT_PATH = "/home/davix/sofa_screenshot.png"
OBS_RESTART_SCRIPT = "/home/davix/.local/bin/restart-obs.sh"
```

Change these values to match your system.

### MPV

`MPV_PLAYLIST` should point to the playlist you want MPV to launch when it is not already running.

The script launches MPV with:

```text
--player-operation-mode=pseudo-gui
--input-ipc-server=/tmp/mpvsocket
--shuffle
```

The IPC socket is then used for commands such as:

* pause
* next track
* previous track
* quit
* relative seeking

### VLC

VLC is launched with its RC interface:

```text
--extraintf=rc
--rc-host=127.0.0.1:4212
```

The port must match:

```python
VLC_PORT = 4212
```

The VLC playlist is configured with:

```python
VLC_PLAYLIST = "/home/davix/Documents/video.m3u"
```

### VLC Resume State

When VLC is quit using Pad 8, the script attempts to save:

1. The current playback time
2. The current playlist item

These are stored in:

```text
~/.vlc_resume_position
```

When VLC is subsequently launched through Pad 4, the script attempts to restore that position.

### Screenshots

Pad 6 in Program Change mode uses Spectacle and saves screenshots to:

```python
SCREENSHOT_PATH = "/home/davix/sofa_screenshot.png"
```

Change this path if required.

### OBS

Pad 3 in Program Change mode executes:

```python
OBS_RESTART_SCRIPT = "/home/davix/.local/bin/restart-obs.sh"
```

The script must exist and be executable:

```bash
chmod +x ~/.local/bin/restart-obs.sh
```

---

# Pad Mapping — PAD / Note Mode

The LPD8 pads send MIDI notes **36–43**.

| Pad | Note | Action                      |
| --- | ---: | --------------------------- |
| P1  |   36 | MPV play/pause or launch    |
| P2  |   37 | MPV next track              |
| P3  |   38 | VLC toggle subtitles        |
| P4  |   39 | VLC play/pause or launch    |
| P5  |   40 | Quit MPV                    |
| P6  |   41 | MPV previous track          |
| P7  |   42 | Hold for fine MPV scrubbing |
| P8  |   43 | Save VLC position and quit  |

## P1 — MPV Play/Pause

If MPV is already running and its IPC socket is available, P1 toggles playback.

If MPV is not running, P1 launches it using the configured playlist.

The playlist is shuffled when MPV is launched.

## P2 — MPV Next

Sends the following MPV IPC command:

```text
playlist-next
```

## P3 — VLC Subtitles

Simulates:

```text
Shift + V
```

This is intended to toggle VLC subtitle visibility.

## P4 — VLC Play/Pause

If VLC is already running and accepting RC commands, P4 toggles playback.

Otherwise, VLC is launched using the configured playlist.

## P5 — Quit MPV

Sends the MPV IPC command:

```text
quit
```

## P6 — MPV Previous

Sends:

```text
playlist-prev
```

## P7 — Fine Scrub Modifier

P7 is a **momentary modifier**.

Hold P7 while moving the MPV scrub knob to enable fine scrubbing.

When released, normal speed-sensitive scrubbing is restored.

## P8 — Save VLC Position and Quit

P8 attempts to determine:

* Current VLC playback time
* Current playlist item

It saves both values to the resume file before terminating VLC.

---

# Pad Mapping — PROG CHNG Mode

The program-change mode uses programs **0–7**.

| Pad | Program | Action                    |
| --- | ------: | ------------------------- |
| P1  |       0 | Toggle secondary monitors |
| P2  |       1 | Toggle system mute        |
| P3  |       2 | Restart OBS               |
| P4  |       3 | Toggle secondary monitors |
| P5  |       4 | Suspend                   |
| P6  |       5 | Screenshot                |
| P7  |       6 | Play/pause                |
| P8  |       7 | Brightness down           |

> **Note:** Programs 4–7 are documented by the physical mapping above, but the current Python implementation only defines handlers for programs 0–3. P5–P8 therefore currently have no corresponding actions in `PAD_PROGRAM_PRESS`.

## P1 / P4 — Toggle Secondary Monitors

P1 and P4 share the same stateful toggle.

When off:

```text
output.DP-1.power.off
output.DP-2.power.off
```

When pressed again:

```text
output.DP-1.power.on
output.DP-2.power.on
```

This requires the relevant outputs to actually be named `DP-1` and `DP-2` by KDE's `kscreen-doctor`.

You can inspect available outputs with:

```bash
kscreen-doctor output
```

## P2 — Toggle Mute

Runs:

```bash
pactl set-sink-mute @DEFAULT_SINK@ toggle
```

This operates on the default PulseAudio/PipeWire sink.

## P3 — Restart OBS

Runs the configured script:

```text
~/.local/bin/restart-obs.sh
```

## P5 — Suspend

The physical mapping describes P5 as **Suspend**, but no program `4` handler is currently implemented.

## P6 — Screenshot

The physical mapping describes P6 as **Screenshot**, but no program `5` handler is currently implemented.

The screenshot helper itself is implemented in the Python source and uses Spectacle, but it is not currently assigned to a program-change mapping.

## P7 — Play/Pause

The physical mapping describes P7 as **Play/pause**, but no program `6` handler is currently implemented.

## P8 — Brightness Down

The physical mapping describes P8 as **Brightness down**, but no program `7` handler is currently implemented.

---

# Knob Mapping — CC Mode

The following MIDI CC numbers are used:

| Knob | CC | Action            |
| ---- | -: | ----------------- |
| K3   |  3 | VLC absolute seek |
| K4   |  4 | VLC jog/shuttle   |
| K5   |  5 | MPV scrub         |
| K8   |  8 | System volume     |

K1, K2, K6 and K7 are currently unused.

---

# K3 — VLC Absolute Seek

K3 maps its MIDI value of `0–127` to a VLC playlist position of `0–100%`.

```text
MIDI 0   → VLC 0%
MIDI 64  → VLC ~50%
MIDI 127 → VLC 100%
```

For example:

```text
K3 = 64
```

results in approximately:

```text
seek 50%
```

This provides direct positioning through the VLC playlist.

---

# K4 — VLC Jog/Shuttle

K4 acts as a jog/shuttle control.

The MIDI range is divided into zones:

| MIDI Value | Zone         | Behaviour              |
| ---------: | ------------ | ---------------------- |
|       0–15 | Fast rewind  | Repeated `-10s` seeks  |
|      16–31 | Fast rewind  | Repeated `-3s` seeks   |
|      32–47 | Slow rewind  | Repeated `-1s` seeks   |
|      48–79 | Normal       | Normal playback        |
|      80–95 | Step forward | Frame-by-frame advance |
|     96–111 | Fast forward | 2× playback            |
|    112–127 | Fast forward | 4× playback            |

VLC does not reliably support negative playback rates, so reverse playback is simulated using repeated backward seeks.

### Frame stepping

The forward frame-stepping zone uses:

```text
key frame-next
```

The script adjusts the repeat interval based on knob position, allowing slower or faster frame advancement.

A small section of the range also supports single-step movement when the knob value changes between adjacent positions.

---

# K5 — MPV Scrub

K5 provides relative MPV seeking.

The LPD8 sends absolute MIDI CC values from `0–127`. The script converts these into relative movement by comparing the current value with the previous value.

It also handles wrap-around:

```text
127 → 0
0 → 127
```

This allows the physical knob to behave like a continuously rotating controller.

## Normal Scrubbing

Scrubbing is speed-sensitive.

The faster the knob is moved, the larger the seek amount becomes:

| Knob movement speed | Seek per MIDI step |
| ------------------- | -----------------: |
| < 2 steps/sec       |           1 second |
| < 5 steps/sec       |          2 seconds |
| < 10 steps/sec      |          5 seconds |
| < 20 steps/sec      |         15 seconds |
| ≥ 20 steps/sec      |         30 seconds |

For example, slowly turning the knob provides precise seeking, while quickly turning it allows large jumps through a long video or playlist.

## Fine Scrubbing

Hold **P7** while turning K5.

Fine mode changes the behaviour to:

```text
1 MIDI step = 1 second
```

This makes it possible to make precise adjustments without needing to move the knob extremely slowly.

---

# K8 — Volume

K8 maps the MIDI range directly to the system's default sink volume:

```text
0   → 0%
127 → 100%
```

The command used is:

```bash
pactl set-sink-volume @DEFAULT_SINK@ <percentage>%
```

This assumes `pactl` is available and that the system audio stack exposes a default sink.

---

# Running

Save the Python script, for example:

```text
lpd8_controller.py
```

Then run:

```bash
python3 lpd8_controller.py
```

When the LPD8 is connected, the script automatically searches the available MIDI input ports for a device whose name contains:

```text
LPD8
```

If found, it prints:

```text
Listening on <LPD8 MIDI port> — Ctrl+C to stop
```

Stop the controller with:

```text
Ctrl+C
```

---

# MIDI Device Detection

The script automatically finds the first MIDI input whose name contains `LPD8`:

```python
def find_port():
    for name in mido.get_input_names():
        if "LPD8" in name:
            return name

    raise RuntimeError("LPD8 not found — is it connected?")
```

To see all MIDI ports detected by Mido:

```bash
python3 -c "import mido; print('\n'.join(mido.get_input_names()))"
```

If the LPD8 is not detected, check:

1. The USB connection.
2. That the device appears in the operating system.
3. That the MIDI backend is installed.
4. The output of `mido.get_input_names()`.

---

# Architecture

The controller is split into several functional sections.

```text
LPD8
 │
 ├── Note messages
 │    └── PAD_PRESS / PAD_RELEASE
 │
 ├── Program Change messages
 │    └── PAD_PROGRAM_PRESS
 │
 └── Control Change messages
      └── CC_HANDLERS
             │
             ├── VLC absolute seek
             ├── VLC jog/shuttle
             ├── MPV scrub
             └── system volume
```

Application communication is handled through different mechanisms.

### MPV

```text
LPD8 → Python → UNIX socket → MPV IPC
```

### VLC

```text
LPD8 → Python → TCP socket → VLC RC interface
```

### Desktop commands

```text
LPD8 → Python → subprocess → Linux/KDE command
```

### Keyboard shortcuts

```text
LPD8 → Python → pynput → virtual keyboard input
```

---

# External Commands Used

The script invokes the following external applications/utilities:

| Command           | Purpose                 |
| ----------------- | ----------------------- |
| `mpv`             | Music/media playback    |
| `vlc`             | Video playback          |
| `pactl`           | Volume and mute control |
| `spectacle`       | Screenshots             |
| `kscreen-doctor`  | Monitor power control   |
| `pkill`           | Terminating VLC         |
| Custom OBS script | Restarting OBS          |

Make sure these commands are available in the environment from which the Python script is launched.

Check with:

```bash
command -v mpv
command -v vlc
command -v pactl
command -v spectacle
command -v kscreen-doctor
command -v pkill
```

---

# Autostart

If you want the controller to start automatically when logging into KDE, create a user systemd service.

For example:

```text
~/.config/systemd/user/lpd8-controller.service
```

Example service:

```ini
[Unit]
Description=Akai LPD8 Controller
After=graphical-session.target

[Service]
ExecStart=/usr/bin/python3 /home/davix/path/to/lpd8_controller.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

Then enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now lpd8-controller.service
```

Check its status with:

```bash
systemctl --user status lpd8-controller.service
```

View logs with:

```bash
journalctl --user -u lpd8-controller.service -f
```

Adjust the Python executable and script path to match your installation.

---

# Troubleshooting

## `LPD8 not found`

List available MIDI inputs:

```bash
python3 -c "import mido; print(mido.get_input_names())"
```

Make sure the LPD8 appears in the output.

If necessary, install the RtMidi backend:

```bash
python3 -m pip install python-rtmidi
```

---

## MPV controls do nothing

Check whether the MPV IPC socket exists:

```bash
ls -l /tmp/mpvsocket
```

If MPV was started manually, make sure it was launched with:

```text
--input-ipc-server=/tmp/mpvsocket
```

The controller automatically adds this option when launching MPV itself.

---

## VLC controls do nothing

Check whether VLC is listening on port `4212`:

```bash
ss -ltn | grep 4212
```

The controller launches VLC with:

```text
--extraintf=rc
--rc-host=127.0.0.1:4212
```

If VLC is already running without the RC interface, the controller cannot communicate with it.

---

## Monitor toggle does not work

Check the available KDE output names:

```bash
kscreen-doctor output
```

The script currently expects:

```text
DP-1
DP-2
```

If your displays use different names, update:

```python
kscreen-doctor output.DP-1.power.off output.DP-2.power.off
```

and the corresponding `.power.on` command.

---

## Volume control does nothing

Check the default sink:

```bash
pactl get-default-sink
```

Test manually:

```bash
pactl set-sink-volume @DEFAULT_SINK@ 50%
```

If that works, K8 should also work.

---

## Screenshot does not work

Test Spectacle manually:

```bash
spectacle -b -o /tmp/test-screenshot.png -m -n
```

Then check:

```bash
ls -l /tmp/test-screenshot.png
```

If successful, update `SCREENSHOT_PATH` as required.

---

# Important Implementation Notes

### Hard-coded paths

The original script contains user-specific absolute paths such as:

```text
/home/davix/Documents/allmusic.m3u
/home/davix/Documents/video.m3u
/home/davix/.local/bin/restart-obs.sh
```

These should be changed before using the script on another machine.

### Program Change mappings

The physical mapping documents eight program-change actions, but only programs `0–3` are currently implemented in Python.

The following mappings are currently unimplemented:

```text
Program 4 — Suspend
Program 5 — Screenshot
Program 6 — Play/pause
Program 7 — Brightness down
```

### VLC jog/shuttle

Reverse playback is intentionally implemented using repeated seek commands rather than a negative VLC playback rate because negative-rate playback is not considered reliable for this use case.

### Thread safety

VLC commands are protected by a lock:

```python
_vlc_lock = threading.Lock()
```

This is necessary because the VLC jog/shuttle repeat thread and other controller actions may issue commands concurrently.

---

# Complete Control Summary

```text
┌─────────────────────────────────────────────────────────────┐
│                         PAD MODE                            │
├────────┬───────┬────────────────────────────────────────────┤
│ Pad    │ Note  │ Action                                     │
├────────┼───────┼────────────────────────────────────────────┤
│ P1     │ 36    │ MPV play/pause or launch                  │
│ P2     │ 37    │ MPV next                                  │
│ P3     │ 38    │ VLC subtitles                             │
│ P4     │ 39    │ VLC play/pause or launch                  │
│ P5     │ 40    │ Quit MPV                                  │
│ P6     │ 41    │ MPV previous                              │
│ P7     │ 42    │ Hold for fine MPV scrubbing               │
│ P8     │ 43    │ Save VLC position and quit                │
└────────┴───────┴────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     PROG CHNG MODE                          │
├────────┬─────────┬──────────────────────────────────────────┤
│ Pad    │ Program │ Action                                   │
├────────┼─────────┼──────────────────────────────────────────┤
│ P1     │ 0       │ Toggle secondary monitors               │
│ P2     │ 1       │ Toggle mute                             │
│ P3     │ 2       │ Restart OBS                             │
│ P4     │ 3       │ Toggle secondary monitors               │
│ P5     │ 4       │ Suspend — not implemented               │
│ P6     │ 5       │ Screenshot — not implemented             │
│ P7     │ 6       │ Play/pause — not implemented             │
│ P8     │ 7       │ Brightness down — not implemented        │
└────────┴─────────┴──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         CC MODE                             │
├────────┬──────┬─────────────────────────────────────────────┤
│ Knob   │ CC   │ Action                                      │
├────────┼──────┼─────────────────────────────────────────────┤
│ K3     │ 3    │ VLC absolute seek (0–100%)                 │
│ K4     │ 4    │ VLC jog/shuttle                            │
│ K5     │ 5    │ MPV speed-sensitive scrub                  │
│ K8     │ 8    │ System volume (0–100%)                     │
└────────┴──────┴─────────────────────────────────────────────┘
```

---

License

This project is released into the public domain under The Unlicense.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell this software without restriction, to the extent permitted by applicable law.

See the LICENSE file for the full text of The Unlicense.
