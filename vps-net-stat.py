#!/usr/bin/env python3
"""
vps-net-stat — VPS Network & Port Statistics Daemon v4.0.0
Точный трафик по портам через iptables/nftables.
Общий трафик — через /proc/net/dev.
Данные в SQLite — переживают перезагрузки.
"""

import sqlite3, subprocess, time, os, sys, signal, logging, shutil
from datetime import date

DB_PATH       = "/var/lib/vps-net-stat/data.db"
LOG_PATH      = "/var/log/vps-net-stat/daemon.log"
CONF_PATH     = "/etc/vps-net-stat/firewall"   # хранит "iptables" или "nftables"
INTERVAL      = 60
PORT_INTERVAL = 30   # опрос трафика по портам теперь чаще — точнее

VIRTUAL_PREFIXES = ("lo","veth","docker","virbr","tun","br-","dummy","bond","vlan","wg","zt")
CHAIN_NAME = "VNS_TRACK"   # наша цепочка в iptables/nftables

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

# ── Автоопределение файрвола ──────────────────────────────────────────────────
def detect_firewall():
    """Определяет доступный файрвол. Возвращает 'nftables', 'iptables' или None."""
    # Сначала проверяем сохранённый выбор
    if os.path.exists(CONF_PATH):
        with open(CONF_PATH) as f:
            saved = f.read().strip()
        if saved in ("nftables", "iptables"):
            return saved

    # Автоопределение
    if shutil.which("nft"):
        try:
            subprocess.run(["nft", "list", "tables"], capture_output=True, timeout=3)
            _save_firewall("nftables")
            return "nftables"
        except Exception:
            pass

    if shutil.which("iptables"):
        try:
            subprocess.run(["iptables", "-L", "-n"], capture_output=True, timeout=3)
            _save_firewall("iptables")
            return "iptables"
        except Exception:
            pass

    return None

def _save_firewall(fw):
    os.makedirs(os.path.dirname(CONF_PATH), exist_ok=True)
    with open(CONF_PATH, "w") as f:
        f.write(fw)

# ── iptables: управление правилами ────────────────────────────────────────────
def ipt(args, check=False):
    return subprocess.run(["iptables"] + args, capture_output=True, check=check)

def ipt6(args, check=False):
    if shutil.which("ip6tables"):
        subprocess.run(["ip6tables"] + args, capture_output=True)

def iptables_setup_chain():
    """Создаёт цепочку VNS_TRACK если её нет и подключает к INPUT/OUTPUT."""
    # Создаём цепочку
    ipt(["-N", CHAIN_NAME])
    ipt6(["-N", CHAIN_NAME])
    # Подключаем если ещё не подключена
    r = ipt(["-C", "INPUT", "-j", CHAIN_NAME])
    if r.returncode != 0:
        ipt(["-I", "INPUT", "-j", CHAIN_NAME])
        ipt6(["-I", "INPUT", "-j", CHAIN_NAME])
    r = ipt(["-C", "OUTPUT", "-j", CHAIN_NAME])
    if r.returncode != 0:
        ipt(["-I", "OUTPUT", "-j", CHAIN_NAME])
        ipt6(["-I", "OUTPUT", "-j", CHAIN_NAME])

def iptables_add_port(port, proto):
    """Добавляет правила для отслеживания порта."""
    # Входящий
    r = ipt(["-C", CHAIN_NAME, "-p", proto, "--dport", str(port), "-j", "ACCEPT"])
    if r.returncode != 0:
        ipt(["-A", CHAIN_NAME, "-p", proto, "--dport", str(port), "-j", "ACCEPT"])
        ipt6(["-A", CHAIN_NAME, "-p", proto, "--dport", str(port), "-j", "ACCEPT"])
    # Исходящий
    r = ipt(["-C", CHAIN_NAME, "-p", proto, "--sport", str(port), "-j", "ACCEPT"])
    if r.returncode != 0:
        ipt(["-A", CHAIN_NAME, "-p", proto, "--sport", str(port), "-j", "ACCEPT"])
        ipt6(["-A", CHAIN_NAME, "-p", proto, "--sport", str(port), "-j", "ACCEPT"])

def iptables_remove_port(port, proto):
    """Удаляет правила для порта."""
    ipt(["-D", CHAIN_NAME, "-p", proto, "--dport", str(port), "-j", "ACCEPT"])
    ipt(["-D", CHAIN_NAME, "-p", proto, "--sport", str(port), "-j", "ACCEPT"])
    ipt6(["-D", CHAIN_NAME, "-p", proto, "--dport", str(port), "-j", "ACCEPT"])
    ipt6(["-D", CHAIN_NAME, "-p", proto, "--sport", str(port), "-j", "ACCEPT"])

def iptables_read_counters(port, proto):
    """Читает счётчики байт для порта из iptables. Возвращает (rx, tx)."""
    try:
        out = subprocess.check_output(
            ["iptables", "-L", CHAIN_NAME, "-v", "-n", "-x"],
            text=True
        )
        rx = tx = 0
        for line in out.splitlines():
            if f"dpt:{port}" in line and proto in line:
                parts = line.split()
                try: rx = int(parts[1])
                except: pass
            if f"spt:{port}" in line and proto in line:
                parts = line.split()
                try: tx = int(parts[1])
                except: pass
        return rx, tx
    except Exception:
        return 0, 0

def iptables_teardown():
    """Полностью удаляет нашу цепочку из iptables."""
    for cmd in [["iptables"], ["ip6tables"] if shutil.which("ip6tables") else None]:
        if cmd is None:
            continue
        subprocess.run(cmd + ["-D", "INPUT",  "-j", CHAIN_NAME], capture_output=True)
        subprocess.run(cmd + ["-D", "OUTPUT", "-j", CHAIN_NAME], capture_output=True)
        subprocess.run(cmd + ["-F", CHAIN_NAME], capture_output=True)
        subprocess.run(cmd + ["-X", CHAIN_NAME], capture_output=True)
    log.info("iptables rules cleaned up")

# ── nftables: управление правилами ───────────────────────────────────────────
NFT_TABLE = "inet vns_track"

def nft(args):
    return subprocess.run(["nft"] + args, capture_output=True, text=True)

def nftables_setup():
    """Создаёт таблицу и цепочки nftables."""
    nft(["add", "table", "inet", "vns_track"])
    nft(["add", "chain", "inet", "vns_track", "input",
         "{ type filter hook input priority 0 ; }"])
    nft(["add", "chain", "inet", "vns_track", "output",
         "{ type filter hook output priority 0 ; }"])

def nftables_add_port(port, proto):
    nft(["add", "rule", "inet", "vns_track", "input",
         proto, "dport", str(port), "counter", "accept"])
    nft(["add", "rule", "inet", "vns_track", "output",
         proto, "sport", str(port), "counter", "accept"])

def nftables_read_counters(port, proto):
    try:
        out = subprocess.check_output(
            ["nft", "-j", "list", "table", "inet", "vns_track"],
            text=True
        )
        import json
        data = json.loads(out)
        rx = tx = 0
        for item in data.get("nftables", []):
            rule = item.get("rule", {})
            expr = rule.get("expr", [])
            # Ищем правила с нашим портом
            port_match = any(
                e.get("match", {}).get("right", {}) == port or
                e.get("match", {}).get("right", {}).get("set", [port]) == [port]
                for e in expr if "match" in e
            )
            if not port_match:
                continue
            chain = rule.get("chain", "")
            for e in expr:
                if "counter" in e:
                    b = e["counter"].get("bytes", 0)
                    if chain == "input":
                        rx = b
                    else:
                        tx = b
        return rx, tx
    except Exception:
        return 0, 0

def nftables_teardown():
    nft(["delete", "table", "inet", "vns_track"])
    log.info("nftables rules cleaned up")

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

        CREATE TABLE IF NOT EXISTS port_counters (
            port     INTEGER NOT NULL,
            proto    TEXT NOT NULL,
            rx_bytes INTEGER NOT NULL DEFAULT 0,
            tx_bytes INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (port, proto)
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

        CREATE TABLE IF NOT EXISTS watched_ports (
            port    INTEGER NOT NULL,
            proto   TEXT NOT NULL DEFAULT 'tcp',
            comment TEXT,
            added   TEXT NOT NULL,
            PRIMARY KEY (port, proto)
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

# ── Точный трафик по портам ───────────────────────────────────────────────────
class PortTrafficTracker:
    """Читает счётчики из iptables/nftables и сохраняет дельты в БД."""

    def __init__(self, conn, fw):
        self.conn = conn
        self.fw   = fw  # 'iptables' или 'nftables'

    def _read(self, port, proto):
        if self.fw == "iptables":
            return iptables_read_counters(port, proto)
        else:
            return nftables_read_counters(port, proto)

    def tick(self):
        watched = self.conn.execute(
            "SELECT port, proto FROM watched_ports"
        ).fetchall()
        if not watched:
            return

        day = date.today().isoformat()
        for row in watched:
            port, proto = row["port"], row["proto"]
            rx, tx = self._read(port, proto)
            if rx == 0 and tx == 0:
                continue

            # Получаем предыдущие значения счётчика
            prev = self.conn.execute(
                "SELECT rx_bytes, tx_bytes FROM port_counters WHERE port=? AND proto=?",
                (port, proto)
            ).fetchone()

            if prev:
                prx, ptx = prev["rx_bytes"], prev["tx_bytes"]
                # Защита от сброса счётчика (перезапуск демона)
                rx_d = rx - prx if rx >= prx else rx
                tx_d = tx - ptx if tx >= ptx else tx
            else:
                rx_d = tx_d = 0

            # Обновляем абсолютные счётчики
            self.conn.execute("""
                INSERT INTO port_counters (port, proto, rx_bytes, tx_bytes)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(port, proto) DO UPDATE SET
                    rx_bytes = excluded.rx_bytes,
                    tx_bytes = excluded.tx_bytes
            """, (port, proto, rx, tx))

            # Сохраняем дельту в дневную статистику
            if rx_d > 0 or tx_d > 0:
                # Ищем имя процесса
                proc = self.conn.execute("""
                    SELECT process FROM ports
                    WHERE port=? AND proto=? AND ts=(SELECT MAX(ts) FROM ports)
                """, (port, proto)).fetchone()
                process = proc["process"] if proc else None

                self.conn.execute("""
                    INSERT INTO port_traffic (day, port, proto, process, rx_bytes, tx_bytes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(day, port, proto) DO UPDATE SET
                        rx_bytes = rx_bytes + excluded.rx_bytes,
                        tx_bytes = tx_bytes + excluded.tx_bytes,
                        process  = COALESCE(excluded.process, process)
                """, (day, port, proto, process, rx_d, tx_d))

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

# ── Синхронизация правил файрвола с watched_ports ────────────────────────────
def sync_firewall_rules(conn, fw, known_ports):
    """Добавляет правила для новых портов, удаляет для удалённых."""
    watched = {(r["port"], r["proto"])
               for r in conn.execute("SELECT port, proto FROM watched_ports").fetchall()}

    # Добавляем новые
    for port, proto in watched - known_ports:
        try:
            if fw == "iptables":
                iptables_add_port(port, proto)
            else:
                nftables_add_port(port, proto)
            log.info(f"Added firewall rule: {proto}/{port}")
        except Exception as e:
            log.error(f"Failed to add rule {proto}/{port}: {e}")

    # Удаляем убранные (только iptables — nftables пересоздаётся)
    for port, proto in known_ports - watched:
        try:
            if fw == "iptables":
                iptables_remove_port(port, proto)
            log.info(f"Removed firewall rule: {proto}/{port}")
        except Exception as e:
            log.error(f"Failed to remove rule {proto}/{port}: {e}")

    return watched

# ── Очистка при выходе ────────────────────────────────────────────────────────
def cleanup(fw):
    if fw == "iptables":
        iptables_teardown()
    elif fw == "nftables":
        nftables_teardown()

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

    fw = detect_firewall()
    if fw:
        log.info(f"Firewall backend: {fw}")
        if fw == "iptables":
            iptables_setup_chain()
        else:
            nftables_setup()
    else:
        log.warning("No firewall found (iptables/nftables). Per-port tracking disabled.")

    conn    = get_db()
    counter = TrafficCounter(conn, ifaces)
    tracker = PortTrafficTracker(conn, fw) if fw else None

    last_port_scan = 0
    last_port_tick = 0
    last_fw_sync   = 0
    known_ports    = set()

    while running:
        now = time.monotonic()

        # Общий трафик — каждые INTERVAL секунд
        try:
            counter.tick()
        except Exception as e:
            log.error(f"Traffic tick error: {e}")

        # Синхронизация правил файрвола — каждые 30 секунд
        if fw and now - last_fw_sync >= 30:
            try:
                known_ports = sync_firewall_rules(conn, fw, known_ports)
                last_fw_sync = now
            except Exception as e:
                log.error(f"Firewall sync error: {e}")

        # Трафик по портам — каждые PORT_INTERVAL секунд
        if fw and tracker and now - last_port_tick >= PORT_INTERVAL:
            try:
                tracker.tick()
                last_port_tick = now
            except Exception as e:
                log.error(f"Port traffic tick error: {e}")

        # Сканирование портов — каждые 300 секунд
        if now - last_port_scan >= 300:
            try:
                scan_ports(conn)
                last_port_scan = now
            except Exception as e:
                log.error(f"Port scan error: {e}")

        time.sleep(INTERVAL)

    # Очистка при выходе
    if fw:
        cleanup(fw)
    log.info("vps-net-stat stopped.")
    conn.close()

if __name__ == "__main__":
    main()
