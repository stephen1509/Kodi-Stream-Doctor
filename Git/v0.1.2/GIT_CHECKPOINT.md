# Kodi Stream Doctor v0.1.2 — Git Checkpoint

Date: 2026-08-17 JST

## Local Git authority

The v0.1.2 audited source was placed in a clean Git repository after the transient working runtime no longer contained the earlier `.git` directory. This checkpoint records the reconstructed development history honestly; it does not pretend to continue an unavailable prior local Git object database.

Branch: `main`
Commit: `65b50b4e531f89e48ac8a41d05a732e50530025c`
Annotated tag: `v0.1.2`
Commit message: `Preserve Kodi Stream Doctor v0.1.2 audit candidate`

QA was rerun from this committed tree:

- 111/111 tests: PASS
- full `tools/qa.py`: PASS
- install ZIP SHA-256: `022063c36ab7893d56f236101e72e542028d1ce849763059898832467480d46b`

A local Git bundle was also generated:

`kodi-stream-doctor-v0.1.2.bundle`
SHA-256: `5bc8263aef24a85dfaf5abf2ec8952e37b4d0fcd9dbaba8fe91231aee908b736`

The Dropbox canonical recovery method does not depend on this binary bundle: the fully preserved v0.1.1 source plus `Source/v0.1.2/PATCH_MANIFEST.md` reconstructs v0.1.2 exactly.

## GitHub status

The intended dedicated repository is `stephen1509/kodi-stream-doctor`. At this checkpoint, the connected GitHub integration does not expose creation of a brand-new repository, and the local environment has no authenticated `gh` CLI. The project has therefore **not** been pushed into an unrelated repository. Once the dedicated repository exists, this checkpoint/source can be published without redesigning or reconstructing the project.
