#!/usr/bin/env python3
"""
verify_release.py

Verifies serenie_v3_0 release directory for:
- file count (expected configurable)
- SHA-256 checksums against checksums/sha256.txt (format: <sha256>  <relative/path>)
- GPG signatures (for files with .sig alongside them)
- Generates a deterministic manifest and compares manifest hash against freeze_seal.txt
- Optionally prints a summary JSON to stdout

Usage: python scripts/verify_release.py --dir serenie_v3_0 --expected 327

This script is safe and read-only by default.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256_of_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_checksums(checksum_file: Path):
    checks = {}
    if not checksum_file.exists():
        return checks
    for line in checksum_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            h, path = parts
            path = path.strip()  # relative path
            checks[path] = h
    return checks


def verify_gpg_signature(artifact: Path):
    sig = artifact.with_suffix(artifact.suffix + '.sig')
    if not sig.exists():
        return None, 'NOSIG'
    try:
        # run gpg --verify sigfile artifact
        subprocess.run(['gpg', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return None, 'GPG_MISSING'
    try:
        res = subprocess.run(['gpg', '--verify', str(sig), str(artifact)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        ok = (res.returncode == 0)
        return ok, res.stdout
    except Exception as e:
        return None, f'ERR:{e}'


def build_deterministic_manifest(base_dir: Path):
    # Collect all files (excluding signature files and registries)
    entries = []
    for p in sorted(base_dir.rglob('*')):
        if p.is_file():
            rel = p.relative_to(base_dir).as_posix()
            # Skip signature files from manifest (they are metadata)
            if rel.endswith('.sig'):
                continue
            # Skip checksum and manifest registries and freeze file to avoid recursion
            if rel.startswith('checksums') or rel.startswith('manifests') or rel == 'freeze_seal.txt':
                continue
            entries.append(rel)
    manifest = []
    for rel in entries:
        path = base_dir / rel
        h = sha256_of_file(path)
        manifest.append({'path': rel, 'sha256': h})
    # Sort manifest deterministically by path
    manifest = sorted(manifest, key=lambda e: e['path'])
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dir', default='serenie_v3_0')
    p.add_argument('--expected', type=int, default=271)
    p.add_argument('--checks', default='serenie_v3_0/checksums/sha256.txt')
    p.add_argument('--freeze', default='serenie_v3_0/freeze_seal.txt')
    args = p.parse_args()

    base = Path(args.dir)
    if not base.exists() or not base.is_dir():
        print(f'ERROR: release dir {base} not found', file=sys.stderr)
        sys.exit(2)

    # Count files (excluding .sig files)
    all_files = [p for p in base.rglob('*') if p.is_file()]
    art_files = [p for p in all_files if not p.name.endswith('.sig')]
    file_count = len(art_files)
    print(f'Found artifacts (excluding .sig): {file_count}')
    if file_count != args.expected:
        print(f'WARNING: expected {args.expected} artifacts but found {file_count}')

    # Load expected checksums
    checksum_path = Path(args.checks)
    checks = load_checksums(checksum_path)
    print(f'Loaded {len(checks)} checksums from {checksum_path}' if checksum_path.exists() else 'No checksum registry found')

    mismatches = []
    missing_checks = []
    for af in art_files:
        rel = af.relative_to(base).as_posix()
        computed = sha256_of_file(af)
        expected = checks.get(rel)
        if expected is None:
            # Allow checksum file itself to be absent from the registry (self-referential)
            if rel == 'checksums/sha256.txt':
                continue
            missing_checks.append(rel)
        elif expected.lower() != computed.lower():
            mismatches.append((rel, expected, computed))

    print(f'Mismatched files: {len(mismatches)}')
    for m in mismatches[:10]:
        print(' MISMATCH:', m)
    print(f'Files missing checksum entries: {len(missing_checks)}')
    for m in missing_checks[:10]:
        print(' MISSING_CHECKSUM:', m)

    # Verify GPG signatures for artifacts that have .sig
    sig_results = {'ok': 0, 'nosig': 0, 'gpg_missing': 0, 'fail': 0}
    for af in art_files:
        ok, info = verify_gpg_signature(af)
        if ok is None:
            if info == 'NOSIG':
                sig_results['nosig'] += 1
            elif info == 'GPG_MISSING':
                sig_results['gpg_missing'] += 1
            else:
                sig_results['fail'] += 1
        elif ok:
            sig_results['ok'] += 1
        else:
            sig_results['fail'] += 1
    print('Signature summary:', sig_results)

    # Build deterministic manifest and compute its hash
    manifest = build_deterministic_manifest(base)
    manifest_json = json.dumps(manifest, separators=(',', ':'), ensure_ascii=False)
    manifest_hash = hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()
    print('Deterministic manifest SHA256:', manifest_hash)

    # Compare to freeze_seal.txt if exists
    freeze = Path(args.freeze)
    if freeze.exists():
        seal = freeze.read_text(encoding='utf-8').strip()
        print('Freeze/seal recorded value:', seal)
        if seal == manifest_hash:
            print('Freeze/Seal OK')
        else:
            print('Freeze/Seal MISMATCH')
    else:
        print('No freeze_seal.txt found')

    # Summary exit code: 0 if no mismatches and signatures not failing
    if mismatches or sig_results['fail']>0:
        print('Validation failed: mismatches or signature failures found', file=sys.stderr)
        sys.exit(3)
    print('Validation complete: OK')
    sys.exit(0)


if __name__ == '__main__':
    main()
