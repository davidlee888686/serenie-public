import shutil
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    dist = root / 'dist'
    if dist.exists():
        shutil.rmtree(dist)
    print('Clean complete.')

if __name__ == '__main__':
    main()
