# Stream Doctor Development Roadmap

## v0.1 — Kodi 22 read-only diagnostic core (current engineering prototype)

- Kodi 22 live A/V bitrate and queue telemetry.
- Cache/playback-stall correlation.
- CPU, memory, temperature and display-cadence context.
- Hardware-decoder and demanding-format evidence.
- PVR signal/error evidence.
- Internet subscription tier and optional deliberate measured capacity kept separate.
- Windows read-only hardware/driver/network inventory.
- User “problem just happened” marker with problem type.
- Bounded local reports and cross-session source/provider pattern detection.
- No automatic settings changes.

Release gate: physical Windows Kodi 22 validation on real good/bad streams plus measured monitor overhead.

## v0.2 — Controlled network stability diagnostics

Add an explicit diagnostic mode, separate from passive playback monitoring:

- local gateway reachability/latency;
- low-bandwidth public latency/delay-variation/loss probes;
- route/path context where safely available;
- session-specific network-adapter error/discard deltas;
- full throughput testing only when the user deliberately requests it and Kodi playback is idle.

Goal: separate source/server, Internet path and home-network hypotheses more confidently without creating the fault through a saturating speed test.

## v0.3 — Windows advanced device diagnostics

- Route-aware active adapter attribution.
- Supported GPU/video engine utilization counters where reliable.
- Power-plan/power-mode advisory evidence.
- Better driver inventory and vendor-specific update advisory, while refusing to claim that an old driver is causal without playback evidence.
- Optional controlled comparison tests (hardware decode on/off where safe and user-approved).

## v0.4 — Android / Android TV first-class capability bridge

- MediaCodec hardware/software decoder inventory.
- `VideoCapabilities` size/rate support.
- API 29+ codec performance points where available.
- Android build/device/thermal/network context using supported APIs.
- Independent physical promotion gates; Windows success does not automatically certify Android.

## Later research tracks

### Render-quality evidence
Kodi's public Python surface does not currently give v0.1 a verified, stable decoded-frame feed for perceptual analysis. Pixelation/blocking/blur detection therefore needs a carefully designed native/companion path or another supported frame-access method. Stream Doctor must not fake a perceptual-quality score from bitrate alone.

### Dropped/skipped frames and A/V error
Kodi internally exposes richer Player Process Info/debug data, but v0.1 does not depend on an unverified public Python interface for dropped/skipped-frame counters or precise A/V error. Continue source/API research and add only when a stable supported path is proven.

### Recommendation-to-fix progression
Recommendations will be classified as:

1. observe only;
2. recommend only;
3. safe/reversible change with explicit user approval;
4. never automatic.

No automatic optimization is promoted until diagnosis accuracy survives controlled physical fault injection and rollback behavior is proven.
