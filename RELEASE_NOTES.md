# Serenie v3.0 — Deterministic CEAP-D4+ Certified Release

Release summary

- Artifacts verified: 271/271
- Deterministic drift: 0.00%
- Signatures: All artifact signature registry validated (no failing signatures on this host)
- Tests: 27/27 passed
- Security audit: No known vulnerabilities (pip-audit)
- Freeze/seal and deterministic manifest: Match
- Tarball: serenie_v3_0_release.tar.gz

Verification artifacts
- final_readiness_report.txt (verification output)

Downstream integrator instructions
- Download and verify the tarball and checksum registry before deployment
- To recreate verification locally:
  - python scripts/generate_checksums.py --dir serenie_v3_0
  - python scripts/verify_release.py --dir serenie_v3_0 --expected 271

Contact
- Maintainer: davidlee888686
