# Diagnostic Evidence Matrix — v0.1

| Cause / hypothesis | Direct evidence available now | Corroboration | v0.1 verdict strength | Action / status |
|---|---|---|---|---|
| Incoming stream starvation | Kodi caching + A/V queue collapse + live bitrate collapse | CPU/memory remain comfortable | Strong for starvation; not always enough to separate server vs Internet/LAN | Implemented: compare sources; later stability test |
| CPU saturation | CPU near saturation + actual playback stall/user problem marker + healthy input | decoder/workload context | Strong when corroborated | Implemented |
| Software decode limitation | HW decoder false + demanding format + high CPU + observed problem | healthy input queues | Strong | Implemented |
| Software decode headroom risk | HW decoder false + demanding format + high CPU but no confirmed fault | none | Advisory only | Implemented; explicitly not causal |
| RAM pressure | free memory <=5% | repeatability/problem timing | Medium | Implemented; no RAM purchase claim from comfortable memory |
| Refresh mismatch | video FPS and screen Hz not clean integer cadence | otherwise healthy playback | Strong for cadence/judder risk | Implemented |
| Thermal/throttling risk | >=90 C under heavy load | large clock reduction vs reported max | Medium; stronger with clock evidence | Implemented |
| LAN capacity bottleneck | Kodi-reported link, or exactly one unambiguous active adapter, <1.5x stream bitrate | live stream bitrate | Strong capacity warning | Implemented conservatively |
| WAN capacity bottleneck | user-supplied deliberate measured capacity <1.5x bitrate | stream bitrate | Strong capacity warning | Implemented |
| Headline plan is too slow | plan tier vs actual bitrate | none | **Never inferred from plan alone** | Implemented guardrail |
| Audio-only starvation | audio queue collapses while video queue remains healthy | little/no general caching | Strong isolation toward audio track/path | Implemented |
| Audio passthrough/output problem | user marks audio/A-V issue + healthy queues + passthrough active | comparison with passthrough disabled | Plausible, not proven | Implemented advisory |
| PVR/tuner/input signal fault | PVR BER/UNC/low-signal telemetry | user marker or starvation | Strong when backend telemetry applies | Implemented |
| Heavy source compression / poor source quality | user marks poor picture + extremely low bitrate for frame size | cross-source comparison | Medium only | Implemented conservative advisory |
| Bad provider/server | repeated starvation isolated to one provider/source | healthy reports from other identifiable sources | Stronger with repeated history | Implemented cross-session correlation |
| Kodi reports Internet unavailable | Kodi InternetState false overlapping queue/cache starvation | Internet-stream context | Strong corroboration for local/router/ISP path; not source-server proof | Implemented |
| Interlaced video with deinterlacing disabled | interlaced scan + explicit none/off deinterlacer + user-marked video/quality problem | stream otherwise characterized | Medium advisory | Implemented |
| Missing core telemetry | insufficient bitrate/queue/system coverage | coverage score | Must not be called GOOD | Implemented: UNKNOWN / not rated |
| Packet loss/jitter | not directly measured in v0.1 | queue/bitrate symptoms | Unknown/ambiguous | Planned controlled stability probe |
| Outdated driver is causal | installed driver version obtainable on Windows | decoder failure/capability evidence | Do not claim from age alone | Planned vendor-specific advisory layer |
| Multiple active adapters / route attribution | adapter inventory available | Kodi link label may disambiguate | Unknown if Kodi link is absent | v0.1 refuses to guess |
| Dropped/skipped rendered frames | Kodi internal debug path exists, but v0.1 does not assume a stable public Python label | other render evidence | Unknown unless exposed/verified | Continue Kodi 22 API audit |
| Precise A/V sync error | internal player/debug evidence exists, stable Python path not yet verified | user marker/audio evidence | Partial/unknown | Continue API audit |
| Perceptual pixelation/blocking/blur | no verified decoded-frame feed in Python v0.1 | bitrate + user marker are only indirect | Cannot directly measure | Native/companion research track |
| Android codec capability | Android MediaCodec APIs can expose support/performance | Kodi runtime evidence | Not in v0.1 Windows prototype | Planned Android bridge |
