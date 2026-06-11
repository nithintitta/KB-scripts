#!/usr/bin/env python3
#Written by Nithin Titta

import sys
import time
import subprocess
import select
import re

# Ensure at least one IP is provided
if len(sys.argv) < 2:
    print("Usage: python3 check_heartbeat.py <IP1> [IP2] [IP3] ...")
    sys.exit(1)

monitored_ips = sys.argv[1:]
current_time = time.time()

# Dictionary to track the last time a packet was seen from each IP
last_seen = {ip: current_time for ip in monitored_ips}

print(f"Monitoring heartbeats on port 902 for the following IPs:")
for ip in monitored_ips:
    print(f"- {ip}")
print("-" * 51)
print("Timeout set to 10 seconds. Press Ctrl+C to stop.")
print("-" * 51)

# Start tcpdump in the background
# -l: line-buffered, -n: no DNS resolution, -i any: all interfaces
cmd = ["tcpdump", "-l", "-n", "-i", "any", "dst port 902"]
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

# Regex to extract the source IP from the tcpdump output line
# Matches "IP 192.168.1.50.5632 >" and captures the "192.168.1.50" part
ip_pattern = re.compile(r'IP (\d+\.\d+\.\d+\.\d+)\.')

try:
    while True:
        # Use select to wait for output with a 1-second timeout
        # This prevents readline() from blocking indefinitely if no packets arrive
        reads, _, _ = select.select([process.stdout], [], [], 1.0)
        
        if process.stdout in reads:
            line = process.stdout.readline()
            if not line:
                break  # tcpdump stopped or pipe closed
            
            # Search for the IP in the tcpdump line
            match = ip_pattern.search(line)
            if match:
                src_ip = match.group(1)
                # If it's an IP we are monitoring, update the timestamp
                if src_ip in last_seen:
                    last_seen[src_ip] = time.time()
        
        # Check for timeouts
        now = time.time()
        for ip in monitored_ips:
            if (now - last_seen[ip]) >= 10:
                # Format the current time
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timestamp}: {ip} missing heartbeat")
                
                # Reset the timer so it doesn't print continuously
                last_seen[ip] = now

except KeyboardInterrupt:
    print("\nCapture stopped by user.")
finally:
    # Ensure tcpdump is killed when the script exits
    process.terminate()
