<div align="center">

# vps-net-stat

**English** | [Русский](README.ru.md)

Simple network traffic and port monitor for Linux servers.  
Tracks incoming/outgoing traffic by day and month, monitors open ports with process names, counts traffic per port. Data is stored in SQLite and **survives reboots**.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.4.1-green.svg)](https://github.com/WowCatQwerty/vps-net-stat/releases)

</div>

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash
```

Language selection (Russian / English) is shown during install.  
The service starts immediately and auto-starts after reboot.

---

## Architecture

```
  systemd (autostart)
        │
        ▼
   netmon.py (daemon)
      /        \
     ▼          ▼
/proc/net/dev   ss (ports)
     │          │
     └────┬─────┘
          ▼
       SQLite
  (/var/lib/vps-net-stat/data.db)
          │
          ▼
   netmon-cli.py (vns)
   interactive menu
```

---

## Interactive Menu

```bash
vns
```

```
  ╔══════════════════════════════════════╗
  ║  vps-net-stat — VPS Network Monitor ║
  ╚══════════════════════════════════════╝
  Version: 3.3.0
  Disk usage: 3.82 MiB  (database: 3.76 MiB, app: 59.20 KiB)
  Monthly limit: ████████████░░░░░░░░  61.2 / 100 GiB (61%)

  Choose an action:

  [1]  Summary (today / month / all time)
  [2]  Open ports with processes
  [3]  Traffic by all months
  [4]  Traffic for last N days
  [5]  Top ports by traffic
  [6]  Traffic charts
  ──────────────────────────────────────
  [7]  Add port for traffic tracking
  [8]  Remove port from tracking
  [9]  Watched ports
  ──────────────────────────────────────
  [10] Reset server traffic stats
  [11] Reset port traffic stats
  [12] Export statistics
  [13] Set monthly traffic limit
  ──────────────────────────────────────
  [14] System info
  [15] Diagnostics
  ──────────────────────────────────────
  [16] Uninstall
  [17] Update vps-net-stat
  [18] Restart service
  [19] Switch language (Переключить на Русский)
  [0]  Exit
```

---

## Examples

### Summary `[1]`
```
  vps-net-stat — summary

  Period        ↓ Incoming     ↑ Outgoing
  ────────────  ─────────────  ──────────────
  Today         28.26 GiB      29.08 GiB
  Month         204.09 GiB     208.62 GiB
  All time      204.09 GiB     208.62 GiB

  Open ports: 43
```

### Traffic chart `[6]`
```
  Traffic for last 7 days

  06-24  ████████░░░░░░░░░░░░░░░░░░░░░░  8.21 GiB
  06-25  ██████████████░░░░░░░░░░░░░░░░  14.30 GiB
  06-26  ███████░░░░░░░░░░░░░░░░░░░░░░░  7.10 GiB
  06-27  ████████████████████░░░░░░░░░░  20.45 GiB
  06-28  █████████░░░░░░░░░░░░░░░░░░░░░  9.87 GiB
  06-29  ██████████████████████████████  30.12 GiB
  06-30  ████████████░░░░░░░░░░░░░░░░░░  12.33 GiB

  █ Incoming   █ Outgoing
```

### Monthly limit in menu header
```
  Monthly limit: ████████████░░░░░░░░  61.2 / 100 GiB (61%)
```
The bar turns yellow at 70%, red at 90%. Not shown if no limit is set.

---

## Port Traffic Tracking

By default, per-port traffic is **not collected** — add only the ports you care about.

**How to add a port:**

1. Open `vns`
2. Check `[2]` — see which ports are open and which process uses them
3. Choose `[7]` — enter port number, protocol, optional comment
4. Traffic starts accumulating from that moment

```
  Port number (e.g. 80): 443
  Protocol: [1] tcp  [2] udp  [3] both
  → 1
  Comment (optional): nginx HTTPS
  ✓ Port added to tracking.
```

> **Note on accuracy:** Overall server traffic (`/proc/net/dev`) is exact.
> Per-port traffic is approximate — the daemon uses `ss` which takes a snapshot
> of active sockets. Short sessions (< 5 min) may not be captured.
> For exact per-port tracking, iptables/nftables support is planned for v4.0.0.

**Default scan frequency:**
- Overall server traffic — every **60 seconds**
- Port scanning and per-port traffic — every **300 seconds** (5 minutes)

To change: edit `INTERVAL` and `PORT_INTERVAL` at the top of `/opt/vps-net-stat/netmon.py`.

---

## IPv6

IPv6 is supported. Port parsing handles both `0.0.0.0:80` and `[::]:80` formats correctly.

---

## Update

From menu: `vns` → `[17]`

Or via command:
```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/update.sh | sudo bash
```

SHA-256 integrity check is performed before replacing any files.  
Data is **not deleted** on update.

---

## Uninstall

From menu: `vns` → `[16]`

Or via command:
```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/uninstall.sh | sudo bash
```

---

## Security

SHA-256 checksums are verified on every install and update.  
Hashes are stored in `checksums.txt` attached to each release under Assets.

Manual check:
```bash
sha256sum /opt/vps-net-stat/netmon.py
sha256sum /opt/vps-net-stat/netmon-cli.py
```
Compare with `checksums.txt` from the release Assets.

---

## How it works

| Component | Description |
|---|---|
| `netmon.py` | Daemon — reads `/proc/net/dev`, tracks traffic deltas, scans ports via `ss` |
| `netmon-cli.py` | CLI with interactive menu |
| `netmon.service` | systemd unit, auto-starts after reboot |
| `/var/lib/vps-net-stat/data.db` | SQLite database, accumulates indefinitely |
| `/var/log/vps-net-stat/daemon.log` | Daemon log |
| `/etc/vps-net-stat/lang` | Selected UI language |

**Interfaces are detected automatically** via `ip route`. Virtual interfaces (docker, veth, tun, lo, etc.) are excluded.

---

## Service management

```bash
systemctl status vps-net-stat
systemctl restart vps-net-stat
systemctl stop vps-net-stat
tail -f /var/log/vps-net-stat/daemon.log
```

---

## Requirements

**Supported OS:**
- Ubuntu 20.04+
- Debian 10+
- CentOS / RHEL 8+
- AlmaLinux / Rocky Linux 8+
- Fedora 33+
- Any Linux with systemd and Python 3.8+

> ⚠️ Root privileges are required for port monitoring (`ss` needs access to process info).

**Dependencies:**
- Python 3.8+
- `iproute2` (`ss`, `ip` — usually pre-installed)

---

## Comparison

| Feature | vps-net-stat | vnStat | nload | iftop | bmon |
|---|:---:|:---:|:---:|:---:|:---:|
| Traffic history | ✅ | ✅ | ❌ | ❌ | ✅ |
| Per-port traffic | ✅ | ❌ | ❌ | ❌ | ❌ |
| Process names | ✅ | ❌ | ❌ | ❌ | ❌ |
| SQLite storage | ✅ | ❌ | ❌ | ❌ | ❌ |
| Interactive menu | ✅ | ❌ | ❌ | ❌ | ❌ |
| Monthly limit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Export CSV/JSON | ✅ | ❌ | ❌ | ❌ | ❌ |
| One-line install | ✅ | ❌ | ❌ | ❌ | ❌ |
| IPv6 | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## License

[GNU GPL v3](LICENSE) — open source, modifications must stay open.
