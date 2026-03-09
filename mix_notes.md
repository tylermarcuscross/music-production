# Mix Notes

Manual Ableton settings that live outside the scripts.
Update this file whenever you change effects, EQ, or routing.

## Signal Chains

### Track 0 — Drums (909 Core Kit)

| Position | Device | Key Settings |
|----------|--------|-------------|
| 1 | **EQ Eight** | See EQ table below |
| 2 | **Compressor** | Ratio 4:1, Attack 10 ms, Release 100 ms, Knee 0 dB, GR target -3 to -4 dB |
| 3 | Saturator | Default |
| 4 | Drum Buss | Default |

### Track 1 — Bass (Dual OSC Plastic Bass)

| Position | Device | Key Settings |
|----------|--------|-------------|
| 1 | Dual OSC Plastic Bass | Synth (no changes) |
| 2 | **EQ Eight** | See EQ table below |
| 3 | Pedal | Distortion |
| 4 | Auto Filter | Sidechain enabled; Frequency automated by arrange.py |
| 5 | Overdrive | Default |
| 6 | Compressor | Default |

### Track 2 — Pad (Glass Low Strings)

| Position | Device | Key Settings |
|----------|--------|-------------|
| 1 | Glass Low Strings | Synth (no changes) |
| 2 | **EQ Eight** | See EQ table below |

### Track 3 — Perc (909 Core Kit — Ride + Rimshot)

| Position | Device | Key Settings |
|----------|--------|-------------|
| 1 | 909 Core Kit | Ride + Rimshot only |
| 2 | **EQ Eight** | See EQ table below |

## EQ Eight Settings

### Drums

| Band | Type | Freq | Gain | Q | Purpose |
|------|------|------|------|---|---------|
| 1 | High-pass 12 | 30 Hz | — | 0.7 | Remove sub-rumble below kick |
| 4 | Bell | 350 Hz | -3 dB | 1.0 | Cut boxiness |
| 6 | Bell | 4,000 Hz | +2 dB | 0.8 | Snap/presence on snare and hats |

### Bass

| Band | Type | Freq | Gain | Q | Purpose |
|------|------|------|------|---|---------|
| 1 | High-pass 12 | 30 Hz | — | 0.7 | Cut sub-rumble |
| 3 | Bell | 250 Hz | -3 dB | 1.0 | Carve room for kick |
| 5 | Bell | 800 Hz | +1.5 dB | 0.8 | Midrange definition |

### Pad

| Band | Type | Freq | Gain | Q | Purpose |
|------|------|------|------|---|---------|
| 1 | High-pass 12 | 200 Hz | — | 0.7 | Clear low end for kick/bass |
| 3 | Bell | 500 Hz | -2 dB | 1.0 | Reduce low-mid mud |
| 6 | Bell | 8,000 Hz | +2 dB | 0.7 | Shimmer/air |

### Perc

| Band | Type | Freq | Gain | Q | Purpose |
|------|------|------|------|---|---------|
| 1 | High-pass 12 | 300 Hz | — | 0.7 | Cut unused low end |
| 4 | Bell | 1,000 Hz | -2 dB | 1.0 | Tame rimshot boxiness |
| 6 | Bell | 5,000 Hz | +2 dB | 0.8 | Crack/snap presence |

## Default Mix Levels

| Track | Volume (0-1) | dB |
|-------|-------------|-----|
| Drums | 0.80 | -1.9 |
| Bass | 0.85 | -1.4 |
| Pad | 0.60 | -4.4 |
| Perc | 0.70 | -3.1 |

## Panning

| Track | Pan | Why |
|-------|-----|-----|
| Drums | **Center (C)** | Kick and snare must stay centered for club systems |
| Bass | **Center (C)** | Low frequencies always centered |
| Pad | **Center (C)** | Use Utility device with Width > 100% for stereo spread instead of pan |
| Perc | **15R** | Slight right offset gives the ride/rimshot its own space |

## Compression

### Drums — Compressor

| Parameter | Value |
|-----------|-------|
| Ratio | 4:1 |
| Attack | 10 ms |
| Release | 100 ms |
| Knee | 0 dB (hard) |
| Threshold | Adjust for -3 to -4 dB gain reduction |
| Output | Match bypass volume |

### Bass — Sidechain

Sidechain compression via Auto Filter (pumping effect). No additional compressor added.

### Master — Glue Compressor

| Parameter | Value |
|-----------|-------|
| Ratio | 2:1 |
| Attack | 10 ms |
| Release | Auto |
| Threshold | Adjust for -1.5 to -2.5 dB gain reduction |
| Range | -6 dB |
| Makeup | Match bypass volume (~+2 dB) |
| Soft Clip | On |
