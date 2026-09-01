# Stream Doctor v0.1 Architecture

## Principle

Diagnosis is a causal-evidence problem, not a settings-tweaking problem. The system separates: source/upstream delivery, WAN capacity/stability, LAN link, Kodi input/cache/queues, decoder/CPU/GPU, memory/thermal pressure, and display cadence.

## Layers

1. **KodiTelemetryReader** — 2 Hz lightweight reads of official Kodi labels/conditions.
2. **WindowsInspector** — one slow, read-only PowerShell/CIM snapshot at service start; failure never disables Kodi telemetry.
3. **SessionAnalyzer** — bounded in-memory session samples and 30-second live windows.
4. **Diagnosis engine** — deterministic multi-signal rules with explicit evidence, confidence and exclusions.
5. **Scoring** — component scores plus overall score; component scores remain visible so one failure is not hidden.
6. **Storage** — bounded local JSON reports; no raw stream URL/token capture.

## Why no active speed test during playback

A saturating speed test can create its own contention and invalidate the observation. v0.1 records the subscribed plan and an optional capacity figure from a deliberate idle-time test, while using Kodi's live bitrate/queue behavior as passive playback evidence. Jitter/loss probing belongs in a later controlled diagnostic mode.

## Why no auto-fix yet

An optimizer that changes cache, refresh, drivers or networking before its diagnosis is validated can turn one problem into several. v0.1 has a hard read-only boundary. Future changes must be classified as observe-only, recommend-only, safe/reversible, or never automatic.
