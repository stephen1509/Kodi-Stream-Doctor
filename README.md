# Kodi Stream Doctor — Kodi 22 Piers

Stream Doctor is a read-only Kodi 22 service add-on that monitors live playback telemetry, detects evidence patterns behind freezing/stutter/judder/audio interruption, and produces conservative diagnoses and recommendations.

## v0.1 safety boundary

- **No automatic setting changes.** It does not edit Kodi cache/advancedsettings, Diggz, Windows, drivers, router, network adapter, or power settings.
- **No bulk speed test while a stream is playing.** Subscription tier and an optional user-supplied measured capacity are treated separately from delivery stability.
- **Local-only reports.** Max 20 files, 20 MiB total, 4 MiB/file. Raw stream URLs, query strings, authorization headers, cookies and tokens are not stored.
- **Unknown remains unknown.** A rule only makes a diagnosis when its required evidence is present.

## Kodi 22 telemetry used

The core consumes Kodi 22's official `Player.Process(...)` live bitrate/queue labels plus decoder, FPS, dimensions, scan type, deinterlacing, system CPU/memory/temperature, network link and display information. The add-on warns when run on Kodi <22 because the key queue/bitrate labels are new in Piers.

## Current diagnosis rules

- incoming-media starvation (source/server/Internet/LAN/input path)
- CPU saturation
- demanding software decoding / absent hardware decoder
- low free memory
- frame-rate / refresh-rate mismatch
- thermal/throttling risk when corroborating evidence exists
- LAN capacity margin
- measured WAN capacity margin
- nominal Internet-plan speed explicitly *not* being the explanation when raw capacity is ample
- audio-only starvation and passthrough/output-path advisories
- PVR signal/error evidence
- conservative low-bitrate/source-compression advisory only when the user marks poor picture quality
- repeated provider/source failure correlation across saved sessions

## Install for physical validation

1. On Windows, use a **separate Kodi 22 portable installation** for the first validation round. Install Piers into a writable non-Program-Files folder and launch its shortcut with `-p`; confirm that its own `portable_data` folder is created. Do not install Piers over the everyday Kodi profile.
2. In that portable Kodi 22 instance: Kodi → Add-ons → Install from zip file → choose `service.streamdoctor-0.1.1.zip`.
3. In Stream Doctor settings, optionally enter your Internet plan in **Mbps** (1000 = 1 Gbps, 2000 = 2 Gbps, 10000 = 10 Gbps).
4. Play representative good and bad live streams.
5. Reports are written under Kodi's profile path: `addon_data/service.streamdoctor/reports`.

Do not change known-good Kodi buffering settings during the first validation round. The point of v0.1 is to observe before optimizing.

## Engineering documents

- `docs/RESEARCH.md` — verified research/non-findings
- `docs/EVIDENCE_MATRIX.md` — what v0.1 can and cannot diagnose
- `docs/METRICS.md` — measurement provenance, data-quality states and diagnostic KPIs
- `docs/TESTING.md` — offline and physical validation gates
- `docs/PHYSICAL_VALIDATION.md` — protected Windows/Kodi 22 test procedure
- `docs/SOURCES.md` — primary research sources
- `docs/BUILD_STATUS.md` — exact engineering status and remaining promotion gates
- `docs/ROADMAP.md` — controlled network diagnostics, Windows expansion and Android bridge
