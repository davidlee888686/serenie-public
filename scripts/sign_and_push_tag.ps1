# Usage: Open PowerShell after GPG is configured and run this script.
param(
    [string] $Tag = 'v3.0.0-final',
    [switch] $ReplaceRemote = $true
)
if (-not (Get-Command gpg -ErrorAction SilentlyContinue)) { Write-Error "gpg not found in PATH. Install GnuPG and ensure gpg is on PATH."; exit 1 }
# Ensure git signing key is configured
$key = git config --global user.signingkey 2>$null
if (-not $key) { Write-Error "No git signing key configured. Run 'git config --global user.signingkey <KEYID>'"; exit 1 }
# Create a signed tag (force update locally)
git tag -f -s $Tag -m "Serenie v3.0.0 Final Deterministic Certification"
# Replace remote tag if requested
if ($ReplaceRemote) {
    # Delete remote tag
    git push origin :refs/tags/$Tag
    # Push signed tag
    git push origin refs/tags/$Tag
} else {
    git push origin refs/tags/$Tag
}
Write-Output "Signed tag $Tag created and pushed to origin."
