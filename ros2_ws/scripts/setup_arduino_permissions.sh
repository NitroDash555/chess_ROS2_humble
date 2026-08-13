#!/usr/bin/env bash
# Настраивает доступ к Arduino (/dev/ttyUSB*, /dev/ttyACM*) без sudo.
# Подробнее: https://docs.arduino.cc/software/ide-v2/tutorials/troubleshooting/ubuntu/
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

RULE_FILE="/etc/udev/rules.d/99-arduino.rules"

# VID/PID популярных плат Arduino (0x2341) и распространённых USB-мостов:
# CH340 (0x1a86:0x7523) на китайских клонах, CP210x (0x10c4), FTDI (0x0403)
cat <<'EOF' | $SUDO tee "$RULE_FILE" > /dev/null
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", MODE="0666"
EOF

$SUDO udevadm control --reload-rules
$SUDO udevadm trigger

echo "Правило установлено в $RULE_FILE"
echo "Подключи Arduino заново и проверь: ls -l /dev/ttyUSB* (должно быть crw-rw-rw-)"
