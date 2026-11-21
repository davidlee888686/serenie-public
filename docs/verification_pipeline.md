# Verification Pipeline

Scripts included in this repository to generate and verify release artifacts:

- scripts/generate_checksums.py — regenerate SHA-256 registry, produce deterministic manifest and freeze/seal
- scripts/verify_release.py — verify artifact count, checksums, signatures, and manifest/freeze consistency
- scripts/recompute_manifest.py — helper to recompute deterministic manifest and update freeze/checksum entries
- release_v3_0.sh / release_v3_0.ps1 — convenience release scripts (commit, tag, push, tarball)

Usage examples:

```bash
python scripts/generate_checksums.py --dir serenie_v3_0
python scripts/verify_release.py --dir serenie_v3_0 --expected 271
```