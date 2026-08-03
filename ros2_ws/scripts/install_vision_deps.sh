#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    pip_install() {
        python3 -m pip install "$@"
    }
else
    pip_install() {
        python3 -m pip install --user "$@"
    }
fi

pip_install --upgrade pip

pip_install "numpy<2.0"
pip_install "opencv-python-headless<4.11.0"
pip_install ultralytics
pip_install shapely
pip_install python-dotenv
pip_install python-chess
pip_install pillow
pip_install matplotlib
pip_install stockfish

if ! command -v stockfish >/dev/null 2>&1; then
    sudo apt-get install -y stockfish >/dev/null 2>&1 || true
fi
