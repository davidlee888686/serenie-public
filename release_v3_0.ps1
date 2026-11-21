Param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$releaseDir = 'serenie_v3_0'
$tarball = 'serenie_v3_0_release.tar.gz'
$tag = 'v3.0.0'
$msg = 'Serenie v3.0.0 Final Release Seal'

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git not found. Install Git from https://git-scm.com/downloads and ensure it's on PATH"
  exit 2
}

if (-not (Test-Path $releaseDir)) {
  Write-Error "$releaseDir not found. Create or point to the correct path."; exit 2
}

# Stage and commit
git add $releaseDir
$staged = git diff --staged --name-only
if ($staged -eq $null) { Write-Output "No staged changes to commit for $releaseDir" }
else { git commit -m "rel(v3.0.0): Serenie v3.0.0 Grand Unified Production Release" }

# Tag: try signed then annotated
try {
  git tag -s $tag -m $msg -v | Out-Null
  Write-Output "Created signed tag $tag"
} catch {
  Write-Warning "GPG sign failed or not configured; creating annotated tag instead"
  git tag -a $tag -m $msg
}

# Push
$branch = git rev-parse --abbrev-ref HEAD
if ((git remote get-url origin) -ne $null) {
  git push origin $branch --tags
} else {
  Write-Error "Remote 'origin' not configured. Add with: git remote add origin <url>"; exit 2
}

# Create tarball using Python
python - <<'PY'
import shutil, os
src = os.path.abspath('serenie_v3_0')
dest = os.path.abspath('serenie_v3_0_release')
shutil.make_archive(dest, 'gztar', root_dir=src)
print('Created:', dest + '.tar.gz')
PY

Write-Output "Release script complete. Run tests and audit as needed."
