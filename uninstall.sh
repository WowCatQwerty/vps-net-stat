#!/bin/bash
# vps-net-stat — uninstaller
# curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/uninstall.sh | sudo bash

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; NC='\033[0m'
ok()  { echo -e "${GRN}✓${NC} $1"; }
err() { echo -e "${RED}✗ $1${NC}"; exit 1; }

[[ $EUID -ne 0 ]] && err "Run as root: curl ... | sudo bash"

echo -e "\n${CYN}  vps-net-stat — удаление / uninstall${NC}\n"
echo -e "  ${RED}Программа и все настройки будут удалены.${NC}"
echo -e "  The program and all settings will be removed.\n"
read -rp "  Продолжить? / Continue? [y/N]: " ans < /dev/tty

if [[ "${ans,,}" != "y" ]]; then
    echo -e "\n  Отмена / Cancelled.\n"
    exit 0
fi

# Отдельный вопрос про базу данных
echo ""
echo -e "  ${YLW}База данных содержит всю статистику трафика.${NC}"
echo -e "  ${YLW}Database contains all traffic statistics.${NC}\n"
read -rp "  Удалить базу данных? / Delete database? [y/N]: " del_db < /dev/tty

echo ""
systemctl stop vps-net-stat    2>/dev/null && ok "Сервис остановлен"
systemctl disable vps-net-stat 2>/dev/null && ok "Автозапуск отключён"

# Очищаем правила файрвола
CONF="/etc/vps-net-stat/firewall"
CHAIN="VNS_TRACK"
if [[ -f "$CONF" ]]; then
    FW=$(cat "$CONF")
    if [[ "$FW" == "iptables" ]]; then
        for cmd in iptables ip6tables; do
            command -v "$cmd" &>/dev/null && {
                $cmd -D INPUT  -j "$CHAIN" 2>/dev/null
                $cmd -D OUTPUT -j "$CHAIN" 2>/dev/null
                $cmd -F "$CHAIN" 2>/dev/null
                $cmd -X "$CHAIN" 2>/dev/null
            }
        done
        ok "Правила iptables очищены"
    elif [[ "$FW" == "nftables" ]]; then
        nft delete table inet vns_track 2>/dev/null
        ok "Правила nftables очищены"
    fi
fi

# Удаляем программу
for path in /opt/vps-net-stat /var/log/vps-net-stat /etc/vps-net-stat; do
    rm -rf "$path" && ok "Удалено: $path"
done

# База данных — только если согласился
if [[ "${del_db,,}" == "y" ]]; then
    rm -rf /var/lib/vps-net-stat && ok "Удалено: /var/lib/vps-net-stat (база данных)"
else
    ok "База данных сохранена: /var/lib/vps-net-stat"
fi

rm -f /etc/systemd/system/vps-net-stat.service && ok "Удалён systemd-юнит"
rm -f /usr/local/bin/vns && ok "Удалена команда vns"
systemctl daemon-reload

echo -e "\n${GRN}  ✓ vps-net-stat удалён.${NC}\n"
