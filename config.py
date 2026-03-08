"""Shared constants for the industrial techno project.

All MIDI note mappings, tempo, bar length, and track indices live here
so that every other module imports from one place.
"""

# --- Tempo and time ---
BPM = 136
BARS = 4
BEATS = BARS * 4

# --- Track indices (Session View column order) ---
TRK_DRUMS = 0
TRK_BASS = 1
TRK_PAD = 2
TRK_PERC = 3

TRACK_NAMES = {
    TRK_DRUMS: "Drums",
    TRK_BASS: "Bass",
    TRK_PAD: "Pad",
    TRK_PERC: "Perc",
}

# --- Drum notes (General MIDI / Drum Rack) ---
KICK = 36  # C1
SNARE = 38  # D1
CLOSED_HAT = 42  # F#1
OPEN_HAT = 46  # Bb1

# --- Bass notes (C minor palette) ---
SUB_C = 36  # C1 sub-bass octave drop (same MIDI note as KICK)
Bb1 = 46  # minor 7th below root
C2 = 48  # root
D2 = 50  # passing tone
Eb2 = 51  # minor 3rd
F2 = 53  # perfect 4th
Gb2 = 54  # tritone
G2 = 55  # perfect 5th

# --- Pad notes (C minor voicings) ---
C3 = 60
Eb3 = 63
F3 = 65
G3 = 67
Ab3 = 68
C4 = 72
Eb4 = 75

# --- Perc notes (Drum Rack pads) ---
RIDE = 36  # pad 1
SHAKER = 38  # pad 2
