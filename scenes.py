"""Scene definitions for the industrial techno track.

This is the Session View grid: each scene is a row, each track key
is a column.  Scenes compose pattern builders from patterns.py with
specific parameters.  Edit this file to reshape the track.

Pitch shapes share the C-Eb-F palette so the ear tracks continuity.
Each shape changes only 1-2 pitches from the previous.
"""

from config import C2, C3, C4, F2, F3, G3, Ab3, Eb2, Eb3, Eb4, Gb2
from patterns import bass, drums, pad, perc

# --- Bass motif data: (pitch, start, duration, velocity) ---
# Spacious, syncopated -- the recognizable hook of the track.

INTRO_MOTIF = [
    # Bar 1: root establishes
    (C2, 0.0, 1.5, 105),
    (C2, 2.5, 0.3, 90),
    (Eb2, 3.0, 0.75, 95),
    # Bar 2: same shape, F replaces Eb
    (C2, 4.0, 1.5, 105),
    (C2, 6.5, 0.3, 90),
    (F2, 7.0, 0.75, 95),
    # Bar 3: energy rises, more hits
    (C2, 8.0, 0.75, 100),
    (Eb2, 9.0, 0.4, 90),
    (F2, 9.5, 0.5, 95),
    (Eb2, 10.5, 0.4, 85),
    (C2, 11.0, 0.75, 90),
    # Bar 4: tritone tension -> resolve
    (C2, 12.0, 1.0, 105),
    (Gb2, 14.0, 0.75, 100),
    (F2, 15.0, 0.3, 85),
    (C2, 15.5, 0.5, 80),
]

KICK_ENTER_MOTIF = [
    # Slight variation on the intro motif
    (C2, 0.0, 1.5, 105),
    (Eb2, 2.0, 0.3, 85),
    (C2, 2.5, 0.3, 90),
    (Eb2, 3.0, 0.75, 95),
    (C2, 4.0, 1.5, 105),
    (C2, 6.0, 0.3, 80),
    (C2, 6.5, 0.3, 90),
    (F2, 7.0, 0.75, 95),
    (C2, 8.0, 0.75, 100),
    (Eb2, 9.0, 0.4, 90),
    (F2, 9.5, 0.5, 95),
    (Eb2, 10.5, 0.4, 85),
    (C2, 11.0, 0.75, 90),
    (C2, 12.0, 1.0, 105),
    (Gb2, 14.0, 0.75, 100),
    (F2, 15.0, 0.3, 85),
    (C2, 15.5, 0.5, 80),
]

# --- 8th-note pitch shapes (8 pitches = 1 bar of 8ths) ---
# Each shape evolves by changing only 1-2 pitches from the previous.

SHAPE_SIMPLE = [C2, C2, C2, C2, C2, C2, Eb2, C2]  # Build: mostly root
SHAPE_DRIVE = [C2, C2, Eb2, C2, C2, C2, F2, C2]  # Drive / Rebuild
SHAPE_DARK = [C2, C2, Eb2, C2, C2, F2, Gb2, C2]  # Intensify / Peak

# --- Breakdown sustain pitches (one per bar) ---
BREAKDOWN_PITCHES = [C2, Eb2, F2, C2]

# --- Scene grid ---
# Each entry: (scene_name, {track_key: (clip_name, builder), ...})
# Missing track keys = empty slot (no clip).

SCENES = [
    # 0: Bass Intro -- solo bass, no drums
    (
        "Bass Intro",
        {
            "bass": ("Bass Solo", bass.motif(INTRO_MOTIF)),
        },
    ),
    # 1: Kick Enter -- kick joins, bass motif continues
    (
        "Kick Enter",
        {
            "drums": ("Kick In", drums.kick_only()),
            "bass": ("Bass Motif", bass.motif(KICK_ENTER_MOTIF)),
            "pad": ("Pad Whisper", pad.chord([C3, G3], vel=35)),
        },
    ),
    # 2: Build -- hats rise, bass transitions to steady 8ths
    (
        "Build",
        {
            "drums": ("Hats Rise", drums.with_hats(rising=True)),
            "bass": ("Bass Pulse", bass.eighths(SHAPE_SIMPLE, vel_on=85, vel_off=55)),
            "pad": ("Pad Enter", pad.chord([C3, G3], vel=50)),
        },
    ),
    # 3: Drive -- full groove, 8ths with pitch contour
    (
        "Drive",
        {
            "drums": ("Full Groove", drums.full_groove()),
            "bass": ("Bass Drive", bass.eighths(SHAPE_DRIVE)),
            "pad": ("Pad Full", pad.chord([C3, Eb3, G3])),
            "perc": ("Ride", perc.quarters()),
        },
    ),
    # 4: Intensify -- same 8th rhythm, higher velocity + darker shape
    (
        "Intensify",
        {
            "drums": ("Ghost Kicks", drums.intensify()),
            "bass": ("Bass Intensify", bass.eighths(SHAPE_DARK, vel_on=115, vel_off=75)),
            "pad": ("Pad Move", pad.moving_chord([[C3, Eb3, G3], [F3, Ab3, C4]])),
            "perc": ("Ride 8ths", perc.eighths(vel=55, accent_vel=65)),
        },
    ),
    # 5: Wind Down -- velocity fading
    (
        "Wind Down",
        {
            "drums": ("Hats Fade", drums.wind_down()),
            "bass": ("Bass Ease", bass.eighths(SHAPE_DRIVE, vel_on=85, vel_off=55)),
            "pad": ("Pad Sustain", pad.chord([C3, Eb3, G3])),
            "perc": ("Ride Fade", perc.fading_quarters()),
        },
    ),
    # 6: Breakdown -- whole-note bass, pad forward
    (
        "Breakdown",
        {
            "drums": ("Thin Hats", drums.breakdown()),
            "bass": ("Sustain", bass.sustain(BREAKDOWN_PITCHES)),
            "pad": ("Pad Big", pad.chord([C3, Eb3, G3], vel=90)),
        },
    ),
    # 7: Rebuild -- 8ths return with Drive contour
    (
        "Rebuild",
        {
            "drums": ("Hats Return", drums.rebuild()),
            "bass": ("Bass Return", bass.eighths(SHAPE_DRIVE, vel_on=90, vel_off=60)),
            "pad": ("Pad Settle", pad.chord([C3, Eb3, G3], vel=75)),
        },
    ),
    # 8: Peak -- max intensity, darkest shape, same 8th rhythm
    (
        "Peak",
        {
            "drums": ("Peak Drums", drums.peak()),
            "bass": ("Peak Bass", bass.eighths(SHAPE_DARK, vel_on=120, vel_off=80)),
            "pad": ("Pad Wide", pad.chord([C3, G3, Eb4], vel=85)),
            "perc": ("Peak Perc", perc.eighths_with_shaker()),
        },
    ),
]
