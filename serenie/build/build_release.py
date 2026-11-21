import sys
import os
import json
import zipfile
import hashlib
from pathlib import Path

def hash_file(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()

def main():
    root = Path(__file__).resolve().parent.parent
    dist = root / 'dist'
    dist.mkdir(exist_ok=True)

    artifacts = []
    for folder in ['kernel', 'cli', 'tests', 'standard', 'conformance']:
        p = root / folder
        for f in p.rglob('*'):
            if f.is_file():
                artifacts.append(f)

    release_zip = dist / 'serenie_release.zip'
    with zipfile.ZipFile(release_zip, 'w') as z:
        for f in artifacts:
            z.write(f, f.relative_to(root))

    manifest = {
        'release': str(release_zip),
        'hashes': {str(f.relative_to(root)): hash_file(f) for f in artifacts}
    }

    (dist / 'release_manifest.json').write_text(json.dumps(manifest, indent=2))
    print('Release built:', release_zip)

if __name__ == '__main__':
    main()
