# Kodi Stream Doctor v0.1.2 — Release Manifest

Date: 2026-08-17 JST
Status: physical-validation candidate
Target: Kodi 22 Piers, Windows first
Safety mode: read-only

## Exact tested install candidate

Filename: `service.streamdoctor-0.1.2.zip`
Size: 31,893 bytes
SHA-256:

`022063c36ab7893d56f236101e72e542028d1ce849763059898832467480d46b`

This checksum is the authority for the package to install in the isolated Kodi 22 physical-validation environment.

## Reproducibility

The install ZIP is generated deterministically from the canonical v0.1.2 source by `tools/build_zip.py`; `python3 tools/qa.py` performs compilation, XML validation, 111 tests, static safety checks, ZIP structure/CRC checks and package/internal version validation.

The canonical Dropbox source reconstruction is documented in `Source/v0.1.2/PATCH_MANIFEST.md`.

## Noncanonical artifact notice

`service.streamdoctor-0.1.2.zip.b64.part-01.txt` is an **incomplete early preservation attempt**. It is not a complete archive and must not be used for installation or reconstruction. It remains only as audit history and is superseded by this manifest plus the canonical source reconstruction process.

## Release gate

v0.1.2 has not yet completed physical Kodi 22 validation. It must not be described as a final production release until representative PVR/HLS/DASH/live-TV testing, runtime-overhead measurement, real fault reproduction and diagnosis-accuracy review are completed.
