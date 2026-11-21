# Sign the tarball and upload signature to GitHub Release
param(
    [string] $Tag = 'v3.0.0-final',
    [string] $Tarball = 'serenie_v3_0_release.tar.gz'
)
if (-not (Get-Command gpg -ErrorAction SilentlyContinue)) { Write-Error "gpg not found. Install GnuPG and ensure gpg is on PATH."; exit 1 }
if (-not (Test-Path $Tarball)) { Write-Error "Tarball $Tarball not found"; exit 1 }
# Create detached ASCII-armored signature
gpg --armor --detach-sign $Tarball
$asc = "$Tarball.asc"
if (-not (Test-Path $asc)) { Write-Error "Signature file not created: $asc"; exit 1 }
# Upload signature to GitHub release (requires gh CLI and authentication)
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Error "gh CLI not found. Install GitHub CLI and authenticate before running this script."; exit 1 }
Write-Output "Uploading $Tarball and $asc to release $Tag"
gh release upload $Tag $Tarball $asc --clobber
Write-Output 'Upload complete'
