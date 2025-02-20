#!/bin/bash
# Installs a version of uv matching the tracked version in UV_VERSION file.
# Will replace existing versions already installed. Expected to be run from repo root.

TARGET_VERSION=$(cat UV_VERSION)

echo "Installing uv version $TARGET_VERSION"

curl -LsSf https://astral.sh/uv/$TARGET_VERSION/install.sh | sh
