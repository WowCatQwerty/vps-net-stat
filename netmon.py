#!/usr/bin/env python3
"""
netmon — Network & Port Monitor Daemon
Отслеживает занятые порты и считает интернет-трафик.
Данные сохраняются в SQLite — переживают перезагрузки.
"""

import sqlite3
import subprocess
import time
import os
import sys
import signal
import logging
from datetime import datetime, date

# ── Конфиг ──────────────────────────────────────────────────────────────────
DB_PATH       = "/var/lib/netmon/netmon.db"
LOG_PATH      = "/var/log/netmon/netmon.log"
INTERVAL      = 60    # секунд между снятием трафика
PORT_INTERVAL = 300   # секунд между сканом портов

# Префиксы виртуальных/внутренних интерфейсов — всегда исключаем
VIRTUAL_PREFIXES = ("lo", "veth", "docker", "virbr", "tun", "br-", "dummy",
                    "bond", "vlan", "wg", "zt")

# ── Логирование ──────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("netmon")

# ── Автодетект интерфейсов ────────────────────────────────────────────────────
def detect_ifaces():
    """
    Определяет «внешние» сетевые интерфейсы автоматически:
    1. Читает /proc/net/dev
    2. Отфильтровывает виртуальные/loopback
    3. Оставляет только те, у которых есть default route (реальный интернет)
    """
    # Интерфейсы с default route
    try:
        out = subprocess.check_output(["ip", "route"], text=True)
        routed = set()
        for line in out.splitlines():
            if line.startswith("default"):
                parts = line.split()
                idx = parts.index("dev") + 1
                routed.add(parts[idx])
    except Exception:
        routed = set()

    # Все интерфейсы из /proc/net/dev
    all_ifaces = []
    with open("/proc/net/dev") as f:
        for line in f:
            if ":" not in line:
                continue
            iface = line.split(":")[0].strip()
            if any(iface.startswith(p) for p in VIRTUAL_PREFIXES):
                continue
            all_ifaces.append(iface)

    # Предпочитаем интерфейсы с default route; если таких нет — берём все реальные
    result = [i for i in all_ifaces if i in routed] or all_ifaces
    return result

# ── База данных ───────────────────────────────────────────────────────────────
def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS traffic_daily (
            day        TEXT NOT NULL,
            iface      TEXT NOT NULL,
            rx_bytes   INTEGER NOT NULL DEFAULT 0,
            tx_bytes   INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (day, iface)
        );

        CREATE TABLE IF NOT EXISTS ports (
            ts         INTEGER NOT NULL,
            proto      TEXT NOT NULL,
            port       INTEGER NOT NULL,
            state      TEXT NOT NULL,
            pid        INTEGER,
            process    TEXT,
            PRIMARY KEY (ts, proto, port)
        );
    """)
    conn.commit()

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn

# ── Чтение /proc/net/dev ──────────────────────────────────────────────────────
def read_iface_stats(ifaces):
    stats = {}
    with open("/proc/net/dev") as f:
        for line in f:
            if ":" not in line:
                continue
            iface, rest = line.split(":", 1)
            iface = iface.strip()
            if iface not in ifaces:
                continue
            fields = rest.split()
            stats[iface] = (int(fields[0]), int(fields[8]))
    return stats

# ── Счётчик трафика ───────────────────────────────────────────────────────────
class TrafficCounter:
    def __init__(self, conn, ifaces):
        self.conn   = conn
        self.ifaces = ifaces
        self.prev   = {}

    def tick(self):
        current = read_iface_stats(self.ifaces)
        for iface, (rx, tx) in current.items():
            if iface in self.prev:
                prx, ptx = self.prev[iface]
                rx_delta = rx - prx if rx >= prx else rx
                tx_delta = tx - ptx if tx >= ptx else tx
                if rx_delta > 0 or tx_delta > 0:
                    day = date.today().isoformat()
                    self.conn.execute("""
                        INSERT INTO traffic_daily (day, iface, rx_bytes, tx_bytes)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(day, iface) DO UPDATE SET
                            rx_bytes = rx_bytes + excluded.rx_bytes,
                            tx_bytes = tx_bytes + excluded.tx_bytes
                    """, (day, iface, rx_delta, tx_delta))
            self.prev[iface] = (rx, tx)
        self.conn.commit()

# ── Сканер портов ─────────────────────────────────────────────────────────────
def scan_ports(conn):
    ts = int(time.time())
    try:
        result = subprocess.run(
            ["ss", "-tlnupH"],
            capture_output=True, text=True, timeout=10
        )
    except Exception as e:
        log.warning(f"ss failed: {e}")
        return

    rows = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        proto = parts[0]
        state = parts[1]
        local = parts[4]
        port_str = local.rsplit(":", 1)[-1]
        try:
            port = int(port_str)
        except ValueError:
            continue

        pid, process = None, None
        for part in parts:
            if "pid=" in part:
                try:
                    pid = int(part.split("pid=")[1].split(",")[0])
                except Exception:
                    pass
            if 'users:((' in part:
                try:
                    process = part.split('((')[1].split('"')[1]
                except Exception:
                    pass

        rows.append((ts, proto, port, state, pid, process))

    if rows:
        conn.executemany("""
            INSERT OR REPLACE INTO ports (ts, proto, port, state, pid, process)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        log.debug(f"Ports snapshot: {len(rows)} entries")

# ── Основной цикл ─────────────────────────────────────────────────────────────
running = True

def handle_signal(sig, frame):
    global running
    log.info(f"Signal {sig} received, shutting down…")
    running = False

def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT,  handle_signal)

    ifaces = detect_ifaces()
    log.info(f"netmon starting… Интерфейсы: {ifaces}")

    conn    = get_db()
    counter = TrafficCounter(conn, ifaces)
    last_port_scan = 0

    while running:
        now = time.monotonic()
        try:
            counter.tick()
        except Exception as e:
            log.error(f"Traffic tick error: {e}")

        if now - last_port_scan >= PORT_INTERVAL:
            try:
                scan_ports(conn)
                last_port_scan = now
            except Exception as e:
                log.error(f"Port scan error: {e}")

        time.sleep(INTERVAL)

    log.info("netmon stopped.")
    conn.close()

if __name__ == "__main__":
    main()
