"""Record session clips into Arrangement View automatically.

Fires each scene for a set number of bars while Ableton records,
producing a complete linear arrangement.  Sends per-section volume
adjustments so the mix breathes with the arrangement.

Usage:
    uv run python arrange.py
"""

import time

import live

from config import BPM, TRK_BASS, TRK_DRUMS, TRK_PAD, TRK_PERC
from scenes import SCENES

# Derive base scene names from the scene definitions.
_BASE_NAMES = [name for name, _ in SCENES]

# --- Arrangement structure: (scene_index, bars, volume_overrides) ---

ARRANGEMENT = [
    (0, 8, {TRK_DRUMS: 0.00, TRK_PAD: 0.00}),  # Bass Intro
    (1, 8, {TRK_DRUMS: 0.80, TRK_PAD: 0.40}),  # Kick Enter
    (2, 16, {TRK_PAD: 0.50}),  # Build
    (3, 32, {TRK_PAD: 0.60, TRK_PERC: 0.65}),  # Drive
    (4, 32, {TRK_PAD: 0.65, TRK_PERC: 0.70}),  # Intensify
    (5, 8, {TRK_PAD: 0.65, TRK_PERC: 0.55}),  # Wind Down
    (6, 8, {TRK_PAD: 0.80, TRK_BASS: 0.90}),  # Breakdown
    (7, 8, {TRK_PAD: 0.65, TRK_BASS: 0.85}),  # Rebuild
    (8, 32, {TRK_PAD: 0.70, TRK_PERC: 0.75}),  # Peak
    (3, 16, {TRK_PAD: 0.60, TRK_PERC: 0.65}),  # Drive (cool down)
    (0, 8, {TRK_DRUMS: 0.00, TRK_PAD: 0.00, TRK_PERC: 0.00}),  # Outro
]

# First N labels come from scene names; extras are arrangement-specific.
SECTION_LABELS = _BASE_NAMES + [
    "Drive (Cool Down)",
    "Outro (Bass Solo)",
]


def _section_label(index, scene_idx):
    """Return the human-readable label for an arrangement section."""
    if index < len(SECTION_LABELS):
        return SECTION_LABELS[index]
    return _BASE_NAMES[scene_idx]


def _bars_to_seconds(bars):
    """Convert a bar count to seconds at the project BPM."""
    return bars * 4 * 60.0 / BPM


def main():
    """Record the arrangement into Ableton."""
    set_ = live.Set()
    set_.scan()

    total_bars = sum(bars for _, bars, _ in ARRANGEMENT)
    total_time = _bars_to_seconds(total_bars)

    print(f"Arrangement: {total_bars} bars ({total_time:.0f}s ~ {total_time / 60:.1f} min)")
    print()
    for i, (scene, bars, _) in enumerate(ARRANGEMENT):
        label = _section_label(i, scene)
        print(f"  {label:22s}  {bars:3d} bars  ({_bars_to_seconds(bars):.1f}s)")
    print()

    set_.current_song_time = 0.0

    input("Press Enter to start recording (make sure you're in Session View)...")
    print()

    live.cmd("/live/song/set/record_mode", (1,))
    time.sleep(0.1)

    for i, (scene, bars, volumes) in enumerate(ARRANGEMENT):
        label = _section_label(i, scene)
        print(f">> {label} ({bars} bars)...")

        for trk_idx, vol in volumes.items():
            live.cmd("/live/track/set/volume", (trk_idx, vol))

        live.cmd("/live/scene/fire", (scene,))
        time.sleep(_bars_to_seconds(bars))

    set_.stop_playing()
    live.cmd("/live/song/set/record_mode", (0,))

    print()
    print("Done! Press Tab to switch to Arrangement View and see your song.")


if __name__ == "__main__":
    main()
