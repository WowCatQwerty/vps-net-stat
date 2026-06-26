#!/usr/bin/env python3
"""
vps-net-stat — VPS Network & Port Statistics Daemon
Отслеживает порты и считает интернет-трафик (в т.ч. по портам).
Данные в SQLite — переживают перезагрузки.
"""

import sqlite3, subprocess, time, os, sys, signal, logging
from datetime import date

DB_PATH       = "/var/lib/vps-net-stat/data.db"
LOG_PATH      = "/var/log/vps-net-stat/daemon.log"
INTERVAL      = 60
PORT_INTERVAL = 300

VIRTUAL_PREFIXES = ("lo","veth","docker","virbr","tun","br-","dummy","bond","vlan","wg","zt")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("vps-net-stat")

# ── Автодетект интерфейсов ────────────────────────────────────────────────────
def detect_ifaces():
    try:
        out = subprocess.check_output(["ip", "route"], text=True)
        routed = set()
        for line in out.splitlines():
            if line.startswith("default"):
                parts = line.split()
                routed.add(parts[parts.index("dev") + 1])
    except Exception:
        routed = set()

    all_ifaces = []
    with open("/proc/net/dev") as f:
        for line in f:
            if ":" not in line:
                continue
            iface = line.split(":")[0].strip()
            if not any(iface.startswith(p) for p in VIRTUAL_PREFIXES):
                all_ifaces.append(iface)

    return [i for i in all_ifaces if i in routed] or all_ifaces

# ── База данных ───────────────────────────────────────────────────────────────
def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS traffic_daily (
            day      TEXT NOT NULL,
            iface    TEXT NOT NULL,
            rx_bytes INTEGER NOT NULL DEFAULT 0,
            tx_bytes INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (day, iface)
        );

        CREATE TABLE IF NOT EXISTS port_traffic (
            day      TEXT NOT NULL,
            port     INTEGER NOT NULL,
            proto    TEXT NOT NULL,
            process  TEXT,
            rx_bytes INTEGER NOT NULL DEFAULT 0,
            tx_bytes INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (day, port, proto)
        );

        CREATE TABLE IF NOT EXISTS ports (
            ts      INTEGER NOT NULL,
            proto   TEXT NOT NULL,
            port    INTEGER NOT NULL,
            state   TEXT NOT NULL,
            pid     INTEGER,
            process TEXT,
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
            if iface in ifaces:
                fields = rest.split()
                stats[iface] = (int(fields[0]), int(fields[8]))
    return stats

# ── Трафик по портам через ss ─────────────────────────────────────────────────
def read_port_traffic(conn):
    """
    Читает статистику трафика по сокетам через ss -tin / ss -uin.
    Суммирует bytes_sent/bytes_acked per port за сегодня.
    """
    day = date.today().isoformat()
    for proto_flag, proto_name in [("-t", "tcp"), ("-u", "udp")]:
        try:
            result = subprocess.run(
                ["ss", proto_flag, "-i", "-n", "-p"],
                capture_output=True, text=True, timeout=15
            )
        except Exception:
            continue

        port, process = None, None
        for line in result.stdout.splitlines():
            # Строка с адресом (Local Address:Port)
            if "LISTEN" in line or "ESTAB" in line or "UNCONN" in line:
                parts = line.split()
                try:
                    local = parts[4] if len(parts) > 4 else ""
                    port = int(local.rsplit(":", 1)[-1])
                except (ValueError, IndexError):
                    port = None
                process = None
                for p in parts:
                    if 'users:((' in p:
                        try:
                            process = p.split('((')[1].split('"')[1]
                        except Exception:
                            pass

            # Строка с bytes_sent/bytes_acked
            elif "bytes_sent" in line and port is not None:
                rx_b = tx_b = 0
                for token in line.split():
                    if token.startswith("bytes_sent:"):
                        try:
                            tx_b = int(token.split(":")[1])
                        except Exception:
                            pass
                    elif token.startswith("bytes_acked:"):
                        try:
                            rx_b = int(token.split(":")[1])
                        except Exception:
                            pass
                if tx_b > 0 or rx_b > 0:
                    conn.execute("""
                        INSERT INTO port_traffic (day, port, proto, process, rx_bytes, tx_bytes)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(day, port, proto) DO UPDATE SET
                            rx_bytes = MAX(excluded.rx_bytes, rx_bytes),
                            tx_bytes = MAX(excluded.tx_bytes, tx_bytes),
                            process  = COALESCE(excluded.process, process)
                    """, (day, port, proto_name, process, rx_b, tx_b))
    conn.commit()

# ── Счётчик общего трафика ────────────────────────────────────────────────────
class TrafficCounter:
    def __init__(self, conn, ifaces):
        self.conn, self.ifaces, self.prev = conn, ifaces, {}

    def tick(self):
        current = read_iface_stats(self.ifaces)
        day = date.today().isoformat()
        for iface, (rx, tx) in current.items():
            if iface in self.prev:
                prx, ptx = self.prev[iface]
                rx_d = rx - prx if rx >= prx else rx
                tx_d = tx - ptx if tx >= ptx else tx
                if rx_d > 0 or tx_d > 0:
                    self.conn.execute("""
                        INSERT INTO traffic_daily (day, iface, rx_bytes, tx_bytes)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(day, iface) DO UPDATE SET
                            rx_bytes = rx_bytes + excluded.rx_bytes,
                            tx_bytes = tx_bytes + excluded.tx_bytes
                    """, (day, iface, rx_d, tx_d))
            self.prev[iface] = (rx, tx)
        self.conn.commit()

# ── Сканер портов ─────────────────────────────────────────────────────────────
def scan_ports(conn):
    ts = int(time.time())
    try:
        result = subprocess.run(["ss", "-tlnupH"], capture_output=True, text=True, timeout=10)
    except Exception as e:
        log.warning(f"ss failed: {e}")
        return

    rows = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        proto, state, local = parts[0], parts[1], parts[4]
        try:
            port = int(local.rsplit(":", 1)[-1])
        except ValueError:
            continue
        pid, process = None, None
        for p in parts:
            if "pid=" in p:
                try: pid = int(p.split("pid=")[1].split(",")[0])
                except: pass
            if 'users:((' in p:
                try: process = p.split('((')[1].split('"')[1]
                except: pass
        rows.append((ts, proto, port, state, pid, process))

    if rows:
        conn.executemany("""
            INSERT OR REPLACE INTO ports (ts, proto, port, state, pid, process)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()

# ── Основной цикл ─────────────────────────────────────────────────────────────
running = True

def handle_signal(sig, frame):
    global running
    log.info(f"Signal {sig}, shutting down…")
    running = False

def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT,  handle_signal)

    ifaces = detect_ifaces()
    log.info(f"vps-net-stat starting… interfaces: {ifaces}")

    conn = get_db()
    counter = TrafficCounter(conn, ifaces)
    last_port_scan = last_port_traffic = 0

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

        if now - last_port_traffic >= PORT_INTERVAL:
            try:
                read_port_traffic(conn)
                last_port_traffic = now
            except Exception as e:
                log.error(f"Port traffic error: {e}")

        time.sleep(INTERVAL)

    log.info("vps-net-stat stopped.")
    conn.close()

if __name__ == "__main__":
    main()
