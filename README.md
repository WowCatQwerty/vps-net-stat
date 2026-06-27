# vps-net-stat

Простой монитор трафика и портов для Ubuntu-серверов.  
Считает входящий/исходящий трафик по дням и месяцам, отслеживает открытые порты с именами процессов, считает трафик по выбранным портам. Данные хранятся в SQLite и **переживают перезагрузки**.

---

## Установка (одна команда)

```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash
```

При установке будет предложено выбрать язык — русский или английский.  
Сервис запускается сразу и поднимается автоматически после перезагрузки.

---

## Использование

### Интерактивное меню

```bash
vns
```

```
  ╔══════════════════════════════════════╗
  ║  vps-net-stat — Мониторинг сети VPS ║
  ╚══════════════════════════════════════╝

  [1]   Сводка (сегодня / месяц / всего)
  [2]   Открытые порты с процессами
  [3]   Трафик за сегодня
  [4]   Трафик за текущий месяц
  [5]   Трафик по всем месяцам
  [6]   Трафик за последние N дней
  [7]   Топ портов по трафику
  ──────────────────────────────────────
  [8]   Добавить порт для отслеживания трафика
  [9]   Убрать порт из отслеживания
  [wl]  Список отслеживаемых портов
  ──────────────────────────────────────
  [10]  Сбросить трафик сервера
  [11]  Сбросить трафик порта
  ──────────────────────────────────────
  [12]  Удалить программу
  [13]  Обновить vps-net-stat
  [14]  Перезапустить сервис
  [15]  Переключить язык (Switch to English)
  [0]   Выйти
```

---

## Отслеживание трафика по портам

По умолчанию трафик по портам **не считается** — сначала нужно добавить нужные порты вручную.  


**Как добавить порт:**

1. Открой меню `vns`
2. Выбери `[2]` — посмотри какие порты заняты и чем
3. Выбери `[8]` — введи номер порта, протокол (tcp/udp) и необязательный комментарий
4. Трафик начнёт копиться с этого момента

**Пример:**
```
  Номер порта (например 80): 443
  Протокол [tcp/udp, по умолчанию tcp]: tcp
  Комментарий (необязательно): nginx HTTPS
  ✓ Порт добавлен в отслеживание.
```

После этого в пункте `[7]` (топ портов) появится статистика по этому порту.  
Убрать порт из отслеживания — пункт `[9]`.

---

## Обновление

Прямо из меню: `vns` → пункт `[13]`

Или вручную:
```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/netmon.py      -o /opt/vps-net-stat/netmon.py
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/netmon-cli.py  -o /opt/vps-net-stat/netmon-cli.py
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh     -o /opt/vps-net-stat/install.sh
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/netmon.service -o /etc/systemd/system/vps-net-stat.service
systemctl daemon-reload && systemctl restart vps-net-stat
```

Данные при обновлении **не удаляются**.

---

## Как это работает

| Компонент | Описание |
|---|---|
| `netmon.py` | Демон — читает `/proc/net/dev`, считает дельты трафика, сканирует порты через `ss` |
| `netmon-cli.py` | CLI с интерактивным меню и прямыми командами |
| `netmon.service` | systemd-юнит, автозапуск после перезагрузки |
| `/var/lib/vps-net-stat/data.db` | SQLite-база, данные копятся бесконечно |
| `/var/log/vps-net-stat/daemon.log` | Лог демона |
| `/etc/vps-net-stat/lang` | Выбранный язык интерфейса |

**Интерфейсы определяются автоматически** через `ip route`. Виртуальные интерфейсы (docker, veth, tun, lo и т.д.) исключаются.

---

## Управление сервисом

```bash
systemctl status vps-net-stat
systemctl restart vps-net-stat
systemctl stop vps-net-stat
tail -f /var/log/vps-net-stat/daemon.log
```

## Удаление

Через меню: `vns` → пункт `[10]`

Или вручную:
```bash
systemctl stop vps-net-stat && systemctl disable vps-net-stat
rm -rf /opt/vps-net-stat /var/lib/vps-net-stat /var/log/vps-net-stat /etc/vps-net-stat
rm -f /etc/systemd/system/vps-net-stat.service /usr/local/bin/vns
systemctl daemon-reload
```

---

## Требования

- Ubuntu 20.04+ (или любой Linux с systemd)
- Python 3.8+
- `iproute2` (пакет `ss`, `ip` — обычно уже есть)

---

## Лицензия

[GNU GPL v3](LICENSE) — код открытый, модификации тоже должны быть открытыми.
