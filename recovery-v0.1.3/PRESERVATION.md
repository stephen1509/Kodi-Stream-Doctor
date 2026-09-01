# Preservation Checkpoint — Kodi Stream Doctor v0.1.1

Date: 2026-08-17 JST
Target: Kodi 22 Piers, Windows first
Safety mode: read-only

## Verified state

- Maintained automated suite: 94 passing tests.
- Approximate production-code coverage: 90%.
- Deterministic diagnosis engine: 100% statement coverage.
- Full compile/XML/static-safety/package/checksum QA: PASS.
- Physical Kodi 22 validation: NOT YET COMPLETED.
- Automatic optimization/settings mutation: NOT ENABLED.

## Canonical release artifacts

- Install ZIP: `dist/service.streamdoctor-0.1.1.zip`
- Source ZIP: `dist/kodi-stream-doctor-source-0.1.1.zip`
- Install ZIP SHA-256: `adf02dcc6a827c98bea574e3a7807b89c2282963fe740f3416e00dceb303ddf4`
- Source ZIP SHA-256 is recorded in `dist/kodi-stream-doctor-source-0.1.1.zip.sha256` after each reproducible build.

## Preservation rule

The expanded source tree is canonical for development. Release ZIPs are reproducible using `tools/build_zip.py` and must be regenerated and re-checked after source changes. Do not treat the physical-validation candidate as a finished Kodi release until the gates in `docs/PHYSICAL_VALIDATION.md` pass.
