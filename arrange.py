"""Record session clips into Arrangement View with smart transitions.

Instead of firing full scenes, fires individual clips per track with
staggered timing at transitions.  Ramps volumes smoothly and automates
the bass Auto Filter frequency at key moments.

Usage:
    uv run python arrange.py
"""

import time

import live

from config import BPM, TRK_BASS, TRK_DRUMS, TRK_PAD, TRK_PERC

ALL_TRACKS = [TRK_DRUMS, TRK_BASS, TRK_PAD, TRK_PERC]

DEFAULT_MIX = {
    TRK_DRUMS: 0.80,
    TRK_BASS: 0.85,
    TRK_PAD: 0.60,
    TRK_PERC: 0.70,
}

# --- Arrangement structure ---
# Each section is a dict with:
#   scene  -- which scene's clips to play
#   bars   -- total duration
#   mix    -- target volumes (unmentioned tracks keep previous value)
#   transition (optional) -- bars: overlap duration, lead: tracks that switch early
#   filter (optional) -- start/end: normalized Auto Filter frequency (0.0-1.0)

ARRANGEMENT = [
    {
        "label": "Bass Intro",
        "scene": 0,
        "bars": 8,
        "mix": {TRK_DRUMS: 0.0, TRK_PAD: 0.0, TRK_PERC: 0.0},
    },
    {
        "label": "Kick Enter",
        "scene": 1,
        "bars": 8,
        "mix": {TRK_DRUMS: 0.80, TRK_PAD: 0.40},
        "transition": {"bars": 2, "lead": [TRK_DRUMS]},
    },
    {
        "label": "Build",
        "scene": 2,
        "bars": 16,
        "mix": {TRK_PAD: 0.50},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
        "filter": {"start": 0.2, "end": 0.6},
    },
    {
        "label": "Drive",
        "scene": 3,
        "bars": 32,
        "mix": {TRK_PAD: 0.60, TRK_PERC: 0.65},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
    },
    {
        "label": "Intensify",
        "scene": 4,
        "bars": 32,
        "mix": {TRK_PAD: 0.65, TRK_PERC: 0.70},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
        "filter": {"start": 0.6, "end": 0.8},
    },
    {
        "label": "Wind Down",
        "scene": 3,
        "bars": 8,
        "mix": {TRK_PAD: 0.65, TRK_PERC: 0.55},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
        "filter": {"start": 0.8, "end": 0.5},
    },
    {
        "label": "Breakdown",
        "scene": 5,
        "bars": 8,
        "mix": {TRK_PAD: 0.80, TRK_BASS: 0.90},
        "transition": {"bars": 2, "lead": [TRK_BASS, TRK_PAD]},
        "filter": {"start": 0.5, "end": 0.2},
    },
    {
        "label": "Rebuild",
        "scene": 3,
        "bars": 8,
        "mix": {TRK_PAD: 0.65, TRK_BASS: 0.85},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
        "filter": {"start": 0.2, "end": 0.6},
    },
    {
        "label": "Peak",
        "scene": 6,
        "bars": 32,
        "mix": {TRK_PAD: 0.70, TRK_PERC: 0.75},
        "transition": {"bars": 4, "lead": [TRK_BASS, TRK_DRUMS]},
        "filter": {"start": 0.6, "end": 0.9},
    },
    {
        "label": "Drive (Cool Down)",
        "scene": 3,
        "bars": 16,
        "mix": {TRK_PAD: 0.60, TRK_PERC: 0.65},
        "transition": {"bars": 2, "lead": [TRK_BASS]},
        "filter": {"start": 0.9, "end": 0.5},
    },
    {
        "label": "Outro",
        "scene": 0,
        "bars": 8,
        "mix": {TRK_DRUMS: 0.0, TRK_PAD: 0.0, TRK_PERC: 0.0},
        "transition": {"bars": 4, "lead": [TRK_DRUMS, TRK_PERC]},
        "filter": {"start": 0.5, "end": 0.1},
    },
]


# --- Helpers ---


def _bars_to_seconds(bars):
    """Convert a bar count to seconds at the project BPM."""
    return bars * 4 * 60.0 / BPM


def _fire_clip(trk_idx, scene_idx):
    """Fire a clip slot.  Empty slots stop the track (intended behavior)."""
    live.cmd("/live/clip_slot/fire", (trk_idx, scene_idx))


def _set_volume(trk_idx, vol):
    """Set a track's volume immediately."""
    live.cmd("/live/track/set/volume", (trk_idx, vol))


def _lerp(a, b, t):
    """Linear interpolation from a to b at progress t (0.0-1.0)."""
    return a + (b - a) * t


def _find_auto_filter(bass_track_idx):
    """Discover the Auto Filter's device and Frequency parameter indices.

    Returns:
        (device_idx, param_idx) or None if not found.
    """
    try:
        resp = live.query("/live/track/get/num_devices", (bass_track_idx,))
        num_devices = resp[1]
    except Exception:
        return None

    for dev_idx in range(num_devices):
        try:
            resp = live.query("/live/device/get/name", (bass_track_idx, dev_idx))
            name = str(resp[2]).lower()
        except Exception:
            continue

        if "auto filter" not in name:
            continue

        try:
            resp = live.query("/live/device/get/parameters/name", (bass_track_idx, dev_idx))
            param_names = resp[2:]
        except Exception:
            continue

        for param_idx, pname in enumerate(param_names):
            if str(pname).lower() == "frequency":
                return (dev_idx, param_idx)

    return None


def _set_filter(bass_track_idx, device_idx, param_idx, value):
    """Set the Auto Filter frequency (0.0-1.0 normalized)."""
    live.cmd(
        "/live/device/set/parameter/value",
        (bass_track_idx, device_idx, param_idx, float(value)),
    )


def _wait_with_updates(seconds, update_fns=None):
    """Sleep for a duration while sending parameter updates at regular intervals.

    Args:
        seconds: Total time to wait.
        update_fns: List of callables that accept progress (0.0-1.0).
    """
    if seconds <= 0:
        return
    if not update_fns:
        time.sleep(seconds)
        return

    steps = max(int(seconds * 2), 4)
    step_time = seconds / steps
    for step in range(steps):
        progress = step / max(steps - 1, 1)
        for fn in update_fns:
            fn(progress)
        time.sleep(step_time)


# --- Main ---
 

def main():
    """Record the arrangement into Ableton with smart transitions."""
    set_ = live.Set()
    set_.scan()

    # Print arrangement overview
    total_bars = sum(s["bars"] for s in ARRANGEMENT)
    total_time = _bars_to_seconds(total_bars)
    print(f"Arrangement: {total_bars} bars ({total_time:.0f}s ~ {total_time / 60:.1f} min)")
    print()
    for s in ARRANGEMENT:
        trans = s.get("transition")
        filt = s.get("filter")
        flags = []
        if trans:
            flags.append(f"lead {trans['bars']}b")
        if filt:
            flags.append(f"filter {filt['start']:.1f}->{filt['end']:.1f}")
        extra = f"  [{', '.join(flags)}]" if flags else ""
        print(f"  {s['label']:22s}  {s['bars']:3d} bars{extra}")
    print()

    # Discover Auto Filter on bass track
    filter_info = _find_auto_filter(TRK_BASS)
    if filter_info:
        filt_dev, filt_param = filter_info
        print(f"Auto Filter found: device {filt_dev}, param {filt_param}")
    else:
        print("Auto Filter not found on bass track -- filter automation disabled")
    print()

    set_.current_song_time = 0.0
    input("Press Enter to start recording (make sure you're in Session View)...")
    print()

    live.cmd("/live/song/set/record_mode", (1,))
    time.sleep(0.1)

    current_mix = dict(DEFAULT_MIX)

    for i, section in enumerate(ARRANGEMENT):
        scene = section["scene"]
        bars = section["bars"]
        label = section["label"]
        target_mix = section.get("mix", {})
        transition = section.get("transition")
        filter_cfg = section.get("filter") if filter_info else None

        # Look ahead: does the NEXT section have a transition?
        next_section = ARRANGEMENT[i + 1] if i + 1 < len(ARRANGEMENT) else None
        next_trans = next_section.get("transition") if next_section else None

        # --- Fire clips for this section ---
        if transition and i > 0:
            # Lead clips were already fired during previous section's tail.
            # Now fire the remaining clips (non-lead tracks).
            lead_set = set(transition.get("lead", []))
            for trk in ALL_TRACKS:
                if trk not in lead_set:
                    _fire_clip(trk, scene)
            # Finalize volume targets (ramp already brought us close)
            for trk, vol in target_mix.items():
                _set_volume(trk, vol)
                current_mix[trk] = vol
            print(f">> {label} ({bars} bars) [remaining clips fired]")
        else:
            # First section or no transition: fire all clips at once.
            for trk in ALL_TRACKS:
                _fire_clip(trk, scene)
            for trk, vol in target_mix.items():
                _set_volume(trk, vol)
                current_mix[trk] = vol
            print(f">> {label} ({bars} bars)")

        # --- Compute body duration (before transition tail starts) ---
        trans_tail_bars = next_trans["bars"] if next_trans else 0
        body_bars = bars - trans_tail_bars

        # --- Build filter automation for the body ---
        body_updates = []
        filter_body_end = None
        if filter_cfg:
            filt_start = filter_cfg["start"]
            filt_end = filter_cfg["end"]
            body_frac = body_bars / bars if bars > 0 else 1.0
            filter_body_end = _lerp(filt_start, filt_end, body_frac)

            def _make_filter_fn(f_start, f_end):
                def fn(progress):
                    _set_filter(TRK_BASS, filt_dev, filt_param, _lerp(f_start, f_end, progress))

                return fn

            body_updates.append(_make_filter_fn(filt_start, filter_body_end))

        # --- Play the body ---
        _wait_with_updates(_bars_to_seconds(body_bars), body_updates)

        # --- Transition tail into next section ---
        if next_trans and next_section:
            next_scene = next_section["scene"]
            next_label = next_section["label"]
            lead_tracks = next_trans.get("lead", [])

            # Fire lead clips from the next section
            for trk in lead_tracks:
                _fire_clip(trk, next_scene)
            print(
                f"   ~ transition: {lead_tracks} lead into {next_label} ({trans_tail_bars} bars)"
            )

            # Build volume ramp from current mix toward next mix
            next_mix = next_section.get("mix", {})
            vol_start = dict(current_mix)
            vol_end = dict(current_mix)
            for trk, vol in next_mix.items():
                vol_end[trk] = vol

            tail_updates = []

            def _make_vol_fn(v_start, v_end):
                def fn(progress):
                    for trk in ALL_TRACKS:
                        if abs(v_start[trk] - v_end[trk]) > 0.01:
                            _set_volume(trk, _lerp(v_start[trk], v_end[trk], progress))

                return fn

            tail_updates.append(_make_vol_fn(vol_start, vol_end))

            # Continue filter automation through the tail
            if filter_cfg and filter_body_end is not None:
                tail_updates.append(_make_filter_fn(filter_body_end, filter_cfg["end"]))

            # Play the transition
            _wait_with_updates(_bars_to_seconds(trans_tail_bars), tail_updates)

            # Update current mix state
            for trk, vol in next_mix.items():
                current_mix[trk] = vol

    # Stop
    set_.stop_playing()
    live.cmd("/live/song/set/record_mode", (0,))

    print()
    print("Done! Press Tab to switch to Arrangement View.")
    print("You can now edit automation curves and clip boundaries manually.")


if __name__ == "__main__":
    main()
