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

echo -e "\n${CYN}  ╔══════════════════════════════════════╗${NC}"
echo -e "${CYN}  ║       vps-net-stat — installer       ║${NC}"
echo -e "${CYN}  ╚══════════════════════════════════════╝${NC}\n"

# ── Определяем ОС ─────────────────────────────────────────────────────────────
if command -v apt-get &>/dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &>/dev/null; then
    PKG_MANAGER="dnf"
elif command -v yum &>/dev/null; then
    PKG_MANAGER="yum"
else
    PKG_MANAGER="unknown"
fi

# ── Выбор языка ───────────────────────────────────────────────────────────────
echo -e "  Выберите язык / Choose language:\n"
echo -e "  [1] Русский"
echo -e "  [2] English"
echo ""
read -rp "  → " LANG_CHOICE < /dev/tty

if [[ "$LANG_CHOICE" == "2" ]]; then
    LANG="en"
    msg_deps="Checking dependencies…"
    msg_install_deps="Installing missing dependencies…"
    msg_dirs="Creating directories…"
    msg_download="Downloading files from GitHub…"
    msg_cmd="Installing vns command…"
    msg_service="Installing systemd service…"
    msg_done="vps-net-stat installed successfully!"
    msg_ifaces="Detected interfaces:"
    msg_menu="Open menu:"
    msg_status="Service status:"
    msg_logs="Logs:"
    msg_update="Update:"
    msg_uninstall="Uninstall:"
else
    LANG="ru"
    msg_deps="Проверяю зависимости…"
    msg_install_deps="Устанавливаю недостающие пакеты…"
    msg_dirs="Создаю директории…"
    msg_download="Скачиваю файлы из GitHub…"
    msg_cmd="Устанавливаю команду vns…"
    msg_service="Устанавливаю systemd-сервис…"
    msg_done="vps-net-stat успешно установлен!"
    msg_ifaces="Обнаруженные интерфейсы:"
    msg_menu="Открыть меню:"
    msg_status="Статус сервиса:"
    msg_logs="Логи:"
    msg_update="Обновление:"
    msg_uninstall="Удаление:"
fi

echo ""

# ── Зависимости ───────────────────────────────────────────────────────────────
inf "$msg_deps"
MISSING=()
for cmd in python3 ss ip curl; do
    command -v "$cmd" &>/dev/null || MISSING+=("$cmd")
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    inf "$msg_install_deps (${MISSING[*]})"
    if [[ "$PKG_MANAGER" == "apt" ]]; then
        apt-get install -y python3 iproute2 curl 2>/dev/null
    elif [[ "$PKG_MANAGER" == "dnf" ]]; then
        dnf install -y python3 iproute curl 2>/dev/null
    elif [[ "$PKG_MANAGER" == "yum" ]]; then
        yum install -y python3 iproute curl 2>/dev/null
    else
        err "Установи вручную: ${MISSING[*]}"
    fi
fi
ok "$msg_deps"

# ── Директории ────────────────────────────────────────────────────────────────
inf "$msg_dirs"
mkdir -p "$INSTALL_DIR" "$DB_DIR" "$LOG_DIR" "$CONF_DIR"
ok "$msg_dirs"

echo "$LANG" > "$CONF_DIR/lang"

# ── Файлы ─────────────────────────────────────────────────────────────────────
inf "$msg_download"
TMPDIR_INS=$(mktemp -d)
trap "rm -rf $TMPDIR_INS" EXIT

curl -fsSL "$REPO/netmon.py"     -o "$TMPDIR_INS/netmon.py"
curl -fsSL "$REPO/netmon-cli.py" -o "$TMPDIR_INS/netmon-cli.py"
curl -fsSL "$REPO/version.txt"   -o "$TMPDIR_INS/version.txt"
curl -fsSL "https://github.com/WowCatQwerty/vps-net-stat/releases/latest/download/checksums.txt" -o "$TMPDIR_INS/checksums.txt"
ok "$msg_download"

if [[ "$LANG_CHOICE" == "2" ]]; then
    inf "Verifying file integrity (SHA-256)…"
else
    inf "Проверяю целостность файлов (SHA-256)…"
fi
cd "$TMPDIR_INS"
CHECKSUM_FAIL=0
while IFS='  ' read -r expected_hash filename; do
    [[ -f "$filename" ]] || continue
    actual_hash=$(sha256sum "$filename" | awk '{print $1}')
    if [[ "$actual_hash" != "$expected_hash" ]]; then
        CHECKSUM_FAIL=1
    fi
done < checksums.txt
cd - > /dev/null

if [[ $CHECKSUM_FAIL -eq 1 ]]; then
    err "Integrity check failed. Files may be corrupted. Try again."
fi
ok "SHA-256 OK"

cp "$TMPDIR_INS/netmon.py"     "$INSTALL_DIR/netmon.py"
cp "$TMPDIR_INS/netmon-cli.py" "$INSTALL_DIR/netmon-cli.py"
cp "$TMPDIR_INS/version.txt"   "$INSTALL_DIR/version.txt"
chmod +x "$INSTALL_DIR/netmon.py" "$INSTALL_DIR/netmon-cli.py"

inf "$msg_cmd"
ln -sf "$INSTALL_DIR/netmon-cli.py" /usr/local/bin/vns
ok "$msg_cmd"

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
echo -e "  ${msg_menu}    ${CYN}vns${NC}"
echo -e "  ${msg_status}  systemctl status ${SERVICE_NAME}"
echo -e "  ${msg_logs}    tail -f ${LOG_DIR}/daemon.log"
echo ""
echo -e "  ${msg_update}     curl -fsSL ${REPO}/update.sh | sudo bash"
echo -e "  ${msg_uninstall}  curl -fsSL ${REPO}/uninstall.sh | sudo bash"
echo ""
