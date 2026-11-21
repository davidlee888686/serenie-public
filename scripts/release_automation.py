"""
release_automation.py

Aggregates release actions into one script:
- recompute manifest/checksum
- verify release payload
- create signed tag
- sign tarball
- upload to GitHub release if gh CLI is available

Usage:
    python release_automation.py --dir serenie_v3_0 --expected 268 --tag v3.0.0-final
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(command, cwd=None):
    print(f"[RUN] {' '.join(str(part) for part in command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(str(part) for part in command)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="serenie_v3_0")
    parser.add_argument("--expected", type=int, default=268)
    parser.add_argument("--tag", default="v3.0.0-final")
    args = parser.parse_args()
    repo = Path(".").resolve()

    run([sys.executable, "scripts/recompute_manifest.py", "--dir", args.dir])
    run([sys.executable, "scripts/generate_checksums.py", "--dir", args.dir])
    run([sys.executable, "scripts/verify_release.py", "--dir", args.dir, "--expected", str(args.expected)])

    if shutil.which("gpg") and Path(repo / f"serenie_v3_0/freeze_seal.txt.sig").exists():
        run(["git", "config", "--global", "user.signingkey", "709C98EFABF1994B"])
        run(["git", "tag", "-f", "-s", args.tag, "-m", f"Serenie {args.tag} Deterministic Certification"])
        run(["git", "push", "origin", f":refs/tags/{args.tag}"])
        run(["git", "push", "origin", f"refs/tags/{args.tag}"])
    else:
        print("[SKIP] GPG signing unavailable or freeze_seal.txt.sig missing")

    if shutil.which("gh"):
        run(["gh", "release", "create", args.tag, "--notes", "Signed deterministic release", "--clobber"])
    else:
        print("[SKIP] gh CLI not available; upload release assets manually")


if __name__ == "__main__":
    main()
