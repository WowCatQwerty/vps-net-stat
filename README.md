# netmon — Network & Port Monitor

Простой монитор трафика и портов для Ubuntu-серверов.  
Считает входящий/исходящий трафик по дням и месяцам, отслеживает открытые порты с именами процессов. Данные хранятся в SQLite и **переживают перезагрузки**.

---

## Установка (одна команда)

```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash
```

Готово. Сервис запускается сразу и поднимается автоматически после перезагрузки.

---

## Использование

```bash
netmon-cli summary      # сводка: сегодня / месяц / всего + кол-во портов
netmon-cli ports        # открытые порты с именами процессов
netmon-cli today        # трафик за сегодня
netmon-cli month        # трафик за текущий месяц
netmon-cli all          # трафик по каждому месяцу отдельно
netmon-cli days 7       # последние N дней (по умолчанию 30)
```

### Пример вывода `summary`

```
  ┌─────────────────────────────────────────────┐
  │             netmon — сводка                 │
  ├────────────┬───────────────┬────────────────┤
  │ Период     │ ↓ Входящий    │ ↑ Исходящий    │
  ├────────────┼───────────────┼────────────────┤
  │ Сегодня    │ 1.23 GiB      │ 340.10 MiB     │
  │ Месяц      │ 24.80 GiB     │ 7.20 GiB       │
  │ Всё время  │ 142.30 GiB    │ 38.50 GiB      │
  └────────────┴───────────────┴────────────────┘
  Открытых портов: 12
```

### Пример вывода `ports`

```
  Открытые порты (снято: 2025-06-01 14:32:00)

  Proto  Port   State   PID    Process
  ─────────────────────────────────────
  tcp    22     LISTEN  1234   sshd
  tcp    80     LISTEN  5678   nginx
  tcp    443    LISTEN  5678   nginx
  tcp    3306   LISTEN  9012   mysqld
```

---

## Как это работает

| Компонент | Описание |
|---|---|
| `netmon.py` | Демон — читает `/proc/net/dev`, считает дельты трафика, сканирует порты через `ss` |
| `netmon-cli.py` | CLI для просмотра статистики |
| `netmon.service` | systemd-юнит, автозапуск после перезагрузки |
| `/var/lib/netmon/netmon.db` | SQLite-база, данные копятся бесконечно |
| `/var/log/netmon/netmon.log` | Лог демона |

**Интерфейсы определяются автоматически** через `ip route` — берётся тот, через который идёт default route. Виртуальные интерфейсы (docker, veth, tun, lo и т.д.) исключаются.

---

## Управление сервисом

```bash
systemctl status netmon      # статус
systemctl restart netmon     # перезапуск
systemctl stop netmon        # остановить
tail -f /var/log/netmon/netmon.log   # живые логи
```

## Удаление

```bash
systemctl stop netmon
systemctl disable netmon
rm -rf /opt/netmon /var/lib/netmon /var/log/netmon
rm /etc/systemd/system/netmon.service
rm /usr/local/bin/netmon-cli
systemctl daemon-reload
```

---

## Требования

- Ubuntu 20.04+ (или любой Linux с systemd)
- Python 3.8+
- `iproute2` (пакет `ss`, `ip` — обычно уже есть)
