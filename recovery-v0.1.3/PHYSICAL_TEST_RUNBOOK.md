# Kodi Stream Doctor v0.1.3 — Physical Test Runbook

## Safety boundary

- Use a separate Kodi 22 portable installation in a writable folder outside `Program Files`.
- Launch only with `-p` and confirm the portable installation created its own `portable_data` folder.
- Do not copy, overwrite or edit the everyday Kodi profile.
- Do not change cache or buffering settings during this test.
- Stream Doctor remains read-only; do not enable any automatic optimization.

## Install candidate

Install `dist/service.streamdoctor-0.1.3.zip` from this recovery workspace.

Expected SHA-256:

`0ae1332bbfaf92c59aaed2c8fd797b6a6743bc1cb76d149f222aba670c62730c`

## Pre-flight record

Record only:

- Kodi version/build and Windows version;
- CPU, installed RAM, GPU and driver version;
- active network connection type;
- optional Internet-plan Mbps figure.

Do not record stream URLs, usernames, passwords, tokens, cookies or authorization headers.

## First test pass

1. Play one stable live stream for several minutes. Expect `GOOD` when coverage is sufficient and no causal warning.
2. If a natural playback problem happens, immediately use **Mark problem** with the closest symptom.
3. Open **Last completed report** and check that the state, evidence and exclusions match what you observed.
4. Confirm the report contains no raw stream URL, token or credential.
5. Repeat only with a known weak source or alternate source if you already have one; do not disrupt a production router or account to create a fault.

## Report back

For each run, report the observed symptom, chosen marker, displayed status and whether the explanation looked plausible. Share only the add-on's redacted report if we need to investigate a discrepancy.

## Release gate

Windows physical validation is still required before any release claim. Android/Android TV is a separate future programme.
