"""Reusable MIDI pattern builders for each instrument track.

Each public method takes configuration parameters and returns a builder
function ``(clip) -> None``.  Scenes compose these by calling e.g.
``drums.full_groove()`` to get a builder they slot into the scene grid.
"""

from config import BARS, BEATS, CLOSED_HAT, KICK, OPEN_HAT, RIDE, SHAKER, SNARE

# --- Drum helpers ---


def _kick_foundation(clip, velocity=100, accent=115):
    for beat in range(BEATS):
        vel = accent if beat % 4 == 0 else velocity
        clip.add_note(KICK, float(beat), 0.5, vel, False)


def _hats_sixteenths(clip, groove=None):
    if groove is None:
        groove = [95, 35, 70, 40]
    for beat in range(BEATS):
        for s in range(4):
            clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)


def _snare_backbeat(clip, velocity=110):
    for bar in range(BARS):
        clip.add_note(SNARE, float(bar * 4 + 1), 0.25, velocity, False)
        clip.add_note(SNARE, float(bar * 4 + 3), 0.25, velocity, False)


# --- drums ---


class drums:
    """Drum pattern builders (Drum Rack on track 0)."""

    @staticmethod
    def kick_only(velocity=100, accent=115):
        """Four-on-the-floor kick, nothing else."""

        def build(clip):
            _kick_foundation(clip, velocity, accent)

        return build

    @staticmethod
    def with_hats(hat_groove=None, rising=False):
        """Kick + hi-hats.  If *rising*, hat velocity grows each bar."""

        def build(clip):
            _kick_foundation(clip)
            if rising:
                for beat in range(BEATS):
                    bar = beat // 4
                    base = 40 + bar * 13
                    groove = [base, max(base - 25, 15), max(base - 10, 15), max(base - 22, 15)]
                    for s in range(4):
                        clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)
            else:
                _hats_sixteenths(clip, hat_groove)

        return build

    @staticmethod
    def full_groove(hat_groove=None, snare_vel=110):
        """Kick + 16th hats + snare backbeat."""

        def build(clip):
            _kick_foundation(clip)
            _hats_sixteenths(clip, hat_groove)
            _snare_backbeat(clip, snare_vel)

        return build

    @staticmethod
    def intensify(ghost_kick_beats=None):
        """Full groove + ghost kicks on beat-4 'and' + open hats."""
        if ghost_kick_beats is None:
            ghost_kick_beats = [b for b in range(BEATS) if b % 4 == 3]

        def build(clip):
            _kick_foundation(clip)
            for beat in ghost_kick_beats:
                clip.add_note(KICK, beat + 0.75, 0.12, 60, False)
            _hats_sixteenths(clip)
            _snare_backbeat(clip)
            for bar in range(BARS):
                clip.add_note(OPEN_HAT, bar * 4 + 3.5, 0.5, 75, False)

        return build

    @staticmethod
    def wind_down(snare_bars=2):
        """Kick + hats fading out + partial snare."""

        def build(clip):
            _kick_foundation(clip)
            for beat in range(BEATS):
                bar = beat // 4
                base = 85 - bar * 12
                groove = [base, max(base - 30, 15), max(base - 12, 15), max(base - 25, 15)]
                for s in range(4):
                    clip.add_note(CLOSED_HAT, beat + s * 0.25, 0.1, groove[s], False)
            for bar in range(snare_bars):
                clip.add_note(SNARE, float(bar * 4 + 1), 0.25, 100, False)
                clip.add_note(SNARE, float(bar * 4 + 3), 0.25, 100, False)

        return build

    @staticmethod
    def breakdown(hat_vel=55):
        """Kick + sparse offbeat hats, stripped back."""

        def build(clip):
            _kick_foundation(clip, velocity=95, accent=108)
            for beat in range(BEATS):
                clip.add_note(CLOSED_HAT, beat + 0.5, 0.2, hat_vel, False)

        return build

    @staticmethod
    def rebuild():
        """Bars 1-2 offbeat hats, bars 3-4 full 16ths + snare."""

        def build(clip):
            _kick_foundation(clip)
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

        return build

    @staticmethod
    def peak(kick_vel=105, kick_accent=118):
        """Maximum intensity: double kick, loud hats, extra snares, fill."""

        def build(clip):
            _kick_foundation(clip, velocity=kick_vel, accent=kick_accent)
            for beat in range(BEATS):
                clip.add_note(KICK, beat + 0.5, 0.2, 65, False)
            _hats_sixteenths(clip, groove=[100, 45, 80, 50])
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

        return build


# --- bass ---


class bass:
    """Bass pattern builders (synth on track 1).

    Three pattern types that graduate naturally:
      motif   -- free-form spacious hits (intro scenes)
      eighths -- driving 8th-note pulse with pitch contour (main body)
      sustain -- whole-note holds (breakdown)
    """

    @staticmethod
    def motif(notes_data):
        """Free-form bass motif from explicit note data.

        Args:
            notes_data: List of (pitch, start, duration, velocity) tuples.
        """

        def build(clip):
            for pitch, start, dur, vel in notes_data:
                clip.add_note(pitch, start, dur, vel, False)

        return build

    @staticmethod
    def eighths(shape, bars=BARS, vel_on=100, vel_off=65, accent_non_root=10):
        """Driving 8th-note pulse with a repeating pitch contour.

        Args:
            shape: List of 8 pitches, one per 8th note within a bar.
            bars: How many bars to fill.
            vel_on: Velocity for downbeat 8ths (even indices).
            vel_off: Velocity for upbeat 8ths (odd indices).
            accent_non_root: Extra velocity for non-root pitches.
        """

        def build(clip):
            for bar in range(bars):
                for i, pitch in enumerate(shape):
                    start = bar * 4 + i * 0.5
                    vel = vel_on if i % 2 == 0 else vel_off
                    if pitch != shape[0] and accent_non_root:
                        vel = min(vel + accent_non_root, 127)
                    clip.add_note(pitch, start, 0.4, vel, False)

        return build

    @staticmethod
    def sustain(pitches_per_bar, vel=80):
        """Whole-note holds, one pitch sustained per bar.

        Args:
            pitches_per_bar: List of pitches (cycles if shorter than BARS).
            vel: Note velocity.
        """

        def build(clip):
            for bar in range(BARS):
                pitch = pitches_per_bar[bar % len(pitches_per_bar)]
                clip.add_note(pitch, float(bar * 4), 4.0, vel, False)

        return build


# --- pad ---


class pad:
    """Pad pattern builders (pad synth on track 2)."""

    @staticmethod
    def chord(notes, vel=65):
        """Whole-bar sustained chord, repeated each bar.

        Args:
            notes: List of MIDI pitches.
            vel: Note velocity.
        """

        def build(clip):
            for bar in range(BARS):
                for note in notes:
                    clip.add_note(note, float(bar * 4), 4.0, vel, False)

        return build

    @staticmethod
    def moving_chord(chords_per_half, vel=75):
        """Chord changes every 2 bars (two chords across 4 bars).

        Args:
            chords_per_half: Two note-lists, e.g. [[C3, Eb3, G3], [F3, Ab3, C4]].
            vel: Note velocity.
        """

        def build(clip):
            for half_idx, notes in enumerate(chords_per_half):
                for bar in range(2):
                    for note in notes:
                        clip.add_note(note, float((half_idx * 2 + bar) * 4), 4.0, vel, False)

        return build


# --- perc ---


class perc:
    """Percussion pattern builders (Drum Rack on track 3)."""

    @staticmethod
    def quarters(vel=50):
        """Ride on every quarter note."""

        def build(clip):
            for beat in range(BEATS):
                clip.add_note(RIDE, float(beat), 0.5, vel, False)

        return build

    @staticmethod
    def eighths(vel=60, accent_vel=None):
        """Ride on every 8th note with optional accent on downbeats."""
        if accent_vel is None:
            accent_vel = vel

        def build(clip):
            for beat in range(BEATS):
                clip.add_note(RIDE, float(beat), 0.4, accent_vel, False)
                clip.add_note(RIDE, beat + 0.5, 0.2, vel, False)

        return build

    @staticmethod
    def eighths_with_shaker(ride_vel=70, ride_accent=80, shaker_vel=75, shaker_offbeat_vel=60):
        """Ride 8ths + shaker on beats 1 and 3 of each bar."""

        def build(clip):
            for beat in range(BEATS):
                clip.add_note(RIDE, float(beat), 0.4, ride_accent, False)
                clip.add_note(RIDE, beat + 0.5, 0.2, ride_vel, False)
            for bar in range(BARS):
                clip.add_note(SHAKER, float(bar * 4), 0.25, shaker_vel, False)
                clip.add_note(SHAKER, bar * 4 + 2, 0.25, shaker_offbeat_vel, False)

        return build

    @staticmethod
    def fading_quarters():
        """Ride quarters with velocity decreasing each bar."""

        def build(clip):
            for beat in range(BEATS):
                bar = beat // 4
                vel = 45 - bar * 8
                clip.add_note(RIDE, float(beat), 0.5, max(vel, 15), False)

        return build
