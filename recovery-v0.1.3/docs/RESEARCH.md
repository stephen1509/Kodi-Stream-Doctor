# Research Findings — Kodi 22 Piers baseline

## Confirmed primary-source facts

- Kodi 22 Beta 1 tag: `22.0b1-Piers`, commit `77395cf42e141000b0475b8d5a54925ad67bfeba`.
- Kodi 22 publicly exposes live audio/video bitrate plus audio/video queue level and queue-data level through `Player.Process(...)` InfoLabels.
- Kodi's `PlayerGUIInfo.cpp` maps those labels directly to `DataCacheCore` live bitrate/queue getters.
- `DataCacheCore` also carries decoder name/HW status, deinterlace method, pixel format, dimensions, FPS, scan/interlace state and audio process details.
- Kodi's Python Player API provides playback callbacks including `onAVStarted`, `onAVChange`, playback stop/end/error; the service prototype uses polling for portability and keeps callbacks as a future enhancement.
- Windows `Get-NetAdapterStatistics` provides adapter errors/discards; v0.1 inventories them read-only at service startup.
- Android's `MediaCodecInfo.VideoCapabilities` can test width/height/frame-rate support and API 29+ performance points; this is the basis for a later Android-native capability bridge rather than guessing codec ability from model names.

## Important non-findings

- A subscribed 1/2/10-Gbps plan is not evidence of stable delivery to a specific streaming server.
- Driver "oldness" is not proof of causality. A driver recommendation requires hardware/codec/decoder evidence and, later, a trustworthy current-version source.
- Temperature alone is not proof of throttling.
- A low bitrate is not automatically poor picture quality because codec efficiency and source content differ.

## Active network-test architecture decision

- Passive playback monitoring must not run a saturating speed test beside the stream it is trying to diagnose.
- M-Lab NDT7 is a credible future deliberate throughput-test option: M-Lab documents NDT as its common third-party integration test, and NDT7 uses WebSockets with separate download/upload tests. Kodi's standard Python runtime does not provide a built-in NDT7 client, so v0.1 does not silently bundle or invent one.
- RFC 6349 treats TCP throughput as a separate measurement from latency/loss/jitter integrity and notes that severe loss/jitter can make throughput results misleading.
- Therefore Stream Doctor keeps **Live Monitor** read-only/passive and reserves future **Full Diagnostic** network load tests for an explicit user action while playback is idle.
