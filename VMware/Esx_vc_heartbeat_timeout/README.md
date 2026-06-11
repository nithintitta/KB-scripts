# vCenter & ESXi Heartbeat Troubleshooting Scripts

This repository contains two Python scripts designed to help troubleshoot UDP heartbeat connectivity issues between VMware ESXi hosts and the vCenter Server Appliance (VCSA). ESXi hosts send heartbeat packets to vCenter over UDP port 902. These scripts allow you to verify if the packets are leaving the host and if they are successfully arriving at the vCenter Server.

## Files Included
* `esx.py` - Runs on the ESXi host.
* `vc.py` - Runs on the vCenter Server Appliance.

---

## 1. `esx.py` (ESXi Host Script)
This script monitors the outgoing network traffic on the ESXi host's management interface (`vmk0`). It intercepts packets destined for UDP port 902 and logs exactly when a heartbeat is sent.

### Prerequisites
* Must be run directly from the ESXi Shell or via SSH.
* No external libraries required (uses ESXi's built-in Python and `tcpdump-uw`).

### Usage
Run the script directly on the ESXi host:
```sh
python esx.py
```

### Expected Output
The script will print a continuous log of sent heartbeats:
```text
Monitoring outgoing heartbeats from vmk0 to vCenter (UDP port 902)...
Press Ctrl+C to stop.
---------------------------------------------------
heartbeat sent with 2026-06-11 10:00:05
heartbeat sent with 2026-06-11 10:00:15
```

---

## 2. `vc.py` (vCenter Server Script)
This script runs on the vCenter Server and listens for incoming heartbeats from specified ESXi hosts. If 10 seconds pass without receiving a heartbeat packet from a monitored host, it triggers an alert.

### Prerequisites
* Must be run from the vCenter Bash shell (SSH into VCSA, type `shell`).
* Runs using vCenter's built-in Python 3.
* Requires elevated privileges (run as `root`).

### Usage
Pass the IP addresses of the ESXi hosts you want to monitor as arguments.

**Monitor a single host:**
```bash
python3 vc.py 10.0.0.15
```

**Monitor multiple specific hosts:**
```bash
python3 vc.py 10.0.0.15 10.0.0.16 192.168.1.50
```

**Monitor an IP range (using bash brace expansion):**
```bash
python3 vc.py 10.0.0.{10..25}
```

### Expected Output
If a host stops sending heartbeats (or a firewall blocks them), the script will output an alert:
```text
Monitoring heartbeats on port 902 for the following IPs:
- 10.0.0.15
---------------------------------------------------
Timeout set to 10 seconds. Press Ctrl+C to stop.
---------------------------------------------------
2026-06-11 10:05:30: 10.0.0.15 missing heartbeat
2026-06-11 10:05:40: 10.0.0.15 missing heartbeat
```

## Troubleshooting Notes
* **Port 902 Blocked:** If `esx.py` shows packets leaving the host, but `vc.py` throws missing heartbeat alerts, a firewall (ESXi firewall, physical switch/router, or vCenter firewall) is likely dropping UDP port 902 traffic.
* **Permissions:** You must execute these scripts as the `root` user, as background packet sniffing requires elevated system privileges.
