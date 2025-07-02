#written by Nithin Titta
#Broadcom KB https://knowledge.broadcom.com/external/article/320525/

import json
import os
import socket
hostname = socket.gethostname()
print("Hostname:", hostname)

#use configstorecli to download
os.system("/bin/configstorecli config current get -c esx -g services -k hostd -outfile tmp.json")
os.system("cp tmp.json "+hostname+"-configstore.json")

file_path = 'tmp.json'
with open(file_path, 'r') as f:
    data = json.load(f)

try:
    data["vmacore"]["http"]["read_timeout_ms"] = 600000
except KeyError:
    raise KeyError("Missing 'vmacore' or 'http' in the JSON structure")

try:
    data["vmacore"]["ssl"]["handshake_timeout_ms"] = 600000
except KeyError:
    raise KeyError("Missing 'vmacore' or 'ssl' in the JSON structure")

with open(file_path, 'w') as f:
    json.dump(data, f, indent=3)

print("Timeout values added successfully, restarting services")

os.system("/etc/init.d/hostd restart && /etc/init.d/vpxa restart && /etc/init.d/rhttpproxy restart")
