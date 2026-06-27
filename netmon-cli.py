#!/usr/bin/env python3
"""vps-net-stat CLI"""

import sqlite3, sys, os, subprocess
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
    w = len(tit) + 4
    print()
    print(f"  ┌{'─'*w}┐")
    print(f"  │  {tit}  │")
    print(f"  ├{'─'*14}┬{'─'*15}┬{'─'*16}┤")
    print(f"  │ {T['period']:<12} │ {T['incoming']:<13} │ {T['outgoing']:<14} │")
    print(f"  ├{'─'*14}┼{'─'*15}┼{'─'*16}┤")
    print(f"  │ {T['today_lbl']:<12} │ {fmt(rx_d):<13} │ {fmt(tx_d):<14} │")
    print(f"  │ {T['month_lbl']:<12} │ {fmt(rx_m):<13} │ {fmt(tx_m):<14} │")
    print(f"  │ {T['alltime_lbl']:<12} │ {fmt(rx_a):<13} │ {fmt(tx_a):<14} │")
    print(f"  └{'─'*14}┴{'─'*15}┴{'─'*16}┘")
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
    proto_raw = input(f"  {T['watch_proto_prompt']}").strip().lower()
    proto = proto_raw if proto_raw in ("tcp", "udp") else "tcp"
    exists = conn.execute(
        "SELECT 1 FROM watched_ports WHERE port=? AND proto=?", (port, proto)
    ).fetchone()
    if exists:
        print(f"  {T['watch_already']}\n")
        return
    comment = input(f"  {T['watch_comment_prompt']}").strip() or None
    from datetime import date
    conn.execute(
        "INSERT INTO watched_ports (port, proto, comment, added) VALUES (?, ?, ?, ?)",
        (port, proto, comment, date.today().isoformat())
    )
    conn.commit()
    print(f"  {T['watch_added']}\n")

def cmd_watch_del(conn):
    cmd_watch_list(conn)
    raw = input(f"  {T['watch_del_prompt']}").strip()
    try:
        port = int(raw)
    except ValueError:
        print(f"  {T['watch_invalid']}\n")
        return
    proto_raw = input(f"  {T['watch_proto_del_prompt']}").strip().lower()
    proto = proto_raw if proto_raw in ("tcp", "udp") else "tcp"
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
    import urllib.request
    files = ["netmon.py", "netmon-cli.py"]
    try:
        for fname in files:
            url = f"{REPO}/{fname}"
            dest = f"{INSTALL_DIR}/{fname}"
            urllib.request.urlretrieve(url, dest)
            os.chmod(dest, 0o755)
        subprocess.run(["systemctl", "restart", "vps-net-stat"], check=False)
        print(f"\n  {T['update_done']}\n")
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
def show_menu():
    clear()

    # Размер на диске
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

    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║  {T['title']:<36}║")
    print(f"  ╚══════════════════════════════════════╝")
    print(f"  {T['disk_usage']} {disk_str}\n")
    print(f"  {T['menu_header']}\n")
    items = [
        ("1",  T["m1"]),
        ("2",  T["m2"]),
        ("3",  T["m3"]),
        ("4",  T["m4"]),
        ("5",  T["m5"]),
        ("6",  T["m6"]),
        ("7",  T["m7"]),
        ("─",  None),
        ("8",  T["m_watch_add"]),
        ("9",  T["m_watch_del"]),
        ("wl", T["m_watch_list"]),
        ("─",  None),
        ("10", T["m_reset_server"]),
        ("11", T["m_reset_port"]),
        ("─",  None),
        ("12", T["m8"]),
        ("13", T["m_update"]),
        ("14", T["m9"]),
        ("15", T["m10"]),
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
        elif choice == "15":
            switch_lang()
            pause()
            continue

        # Команды требующие БД
        if choice in ("1","2","3","4","5","6","7","wl","8","9","10","11"):
            conn = get_db()
            clear()
            if   choice == "1": cmd_summary(conn)
            elif choice == "2": cmd_ports(conn)
            elif choice == "3": cmd_today(conn)
            elif choice == "4": cmd_month(conn)
            elif choice == "5": cmd_all(conn)
            elif choice == "6":
                try:
                    raw = input(f"  {T['days_prompt']}").strip()
                    n = int(raw) if raw else 30
                except ValueError:
                    n = 30
                cmd_days(conn, n)
            elif choice == "7": cmd_port_top(conn)
            elif choice == "wl": cmd_watch_list(conn)
            elif choice == "8": cmd_watch_add(conn)
            elif choice == "9": cmd_watch_del(conn)
            elif choice == "10": do_reset_server(conn)
            elif choice == "11": do_reset_port(conn)
            conn.close()
            pause()
        elif choice == "12":
            do_uninstall()
            pause()
        elif choice == "13":
            do_update()
            pause()
        elif choice == "14":
            do_restart()
            pause()
        else:
            pass  # неверный ввод — просто перерисуем меню

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    interactive_menu()

if __name__ == "__main__":
    main()
