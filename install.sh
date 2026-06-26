#!/bin/bash
# vps-net-stat — installer
# curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash

set -e

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; NC='\033[0m'
ok()  { echo -e "${GRN}✓${NC} $1"; }
err() { echo -e "${RED}✗ $1${NC}"; exit 1; }
inf() { echo -e "${YLW}→${NC} $1"; }

REPO="https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main"
INSTALL_DIR="/opt/vps-net-stat"
DB_DIR="/var/lib/vps-net-stat"
LOG_DIR="/var/log/vps-net-stat"
CONF_DIR="/etc/vps-net-stat"
SERVICE_NAME="vps-net-stat"

[[ $EUID -ne 0 ]] && err "Run as root: curl ... | sudo bash"

# ── Выбор языка / Language selection ─────────────────────────────────────────
echo ""
echo -e "${CYN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYN}  ║       vps-net-stat — installer       ║${NC}"
echo -e "${CYN}  ╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  Выберите язык / Choose language:\n"
echo -e "  [1] Русский"
echo -e "  [2] English"
echo ""
read -rp "  → " LANG_CHOICE

if [[ "$LANG_CHOICE" == "2" ]]; then
    LANG="en"
    msg_deps="Checking dependencies…"
    msg_dirs="Creating directories…"
    msg_download="Downloading files from GitHub…"
    msg_cmd="Installing vns command…"
    msg_service="Installing systemd service…"
    msg_done="vps-net-stat installed successfully!"
    msg_ifaces="Detected interfaces:"
    msg_menu="Open menu:"
    msg_status="Service status:"
    msg_logs="Logs:"
else
    LANG="ru"
    msg_deps="Проверяю зависимости…"
    msg_dirs="Создаю директории…"
    msg_download="Скачиваю файлы из GitHub…"
    msg_cmd="Устанавливаю команду vns…"
    msg_service="Устанавливаю systemd-сервис…"
    msg_done="vps-net-stat успешно установлен!"
    msg_ifaces="Обнаруженные интерфейсы:"
    msg_menu="Открыть меню:"
    msg_status="Статус сервиса:"
    msg_logs="Логи:"
fi

echo ""

# ── Зависимости / Dependencies ────────────────────────────────────────────────
inf "$msg_deps"
for cmd in python3 ss ip curl; do
    command -v "$cmd" &>/dev/null || err "Missing: $cmd  (apt install iproute2 curl python3)"
done
ok "$msg_deps"

# ── Директории ────────────────────────────────────────────────────────────────
inf "$msg_dirs"
mkdir -p "$INSTALL_DIR" "$DB_DIR" "$LOG_DIR" "$CONF_DIR"
ok "$msg_dirs"

# ── Сохраняем язык ────────────────────────────────────────────────────────────
echo "$LANG" > "$CONF_DIR/lang"

# ── Скачиваем файлы ───────────────────────────────────────────────────────────
inf "$msg_download"
curl -fsSL "$REPO/netmon.py"     -o "$INSTALL_DIR/netmon.py"
curl -fsSL "$REPO/netmon-cli.py" -o "$INSTALL_DIR/netmon-cli.py"
chmod +x "$INSTALL_DIR/netmon.py" "$INSTALL_DIR/netmon-cli.py"
ok "$msg_download"

# ── Команда vns ───────────────────────────────────────────────────────────────
inf "$msg_cmd"
ln -sf "$INSTALL_DIR/netmon-cli.py" /usr/local/bin/vns
ok "$msg_cmd"

# ── Systemd ───────────────────────────────────────────────────────────────────
inf "$msg_service"
curl -fsSL "$REPO/netmon.service" -o "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
ok "$msg_service"

sleep 2

IFACES=$(ip route 2>/dev/null | awk '/^default/ {print $5}' | tr '\n' ' ')

echo ""
echo -e "${GRN}  ══════════════════════════════════════${NC}"
echo -e "${GRN}  ✓ ${msg_done}${NC}"
echo -e "${GRN}  ══════════════════════════════════════${NC}"
echo ""
echo -e "  ${msg_ifaces} ${CYN}${IFACES}${NC}"
echo ""
echo -e "  ${msg_menu}  ${CYN}vns${NC}"
echo -e "  ${msg_status} systemctl status ${SERVICE_NAME}"
echo -e "  ${msg_logs}   tail -f ${LOG_DIR}/daemon.log"
echo ""
