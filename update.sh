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
curl -fsSL "$REPO/netmon.py"      -o "$INSTALL_DIR/netmon.py"
curl -fsSL "$REPO/netmon-cli.py"  -o "$INSTALL_DIR/netmon-cli.py"
curl -fsSL "$REPO/netmon.service" -o "/etc/systemd/system/vps-net-stat.service"
curl -fsSL "$REPO/version.txt"    -o "$INSTALL_DIR/version.txt"
chmod +x "$INSTALL_DIR/netmon.py" "$INSTALL_DIR/netmon-cli.py"
ok "Файлы обновлены"

inf "Перезапускаю сервис…"
systemctl daemon-reload
systemctl restart vps-net-stat
ok "Сервис перезапущен"

NEW_VER=$(cat "$INSTALL_DIR/version.txt" | tr -d '\n\r')
echo -e "\n${GRN}  ✓ Обновление до v${NEW_VER} завершено! Данные сохранены.${NC}\n"
