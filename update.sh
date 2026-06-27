#!/bin/bash
# vps-net-stat — updater
# curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/update.sh | sudo bash

set -e

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; NC='\033[0m'
ok()  { echo -e "${GRN}✓${NC} $1"; }
err() { echo -e "${RED}✗ $1${NC}"; exit 1; }
inf() { echo -e "${YLW}→${NC} $1"; }

REPO="https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main"
INSTALL_DIR="/opt/vps-net-stat"

[[ $EUID -ne 0 ]] && err "Run as root: curl ... | sudo bash"

echo -e "\n${CYN}  vps-net-stat — обновление / update${NC}\n"

[[ ! -d "$INSTALL_DIR" ]] && err "vps-net-stat не установлен. Запусти install.sh"

inf "Скачиваю файлы…"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

curl -fsSL "$REPO/netmon.py"      -o "$TMPDIR/netmon.py"
curl -fsSL "$REPO/netmon-cli.py"  -o "$TMPDIR/netmon-cli.py"
curl -fsSL "$REPO/netmon.service" -o "$TMPDIR/netmon.service"
curl -fsSL "$REPO/version.txt"    -o "$TMPDIR/version.txt"
NEW_VER=$(curl -fsSL "$REPO/version.txt" | tr -d '\n\r')
curl -fsSL "https://github.com/WowCatQwerty/vps-net-stat/releases/download/v${NEW_VER}/checksums.txt" -o "$TMPDIR/checksums.txt"
ok "Файлы скачаны"

inf "Проверяю целостность файлов (SHA-256)…"
cd "$TMPDIR"
CHECKSUM_FAIL=0
while IFS='  ' read -r expected_hash filename; do
    [[ -f "$filename" ]] || continue
    actual_hash=$(sha256sum "$filename" | awk '{print $1}')
    if [[ "$actual_hash" != "$expected_hash" ]]; then
        echo -e "${RED}✗ Контрольная сумма не совпадает: $filename${NC}"
        CHECKSUM_FAIL=1
    fi
done < checksums.txt

if [[ $CHECKSUM_FAIL -eq 1 ]]; then
    err "Проверка целостности не пройдена. Файлы могли скачаться повреждёнными. Попробуй снова."
fi
ok "Целостность файлов подтверждена"

inf "Устанавливаю файлы…"
cp "$TMPDIR/netmon.py"      "$INSTALL_DIR/netmon.py"
cp "$TMPDIR/netmon-cli.py"  "$INSTALL_DIR/netmon-cli.py"
cp "$TMPDIR/netmon.service" "/etc/systemd/system/vps-net-stat.service"
cp "$TMPDIR/version.txt"    "$INSTALL_DIR/version.txt"
chmod +x "$INSTALL_DIR/netmon.py" "$INSTALL_DIR/netmon-cli.py"
ok "Файлы обновлены"

inf "Перезапускаю сервис…"
systemctl daemon-reload
systemctl restart vps-net-stat
ok "Сервис перезапущен"

echo -e "\n${GRN}  ✓ Обновление завершено! Данные сохранены.${NC}\n"
