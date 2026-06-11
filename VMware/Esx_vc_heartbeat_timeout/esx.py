#!/usr/bin/env python
#Written by Nithin Titta

import subprocess
import time
import sys

print("Monitoring outgoing heartbeats from vmk0 to vCenter (UDP port 902)...")
print("Press Ctrl+C to stop.")
print("-" * 51)

# ESXi uses tcpdump-uw instead of tcpdump
cmd = ["tcpdump-uw", "-i", "vmk0", "-n", "-l", "udp and dst port 902"]

try:
    # Start the packet capture in the background
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.DEVNULL, 
        universal_newlines=True # Ensures compatibility with older ESXi Python versions
    )
    
    while True:
        # Read the background output line by line
        line = process.stdout.readline()
        if not line:
            break  # Break if tcpdump-uw stops
            
        # Every time a line (packet) is captured, print the custom message
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"heartbeat sent with {timestamp}")

except KeyboardInterrupt:
    print("\nCapture stopped by user.")
finally:
    # Clean up the background packet capture
    if 'process' in locals():
        process.terminate()
