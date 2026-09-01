# Validation Strategy

## Current offline status

The current engineering prototype passes **111 deterministic unit/adversarial/integration tests**, including an 800-case fixed-seed randomized telemetry suite. This is not a substitute for physical Kodi testing.

## Offline gates

1. Unit tests for parsers, redaction, retention, history and diagnosis rules.
2. False-positive tests: healthy playback must not be diagnosed as bad; high CPU alone must not become a causal CPU diagnosis; comfortable memory must not trigger RAM advice; a large Internet plan must not create a network fault.
3. Synthetic fault scenarios: starvation, CPU saturation, software decoding, RAM pressure, refresh mismatch, audio-only starvation, PVR errors, LAN/WAN capacity margin.
4. User-marker tests for picture/audio/A-V/source-quality problem windows.
5. Privacy tests with credentialed/tokenized stream URLs.
6. Corrupt-history/report resilience.
7. Python compile gate.
8. XML parse gate.
9. ZIP structure/install-package gate.
10. Secret/URL logging scan.
11. Randomized invariant testing for score/confidence bounds and crash resistance.
12. Repeated full-suite runs to catch accidental state/order dependence.
13. Offline diagnosis micro-benchmark (informational only; not a physical runtime certification).
14. End-to-end fake-Kodi service integration: startup, sampling, live warning, final report, persistence and privacy boundaries.

## False-positive principles

- High CPU with advancing playback is a headroom risk, not proof of failure.
- High temperature at low load is not called throttling.
- 100-Mbit LAN is not called inadequate for a ~10-Mbit stream.
- 10-Gbit subscription does not imply healthy delivery and does not create a fault finding on a healthy stream.
- Multiple active adapter speeds are not guessed into a route attribution.
- Low bitrate is not called poor visual quality unless the user marks a picture-quality problem.
- Audio passthrough is not blamed unless the user marks an audio/A-V problem and queues remain healthy.

## Physical gates (still required)

Offline tests cannot prove Kodi/driver/platform behavior. Before a release-quality claim:

- Windows + Kodi 22: healthy H.264, HEVC, 25/50/59.94/60 fps, interlaced Live TV, deliberately weak source, Wi-Fi/Ethernet comparison, software-decoder case if reproducible.
- Confirm the new Kodi 22 bitrate/queue labels behave as expected across PVR, HLS/DASH and other representative live-stream paths.
- Validate user markers against visibly observed freeze, stutter, audio and A/V events.
- Measure the service itself; target <1 percentage point average CPU overhead at default 2 Hz sampling on the first Windows test system.
- Verify report paths, retention, localization, notifications, disable/uninstall behavior and recovery from malformed/unsupported labels.
- Compare diagnoses against Kodi Player Process Info/debug evidence and controlled fault injections.
- Android/Android TV + Kodi 22 gets separate gates and is not considered certified from Windows results.
