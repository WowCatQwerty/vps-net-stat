#!/usr/bin/env python3
"""
netmon-cli — просмотр статистики netmon
Использование:
  netmon-cli ports          — текущие открытые порты
  netmon-cli today          — трафик за сегодня
  netmon-cli month          — трафик за текущий месяц
  netmon-cli all            — трафик по всем месяцам
  netmon-cli days [N]       — последние N дней (по умолчанию 30)
  netmon-cli summary        — сводка: сегодня / месяц / всего
"""

import sqlite3
import sys
import os
from datetime import date, datetime

DB_PATH = "/var/lib/netmon/netmon.db"

UNITS = [
    (1024**4, "TiB"),
    (1024**3, "GiB"),
    (1024**2, "MiB"),
    (1024,    "KiB"),
    (1,       "B"),
]

def fmt(b):
    for div, unit in UNITS:
        if b >= div:
            return f"{b/div:.2f} {unit}"
    return f"{b} B"

def get_db():
    if not os.path.exists(DB_PATH):
        print(f"База данных не найдена: {DB_PATH}")
        print("Запущен ли сервис netmon?")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Таблица ───────────────────────────────────────────────────────────────────
def print_table(headers, rows, col_widths=None):
    if not col_widths:
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    fmt_str = "  ".join(f"{{:<{w}}}" for w in col_widths)
    sep = "  ".join("─" * w for w in col_widths)
    print(fmt_str.format(*headers))
    print(sep)
    for row in rows:
        print(fmt_str.format(*[str(c) for c in row]))

# ── Команды ───────────────────────────────────────────────────────────────────
def cmd_ports(conn):
    """Последний снапшот портов"""
    cur = conn.execute("SELECT MAX(ts) FROM ports")
    ts = cur.fetchone()[0]
    if not ts:
        print("Нет данных о портах.")
        return

    when = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n  Открытые порты (снято: {when})\n")

    rows_raw = conn.execute("""
        SELECT proto, port, state, pid, process
        FROM ports WHERE ts = ?
        ORDER BY port
    """, (ts,)).fetchall()

    rows = []
    for r in rows_raw:
        rows.append((
            r["proto"],
            r["port"],
            r["state"],
            r["pid"] or "—",
            r["process"] or "—",
        ))

    print_table(["Proto", "Port", "State", "PID", "Process"], rows)
    print(f"\n  Итого: {len(rows)} портов\n")

def _traffic_for_days(conn, days_rows):
    """Форматирует список строк (day, rx_bytes, tx_bytes) в таблицу"""
    if not days_rows:
        print("  Нет данных.\n")
        return

    rows = []
    total_rx = total_tx = 0
    for r in days_rows:
        rx, tx = r["rx_bytes"], r["tx_bytes"]
        total_rx += rx
        total_tx += tx
        rows.append((r["day"], fmt(rx), fmt(tx), fmt(rx + tx)))

    print_table(["День", "Входящий", "Исходящий", "Всего"], rows)
    print()
    print(f"  {'Итого':<12}  {fmt(total_rx):<12}  {fmt(total_tx):<12}  {fmt(total_rx+total_tx)}")
    print()

def cmd_today(conn):
    today = date.today().isoformat()
    print(f"\n  Трафик за {today}\n")
    rows = conn.execute("""
        SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
        FROM traffic_daily WHERE day = ?
        GROUP BY day
    """, (today,)).fetchall()
    _traffic_for_days(conn, rows)

def cmd_month(conn):
    month = date.today().strftime("%Y-%m")
    print(f"\n  Трафик за месяц {month}\n")
    rows = conn.execute("""
        SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
        FROM traffic_daily WHERE day LIKE ?
        GROUP BY day ORDER BY day
    """, (f"{month}%",)).fetchall()
    _traffic_for_days(conn, rows)

def cmd_days(conn, n=30):
    print(f"\n  Трафик за последние {n} дней\n")
    rows = conn.execute("""
        SELECT day, SUM(rx_bytes) rx_bytes, SUM(tx_bytes) tx_bytes
        FROM traffic_daily
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
    """, (n,)).fetchall()
    rows = list(reversed(rows))
    _traffic_for_days(conn, rows)

def cmd_all(conn):
    """По месяцам"""
    print("\n  Трафик по месяцам\n")
    rows = conn.execute("""
        SELECT substr(day,1,7) AS month,
               SUM(rx_bytes) rx_bytes,
               SUM(tx_bytes) tx_bytes
        FROM traffic_daily
        GROUP BY month
        ORDER BY month
    """).fetchall()

    if not rows:
        print("  Нет данных.\n")
        return

    table_rows = []
    total_rx = total_tx = 0
    for r in rows:
        rx, tx = r["rx_bytes"], r["tx_bytes"]
        total_rx += rx
        total_tx += tx
        table_rows.append((r["month"], fmt(rx), fmt(tx), fmt(rx + tx)))

    print_table(["Месяц", "Входящий", "Исходящий", "Всего"], table_rows)
    print()
    print(f"  {'Всего':<12}  {fmt(total_rx):<12}  {fmt(total_tx):<12}  {fmt(total_rx+total_tx)}")
    print()

def cmd_summary(conn):
    today = date.today().isoformat()
    month = date.today().strftime("%Y-%m")

    def get(where, param):
        r = conn.execute(f"""
            SELECT COALESCE(SUM(rx_bytes),0) rx, COALESCE(SUM(tx_bytes),0) tx
            FROM traffic_daily WHERE {where}
        """, (param,)).fetchone()
        return r["rx"], r["tx"]

    rx_d, tx_d = get("day = ?", today)
    rx_m, tx_m = get("day LIKE ?", f"{month}%")

    r_all = conn.execute("""
        SELECT COALESCE(SUM(rx_bytes),0) rx, COALESCE(SUM(tx_bytes),0) tx
        FROM traffic_daily
    """).fetchone()
    rx_a, tx_a = r_all["rx"], r_all["tx"]

    # Порты
    cur = conn.execute("SELECT COUNT(DISTINCT port) FROM ports WHERE ts = (SELECT MAX(ts) FROM ports)")
    port_cnt = cur.fetchone()[0]

    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │             netmon — сводка                 │")
    print("  ├────────────┬───────────────┬────────────────┤")
    print("  │ Период     │ ↓ Входящий    │ ↑ Исходящий    │")
    print("  ├────────────┼───────────────┼────────────────┤")
    print(f"  │ Сегодня    │ {fmt(rx_d):<13} │ {fmt(tx_d):<14} │")
    print(f"  │ Месяц      │ {fmt(rx_m):<13} │ {fmt(tx_m):<14} │")
    print(f"  │ Всё время  │ {fmt(rx_a):<13} │ {fmt(tx_a):<14} │")
    print("  └────────────┴───────────────┴────────────────┘")
    print(f"  Открытых портов: {port_cnt}")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    conn = get_db()

    if cmd == "ports":
        cmd_ports(conn)
    elif cmd == "today":
        cmd_today(conn)
    elif cmd == "month":
        cmd_month(conn)
    elif cmd == "all":
        cmd_all(conn)
    elif cmd == "days":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cmd_days(conn, n)
    elif cmd == "summary":
        cmd_summary(conn)
    else:
        print(__doc__)

    conn.close()

if __name__ == "__main__":
    main()
