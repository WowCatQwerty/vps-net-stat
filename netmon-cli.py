#!/usr/bin/env python3
"""
vps-net-stat CLI — интерактивное меню / direct commands
Вызов меню:  vns
Прямые команды: vns summary / ports / today / month / all / days [N] / port-top
"""

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
        "summary_title":"vps-net-stat — сводка",
        "day_col":      "День",
        "month_col":    "Месяц",
        "traffic_today":"Трафик за",
        "traffic_month":"Трафик за месяц",
        "traffic_months":"Трафик по месяцам",
        "traffic_days": "Трафик за последние {} дней",
        "port_top":     "Топ портов по трафику (сегодня)",
        "port_col":     "Порт",
        "proto_col":    "Протокол",
        "process_col":  "Процесс",
        "uninstall_confirm": "Удалить vps-net-stat? Все данные будут удалены. [y/N]: ",
        "uninstall_done":    "Программа удалена.",
        "uninstall_abort":   "Отмена.",
        "restart_done":      "Сервис перезапущен.",
        "lang_switched":     "Язык переключён. Язык / Language: English",
        "press_enter":       "\nНажмите Enter для возврата в меню…",
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
        "summary_title":"vps-net-stat — summary",
        "day_col":      "Day",
        "month_col":    "Month",
        "traffic_today":"Traffic for",
        "traffic_month":"Traffic for month",
        "traffic_months":"Traffic by month",
        "traffic_days": "Traffic for last {} days",
        "port_top":     "Top ports by traffic (today)",
        "port_col":     "Port",
        "proto_col":    "Protocol",
        "process_col":  "Process",
        "uninstall_confirm": "Uninstall vps-net-stat? All data will be deleted. [y/N]: ",
        "uninstall_done":    "Uninstalled successfully.",
        "uninstall_abort":   "Cancelled.",
        "restart_done":      "Service restarted.",
        "lang_switched":     "Language switched. Язык / Language: Русский",
        "press_enter":       "\nPress Enter to return to menu…",
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
    print()

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
    today = date.today().isoformat()
    print(f"\n  {T['port_top']}\n")
    rows = conn.execute("""
        SELECT port, proto, process,
               SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
        FROM port_traffic WHERE day=?
        GROUP BY port, proto
        ORDER BY (rx_bytes+tx_bytes) DESC
        LIMIT 20
    """, (today,)).fetchall()
    if not rows:
        print(f"  {T['no_data']}\n"); return
    table = [
        (r["port"], r["proto"], r["process"] or "—", fmt(r["rx_bytes"]), fmt(r["tx_bytes"]), fmt((r["rx_bytes"] or 0)+(r["tx_bytes"] or 0)))
        for r in rows
    ]
    print_table([T["port_col"], T["proto_col"], T["process_col"], T["incoming"], T["outgoing"], T["total"]], table)
    print()

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
    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║  {T['title']:<36}║")
    print(f"  ╚══════════════════════════════════════╝\n")
    print(f"  {T['menu_header']}\n")
    items = [
        ("1", T["m1"]),
        ("2", T["m2"]),
        ("3", T["m3"]),
        ("4", T["m4"]),
        ("5", T["m5"]),
        ("6", T["m6"]),
        ("7", T["m7"]),
        ("─", None),
        ("8", T["m8"]),
        ("9", T["m9"]),
        ("10",T["m10"]),
        ("0", T["m0"]),
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
        elif choice == "10":
            switch_lang()
            pause()
            continue

        # Команды требующие БД
        if choice in ("1","2","3","4","5","6","7"):
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
            conn.close()
            pause()
        elif choice == "8":
            do_uninstall()
            pause()
        elif choice == "9":
            do_restart()
            pause()
        else:
            pass  # неверный ввод — просто перерисуем меню

# ── Direct CLI ────────────────────────────────────────────────────────────────
def direct_cli():
    cmd  = sys.argv[1]
    conn = get_db()
    if   cmd == "summary": cmd_summary(conn)
    elif cmd == "ports":   cmd_ports(conn)
    elif cmd == "today":   cmd_today(conn)
    elif cmd == "month":   cmd_month(conn)
    elif cmd == "all":     cmd_all(conn)
    elif cmd == "days":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cmd_days(conn, n)
    elif cmd == "port-top": cmd_port_top(conn)
    else:
        print(__doc__)
    conn.close()

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) > 1:
        direct_cli()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
