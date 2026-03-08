"""Deploy scenes to Ableton Live, or check the connection.

Handles all communication with Ableton via pylive/OSC: connecting,
ensuring tracks/scenes exist, clearing old clips, and writing new ones.

Usage:
    uv run python deploy.py          # push all scenes to Session View
    uv run python deploy.py --check  # test Ableton connection only
"""

import sys
import time

import live

from config import (
    BEATS,
    BPM,
    TRACK_NAMES,
    TRK_BASS,
    TRK_DRUMS,
    TRK_PAD,
    TRK_PERC,
)
from scenes import SCENES

TRACK_ORDER = ["drums", "bass", "pad", "perc"]
TRACK_INDICES = {
    "drums": TRK_DRUMS,
    "bass": TRK_BASS,
    "pad": TRK_PAD,
    "perc": TRK_PERC,
}


def _clear_slot(track, slot):
    """Delete a clip from a slot, ignoring errors if empty."""
    try:
        track.delete_clip(slot)
        time.sleep(0.05)
    except Exception:
        pass


def _make_clip(track, track_idx, slot, length, name):
    """Clear a slot, create a looping clip, and return it."""
    _clear_slot(track, slot)
    clip = track.create_clip(slot, float(length))
    live.cmd("/live/clip/set/name", (track_idx, slot, name))
    live.cmd("/live/clip/set/looping", (track_idx, slot, 1))
    return clip


def deploy(scenes, mix=None):
    """Connect to Ableton and deploy a list of scenes.

    Args:
        scenes: List of (name, dict) tuples.  Each dict maps track keys
            ("drums", "bass", "pad", "perc") to (clip_name, builder_fn).
        mix: Optional track-key -> volume (0.0-1.0) dict.
    """
    print("Connecting to Ableton Live...")
    set_ = live.Set()
    set_.scan()

    set_.tempo = BPM
    print(f"Tempo -> {BPM} BPM")

    # Ensure Pad and Perc slots are MIDI tracks
    created = 0
    for idx in [TRK_PAD, TRK_PERC]:
        if idx >= len(set_.tracks) or set_.tracks[idx].is_audio_track:
            set_.create_midi_track(idx)
            created += 1
    if created > 0:
        set_.scan()
        print(f"Created {created} new MIDI track(s) for Pad/Perc")

    tracks = {
        "drums": set_.tracks[TRK_DRUMS],
        "bass": set_.tracks[TRK_BASS],
        "pad": set_.tracks[TRK_PAD],
        "perc": set_.tracks[TRK_PERC],
    }

    for key, name in TRACK_NAMES.items():
        live.cmd("/live/track/set/name", (key, name))

    if mix is None:
        mix = {"drums": 0.80, "bass": 0.85, "pad": 0.60, "perc": 0.70}
    for key, vol in mix.items():
        tracks[key].volume = vol
    print(f"Mix: {', '.join(f'{k}={v:.2f}' for k, v in mix.items())}")

    # Ensure enough scenes exist
    needed = len(scenes)
    while set_.num_scenes < needed:
        set_.create_scene(-1)
        set_.scan()
    print(f"Scenes available: {set_.num_scenes} (need {needed})")

    # Clear old clips in every slot we're about to write
    for slot in range(needed):
        for trk in tracks.values():
            _clear_slot(trk, slot)
    print("Cleared old clips")

    # Build scenes
    for scene_idx, (scene_name, clip_map) in enumerate(scenes):
        live.cmd("/live/scene/set/name", (scene_idx, scene_name))

        for key in TRACK_ORDER:
            if key not in clip_map:
                continue
            clip_name, builder_fn = clip_map[key]
            trk_idx = TRACK_INDICES[key]
            clip = _make_clip(tracks[key], trk_idx, scene_idx, BEATS, clip_name)
            builder_fn(clip)

        print(f"  Scene {scene_idx}: {scene_name}")

    print()
    print(f"Done! {len(scenes)} scenes ready on {len(tracks)} tracks.")


def check_connection():
    """Test the Ableton Live / AbletonOSC connection and print diagnostics."""
    print("Connecting to Ableton Live...")
    try:
        set_ = live.Set()
        set_.scan()

        print(f"Connected! Tempo: {set_.tempo} BPM")
        print(f"Tracks ({len(set_.tracks)}):")
        for i, track in enumerate(set_.tracks):
            clip_count = sum(1 for c in track.clips if c is not None)
            device_count = len(track.devices)
            print(f"  [{i}] {track.name}  ({clip_count} clips, {device_count} devices)")
    except Exception as e:
        print(f"Could not connect to Ableton Live: {e}")
        print()
        print("Make sure:")
        print("  1. Ableton Live 11+ is running")
        print("  2. AbletonOSC is installed as a Control Surface")
        print("     (Preferences > Link/Tempo/MIDI > Control Surface)")


def main():
    """CLI entry point."""
    if "--check" in sys.argv:
        check_connection()
        return

    deploy(SCENES)


if __name__ == "__main__":
    main()
