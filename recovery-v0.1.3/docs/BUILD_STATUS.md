# Build Status — v0.1.3 Recovery Candidate

Date: 2026-08-17 JST
Target: Kodi 22 "Piers", Windows first
Safety mode: read-only

## Implemented

- 2 Hz live Kodi telemetry sampler with rolling 30-second evidence windows.
- Kodi 22 live A/V bitrate and queue telemetry plus caching/playback state.
- CPU/RAM/temperature/decoder/video-format/display/network/PVR context.
- Read-only Windows CPU/GPU/driver/RAM/network inventory.
- Evidence-correlated diagnoses with exclusions and confidence.
- GOOD / DEGRADED / BAD / UNKNOWN status with telemetry-coverage gate.
- User "problem just happened" marker by symptom type.
- Cross-session provider/source-pattern correlation.
- Local bounded/redacted report storage.
- Kodi menu for live status, last report, problem marker and settings.
- Reproducible install ZIP and source ZIP builder.

## Automated validation

Recovery QA passed on 2026-09-01 NZST: **111 tests** plus compile, XML, static-safety, package, CRC and checksum gates. The migration carries the historical v0.1.2 audit test additions, but no v0.1.2 result is claimed for this new candidate.

Coverage must be re-measured for v0.1.3 before any promotion claim. UI/platform branches that require real Kodi/Windows remain lower and are explicitly covered by physical gates.

Coverage includes:
- canonical diagnoses;
- false-positive guardrails;
- missing/stale data quality;
- 800 randomized fixed-seed telemetry windows;
- credential/token URL privacy;
- corrupt report/history resilience;
- service lifecycle integration with fake Kodi modules;
- live warning and final persisted report integration;
- source/provider history logic;
- marker freshness;
- bitrate/localized-number parsing;
- ambiguous multi-adapter handling.

## Not yet certified

The current package is an **engineering alpha / physical-validation candidate**, not a finished release. Offline tests cannot prove:

- real Kodi 22 label behavior across every PVR/HLS/DASH/inputstream path;
- real Windows/Kodi runtime overhead;
- diagnosis accuracy against naturally occurring live-stream faults;
- device-specific driver/decoder quirks;
- Android behavior;
- direct perceptual pixelation/blocking analysis;
- stable public access to all dropped/skipped-frame and precise A/V error metrics.

These require the protected portable-mode physical test programme in `PHYSICAL_VALIDATION.md`.

## Promotion rule

Do not enable automatic optimization/settings changes in v0.1. Any future auto-fix must be safe, reversible, explicitly approved where appropriate, and promoted only after fault-injection testing proves both diagnosis and rollback behavior.

## Packaging/compliance note

The install ZIP now includes `LICENSE.txt`, uses the add-on's own profile for reports, contains no compiled bytecode, and passes local XML/package checks. It is **not yet an official Kodi repository submission candidate**: Team Kodi's current repository rules also require artwork and localization of user-visible strings. Those submission-specific tasks are intentionally downstream of physical playback validation.
