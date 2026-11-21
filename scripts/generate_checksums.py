#!/usr/bin/env python3
"""
generate_checksums.py

Generates SHA-256 checksum registry for serenie_v3_0 and creates a deterministic manifest and freeze_seal.txt.
Optionally attempts to GPG-sign the freeze_seal.txt if gpg is available.

Usage: python scripts/generate_checksums.py --dir serenie_v3_0
"""
import argparse
import hashlib
import os
from pathlib import Path
import json
import subprocess
import sys


def sha256_of_file(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dir', default='serenie_v3_0')
    args = p.parse_args()
    base = Path(args.dir)
    if not base.exists():
        print('ERROR: release dir not found', file=sys.stderr)
        sys.exit(2)

    checksum_dir = base / 'checksums'
    checksum_dir.mkdir(exist_ok=True)
    sha_file = checksum_dir / 'sha256.txt'

    # Build a complete list of files (excluding .sig, checksum file, manifest, and freeze seal)
    files = [p for p in sorted(base.rglob('*')) if p.is_file()]
    file_hashes = {}
    for pth in files:
        rel = pth.relative_to(base).as_posix()
        if rel.endswith('.sig'):
            continue
        if rel == sha_file.relative_to(base).as_posix():
            continue
        if rel.startswith('checksums') or rel.startswith('manifests') or rel == 'freeze_seal.txt':
            continue
        h = sha256_of_file(pth)
        file_hashes[rel] = h

    # Write checksum file (fresh)
    with sha_file.open('w', encoding='utf-8') as fh:
        for rel in sorted(file_hashes.keys()):
            fh.write(f"{file_hashes[rel]}  {rel}\n")
    print('Wrote', sha_file)

    # Create deterministic manifest using verification rules (exclude registries and freeze)
    manifest_entries = []
    for rel in sorted(file_hashes.keys()):
        if rel.startswith('checksums') or rel.startswith('manifests') or rel == 'freeze_seal.txt':
            continue
        manifest_entries.append({'path': rel, 'sha256': file_hashes[rel]})
    manifest_json = json.dumps(manifest_entries, separators=(',', ':'), ensure_ascii=False)
    manifest_file = base / 'manifests' / 'deterministic_manifest.json'
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(manifest_json, encoding='utf-8')
    print('Wrote manifest', manifest_file)

    # Freeze/seal: sha256 of manifest
    manifest_hash = hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()
    freeze_file = base / 'freeze_seal.txt'
    freeze_file.write_text(manifest_hash + '\n', encoding='utf-8')
    print('Wrote freeze/seal', freeze_file)

    # Append checksum entries for manifest and freeze if missing
    with sha_file.open('r+', encoding='utf-8') as fh:
        existing = [line.split(None, 1)[1].strip() for line in fh.read().splitlines() if line.strip() and not line.strip().startswith('#')]
        to_append = []
        for special in ['manifests/deterministic_manifest.json', 'freeze_seal.txt']:
            if special not in existing:
                h = sha256_of_file(base / special)
                to_append.append((special, h))
        if to_append:
            for rel, h in to_append:
                fh.write(f"{h}  {rel}\n")
            print('Appended registry entries for manifest and freeze to', sha_file)

    # Attempt to sign freeze_seal.txt
    try:
        subprocess.run(['gpg', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sig = base / 'freeze_seal.txt.sig'
        subprocess.run(['gpg', '--batch', '--yes', '--output', str(sig), '--detach-sign', str(freeze_file)], check=True)
        print('Signed freeze_seal.txt ->', sig)
    except FileNotFoundError:
        print('gpg not found; skipping signature')
    except subprocess.CalledProcessError as e:
        print('gpg signing failed:', e)

    print('Done')

if __name__ == '__main__':
    main()
