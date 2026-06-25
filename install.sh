#!/bin/bash
# install.sh — установка netmon
# Однострочная установка:
#   curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/netmon/main/install.sh | sudo bash

set -e

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
CYN='\033[0;36m'
NC='\033[0m'

ok()  { echo -e "${GRN}✓${NC} $1"; }
err() { echo -e "${RED}✗ $1${NC}"; exit 1; }
inf() { echo -e "${YLW}→${NC} $1"; }

REPO="https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main"
INSTALL_DIR="/opt/netmon"
DB_DIR="/var/lib/netmon"
LOG_DIR="/var/log/netmon"

echo -e "\n${CYN}  netmon — Network & Port Monitor${NC}"
echo -e "${CYN}  ──────────────────────────────${NC}\n"

[[ $EUID -ne 0 ]] && err "Запускай от root: curl ... | sudo bash"

# Проверка зависимостей
for cmd in python3 ss ip curl; do
    command -v "$cmd" &>/dev/null || err "Не найдена команда: $cmd  (apt install $cmd)"
done
ok "Зависимости в порядке"

inf "Создаю директории…"
mkdir -p "$INSTALL_DIR" "$DB_DIR" "$LOG_DIR"
ok "Директории: $INSTALL_DIR, $DB_DIR, $LOG_DIR"

inf "Скачиваю файлы из GitHub…"
curl -fsSL "$REPO/netmon.py"     -o "$INSTALL_DIR/netmon.py"
curl -fsSL "$REPO/netmon-cli.py" -o "$INSTALL_DIR/netmon-cli.py"
chmod +x "$INSTALL_DIR/netmon.py" "$INSTALL_DIR/netmon-cli.py"
ok "Файлы скачаны в $INSTALL_DIR"

inf "Устанавливаю команду netmon-cli…"
ln -sf "$INSTALL_DIR/netmon-cli.py" /usr/local/bin/netmon-cli
ok "Команда netmon-cli готова"

inf "Устанавливаю systemd-сервис…"
curl -fsSL "$REPO/netmon.service" -o /etc/systemd/system/netmon.service
systemctl daemon-reload
systemctl enable netmon
systemctl restart netmon
ok "Сервис запущен и добавлен в автозагрузку"

# Пауза — дать демону секунду подняться
sleep 2

# Покажем какие интерфейсы были обнаружены
IFACES=$(ip route | awk '/^default/ {print $5}' | tr '\n' ' ')

echo ""
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo -e "${GRN}  netmon успешно установлен!${NC}"
echo -e "${GRN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "  Обнаруженные интерфейсы: ${CYN}${IFACES}${NC}"
echo ""
echo "  Команды:"
echo "  netmon-cli summary      — сводка (трафик + порты)"
echo "  netmon-cli ports        — открытые порты"
echo "  netmon-cli today        — трафик за сегодня"
echo "  netmon-cli month        — трафик за месяц"
echo "  netmon-cli all          — по всем месяцам"
echo "  netmon-cli days 7       — последние 7 дней"
echo ""
echo "  Логи:    tail -f /var/log/netmon/netmon.log"
echo "  Статус:  systemctl status netmon"
echo "  База:    /var/lib/netmon/netmon.db"
echo ""
