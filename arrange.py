"""
Records the session clips into Arrangement View automatically.

Fires each scene for a set number of bars while Ableton records,
producing a complete linear arrangement. Sends per-section volume
adjustments so the pad and bass breathe with the arrangement.
"""

import live
import time

BPM = 136

# Track indices (must match techno_track.py)
TRK_DRUMS = 0
TRK_BASS = 1
TRK_PAD = 2
TRK_PERC = 3

# (scene_index, bars, volume_overrides)
# volume_overrides: dict of {track_idx: volume} sent at section start
ARRANGEMENT = [
    (0, 16,  {TRK_PAD: 0.00}),                         # Intro: no pad yet
    (1, 16,  {TRK_PAD: 0.50}),                         # Build: pad sneaks in
    (2, 32,  {TRK_PAD: 0.60, TRK_PERC: 0.65}),        # Drive: full groove
    (3, 32,  {TRK_PAD: 0.65, TRK_PERC: 0.70}),        # Intensify
    (4, 8,   {TRK_PAD: 0.65, TRK_PERC: 0.55}),        # Wind Down: perc fades
    (5, 8,   {TRK_PAD: 0.80, TRK_BASS: 0.75}),        # Breakdown: pad prominent
    (6, 8,   {TRK_PAD: 0.65, TRK_BASS: 0.80}),        # Rebuild: rebalance
    (7, 32,  {TRK_PAD: 0.70, TRK_PERC: 0.75}),        # Peak: everything up
    (2, 16,  {TRK_PAD: 0.60, TRK_PERC: 0.65}),        # Drive (cool down)
    (0, 8,   {TRK_PAD: 0.00, TRK_PERC: 0.00}),        # Outro: strip to kick
]

SCENE_NAMES = [
    "Intro", "Build", "Drive", "Intensify",
    "Wind Down", "Breakdown", "Rebuild", "Peak",
    "Drive (Cool Down)", "Outro",
]


def bars_to_seconds(bars):
    return bars * 4 * 60.0 / BPM


def main():
    set = live.Set()
    set.scan()

    total_bars = sum(bars for _, bars, _ in ARRANGEMENT)
    total_time = bars_to_seconds(total_bars)

    print(f"Arrangement: {total_bars} bars ({total_time:.0f}s ≈ {total_time/60:.1f} min)")
    print()
    for i, (scene, bars, _) in enumerate(ARRANGEMENT):
        label = SCENE_NAMES[i] if i < len(SCENE_NAMES) else f"Scene {scene}"
        print(f"  {label:20s}  {bars:3d} bars  ({bars_to_seconds(bars):.1f}s)")
    print()

    set.current_song_time = 0.0

    input("Press Enter to start recording (make sure you're in Session View)...")
    print()

    live.cmd("/live/song/set/record_mode", (1,))
    time.sleep(0.1)

    for i, (scene, bars, volumes) in enumerate(ARRANGEMENT):
        label = SCENE_NAMES[i] if i < len(SCENE_NAMES) else f"Scene {scene}"
        print(f"▶ {label} ({bars} bars)...")

        # apply volume overrides for this section
        for trk_idx, vol in volumes.items():
            live.cmd("/live/track/set/volume", (trk_idx, vol))

        live.cmd("/live/scene/fire", (scene,))
        time.sleep(bars_to_seconds(bars))

    set.stop_playing()
    live.cmd("/live/song/set/record_mode", (0,))

    print()
    print("Done! Press Tab to switch to Arrangement View and see your song.")


if __name__ == "__main__":
    main()
