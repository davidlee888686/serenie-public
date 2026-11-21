import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / 'dist' / 'release_manifest.json'

    if not manifest_path.exists():
        print('No manifest found.')
        return

    manifest = json.loads(manifest_path.read_text())
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
