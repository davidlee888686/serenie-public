#!/usr/bin/env python3
"""
Recompute deterministic manifest using verify_release's rules (exclude checksums, manifests, freeze_seal.txt from manifest entries)
Write deterministic_manifest.json and freeze_seal.txt, and ensure checksums registry contains entries for manifest and freeze.
"""
import hashlib, json
from pathlib import Path

base = Path('serenie_v3_0')
if not base.exists():
    print('Release dir missing', flush=True)
    raise SystemExit(2)

entries = []
for p in sorted(base.rglob('*')):
    if p.is_file():
        rel = p.relative_to(base).as_posix()
        if rel.endswith('.sig'):
            continue
        if rel.startswith('checksums') or rel.startswith('manifests') or rel == 'freeze_seal.txt':
            continue
        entries.append(rel)

manifest = [{'path': rel, 'sha256': hashlib.sha256((base/rel).read_bytes()).hexdigest()} for rel in entries]
manifest = sorted(manifest, key=lambda e: e['path'])
manifest_json = json.dumps(manifest, separators=(',', ':'), ensure_ascii=False)
manifest_file = base / 'manifests' / 'deterministic_manifest.json'
manifest_file.parent.mkdir(parents=True, exist_ok=True)
manifest_file.write_text(manifest_json, encoding='utf-8')
manifest_hash = hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()
freeze_file = base / 'freeze_seal.txt'
freeze_file.write_text(manifest_hash + '\n', encoding='utf-8')

# Ensure checksum file contains entries for manifest and freeze
sha_file = base / 'checksums' / 'sha256.txt'
if sha_file.exists():
    s = sha_file.read_text(encoding='utf-8')
    lines = [line for line in s.splitlines() if line.strip() and not line.strip().startswith('#')]
    existing = [line.split(None, 1)[1].strip() for line in lines]
    append_lines = []
    for special in ['manifests/deterministic_manifest.json', 'freeze_seal.txt']:
        if special not in existing:
            h = hashlib.sha256((base / special).read_bytes()).hexdigest()
            append_lines.append(f"{h}  {special}")
    if append_lines:
        with sha_file.open('a', encoding='utf-8') as fh:
            fh.write('\n'.join(append_lines) + "\n")
        print('Appended', append_lines, flush=True)

print('WROTE_MANIFEST_HASH', manifest_hash, flush=True)
