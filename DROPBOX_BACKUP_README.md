# Kodi Stream Doctor — Dropbox Preservation

Canonical checkpoint: v0.1.1, 2026-08-17 JST.
Target: Kodi 22 Piers, Windows first. Safety mode: read-only.

This Dropbox folder preserves the tested project even if GitHub publication is temporarily unavailable.

## Contents

- `README.md` — project overview and install/testing notes.
- `PRESERVATION.md` — checkpoint and promotion boundaries.
- `BUILD_STATUS.md` — latest verified build/test state.
- `PHYSICAL_VALIDATION.md` — real Kodi 22 test programme.
- `Releases/` — release-preservation files.
- `Source/` — source-preservation files.
- `Git/` — Git checkpoint information.
- `CHECKSUMS.txt` — SHA-256 values for the canonical local artifacts.

## Git checkpoint

The project is initialized locally as a Git repository on `main` at commit:

`c59f64480e5748803b1d7ad0cec9d76eafe8e1d3`

A dedicated private GitHub repository should be named `stephen1509/kodi-stream-doctor`.

## GitHub publication status

The connected GitHub integration can write to existing repositories but does not expose repository creation, and the working environment has no authenticated `gh` CLI. I therefore did not place this project into an unrelated repository merely to force a GitHub write. The source/checkpoint is preserved here so the exact project can be pushed as soon as the dedicated repository exists.
