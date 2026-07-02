<div align="center">

# vps-net-stat

**English** | [Русский](README.ru.md)

Simple network traffic and port monitor for Linux servers.  
Tracks incoming/outgoing traffic by day and month, monitors open ports with process names, counts exact traffic per port via iptables/nftables. Data is stored in SQLite and **survives reboots**.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.4.0-green.svg)](https://github.com/WowCatQwerty/vps-net-stat/releases)

</div>

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/install.sh | sudo bash
```

> ⚠️ Root privileges are required.

Language selection (Russian / English) is shown during install.  
The service starts immediately and auto-starts after reboot.

---

## Architecture

```text
  systemd (autostart)
        │
        ▼
  vps-net-stat.py (daemon)
      /        \
     ▼          ▼
/proc/net/dev  iptables/nftables
(total traffic) (per-port traffic)
     │          │
     └────┬─────┘
          ▼
       SQLite
  (/var/lib/vps-net-stat/data.db)
          │
          ▼
      vns.py (vns)
   interactive menu
```

---

## Interactive Menu

```bash
vns
```

```text
  ╔══════════════════════════════════════╗
  ║  vps-net-stat — VPS Network Monitor ║
  ╚══════════════════════════════════════╝
  Version: 4.0.0
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
  [12] Export / Import statistics
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
```text
  vps-net-stat — summary

  Period        ↓ Incoming     ↑ Outgoing
  ────────────  ─────────────  ──────────────
  Today         28.26 GiB      29.08 GiB
  Month         204.09 GiB     208.62 GiB
  All time      204.09 GiB     208.62 GiB

  Open ports: 43
```

### Traffic chart `[6]`
```text
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
```text
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

```text
  Port number (e.g. 80): 443
  Protocol: [1] tcp  [2] udp  [3] both
  → 1
  Comment (optional): nginx HTTPS
  ✓ Port added to tracking.
```

Per-port traffic is measured via **iptables/nftables** — exact counting, no missed connections.  
The firewall backend is detected automatically (nftables preferred, falls back to iptables).  
A dedicated chain `VNS_TRACK` is created — existing firewall rules are not affected.  
Rules are automatically cleaned up when the service stops or the program is uninstalled.

**No firewall available?** If neither `iptables` nor `nftables` is found, vps-net-stat automatically
falls back to `ss`-based tracking. It's less precise than the firewall backend:
- TCP only — UDP ports aren't tracked in this mode (no byte counters available via `ss`).
- Very short-lived connections that open and close between two polls may be undercounted.

The active backend is shown in `vns` → `[14] System info`. When running in `ss` fallback mode, a visible warning is also shown right when you add a port to tracking, and again in System info — accuracy is not guaranteed in this mode.

**Default scan frequency:**
- Overall server traffic — every **60 seconds**
- Per-port traffic counters — every **30 seconds**
- Port list scan — every **300 seconds** (5 minutes)

To change: edit `INTERVAL` and `PORT_INTERVAL` at the top of `/opt/vps-net-stat/vps-net-stat.py`.

**Timezone:** daily statistics reset at midnight **server time**. To check or change your server timezone:
```bash
timedatectl status        # check current timezone
timedatectl set-timezone Europe/Moscow  # set timezone
```

---

## IPv6

IPv6 is fully supported. Port rules are applied to both `iptables` and `ip6tables`.

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

## Export / Import

From menu: `vns` → `[12]`

**Export** saves your data to a directory (`/root/vns-backup` by default) as CSV, JSON, or both.

**Import** reads a backup from a directory. It looks for `vns_export.json` first; if that's not
present, it falls back to reading the CSV files (`vns_traffic.csv`, `vns_port_traffic.csv`,
`vns_watched.csv`) — whatever it finds. It reports what it found before doing anything.

If a record from the backup already exists (same day/port/protocol), you're asked how to resolve it:
- **Sum traffic together** — add backup values to existing ones
- **Keep current data** — skip the backup value, existing data is untouched
- **Overwrite with backup data** — replace existing values with the backup's

---

## Uninstall

From menu: `vns` → `[16]`

Or via command:
```bash
curl -fsSL https://raw.githubusercontent.com/WowCatQwerty/vps-net-stat/main/uninstall.sh | sudo bash
```

You will be asked separately whether to keep or delete the traffic database.

---

## Security

SHA-256 checksums are verified on every install and update.  
Hashes are stored in `checksums.txt` attached to each release under Assets.

Manual check:
```bash
sha256sum /opt/vps-net-stat/vps-net-stat.py
sha256sum /opt/vps-net-stat/vns.py
```
Compare with `checksums.txt` from the release Assets.

---

## How it works

| Component | Description |
|---|---|
| `vps-net-stat.py` | Daemon — reads `/proc/net/dev` for total traffic, uses iptables/nftables for per-port traffic |
| `vns.py` | CLI with interactive menu |
| `vps-net-stat.service` | systemd unit, auto-starts after reboot |
| `/var/lib/vps-net-stat/data.db` | SQLite database, accumulates indefinitely |
| `/var/log/vps-net-stat/daemon.log` | Daemon log |
| `/etc/vps-net-stat/lang` | Selected UI language |
| `/etc/vps-net-stat/firewall` | Detected port-traffic backend (iptables/nftables/ss) |

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

> ⚠️ Root privileges are required for port monitoring and firewall rule management.

**Dependencies:**
- Python 3.8+
- `iproute2` (`ss`, `ip` — usually pre-installed)
- `iptables` or `nftables` recommended (exact per-port traffic tracking; falls back to `ss` — TCP only, approximate — if neither is available)

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
| Exact per-port (fw) | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## License

[GNU GPL v3](LICENSE) — open source, modifications must stay open.
