import live

def main():
    print("Connecting to Ableton Live...")
    try:
        set = live.Set()
        set.scan()

        print(f"Connected! Tempo: {set.tempo} BPM")
        print(f"Tracks ({len(set.tracks)}):")
        for i, track in enumerate(set.tracks):
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

if __name__ == "__main__":
    main()
