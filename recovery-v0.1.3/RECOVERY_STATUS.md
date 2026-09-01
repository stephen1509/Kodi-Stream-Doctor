# Kodi Stream Doctor v0.1.3 Recovery Candidate

Date: 2026-09-01 NZST

This workspace begins with the verified v0.1.1 source archive (`87987b74d81cda97e99d1d267a16b122a271ec5d6f7bdf2a8a0f9b601657408f`) and applies the verified canonical v0.1.2 patch (`4d7a1847ed7e7e4a7ba4ea7badb2715bab996b5d09117f53900138454160a835`) wherever it matched.

The original v0.1.2 recovery record named a different v0.1.1 base archive, so this candidate is deliberately versioned `0.1.3` and must not be represented as the lost audited v0.1.2 build. The runtime code, tests, package metadata and QA tooling applied cleanly; two historical status-document hunks did not and are recorded in `docs/BUILD_STATUS.md.rej`.

Validation status: recovery QA passed on 2026-09-01 NZST: 111 tests plus compile, XML, static-safety, package, CRC and checksum gates. The generated install ZIP is `dist/service.streamdoctor-0.1.3.zip` with SHA-256 `0ae1332bbfaf92c59aaed2c8fd797b6a6743bc1cb76d149f222aba670c62730c`.

Physical Kodi 22 validation remains required before any release claim.
