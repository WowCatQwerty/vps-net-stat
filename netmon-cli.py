#!/usr/bin/env python3
"""vps-net-stat CLI"""

import sqlite3, sys, os, subprocess, time
from datetime import date, datetime

DB_PATH = "/var/lib/vps-net-stat/data.db"

# ── i18n ─────────────────────────────────────────────────────────────────────
LANG_FILE = "/etc/vps-net-stat/lang"

def load_lang():
    try:
        with open(LANG_FILE) as f:
            return f.read().strip()
    except Exception:
        return "ru"

STRINGS = {
    "ru": {
        "title":        "vps-net-stat — Мониторинг сети VPS",
        "menu_header":  "Выберите действие:",
        "m1":  "Сводка (сегодня / месяц / всего)",
        "m2":  "Открытые порты с процессами",
        "m3":  "Трафик за сегодня",
        "m4":  "Трафик за текущий месяц",
        "m5":  "Трафик по всем месяцам",
        "m6":  "Трафик за последние N дней",
        "m7":  "Топ портов по трафику",
        "m8":  "Удалить программу",
        "m9":  "Перезапустить сервис",
        "m10": "Переключить язык (Switch to English)",
        "m0":  "Выйти",
        "choose":       "Ваш выбор: ",
        "days_prompt":  "Сколько дней показать? [30]: ",
        "no_data":      "Нет данных.",
        "no_db":        "База данных не найдена. Запущен ли сервис?",
        "ports_header": "Открытые порты",
        "ports_scanned":"снято:",
        "ports_total":  "Итого портов:",
        "period":       "Период",
        "incoming":     "↓ Входящий",
        "outgoing":     "↑ Исходящий",
        "total":        "Всего",
        "today_lbl":    "Сегодня",
        "month_lbl":    "Месяц",
        "alltime_lbl":  "Всё время",
        "open_ports":   "Открытых портов:",
        "disk_usage":   "Размер на диске:",
        "disk_db":      "база",
        "disk_app":     "программа",
        "summary_title":"vps-net-stat — сводка",
        "day_col":      "День",
        "month_col":    "Месяц",
        "traffic_today":"Трафик за",
        "traffic_month":"Трафик за месяц",
        "traffic_months":"Трафик по месяцам",
        "traffic_days": "Трафик за последние {} дней",
        "port_top":     "Топ портов по трафику",
        "port_col":     "Порт",
        "proto_col":    "Протокол",
        "process_col":  "Процесс",
        "uninstall_confirm": "Удалить vps-net-stat? Все данные будут удалены. [y/N]: ",
        "uninstall_done":    "Программа удалена.",
        "uninstall_abort":   "Отмена.",
        "restart_done":      "Сервис перезапущен.",
        "lang_switched":     "Язык переключён. Язык / Language: English",
        "press_enter":       "\nНажмите Enter для возврата в меню…",
        "m_watch_add":  "Добавить порт для отслеживания трафика",
        "m_watch_del":  "Убрать порт из отслеживания",
        "m_watch_list": "Отслеживаемые порты",
        "watch_list_empty": "Нет отслеживаемых портов. Добавь через пункт меню.",
        "watch_add_prompt": "Номер порта (например 80): ",
        "watch_proto_prompt": "Протокол [tcp/udp, по умолчанию tcp]: ",
        "watch_comment_prompt": "Комментарий (необязательно): ",
        "watch_added": "Порт добавлен в отслеживание.",
        "watch_already": "Этот порт уже отслеживается.",
        "watch_del_prompt": "Номер порта для удаления: ",
        "watch_proto_del_prompt": "Протокол [tcp/udp, по умолчанию tcp]: ",
        "watch_deleted": "Порт убран из отслеживания.",
        "watch_not_found": "Порт не найден в списке.",
        "watch_invalid": "Некорректный номер порта.",
        "comment_col": "Комментарий",
        "added_col": "Добавлен",
        "version_cur":  "Версия:",
        "version_new":  "🟢 Доступна новая версия:",
        "version_ok":   "Версия актуальна",
        "svc_running":  "Сервис: запущен",
        "svc_stopped":  "Сервис: остановлен",
        "last_scan":    "Последнее сканирование:",
        "db_size_lbl":  "База данных:",
        "tracked_lbl":  "Отслеживаемых портов:",
        "uptime_lbl":   "Время работы сервиса:",
        "ago":          "назад",
        "never":        "никогда",
        "sec":          "сек",
        "min":          "мин",
        "hrs":          "ч",
        "days_ago":     "д",
        "info_title":   "vps-net-stat — информация",
        "doctor_title": "vps-net-stat — диагностика",
        "doc_sqlite":   "SQLite база доступна",
        "doc_sqlite_bad":"SQLite база повреждена",
        "doc_svc":      "systemd сервис запущен",
        "doc_svc_bad":  "systemd сервис не запущен",
        "doc_proc":     "/proc/net/dev читается",
        "doc_proc_bad": "/proc/net/dev недоступен",
        "doc_ss":       "ss установлен",
        "doc_ss_bad":   "ss не найден (apt install iproute2)",
        "doc_ip":       "ip установлен",
        "doc_ip_bad":   "ip не найден (apt install iproute2)",
        "doc_iface":    "Интерфейс обнаружен:",
        "doc_iface_bad":"Интерфейс не найден",
        "doc_write":    "Права на запись в директории данных",
        "doc_write_bad":"Нет прав на запись в",
        "doc_disk":     "Свободно на диске:",
        "doc_disk_bad": "Мало места на диске:",
        "doc_fresh":    "База обновлялась недавно",
        "doc_fresh_bad":"База не обновлялась давно — сервис завис?",
        "doc_all_ok":   "✓ Всё в порядке",
        "doc_issues":   "Найдены проблемы:",
        "m_info":       "Информация о системе",
        "m_doctor":     "Диагностика",
        "m_export":     "Экспорт статистики",
        "m_limit":      "Настроить месячный лимит трафика",
        "export_choose":"Формат: [1] CSV  [2] JSON  [3] Оба: ",
        "export_path":  "Сохранить в директорию [/root/vns-backup]: ",
        "export_done":  "Экспорт завершён:",
        "limit_prompt": "Месячный лимит ГиБ (0 = отключить): ",
        "limit_set":    "Лимит установлен:",
        "limit_bar_lbl":"Месячный лимит:",
        "limit_none":   "Лимит не установлен",
        "m_charts":     "Графики трафика",
        "chart_title":  "Трафик за последние {} дней",
        "chart_rx":     "↓ Входящий",
        "chart_tx":     "↑ Исходящий",
        "chart_empty":  "Нет данных для графика",
        "chart_prompt": "Период: [1] 7 дней  [2] 14 дней  [3] 30 дней [1]: ",
        "period_prompt": "Период: [1] Сегодня  [2] Текущий месяц  [3] Всё время: ",
        "rx_total": "Входящий всего",
        "tx_total": "Исходящий всего",
        "m_update": "Обновить vps-net-stat",
        "m_reset_server": "Сбросить трафик сервера",
        "m_reset_port": "Сбросить трафик порта",
        "reset_server_confirm": "Удалить весь трафик сервера? [y/N]: ",
        "reset_port_confirm": "Удалить трафик порта {}? [y/N]: ",
        "reset_done": "Трафик удалён.",
        "reset_abort": "Отмена.",
        "reset_port_prompt": "Номер порта: ",
        "update_done": "Обновление завершено. Сервис перезапущен.",
        "update_fail": "Ошибка обновления. Проверь подключение к интернету.",
        "итого":             "Итого",
        "всего":             "Всего",
    },
    "en": {
        "title":        "vps-net-stat — VPS Network Monitor",
        "menu_header":  "Choose an action:",
        "m1":  "Summary (today / month / all time)",
        "m2":  "Open ports with processes",
        "m3":  "Traffic for today",
        "m4":  "Traffic for current month",
        "m5":  "Traffic by all months",
        "m6":  "Traffic for last N days",
        "m7":  "Top ports by traffic",
        "m8":  "Uninstall",
        "m9":  "Restart service",
        "m10": "Switch language (Переключить на Русский)",
        "m0":  "Exit",
        "choose":       "Your choice: ",
        "days_prompt":  "How many days to show? [30]: ",
        "no_data":      "No data yet.",
        "no_db":        "Database not found. Is the service running?",
        "ports_header": "Open ports",
        "ports_scanned":"scanned at:",
        "ports_total":  "Total ports:",
        "period":       "Period",
        "incoming":     "↓ Incoming",
        "outgoing":     "↑ Outgoing",
        "total":        "Total",
        "today_lbl":    "Today",
        "month_lbl":    "Month",
        "alltime_lbl":  "All time",
        "open_ports":   "Open ports:",
        "disk_usage":   "Disk usage:",
        "disk_db":      "database",
        "disk_app":     "app",
        "summary_title":"vps-net-stat — summary",
        "day_col":      "Day",
        "month_col":    "Month",
        "traffic_today":"Traffic for",
        "traffic_month":"Traffic for month",
        "traffic_months":"Traffic by month",
        "traffic_days": "Traffic for last {} days",
        "port_top":     "Top ports by traffic",
        "port_col":     "Port",
        "proto_col":    "Protocol",
        "process_col":  "Process",
        "uninstall_confirm": "Uninstall vps-net-stat? All data will be deleted. [y/N]: ",
        "uninstall_done":    "Uninstalled successfully.",
        "uninstall_abort":   "Cancelled.",
        "restart_done":      "Service restarted.",
        "lang_switched":     "Language switched. Язык / Language: Русский",
        "press_enter":       "\nPress Enter to return to menu…",
        "m_watch_add":  "Add port for traffic tracking",
        "m_watch_del":  "Remove port from tracking",
        "m_watch_list": "Watched ports",
        "watch_list_empty": "No watched ports. Add one via menu.",
        "watch_add_prompt": "Port number (e.g. 80): ",
        "watch_proto_prompt": "Protocol [tcp/udp, default tcp]: ",
        "watch_comment_prompt": "Comment (optional): ",
        "watch_added": "Port added to tracking.",
        "watch_already": "This port is already being tracked.",
        "watch_del_prompt": "Port number to remove: ",
        "watch_proto_del_prompt": "Protocol [tcp/udp, default tcp]: ",
        "watch_deleted": "Port removed from tracking.",
        "watch_not_found": "Port not found in list.",
        "watch_invalid": "Invalid port number.",
        "comment_col": "Comment",
        "added_col": "Added",
        "version_cur":  "Version:",
        "version_new":  "🟢 New version available:",
        "version_ok":   "Version is up to date",
        "svc_running":  "Service: running",
        "svc_stopped":  "Service: stopped",
        "last_scan":    "Last scan:",
        "db_size_lbl":  "Database:",
        "tracked_lbl":  "Tracked ports:",
        "uptime_lbl":   "Service uptime:",
        "ago":          "ago",
        "never":        "never",
        "sec":          "sec",
        "min":          "min",
        "hrs":          "h",
        "days_ago":     "d",
        "info_title":   "vps-net-stat — info",
        "doctor_title": "vps-net-stat — doctor",
        "doc_sqlite":   "SQLite database accessible",
        "doc_sqlite_bad":"SQLite database corrupted",
        "doc_svc":      "systemd service running",
        "doc_svc_bad":  "systemd service not running",
        "doc_proc":     "/proc/net/dev readable",
        "doc_proc_bad": "/proc/net/dev not accessible",
        "doc_ss":       "ss installed",
        "doc_ss_bad":   "ss not found (apt install iproute2)",
        "doc_ip":       "ip installed",
        "doc_ip_bad":   "ip not found (apt install iproute2)",
        "doc_iface":    "Interface detected:",
        "doc_iface_bad":"No interface detected",
        "doc_write":    "Write access to data directory",
        "doc_write_bad":"No write access to",
        "doc_disk":     "Free disk space:",
        "doc_disk_bad": "Low disk space:",
        "doc_fresh":    "Database updated recently",
        "doc_fresh_bad":"Database not updated — service hung?",
        "doc_all_ok":   "✓ Everything looks good",
        "doc_issues":   "Issues found:",
        "m_info":       "System info",
        "m_doctor":     "Diagnostics",
        "m_export":     "Export statistics",
        "m_limit":      "Set monthly traffic limit",
        "export_choose":"Format: [1] CSV  [2] JSON  [3] Both: ",
        "export_path":  "Save to directory [/root/vns-backup]: ",
        "export_done":  "Export complete:",
        "limit_prompt": "Monthly limit GiB (0 = disable): ",
        "limit_set":    "Limit set:",
        "limit_bar_lbl":"Monthly limit:",
        "limit_none":   "No limit set",
        "m_charts":     "Traffic charts",
        "chart_title":  "Traffic for last {} days",
        "chart_rx":     "↓ Incoming",
        "chart_tx":     "↑ Outgoing",
        "chart_empty":  "No data for chart",
        "chart_prompt": "Period: [1] 7 days  [2] 14 days  [3] 30 days [1]: ",
        "period_prompt": "Period: [1] Today  [2] This month  [3] All time: ",
        "rx_total": "Total incoming",
        "tx_total": "Total outgoing",
        "m_update": "Update vps-net-stat",
        "m_reset_server": "Reset server traffic stats",
        "m_reset_port": "Reset port traffic stats",
        "reset_server_confirm": "Delete all server traffic data? [y/N]: ",
        "reset_port_confirm": "Delete traffic for port {}? [y/N]: ",
        "reset_done": "Traffic data deleted.",
        "reset_abort": "Cancelled.",
        "reset_port_prompt": "Port number: ",
        "update_done": "Update complete. Service restarted.",
        "update_fail": "Update failed. Check internet connection.",
        "итого":             "Total",
        "всего":             "Grand total",
    },
}

lang = load_lang()
T = STRINGS.get(lang, STRINGS["ru"])

# ── Форматирование ────────────────────────────────────────────────────────────
UNITS = [(1024**4,"TiB"),(1024**3,"GiB"),(1024**2,"MiB"),(1024,"KiB"),(1,"B")]

def fmt(b):
    b = b or 0
    for div, unit in UNITS:
        if b >= div:
            return f"{b/div:.2f} {unit}"
    return f"{b} B"

def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    fmt_str = "  ".join(f"{{:<{w}}}" for w in widths)
    sep     = "  ".join("─" * w for w in widths)
    print("  " + fmt_str.format(*headers))
    print("  " + sep)
    for row in rows:
        print("  " + fmt_str.format(*[str(c) for c in row]))

def clear():
    os.system("clear")

def pause():
    input(T["press_enter"])

# ── БД ───────────────────────────────────────────────────────────────────────
def get_db():
    if not os.path.exists(DB_PATH):
        print(f"\n  {T['no_db']}\n")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Команды ──────────────────────────────────────────────────────────────────
def cmd_summary(conn):
    today = date.today().isoformat()
    month = date.today().strftime("%Y-%m")

    def get(where, param):
        r = conn.execute(
            f"SELECT COALESCE(SUM(rx_bytes),0) rx, COALESCE(SUM(tx_bytes),0) tx "
            f"FROM traffic_daily WHERE {where}", (param,)
        ).fetchone()
        return r["rx"], r["tx"]

    rx_d, tx_d = get("day = ?", today)
    rx_m, tx_m = get("day LIKE ?", f"{month}%")
    r = conn.execute("SELECT COALESCE(SUM(rx_bytes),0) rx, COALESCE(SUM(tx_bytes),0) tx FROM traffic_daily").fetchone()
    rx_a, tx_a = r["rx"], r["tx"]
    port_cnt = conn.execute("SELECT COUNT(DISTINCT port) FROM ports WHERE ts=(SELECT MAX(ts) FROM ports)").fetchone()[0]

    tit = T["summary_title"]
    print(f"\n  {tit}")
    print_table(
        [T["period"], T["incoming"], T["outgoing"]],
        [
            (T["today_lbl"],   fmt(rx_d), fmt(tx_d)),
            (T["month_lbl"],   fmt(rx_m), fmt(tx_m)),
            (T["alltime_lbl"], fmt(rx_a), fmt(tx_a)),
        ]
    )
    print(f"  {T['open_ports']} {port_cnt}")


def cmd_ports(conn):
    ts = conn.execute("SELECT MAX(ts) FROM ports").fetchone()[0]
    if not ts:
        print(f"\n  {T['no_data']}\n")
        return
    when = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n  {T['ports_header']} ({T['ports_scanned']} {when})\n")
    rows_raw = conn.execute(
        "SELECT proto, port, state, pid, process FROM ports WHERE ts=? ORDER BY port", (ts,)
    ).fetchall()
    rows = [(r["proto"], r["port"], r["state"], r["pid"] or "—", r["process"] or "—") for r in rows_raw]
    print_table(["Proto","Port","State","PID","Process"], rows)
    print(f"\n  {T['ports_total']} {len(rows)}\n")

def _print_days(rows):
    if not rows:
        print(f"\n  {T['no_data']}\n")
        return
    table, total_rx, total_tx = [], 0, 0
    for r in rows:
        rx, tx = r["rx_bytes"], r["tx_bytes"]
        total_rx += rx; total_tx += tx
        table.append((r["day"] if "day" in r.keys() else r["month"], fmt(rx), fmt(tx), fmt(rx+tx)))
    print_table([T["day_col"], T["incoming"], T["outgoing"], T["total"]], table)
    print()
    lbl = T["итого"]
    print(f"  {lbl:<12}  {fmt(total_rx):<14} {fmt(total_tx):<14} {fmt(total_rx+total_tx)}")
    print()

def cmd_today(conn):
    today = date.today().isoformat()
    print(f"\n  {T['traffic_today']} {today}\n")
    rows = conn.execute(
        "SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes FROM traffic_daily WHERE day=? GROUP BY day",
        (today,)
    ).fetchall()
    _print_days(rows)

def cmd_month(conn):
    month = date.today().strftime("%Y-%m")
    print(f"\n  {T['traffic_month']} {month}\n")
    rows = conn.execute(
        "SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes FROM traffic_daily WHERE day LIKE ? GROUP BY day ORDER BY day",
        (f"{month}%",)
    ).fetchall()
    _print_days(rows)

def cmd_all(conn):
    print(f"\n  {T['traffic_months']}\n")
    rows = conn.execute(
        "SELECT substr(day,1,7) month, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes FROM traffic_daily GROUP BY month ORDER BY month"
    ).fetchall()
    if not rows:
        print(f"  {T['no_data']}\n"); return
    table, total_rx, total_tx = [], 0, 0
    for r in rows:
        rx, tx = r["rx_bytes"], r["tx_bytes"]
        total_rx += rx; total_tx += tx
        table.append((r["month"], fmt(rx), fmt(tx), fmt(rx+tx)))
    print_table([T["month_col"], T["incoming"], T["outgoing"], T["total"]], table)
    print()
    lbl = T["всего"]
    print(f"  {lbl:<12}  {fmt(total_rx):<14} {fmt(total_tx):<14} {fmt(total_rx+total_tx)}")
    print()

def cmd_days(conn, n=30):
    print(f"\n  {T['traffic_days'].format(n)}\n")
    rows = conn.execute(
        "SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes FROM traffic_daily GROUP BY day ORDER BY day DESC LIMIT ?",
        (n,)
    ).fetchall()
    _print_days(list(reversed(rows)))

def cmd_port_top(conn):
    period = input(f"\n  {T['period_prompt']}").strip()
    today = date.today().isoformat()
    month = date.today().strftime("%Y-%m")
    if period == "2":
        where, param, label = "day LIKE ?", f"{month}%", T["month_lbl"]
    elif period == "3":
        where, param, label = "1=1", None, T["alltime_lbl"]
    else:
        where, param, label = "day = ?", today, T["today_lbl"]

    print(f"\n  {T['port_top']} — {label}\n")
    if param is not None:
        rows = conn.execute(f"""
            SELECT port, proto, process,
                   SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
            FROM port_traffic WHERE {where}
            GROUP BY port, proto
            ORDER BY (rx_bytes+tx_bytes) DESC
            LIMIT 20
        """, (param,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT port, proto, process,
                   SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
            FROM port_traffic
            GROUP BY port, proto
            ORDER BY (rx_bytes+tx_bytes) DESC
            LIMIT 20
        """).fetchall()
    if not rows:
        print(f"  {T['no_data']}\n"); return
    table = [
        (r["port"], r["proto"], r["process"] or "—",
         fmt(r["rx_bytes"]), fmt(r["tx_bytes"]),
         fmt((r["rx_bytes"] or 0)+(r["tx_bytes"] or 0)))
        for r in rows
    ]
    print_table([T["port_col"], T["proto_col"], T["process_col"], T["incoming"], T["outgoing"], T["total"]], table)
    print()

def cmd_watch_list(conn):
    print(f"\n  {T['m_watch_list']}\n")
    rows = conn.execute(
        "SELECT port, proto, comment, added FROM watched_ports ORDER BY port"
    ).fetchall()
    if not rows:
        print(f"  {T['watch_list_empty']}\n")
        return
    table = []
    for r in rows:
        tr = conn.execute("""
            SELECT COALESCE(SUM(rx_bytes),0) rx, COALESCE(SUM(tx_bytes),0) tx
            FROM port_traffic WHERE port=? AND proto=?
        """, (r["port"], r["proto"])).fetchone()
        rx, tx = tr["rx"], tr["tx"]
        table.append((
            r["port"], r["proto"], r["comment"] or "—", r["added"],
            fmt(rx), fmt(tx), fmt(rx+tx)
        ))
    print_table([T["port_col"], T["proto_col"], T["comment_col"], T["added_col"],
                 T["incoming"], T["outgoing"], T["total"]], table)
    print()

def cmd_watch_add(conn):
    raw = input(f"\n  {T['watch_add_prompt']}").strip()
    try:
        port = int(raw)
        if not (1 <= port <= 65535):
            raise ValueError
    except ValueError:
        print(f"  {T['watch_invalid']}\n")
        return
    print(f"  Протокол: [1] tcp  [2] udp  [3] оба")
    proto_raw = input(f"  → ").strip()
    if proto_raw == "2":
        protos = ["udp"]
    elif proto_raw == "3":
        protos = ["tcp", "udp"]
    else:
        protos = ["tcp"]
    comment = input(f"  {T['watch_comment_prompt']}").strip() or None
    from datetime import date
    added = 0
    for proto in protos:
        exists = conn.execute(
            "SELECT 1 FROM watched_ports WHERE port=? AND proto=?", (port, proto)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO watched_ports (port, proto, comment, added) VALUES (?, ?, ?, ?)",
                (port, proto, comment, date.today().isoformat())
            )
            added += 1
    conn.commit()
    if added:
        print(f"  {T['watch_added']}\n")
    else:
        print(f"  {T['watch_already']}\n")

def cmd_watch_del(conn):
    cmd_watch_list(conn)
    raw = input(f"  {T['watch_del_prompt']}").strip()
    try:
        port = int(raw)
    except ValueError:
        print(f"  {T['watch_invalid']}\n")
        return
    proto_raw = input(f"  Протокол: [1] tcp  [2] udp [1]: ").strip()
    proto = "udp" if proto_raw == "2" else "tcp"
    cur = conn.execute(
        "DELETE FROM watched_ports WHERE port=? AND proto=?", (port, proto)
    )
    conn.commit()
    if cur.rowcount:
        print(f"  {T['watch_deleted']}\n")
    else:
        print(f"  {T['watch_not_found']}\n")

def do_reset_server(conn):
    ans = input(f"\n  {T['reset_server_confirm']}").strip().lower()
    if ans == "y":
        conn.execute("DELETE FROM traffic_daily")
        conn.commit()
        print(f"  {T['reset_done']}\n")
    else:
        print(f"  {T['reset_abort']}\n")

def do_reset_port(conn):
    cmd_watch_list(conn)
    raw = input(f"  {T['reset_port_prompt']}").strip()
    try:
        port = int(raw)
    except ValueError:
        print(f"  {T['watch_invalid']}\n")
        return
    ans = input(f"  {T['reset_port_confirm'].format(port)}").strip().lower()
    if ans == "y":
        conn.execute("DELETE FROM port_traffic WHERE port=?", (port,))
        conn.commit()
        print(f"  {T['reset_done']}\n")
    else:
        print(f"  {T['reset_abort']}\n")

REPO = "https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main"
INSTALL_DIR = "/opt/vps-net-stat"

def do_update():
    try:
        update_script = f"{INSTALL_DIR}/update.sh"
        # Скачиваем свежий update.sh
        subprocess.run([
            "curl", "-fsSL",
            f"{REPO_RAW}/update.sh",
            "-o", update_script
        ], check=True)
        os.chmod(update_script, 0o755)
        # Запускаем — прогресс виден прямо в терминале
        subprocess.run(["bash", update_script], check=False)
    except Exception as e:
        print(f"\n  {T['update_fail']} ({e})\n")

def do_uninstall():
    ans = input(f"\n  {T['uninstall_confirm']}").strip().lower()
    if ans == "y":
        subprocess.run(["systemctl","stop","vps-net-stat"], check=False)
        subprocess.run(["systemctl","disable","vps-net-stat"], check=False)
        for path in ["/opt/vps-net-stat","/var/lib/vps-net-stat","/var/log/vps-net-stat",
                     "/etc/systemd/system/vps-net-stat.service","/usr/local/bin/vns",
                     "/etc/vps-net-stat"]:
            subprocess.run(["rm","-rf",path], check=False)
        subprocess.run(["systemctl","daemon-reload"], check=False)
        print(f"\n  {T['uninstall_done']}\n")
        sys.exit(0)
    else:
        print(f"  {T['uninstall_abort']}")

def do_restart():
    subprocess.run(["systemctl","restart","vps-net-stat"], check=False)
    print(f"\n  {T['restart_done']}\n")

def switch_lang():
    global lang, T
    new_lang = "en" if lang == "ru" else "ru"
    os.makedirs(os.path.dirname(LANG_FILE), exist_ok=True)
    with open(LANG_FILE, "w") as f:
        f.write(new_lang)
    lang = new_lang
    T = STRINGS[lang]
    print(f"\n  {T['lang_switched']}\n")

# ── Интерактивное меню ────────────────────────────────────────────────────────

VERSION = "3.3.0"
REPO_RAW = "https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main"
VERSION_URL = f"{REPO_RAW}/version.txt"

# ── Версия и проверка обновлений ─────────────────────────────────────────────
def get_local_version():
    try:
        with open("/opt/vps-net-stat/version.txt") as f:
            return f.read().strip()
    except Exception:
        return VERSION

def check_remote_version():
    try:
        import urllib.request
        with urllib.request.urlopen(VERSION_URL, timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return None

# ── Время с последнего скана ─────────────────────────────────────────────────
def time_ago(ts):
    if not ts:
        return T["never"]
    diff = int(time.time()) - ts
    if diff < 60:   return f"{diff} {T['sec']} {T['ago']}"
    if diff < 3600: return f"{diff//60} {T['min']} {T['ago']}"
    if diff < 86400:return f"{diff//3600} {T['hrs']} {T['ago']}"
    return f"{diff//86400} {T['days_ago']} {T['ago']}"

def service_uptime():
    try:
        out = subprocess.check_output(
            ["systemctl", "show", "vps-net-stat",
             "--property=ActiveEnterTimestampMonotonic"],
            text=True
        ).strip()
        val = out.split("=", 1)[-1].strip()
        if not val or val == "0":
            return "—"
        # Монотонное время в микросекундах
        mono_us = int(val)
        # Текущее монотонное время через /proc/uptime
        with open("/proc/uptime") as f:
            uptime_sec = float(f.read().split()[0])
        boot_mono_us = uptime_sec * 1_000_000
        # Когда сервис стартовал относительно сейчас
        diff = int((boot_mono_us - mono_us) / 1_000_000)
        if diff < 0:
            diff = 0
        d, h, m = diff//86400, (diff%86400)//3600, (diff%3600)//60
        return f"{d}{T['days_ago']} {h}{T['hrs']} {m}{T['min']}"
    except Exception:
        return "—"

# ── vns info ─────────────────────────────────────────────────────────────────
def cmd_info(conn):
    local_ver = get_local_version()
    remote_ver = check_remote_version()

    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    tracked = conn.execute("SELECT COUNT(*) FROM watched_ports").fetchone()[0]
    last_ts = conn.execute("SELECT MAX(ts) FROM ports").fetchone()[0]

    try:
        svc = subprocess.check_output(
            ["systemctl", "is-active", "vps-net-stat"], text=True
        ).strip()
        svc_ok = svc == "active"
    except Exception:
        svc_ok = False

    GRN = "\033[0;32m"; RED = "\033[0;31m"; NC = "\033[0m"
    svc_color = GRN if svc_ok else RED
    svc_str   = T["svc_running"] if svc_ok else T["svc_stopped"]

    print(f"\n  {T['info_title']}\n")
    print(f"  {T['svc_running' if svc_ok else 'svc_stopped']:<26}".replace(
        T['svc_running' if svc_ok else 'svc_stopped'],
        f"{svc_color}{svc_str}{NC}"
    ))
    print(f"  {T['uptime_lbl']:<26} {service_uptime()}")
    print(f"  {T['last_scan']:<26} {time_ago(last_ts)}")
    print(f"  {T['db_size_lbl']:<26} {fmt(db_size)}")
    print(f"  {T['tracked_lbl']:<26} {tracked}")
    print()

# ── vns doctor ───────────────────────────────────────────────────────────────
def cmd_doctor(conn):
    print(f"\n  {T['doctor_title']}\n")
    issues = []

    def chk(ok, msg_ok, msg_fail):
        sym = "\033[0;32m✓\033[0m" if ok else "\033[0;31m✗\033[0m"
        msg = msg_ok if ok else msg_fail
        print(f"  {sym} {msg}")
        if not ok:
            issues.append(msg_fail)

    # systemd
    try:
        svc = subprocess.check_output(["systemctl","is-active","vps-net-stat"],text=True).strip()
        chk(svc=="active", T["doc_svc"], T["doc_svc_bad"])
    except Exception:
        chk(False, T["doc_svc"], T["doc_svc_bad"])

    # SQLite
    try:
        conn.execute("SELECT 1 FROM traffic_daily LIMIT 1")
        chk(True, T["doc_sqlite"], T["doc_sqlite_bad"])
    except Exception:
        chk(False, T["doc_sqlite"], T["doc_sqlite_bad"])

    # /proc/net/dev
    chk(os.path.readable("/proc/net/dev") if hasattr(os.path,"readable") else os.access("/proc/net/dev", os.R_OK),
        T["doc_proc"], T["doc_proc_bad"])

    # ss
    import shutil
    chk(shutil.which("ss") is not None, T["doc_ss"], T["doc_ss_bad"])

    # ip
    chk(shutil.which("ip") is not None, T["doc_ip"], T["doc_ip_bad"])

    # Интерфейс
    try:
        out = subprocess.check_output(["ip","route"],text=True)
        ifaces = [l.split()[l.split().index("dev")+1] for l in out.splitlines() if "default" in l and "dev" in l]
        chk(bool(ifaces), f"{T['doc_iface']} {', '.join(ifaces)}", T["doc_iface_bad"])
    except Exception:
        chk(False, T["doc_iface"], T["doc_iface_bad"])

    # Права на запись
    chk(os.access("/var/lib/vps-net-stat", os.W_OK),
        T["doc_write"], f"{T['doc_write_bad']} /var/lib/vps-net-stat")

    # Свободное место
    try:
        st = os.statvfs("/var/lib/vps-net-stat")
        free = st.f_bavail * st.f_frsize
        ok_disk = free > 100 * 1024 * 1024
        chk(ok_disk, f"{T['doc_disk']} {fmt(free)}", f"{T['doc_disk_bad']} {fmt(free)}")
    except Exception:
        pass

    # Свежесть базы
    last_ts = conn.execute("SELECT MAX(ts) FROM ports").fetchone()[0]
    if last_ts:
        fresh = (time.time() - last_ts) < 600
        chk(fresh, T["doc_fresh"], T["doc_fresh_bad"])

    print()
    if not issues:
        print(f"  {T['doc_all_ok']}\n")
    else:
        print(f"  {T['doc_issues']} {len(issues)}\n")

# ── Экспорт ──────────────────────────────────────────────────────────────────
def cmd_export(conn):
    fmt_choice = input(f"\n  {T['export_choose']}").strip()
    path_raw = input(f"  {T['export_path']}").strip()
    out_dir = path_raw if path_raw else "/root/vns-backup"
    os.makedirs(out_dir, exist_ok=True)

    do_csv  = fmt_choice in ("1", "3", "")
    do_json = fmt_choice in ("2", "3")

    rows_traffic = conn.execute(
        "SELECT day, iface, rx_bytes, tx_bytes FROM traffic_daily ORDER BY day"
    ).fetchall()
    rows_ports = conn.execute(
        "SELECT port, proto, process, day, rx_bytes, tx_bytes FROM port_traffic ORDER BY day"
    ).fetchall()
    rows_watched = conn.execute(
        "SELECT port, proto, comment, added FROM watched_ports"
    ).fetchall()

    saved = []

    if do_csv:
        import csv
        p = os.path.join(out_dir, "vns_traffic.csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["day","iface","rx_bytes","tx_bytes"])
            for r in rows_traffic:
                w.writerow([r["day"],r["iface"],r["rx_bytes"],r["tx_bytes"]])
        saved.append(p)

        p = os.path.join(out_dir, "vns_port_traffic.csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["port","proto","process","day","rx_bytes","tx_bytes"])
            for r in rows_ports:
                w.writerow([r["port"],r["proto"],r["process"],r["day"],r["rx_bytes"],r["tx_bytes"]])
        saved.append(p)

        p = os.path.join(out_dir, "vns_watched.csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["port","proto","comment","added"])
            for r in rows_watched:
                w.writerow([r["port"],r["proto"],r["comment"],r["added"]])
        saved.append(p)

    if do_json:
        import json
        data = {
            "traffic_daily":  [dict(r) for r in rows_traffic],
            "port_traffic":   [dict(r) for r in rows_ports],
            "watched_ports":  [dict(r) for r in rows_watched],
        }
        p = os.path.join(out_dir, "vns_export.json")
        with open(p, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        saved.append(p)

    print(f"\n  {T['export_done']}")
    for s in saved:
        print(f"    {s}")
    print()


# ── Графики ───────────────────────────────────────────────────────────────────
def cmd_charts(conn):
    choice = input(f"\n  {T['chart_prompt']}").strip()
    days = 14 if choice == "2" else 30 if choice == "3" else 7

    rows = conn.execute("""
        SELECT day, SUM(rx_bytes) rx, SUM(tx_bytes) tx
        FROM traffic_daily
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
    """, (days,)).fetchall()
    rows = list(reversed(rows))

    if not rows:
        print(f"\n  {T['chart_empty']}\n")
        return

    print(f"\n  {T['chart_title'].format(days)}\n")

    max_val = max((r["rx"] + r["tx"]) for r in rows) or 1
    bar_width = 30

    GRN = "\033[0;32m"
    CYN = "\033[0;36m"
    NC  = "\033[0m"

    for r in rows:
        day   = r["day"][5:]  # MM-DD
        rx, tx = r["rx"], r["tx"]
        total  = rx + tx

        rx_len = int(rx / max_val * bar_width)
        tx_len = int(tx / max_val * bar_width)

        rx_bar = GRN + "█" * rx_len + NC
        tx_bar = CYN + "█" * tx_len + NC

        print(f"  {day}  {rx_bar}{tx_bar}  {fmt(total)}")

    print()
    # Легенда
    print(f"  \033[0;32m█\033[0m {T['chart_rx']}   \033[0;36m█\033[0m {T['chart_tx']}")

    # Итого
    total_rx = sum(r["rx"] for r in rows)
    total_tx = sum(r["tx"] for r in rows)
    print(f"\n  {T['итого']}: {fmt(total_rx + total_tx)}  ({T['chart_rx']}: {fmt(total_rx)}, {T['chart_tx']}: {fmt(total_tx)})")
    print()

# ── Месячный лимит ────────────────────────────────────────────────────────────
LIMIT_FILE = "/etc/vps-net-stat/limit_gib"

def get_limit():
    try:
        with open(LIMIT_FILE) as f:
            v = float(f.read().strip())
            return v if v > 0 else None
    except Exception:
        return None

def cmd_set_limit():
    current = get_limit()
    cur_str = f"{current} GiB" if current else T["limit_none"]
    print(f"\n  {T['limit_bar_lbl']} {cur_str}")
    raw = input(f"  {T['limit_prompt']}").strip()
    try:
        val = float(raw)
        os.makedirs("/etc/vps-net-stat", exist_ok=True)
        with open(LIMIT_FILE, "w") as f:
            f.write(str(val))
        if val > 0:
            print(f"  {T['limit_set']} {val} GiB\n")
        else:
            print(f"  {T['limit_none']}\n")
    except ValueError:
        print(f"  {T['watch_invalid']}\n")

def limit_bar(conn):
    limit = get_limit()
    if limit is None:
        return None
    month = date.today().strftime("%Y-%m")
    r = conn.execute(
        "SELECT COALESCE(SUM(rx_bytes+tx_bytes),0) total FROM traffic_daily WHERE day LIKE ?",
        (f"{month}%",)
    ).fetchone()
    used_gib = r["total"] / (1024**3)
    pct = min(used_gib / limit, 1.0)
    bar_len = 20
    filled = int(pct * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    color = "\033[0;31m" if pct > 0.9 else "\033[1;33m" if pct > 0.7 else "\033[0;32m"
    nc = "\033[0m"
    return f"  {T['limit_bar_lbl']} {color}{bar}{nc} {used_gib:.1f} / {limit:.0f} GiB ({pct*100:.0f}%)"

def show_menu():
    clear()

    def dir_size(path):
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += dir_size(entry.path)
        except Exception:
            pass
        return total

    db_size  = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    app_size = dir_size("/opt/vps-net-stat")
    disk_str = f"{fmt(db_size + app_size)}  ({T['disk_db']}: {fmt(db_size)}, {T['disk_app']}: {fmt(app_size)})"

    local_ver   = get_local_version()
    remote_ver  = check_remote_version()
    # Лимит (только если установлен — нужна БД)
    bar_line = None
    try:
        conn_tmp = sqlite3.connect(DB_PATH)
        conn_tmp.row_factory = sqlite3.Row
        bar_line = limit_bar(conn_tmp)
        conn_tmp.close()
    except Exception:
        pass

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║  {T['title']:<36}║")
    print(f"  ╚══════════════════════════════════════╝")
    if remote_ver and remote_ver != local_ver:
        ver_color = "\033[0;31m"  # красный — устарела
        update_note = f"  \033[0;32m{T['version_new']} {remote_ver}\033[0m"
    else:
        ver_color = "\033[0;32m"  # зелёный — актуальна
        update_note = None
    print(f"  {T['version_cur']} {ver_color}{local_ver}\033[0m")
    if update_note:
        print(update_note)
    print(f"  {T['disk_usage']} {disk_str}")
    if bar_line:
        print(bar_line)
    print(f"\n  {T['menu_header']}\n")
    items = [
        ("1",  T["m1"]),
        ("2",  T["m2"]),
        ("3",  T["m5"]),
        ("4",  T["m6"]),
        ("5",  T["m7"]),
        ("6",  T["m_charts"]),
        ("─",  None),
        ("7",  T["m_watch_add"]),
        ("8",  T["m_watch_del"]),
        ("9",  T["m_watch_list"]),
        ("─",  None),
        ("10", T["m_reset_server"]),
        ("11", T["m_reset_port"]),
        ("12", T["m_export"]),
        ("13", T["m_limit"]),
        ("─",  None),
        ("14", T["m_info"]),
        ("15", T["m_doctor"]),
        ("─",  None),
        ("16", T["m8"]),
        ("17", T["m_update"]),
        ("18", T["m9"]),
        ("19", T["m10"]),
        ("0",  T["m0"]),
    ]
    for key, label in items:
        if key == "─":
            print(f"  {'─'*40}")
        else:
            print(f"  [{key}] {label}")
    print()

def interactive_menu():
    while True:
        show_menu()
        choice = input(f"  {T['choose']}").strip()

        if choice == "0":
            clear()
            sys.exit(0)
        elif choice == "19":
            switch_lang()
            pause()
            continue

        # Команды требующие БД
        if choice in ("1","2","3","4","5","6","7","8","9","10","11","12","14","15"):
            conn = get_db()
            clear()
            if   choice == "1":  cmd_summary(conn)
            elif choice == "2":  cmd_ports(conn)
            elif choice == "3":  cmd_all(conn)
            elif choice == "4":
                try:
                    raw = input(f"  {T['days_prompt']}").strip()
                    n = int(raw) if raw else 30
                except ValueError:
                    n = 30
                cmd_days(conn, n)
            elif choice == "5":  cmd_port_top(conn)
            elif choice == "6":  cmd_charts(conn)
            elif choice == "7":  cmd_watch_add(conn)
            elif choice == "8":  cmd_watch_del(conn)
            elif choice == "9":  cmd_watch_list(conn)
            elif choice == "10": do_reset_server(conn)
            elif choice == "11": do_reset_port(conn)
            elif choice == "12": cmd_export(conn)
            elif choice == "14": cmd_info(conn)
            elif choice == "15": cmd_doctor(conn)
            conn.close()
            pause()
        elif choice == "13":
            cmd_set_limit()
            pause()
        elif choice == "16":
            do_uninstall()
            pause()
        elif choice == "17":
            do_update()
            pause()
        elif choice == "18":
            do_restart()
            pause()
        else:
            pass

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    interactive_menu()

if __name__ == "__main__":
    main()
