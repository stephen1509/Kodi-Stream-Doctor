# Physical Validation Plan — Windows + Kodi 22 Piers

## Objective

Prove that Stream Doctor's measurements and diagnoses correspond to what actually happens on a real Kodi 22 Windows system, while leaving the user's everyday Kodi installation and known-good playback settings untouched.

## Safety boundary

- Use a separate **Kodi 22 portable-mode** installation on Windows.
- Install it in a writable folder outside Program Files.
- Launch that installation only through a shortcut whose target ends in `-p`.
- Confirm the separate `portable_data` directory exists before installing Stream Doctor or configuring streams.
- Do not copy, overwrite or edit the everyday Kodi profile.
- Do not change existing cache/advancedsettings during the first validation round.
- Stream Doctor v0.1 remains read-only.

## Pre-flight evidence

Record, without secrets:

- Kodi version/build;
- Windows version;
- CPU model/core count;
- installed RAM;
- GPU model and installed driver version;
- active network adapter type and link speed where unambiguous;
- Internet subscription tier in Mbps, if known;
- deliberately measured Internet capacity only if the measurement was made separately from playback.

Do not record IPTV usernames/passwords, authorization headers, signed query strings, cookies or raw stream URLs.

## Test matrix

### A. Healthy baseline

Use at least one stream that appears subjectively stable for several minutes.

Expected result:
- status GOOD when telemetry coverage is sufficient;
- no high-confidence notification;
- queues/bitrate remain broadly healthy;
- no invented CPU/RAM/network cause.

### B. Known weak/bad source

Use a stream that visibly freezes, buffers or breaks up if available.

Expected result:
- user can press **Mark problem → Freeze/stutter/audio/A-V/quality** immediately after the event;
- the rolling 30-second evidence window captures the event;
- Stream Doctor explains what the evidence proves and what remains ambiguous.

### C. Same channel, different source/provider

Where legitimately available, compare two sources for the same/similar content.

Expected result:
- repeated source/provider-specific starvation strengthens a source/provider pattern;
- healthy alternatives reduce the probability that CPU/RAM/display are the primary cause.

### D. Frame-rate/display cadence

Exercise representative 25/50 and 29.97/59.94/60 fps content.

Expected result:
- clean integer/standard cadence is not falsely flagged;
- deliberate mismatch is reported as a display-cadence risk, not a network fault.

### E. Interlaced Live TV

Use 576i/1080i content if available.

Expected result:
- scan type and deinterlace method are captured;
- deinterlacing is not blamed merely because content is interlaced;
- an explicit disabled deinterlacer plus a user-marked video-quality problem produces only a conservative advisory.

### F. Decode pressure

If safely reproducible, test a demanding stream that falls back to software decoding.

Expected result:
- software decoding/high CPU without an observed playback fault is only a headroom warning;
- software decoding + high CPU + actual stall/marker + healthy input path can become a causal decoder/device diagnosis;
- no hardware purchase recommendation is made from CPU utilization alone.

### G. Ethernet vs Wi-Fi

Where practical, compare the same stream under each connection type without changing unrelated Kodi settings.

Expected result:
- link capacity is treated separately from Internet-plan speed and from delivery stability;
- ambiguous multi-adapter routing remains UNKNOWN rather than guessed.

### H. Kodi Internet-state interruption

If a natural local/ISP interruption occurs, capture it; do not intentionally disrupt a production router unless separately approved.

Expected result:
- Kodi's own Internet-unavailable state only corroborates a connectivity diagnosis when it overlaps the starvation window.

## Runtime-overhead gate

Compare representative playback with Stream Doctor disabled vs enabled at the default 500 ms (2 Hz) interval.

Target for the first Windows machine: **<1 percentage point increase in average CPU utilization** attributable to the monitor over a comparable observation period. Also check that enabling the add-on does not introduce visible stutter, audio breakup, excessive disk writes or notification spam.

The existing offline micro-benchmark measures only the deterministic diagnosis function and is not a substitute for this gate.

## Report QA

For each test:

1. Open **Stream Doctor → Last completed report**.
2. Verify GOOD/DEGRADED/BAD/UNKNOWN is plausible.
3. Verify telemetry coverage honestly reflects missing labels.
4. Check each finding's evidence, exclusions and recommendation.
5. Verify no raw stream URL/token/credential appears in the report.
6. Compare with Kodi Player Process Info/debug evidence when a discrepancy needs investigation.

## Promotion criteria

v0.1 is not release-certified until:

- healthy real streams avoid false causal diagnoses;
- representative real faults are detected or honestly left UNKNOWN;
- Kodi 22 live bitrate/queue labels behave consistently on the tested stream paths;
- Windows inventory and route ambiguity fail safely;
- privacy/retention behavior is confirmed on-device;
- runtime-overhead target is met or sampling is adjusted;
- any physical-test defect is reproduced, fixed and regression-tested.

Android/Android TV requires a separate promotion programme and is not certified by Windows success.
