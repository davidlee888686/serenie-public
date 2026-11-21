#!/usr/bin/env bash
set -euo pipefail

RELEASE_DIR=serenie_v3_0
TARBALL=serenie_v3_0_release.tar.gz
TAG=v3.0.0
MSG="Serenie v3.0.0 Final Release Seal"

# Check git
if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git not found. Install Git: https://git-scm.com/downloads" >&2
  exit 2
fi

# Ensure in repo root
if [ ! -d "$RELEASE_DIR" ]; then
  echo "ERROR: $RELEASE_DIR not found. Create or point to the correct path." >&2
  exit 2
fi

# Stage and commit
git add "$RELEASE_DIR"
if git diff --staged --quiet; then
  echo "No staged changes to commit for $RELEASE_DIR"
else
  git commit -m "rel(v3.0.0): Serenie v3.0.0 Grand Unified Production Release"
fi

# Tag (try signed, fallback to annotated)
if git tag -s "$TAG" -m "$MSG" 2>/dev/null; then
  echo "Created signed tag $TAG"
else
  echo "GPG sign failed or not configured; creating annotated tag instead"
  git tag -a "$TAG" -m "$MSG"
fi

# Push branch and tags
if ! git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
  echo "ERROR: failed to determine current branch" >&2
  exit 2
fi
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if git remote get-url origin >/dev/null 2>&1; then
  git push origin "$CURRENT_BRANCH" --tags
else
  echo "ERROR: remote 'origin' not configured. Configure with: git remote add origin <url>" >&2
  exit 2
fi

# Create tarball
python - <<'PY'
import shutil, os
src = os.path.abspath("serenie_v3_0")
dest = os.path.abspath("serenie_v3_0_release")
shutil.make_archive(dest, 'gztar', root_dir=src)
print('Created:', dest + '.tar.gz')
PY

echo "Release packaging complete. Run tests and audit locally:"
echo "  python -m pytest tests/integration/ -q --tb=line"
echo "  python -m pip_audit -r requirements.txt"
