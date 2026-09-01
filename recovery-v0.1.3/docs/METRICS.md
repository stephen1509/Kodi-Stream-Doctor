# Stream Doctor Measurement & Diagnostic Metrics

Stream Doctor treats diagnostics as a data-quality and causal-attribution problem. A measurement is useful only when its provenance, unit, freshness and limitations are known.

## Data-quality states

Every signal belongs to one of four states conceptually:

- **Known** — directly observed from Kodi or a supported platform API during the relevant window.
- **Missing** — the platform/API did not expose the value. Missing is never silently converted to zero.
- **Stale/contextual** — useful inventory captured outside the exact failure window (for example a Windows startup hardware snapshot).
- **Inferred** — a conclusion produced by correlating multiple known signals. Inference is always surfaced with confidence and evidence.

## Primary playback measurements

| Metric | Source | Normal use | Important limitation |
|---|---|---|---|
| Video live bitrate | Kodi 22 `Player.Process(VideoLiveBitrate)` | Detect collapses; estimate stream capacity need | Bitrate alone does not measure visual quality |
| Audio live bitrate | Kodi 22 `Player.Process(AudioLiveBitrate)` | Audio capacity/context | Codec efficiency varies |
| Video queue / data level | Kodi 22 process labels | Detect starvation vs healthy input | Queue behavior depends on playback pipeline |
| Audio queue / data level | Kodi 22 process labels | Isolate audio-only starvation | Low queue must be interpreted with video/cache evidence |
| Caching state | Kodi `Player.Caching` | Corroborate delivery starvation | Caching is a symptom, not a source attribution |
| Playback time | Kodi Player API | Detect prolonged non-paused stalls | Some live/PVR modes may expose time differently |
| Hardware decoder active | Kodi `Player.Process(videohwdecoder)` | Distinguish HW vs software decode | False does not by itself prove a problem |
| Decoder / codec / dimensions / FPS | Kodi labels | Quantify decode workload | Codec profile/bit depth may add complexity not yet captured |
| CPU usage | Kodi system label | Compute-pressure evidence | High CPU alone is not causal |
| Free memory | Kodi system label | Detect severe memory pressure | Low free memory needs temporal/problem correlation before hardware advice |
| CPU/GPU temperature | Kodi system labels | Thermal-risk evidence | Temperature alone is not throttling proof |
| CPU frequency | Kodi system label | Corroborate possible throttling | Dynamic frequency scaling is normal |
| Display refresh | Kodi screen info | Detect cadence mismatch | Driver/display modes may be rounded |
| Network link rate | Kodi link info; unambiguous platform context fallback | Capacity-margin check | Link rate is not throughput, jitter or packet loss |
| PVR BER/UNC/signal/status | Kodi PVR labels | Strong tuner/backend input evidence | Applicability depends on PVR backend/input type |
| Internet plan Mbps | User setting | Rule out simplistic headline-speed claims | Subscription tier is not measured path performance |
| Known tested capacity Mbps | User setting | Capacity-margin context | Must come from a deliberate separate test; may become stale |

## Diagnostic KPIs for development

These are engineering acceptance metrics, not user-facing health scores.

1. **Synthetic healthy false-causal-diagnosis rate:** 0 across the maintained healthy scenario suite.
2. **Known fault detection:** every deliberately encoded canonical fault has at least one matching diagnosis test.
3. **Confidence bounds:** every emitted finding has confidence 0–100.
4. **Score bounds:** every component and overall health score remains 0–100 under randomized input.
5. **Missing-data safety:** unsupported/missing signals must not cause a crash or be silently treated as evidence of failure.
6. **Privacy leakage:** raw stream credentials, paths, signed/token query data and fragments must not appear in persisted reports.
7. **Purchase-advice guardrail:** no CPU/RAM/Internet-plan upgrade recommendation may be promoted solely from one utilization/tier number.
8. **Runtime overhead target:** physical validation should show the 2 Hz monitor adds <1 percentage point average CPU load on the first Windows target during representative playback. This target cannot be certified in offline tests.
9. **Unknown-diagnosis honesty:** when evidence only proves starvation, the engine must not invent server-vs-ISP-vs-LAN attribution.

## Health score interpretation

Component evidence scores are intentionally separate. The overall score is a summary, not the diagnosis. A stream can have excellent device/RAM/decoder scores and a poor delivery score. Recommendations are driven by findings/evidence, never by the overall number alone.

## Measurement cadence

The default Kodi sampling interval is 500 ms (2 Hz). Live diagnosis uses a rolling 30-second window, while session history retains the strongest evidence from short fault windows so a brief freeze is not averaged away by a long healthy tail.

## Do-not-infer rules

- Do not infer Internet stability from 1/2/10-Gbps subscription speed.
- Do not infer driver causality from driver age alone.
- Do not infer insufficient RAM while memory remains comfortable.
- Do not infer a weak CPU from high utilization unless an actual playback problem/stall is corroborated.
- Do not infer source visual quality from resolution alone or bitrate alone.
- Do not infer a LAN bottleneck from an unrelated/ambiguous active network adapter.
- Do not infer thermal throttling from temperature alone.

## Component-score honesty

Unsupported component telemetry is omitted from component evidence scores rather than represented as 100/100. A score of 100 means no adverse evidence was found in a component that had relevant measurements; it does not certify every possible failure mode in that subsystem.
