"""
industrial_techno.py

Builds a high-energy industrial techno track across 8 scenes on 4 tracks.
Scenes are designed for continuity: each is a small intensity step from the
previous one. A Pad provides harmonic glue across transitions, and a
Percussion track adds rhythmic texture in the energy sections.

Track layout:
  0 "Drums" → Drum Rack (909/808/606) + Saturator or Drum Bus
  1 "Bass"  → Analog or Operator + Overdrive + Compressor (sidechain)
  2 "Pad"   → Analog or Drift pad preset (e.g. Charry Pad, Glass Low Strings Pad)
  3 "Perc"  → Drum Rack with ride/shaker/percussion samples
"""

import live
import time

# ── Drum note mapping ──
KICK = 36        # C1
SNARE = 38       # D1
CLOSED_HAT = 42  # F#1
OPEN_HAT = 46    # Bb1

# ── Bass notes (C minor + tritone) ──
C2 = 48
Eb2 = 51
F2 = 53
Gb2 = 54         # tritone

# ── Pad notes (C minor voicings) ──
C3 = 60
Eb3 = 63
F3 = 65
G3 = 67
Ab3 = 68
C4 = 72
Eb4 = 75

# ── Perc notes (mapped to Drum Rack pads) ──
RIDE = 36        # pad 1 on the perc rack
SHAKER = 38      # pad 2

BPM = 136
BARS = 4
BEATS = BARS * 4

# Track indices
TRK_DRUMS = 0
TRK_BASS = 1
TRK_PAD = 2
TRK_PERC = 3


def clear_slot(track, slot):
    try:
        track.delete_clip(slot)
        time.sleep(0.05)
    except Exception:
        pass


def make_clip(track, track_idx, slot, length, name):
    clear_slot(track, slot)
    clip = track.create_clip(slot, float(length))
    live.cmd("/live/clip/set/name", (track_idx, slot, name))
    live.cmd("/live/clip/set/looping", (track_idx, slot, 1))
    return clip


# ── Shared drum helpers ──

def kick_foundation(clip, velocity=100, accent=115):
    for beat in range(BEATS):
        vel = accent if beat % 4 == 0 else velocity
        clip.add_note(KICK, float(beat), 0.5, vel, False)


def hats_sixteenths(clip, groove=None):
    if groove is None:
        groove = [95, 35, 70, 40]
    for beat in range(BEATS):
        for s in range(4):
            clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)


def snare_backbeat(clip, velocity=110):
    for bar in range(BARS):
        clip.add_note(SNARE, float(bar * 4 + 1), 0.25, velocity, False)
        clip.add_note(SNARE, float(bar * 4 + 3), 0.25, velocity, False)


# ── Shared bass helpers ──

def bass_eighths(clip, velocity=100, off_vel=None):
    if off_vel is None:
        off_vel = max(velocity - 30, 30)
    for beat in range(BEATS):
        for i in range(2):
            start = beat + i * 0.5
            vel = velocity if i == 0 else off_vel
            clip.add_note(C2, start, 0.45, vel, False)


def bass_sixteenths(clip, pitches_by_bar=None, accent=110, mid=78, ghost=50):
    if pitches_by_bar is None:
        pitches_by_bar = [C2, C2, F2, C2]
    for beat in range(BEATS):
        bar = beat // 4
        pitch = pitches_by_bar[bar] if bar < len(pitches_by_bar) else C2
        vels = [accent, ghost, mid, ghost]
        for s in range(4):
            clip.add_note(pitch, beat + s * 0.25, 0.2, vels[s], False)


# ── Shared pad helper ──

def pad_chord(clip, notes, vel=65):
    """Whole-note sustained chord across all 4 bars."""
    for bar in range(BARS):
        for note in notes:
            clip.add_note(note, float(bar * 4), 4.0, vel, False)


# ── Shared perc helpers ──

def perc_quarters(clip, vel=50):
    for beat in range(BEATS):
        clip.add_note(RIDE, float(beat), 0.5, vel, False)


def perc_eighths(clip, vel=60, accent_vel=None):
    if accent_vel is None:
        accent_vel = vel
    for beat in range(BEATS):
        clip.add_note(RIDE, float(beat), 0.4, accent_vel, False)
        clip.add_note(RIDE, beat + 0.5, 0.2, vel, False)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 0 — INTRO
#  Kick only. Stark, hypnotic.
# ═══════════════════════════════════════════════════════════════════

def intro_drums(clip):
    kick_foundation(clip)
    clip.add_note(SNARE, float(BEATS - 0.5), 0.25, 95, False)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 1 — BUILD
#  Kick + hats fading in + bass 8ths building + pad enters quietly.
# ═══════════════════════════════════════════════════════════════════

def build_drums(clip):
    kick_foundation(clip)
    for beat in range(BEATS):
        bar = beat // 4
        base = 40 + bar * 13
        groove = [base, max(base - 25, 15), max(base - 10, 15), max(base - 22, 15)]
        for s in range(4):
            clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)


def build_bass(clip):
    for beat in range(BEATS):
        bar = beat // 4
        base_vel = 55 + bar * 12
        off_vel = max(base_vel - 25, 30)
        for i in range(2):
            start = beat + i * 0.5
            vel = base_vel if i == 0 else off_vel
            clip.add_note(C2, start, 0.45, vel, False)


def build_pad(clip):
    pad_chord(clip, [C3, G3], vel=50)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 2 — DRIVE
#  The main groove. Full hats, snare, bass 8ths, pad fills out, perc enters.
# ═══════════════════════════════════════════════════════════════════

def drive_drums(clip):
    kick_foundation(clip)
    hats_sixteenths(clip)
    snare_backbeat(clip)


def drive_bass(clip):
    bass_eighths(clip, velocity=105, off_vel=70)


def drive_pad(clip):
    pad_chord(clip, [C3, Eb3, G3], vel=65)


def drive_perc(clip):
    perc_quarters(clip, vel=50)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 3 — INTENSIFY
#  Drive + ghost kicks + bass 16ths + open hats + louder pad + ride 8ths.
# ═══════════════════════════════════════════════════════════════════

def intensify_drums(clip):
    kick_foundation(clip)
    for beat in range(BEATS):
        if beat % 4 == 3:
            clip.add_note(KICK, beat + 0.75, 0.12, 60, False)
    hats_sixteenths(clip)
    snare_backbeat(clip)
    for bar in range(BARS):
        clip.add_note(OPEN_HAT, bar * 4 + 3.5, 0.5, 75, False)


def intensify_bass(clip):
    bass_sixteenths(clip, pitches_by_bar=[C2, C2, F2, C2])


def intensify_pad(clip):
    # C minor bars 1-2, shift to F minor bar 3-4 for movement
    for bar in range(2):
        for note in [C3, Eb3, G3]:
            clip.add_note(note, float(bar * 4), 4.0, 75, False)
    for bar in range(2, 4):
        for note in [F3, Ab3, C4]:
            clip.add_note(note, float(bar * 4), 4.0, 75, False)


def intensify_perc(clip):
    perc_eighths(clip, vel=55, accent_vel=65)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 — WIND DOWN
#  Transition: ghost kicks + open hats gone. Hats fade, snare thins,
#  bass goes from 16ths to 8ths. Pad sustains. Perc fades.
# ═══════════════════════════════════════════════════════════════════

def winddown_drums(clip):
    kick_foundation(clip)

    # 16th hats fading across bars
    for beat in range(BEATS):
        bar = beat // 4
        base = 85 - bar * 12  # 85, 73, 61, 49 — fading
        groove = [base, max(base - 30, 15), max(base - 12, 15), max(base - 25, 15)]
        for s in range(4):
            clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)

    # snare bars 1-2 only, then drops
    for bar in [0, 1]:
        clip.add_note(SNARE, float(bar * 4 + 1), 0.25, 100, False)
        clip.add_note(SNARE, float(bar * 4 + 3), 0.25, 100, False)


def winddown_bass(clip):
    for beat in range(BEATS):
        bar = beat // 4
        if bar < 2:
            # bars 1-2: 16ths (continuing from Intensify)
            vels = [100, 45, 70, 40]
            for s in range(4):
                clip.add_note(C2, beat + s * 0.25, 0.2, vels[s], False)
        else:
            # bars 3-4: 8ths (transitioning toward Breakdown)
            for i in range(2):
                start = beat + i * 0.5
                vel = 90 if i == 0 else 60
                clip.add_note(C2, start, 0.45, vel, False)


def winddown_pad(clip):
    pad_chord(clip, [C3, Eb3, G3], vel=65)


def winddown_perc(clip):
    # ride on quarters, fading
    for beat in range(BEATS):
        bar = beat // 4
        vel = 45 - bar * 8  # 45, 37, 29, 21
        clip.add_note(RIDE, float(beat), 0.5, max(vel, 15), False)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 5 — BREAKDOWN
#  Energy dips. Kick stays. Hats thin to 8ths. Bass sustains.
#  Pad becomes prominent — fills the space.
# ═══════════════════════════════════════════════════════════════════

def breakdown_drums(clip):
    kick_foundation(clip, velocity=95, accent=108)
    for beat in range(BEATS):
        clip.add_note(CLOSED_HAT, beat + 0.5, 0.2, 55, False)


def breakdown_bass(clip):
    clip.add_note(C2, 0.0, 4.0, 80, False)
    clip.add_note(Eb2, 4.0, 4.0, 75, False)
    clip.add_note(F2, 8.0, 4.0, 75, False)
    clip.add_note(C2, 12.0, 4.0, 80, False)


def breakdown_pad(clip):
    # prominent — fills the gap left by thinning drums
    pad_chord(clip, [C3, Eb3, G3], vel=90)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 6 — REBUILD
#  Hats build back, snare returns, bass ramps, pad settles.
# ═══════════════════════════════════════════════════════════════════

def rebuild_drums(clip):
    kick_foundation(clip)
    for beat in range(BEATS):
        bar = beat // 4
        if bar < 2:
            clip.add_note(CLOSED_HAT, beat + 0.5, 0.15, 65, False)
        else:
            groove = [85, 30, 60, 35]
            for s in range(4):
                clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)
    for bar in [2, 3]:
        clip.add_note(SNARE, float(bar * 4 + 1), 0.25, 100, False)
        clip.add_note(SNARE, float(bar * 4 + 3), 0.25, 100, False)


def rebuild_bass(clip):
    for beat in range(BEATS):
        bar = beat // 4
        if bar < 2:
            for i in range(2):
                start = beat + i * 0.5
                vel = 90 if i == 0 else 60
                clip.add_note(C2, start, 0.45, vel, False)
        else:
            vels = [105, 50, 75, 45]
            for s in range(4):
                clip.add_note(C2, beat + s * 0.25, 0.2, vels[s], False)


def rebuild_pad(clip):
    pad_chord(clip, [C3, Eb3, G3], vel=75)


# ═══════════════════════════════════════════════════════════════════
#  SCENE 7 — PEAK
#  Maximum intensity. Double kicks, loud hats, snare on 2/3/4,
#  open hats, aggressive bass with tritone, kick roll, full pad, perc.
# ═══════════════════════════════════════════════════════════════════

def peak_drums(clip):
    kick_foundation(clip, velocity=105, accent=118)
    for beat in range(BEATS):
        clip.add_note(KICK, beat + 0.5, 0.2, 65, False)
    hats_sixteenths(clip, groove=[100, 45, 80, 50])
    for bar in range(BARS):
        clip.add_note(SNARE, float(bar * 4 + 1), 0.25, 115, False)
        clip.add_note(SNARE, float(bar * 4 + 2), 0.25, 75, False)
        clip.add_note(SNARE, float(bar * 4 + 3), 0.25, 115, False)
    for bar in range(BARS):
        clip.add_note(OPEN_HAT, bar * 4 + 1.5, 0.5, 80, False)
        clip.add_note(OPEN_HAT, bar * 4 + 3.5, 0.5, 80, False)
    for i in range(8):
        pos = 15.0 + i * 0.125
        clip.add_note(KICK, pos, 0.1, 75 + i * 5, False)


def peak_bass(clip):
    bass_sixteenths(
        clip,
        pitches_by_bar=[C2, Eb2, Gb2, C2],
        accent=115, mid=82, ghost=55,
    )


def peak_pad(clip):
    # wide voicing for maximum presence
    pad_chord(clip, [C3, G3, Eb4], vel=85)


def peak_perc(clip):
    perc_eighths(clip, vel=70, accent_vel=80)
    # extra accent hits on bar downbeats
    for bar in range(BARS):
        clip.add_note(SHAKER, float(bar * 4), 0.25, 75, False)
        clip.add_note(SHAKER, bar * 4 + 2, 0.25, 60, False)


# ═══════════════════════════════════════════════════════════════════
#  SCENE TABLE
#  Each entry: (name, [(drum_fn, clip_name)], [(bass_fn, name)],
#                     [(pad_fn, name)], [(perc_fn, name)])
# ═══════════════════════════════════════════════════════════════════

SCENES = [
    # (name, drums, bass, pad, perc)
    ("Intro",
        [(intro_drums, "Kick Only")], [], [], []),
    ("Build",
        [(build_drums, "Hats Rise")],
        [(build_bass, "Bass Enter")],
        [(build_pad, "Pad Enter")],
        []),
    ("Drive",
        [(drive_drums, "Full Groove")],
        [(drive_bass, "Bass 8ths")],
        [(drive_pad, "Pad Full")],
        [(drive_perc, "Ride")]),
    ("Intensify",
        [(intensify_drums, "Ghost Kicks")],
        [(intensify_bass, "Bass 16ths")],
        [(intensify_pad, "Pad Move")],
        [(intensify_perc, "Ride 8ths")]),
    ("Wind Down",
        [(winddown_drums, "Hats Fade")],
        [(winddown_bass, "Bass Ease")],
        [(winddown_pad, "Pad Sustain")],
        [(winddown_perc, "Ride Fade")]),
    ("Breakdown",
        [(breakdown_drums, "Thin Hats")],
        [(breakdown_bass, "Sustain")],
        [(breakdown_pad, "Pad Big")],
        []),
    ("Rebuild",
        [(rebuild_drums, "Hats Return")],
        [(rebuild_bass, "Bass Ramp")],
        [(rebuild_pad, "Pad Settle")],
        []),
    ("Peak",
        [(peak_drums, "Peak Drums")],
        [(peak_bass, "Peak Bass")],
        [(peak_pad, "Pad Wide")],
        [(peak_perc, "Peak Perc")]),
]


def main():
    print("Connecting to Ableton Live...")
    set = live.Set()
    set.scan()

    set.tempo = BPM
    print(f"Tempo → {BPM} BPM")

    # ── Ensure tracks 2 and 3 are MIDI tracks ──
    # The default set has Audio tracks at positions 2-3 which can't host instruments.
    # Insert MIDI tracks at position 2 if needed (pushes Audio tracks right).
    created = 0
    for idx in [TRK_PAD, TRK_PERC]:
        if idx >= len(set.tracks) or set.tracks[idx].is_audio_track:
            set.create_midi_track(idx)
            created += 1
    if created > 0:
        set.scan()
        print(f"Created {created} new MIDI track(s) for Pad/Perc")

    drums = set.tracks[TRK_DRUMS]
    bass = set.tracks[TRK_BASS]
    pad = set.tracks[TRK_PAD]
    perc = set.tracks[TRK_PERC]

    # ── Track names ──
    live.cmd("/live/track/set/name", (TRK_DRUMS, "Drums"))
    live.cmd("/live/track/set/name", (TRK_BASS, "Bass"))
    live.cmd("/live/track/set/name", (TRK_PAD, "Pad"))
    live.cmd("/live/track/set/name", (TRK_PERC, "Perc"))

    # ── Mix levels ──
    drums.volume = 0.85   # 0 dB reference
    bass.volume = 0.80    # sits just under drums
    pad.volume = 0.60     # atmospheric, not dominant
    perc.volume = 0.70    # audible but supportive
    print("Mix levels set: Drums 0dB, Bass -2dB, Pad -12dB, Perc -6dB")

    # ── Build all scenes ──
    track_map = [
        (drums, TRK_DRUMS),
        (bass, TRK_BASS),
        (pad, TRK_PAD),
        (perc, TRK_PERC),
    ]

    for scene_idx, (scene_name, *builder_lists) in enumerate(SCENES):
        live.cmd("/live/scene/set/name", (scene_idx, scene_name))

        for (track, trk_idx), builders in zip(track_map, builder_lists):
            for builder_fn, clip_name in builders:
                clip = make_clip(track, trk_idx, scene_idx, BEATS, clip_name)
                builder_fn(clip)

        print(f"  Scene {scene_idx}: {scene_name}")

    print()
    print(f"Done! {len(SCENES)} scenes ready on 4 tracks.")
    print()
    print("Add instruments to the new tracks:")
    print("  Pad  → Instruments > Analog > pick a pad preset (e.g. Charry Pad)")
    print("  Perc → Drums > Drum Rack > pick a percussion kit")


if __name__ == "__main__":
    main()
