# Installs a version of uv matching the tracked version in UV_VERSION file.
# Will replace existing versions already installed. Expected to be run from repo root.

$TARGET_VERSION = Get-Content -Path .\UV_VERSION

Write-Host "Installing uv version $TARGET_VERSION"

powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/$TARGET_VERSION/install.ps1 | iex"
