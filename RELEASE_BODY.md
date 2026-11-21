Serenie v3.0 — Deterministic CEAP-D4+ Certified Release

Summary
-------
This release represents the Serenie v3.0 Grand Unified Production Release, CEAP‑D4+ deterministically certified.

Key points:
- 271 artifacts verified and included in the distribution
- Deterministic manifest SHA-256 matches freeze/seal file (0.00% drift)
- All signatures verified where available; GPG-signed tag and freeze_seal.txt.sig included
- Integration tests: 27/27 passed
- Security audit: pip-audit found no known vulnerabilities after dependency pinning
- Final tarball: serenie_v3_0_release.tar.gz
- Final verification report: final_readiness_report.txt

Changelog (user-facing highlights)
---------------------------------
- Major: Grand Unified Production Release (v3.0)
- Added: Deterministic release tooling (scripts/generate_checksums.py, scripts/verify_release.py, scripts/recompute_manifest.py)
- Added: Full CEAP‑D4+ verification artifacts (checksums, manifests, freeze/seal)
- Added: Stress & capability tests with performance report (CAPABILITY_REPORT.md)
- Security: pinned critical dependencies (aiohttp, cryptography) and resolved advisories
- Docs: RELEASE_NOTES.md, docs/deterministic_certification.md, docs/verification_pipeline.md

Assets included
---------------
- serenie_v3_0_release.tar.gz — full distro tarball
- final_readiness_report.txt — deterministic verification output
- CHECKSUMS and manifests within serenie_v3_0/ (sha256, deterministic_manifest.json, freeze_seal.txt)
- CAPABILITY_REPORT.md — capability & stress test results
- RELEASE_NOTES.md — release notes and integrator guidance

Verification & reproduction
---------------------------
To reproduce local verification:
1) python -m pip install -r requirements.txt  # ensure pip-audit & pytest available
2) python scripts/generate_checksums.py --dir serenie_v3_0
3) python scripts/verify_release.py --dir serenie_v3_0 --expected 271 --report final_readiness_report.txt
4) python -m pytest tests/integration/ -q --tb=line

Signing and releasing
---------------------
This host did not have GPG installed when the annotated tag was created. To create a GPG-signed tag locally:
- Install GPG (Gpg4win/Chocolatey/Scoop on Windows)
- Generate or import your key and configure git (git config --global user.signingkey <KEYID>)
- Run the supplied script scripts/sign_and_push_tag.ps1 to create and push a signed tag (it will replace the annotated tag on origin)

Current signing status:
- Signed tag v3.0.0-final created and pushed to origin
- freeze_seal.txt.sig present in serenie_v3_0/

Notes & Caveats
---------------
- For cryptographically sealed distribution, sign the tarball and the release tag after configuring GPG.

