# Kodi Stream Doctor v0.1.2 — Canonical Source Reconstruction Manifest

Date: 2026-08-17 JST

## Authority

v0.1.2 is reconstructed from the already-preserved v0.1.1 source checkpoint plus the seven files named exactly:

`v011_to_v012.patch.canonical.part-00.txt` through `v011_to_v012.patch.canonical.part-06.txt`.

The older files `v011_to_v012.patch.part-00.txt` and `v011_to_v012.patch.part-01.txt` are abandoned attempts and are **NOT CANONICAL**. Part-01 is known to have a one-byte boundary mismatch. Do not use either of them.

## Base checkpoint

v0.1.1 source archive SHA-256:

`c72c25b01b04bf0a4e0c7c619312e56732abbc85000a411358b60120d10ab415`

## Canonical patch

Concatenated patch size: 51,022 bytes

Concatenated patch SHA-256:

`4d7a1847ed7e7e4a7ba4ea7badb2715bab996b5d09117f53900138454160a835`

Canonical part checksums and sizes:

- part-00: 7,951 bytes — `b37dbb126683875a37cde40b42520c606fac06a1b42d326efd60848876d9ee36`
- part-01: 7,906 bytes — `e314a75153dcce460302e17b83e499097091915b58806590a64f8d0ad7f86934`
- part-02: 7,944 bytes — `3701a82b19027004260c9fa4f2e6e027acbc333f3b8b63e4cf077f14a938aef9`
- part-03: 7,993 bytes — `ec5cb682655a9d3a2fb98131f8a081b4cfff5ee40880b11789e4fcaeafc36c58`
- part-04: 7,992 bytes — `7bfc9cb17d7b55aefb9d21caf14e07b4f85211f9b33554326865c8e4e775bf50`
- part-05: 7,962 bytes — `42ebb6569156100432b914ef1271d0ad50bd1dfda06f0af211ef6f175964cdfd`
- part-06: 3,274 bytes — `8a7c59cd211262f0980bce41107ca3b3bdd8f43c3d3b0eb4f34c2663e3e4a75b`

All seven Dropbox files were verified to have these exact byte sizes after upload.

## Reconstruct

On a system with `cat` and `patch` available:

```sh
cat v011_to_v012.patch.canonical.part-*.txt > v011_to_v012.patch
sha256sum v011_to_v012.patch
# Expected: 4d7a1847ed7e7e4a7ba4ea7badb2715bab996b5d09117f53900138454160a835

# Extract the preserved v0.1.1 source archive first, then enter its kodi-stream-doctor directory.
cd kodi-stream-doctor
patch -p6 < ../v011_to_v012.patch
python3 tools/qa.py
```

This procedure was tested before preservation. Applying the patch to the preserved v0.1.1 tree produced a byte-for-byte match of the v0.1.2 non-build source tree.

## Release verification

The deterministic QA/build must reproduce the v0.1.2 physical-validation install ZIP with SHA-256:

`022063c36ab7893d56f236101e72e542028d1ce849763059898832467480d46b`

The authoritative development source is the reconstructed tree; generated `dist/` files are rebuild products.
