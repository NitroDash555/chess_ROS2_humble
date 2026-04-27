#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS2_WS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REQ_FILE="$ROS2_WS_DIR/requirements/vision.txt"
WHEEL_DIR="$ROS2_WS_DIR/requirements/wheels"

if [[ ! -f "$REQ_FILE" ]]; then
    echo "[vision] Requirements file not found: $REQ_FILE"
    exit 1
fi

mkdir -p "$WHEEL_DIR"

echo "[vision] Trying offline install from local wheelhouse..."
if python3 -m pip install --no-index --find-links="$WHEEL_DIR" -r "$REQ_FILE"; then
    echo "[vision] Installed from local wheels."
    exit 0
fi

echo "[vision] Local wheelhouse is missing some packages. Downloading into $WHEEL_DIR ..."
python3 -m pip download -r "$REQ_FILE" -d "$WHEEL_DIR"

echo "[vision] Installing from freshly downloaded local wheels..."
python3 -m pip install --no-index --find-links="$WHEEL_DIR" -r "$REQ_FILE"

echo "[vision] Done."
