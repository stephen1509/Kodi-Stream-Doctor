# Primary Research Sources

Research baseline: 2026-08-16 JST. Prefer these primary/official sources over secondary Kodi tuning guides.

## Kodi 22 / playback telemetry

- Team Kodi — Kodi 22 "Piers" Beta 1: https://kodi.tv/article/kodi-22-piers-beta-1/
- Official Kodi Wiki — InfoLabels: https://kodi.wiki/view/InfoLabel
- Official Kodi Wiki — Boolean conditions: https://kodi.wiki/view/List_of_boolean_conditions
- Official Kodi Wiki — Player process info: https://kodi.wiki/view/Player_process_info
- Official Kodi Wiki — Service add-ons: https://kodi.wiki/view/Service_add-ons
- Official Kodi Wiki — Add-on rules: https://kodi.wiki/view/Add-on_rules
- Official Kodi Wiki — Portable mode: https://kodi.wiki/view/Portable_mode
- Kodi source — `xbmc/cores/DataCacheCore.h`: https://github.com/xbmc/xbmc/blob/master/xbmc/cores/DataCacheCore.h
- Kodi source — `xbmc/guilib/guiinfo/PlayerGUIInfo.cpp`: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/guiinfo/PlayerGUIInfo.cpp
- Kodi source tag used for Beta 1 verification: `22.0b1-Piers` / commit `77395cf42e141000b0475b8d5a54925ad67bfeba`.

## Windows system evidence

- Microsoft Learn — Get-NetAdapter: https://learn.microsoft.com/powershell/module/netadapter/get-netadapter
- Microsoft Learn — Get-NetAdapterStatistics: https://learn.microsoft.com/powershell/module/netadapter/get-netadapterstatistics
- Microsoft Learn — Win32_VideoController: https://learn.microsoft.com/windows/win32/cimwin32prov/win32-videocontroller
- Microsoft Learn — Win32_Processor: https://learn.microsoft.com/windows/win32/cimwin32prov/win32-processor
- Microsoft Learn — Win32_OperatingSystem: https://learn.microsoft.com/windows/win32/cimwin32prov/win32-operatingsystem

## Android future track

- Android Developers — MediaCodecInfo.VideoCapabilities: https://developer.android.com/reference/android/media/MediaCodecInfo.VideoCapabilities
- Android Developers — MediaCodecInfo.CodecCapabilities: https://developer.android.com/reference/android/media/MediaCodecInfo.CodecCapabilities

## Network-quality concepts

- IETF RFC 3393 — IP Packet Delay Variation Metric: https://www.rfc-editor.org/rfc/rfc3393
- IETF RFC 7680 — One-Way Loss Metric for IPPM: https://www.rfc-editor.org/rfc/rfc7680

## Research rules derived from the sources

- A nominal 1/2/10-Gbps Internet plan is capacity context, not proof of path stability.
- Kodi 22's public live bitrate/queue labels justify a pure-Python read-only core for v0.1.
- Kodi's richer debug overlay contains useful render/A-V data, but Stream Doctor will not depend on a metric until a stable supported programmatic path is verified.
- Windows driver age, temperature or CPU utilization alone is not treated as proof of causality.
- Physical validation uses Kodi portable mode so the everyday Kodi profile is not overwritten.

## Future controlled throughput diagnostics

- Measurement Lab — Developer Resources / NDT: https://www.measurementlab.net/develop/
- M-Lab NDT7 protocol: https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md
- IETF RFC 6349 — Framework for TCP Throughput Testing: https://www.rfc-editor.org/rfc/rfc6349
