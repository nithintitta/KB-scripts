#Written by Nithin Titta
#Replace HARDCODED_TOKEN value with a valid token
#Replace VCD_HOST with Public URL
#API version should mostly work wth VCD10.6+
#script will prompt you for the Edge Firewall Rule UUID, Grab it from the browser URL. Eg:  7e817e69-d869-4f8e-8d73-3db114d6a2e6 from URL: https://vcd10-6-1.rainpole.local/tenant/Coke/vdcs/59f11807-c6e9-432f-af19-42e1c2fbcaa0/org-vdc-edge-gateways/cloud/urn:vcloud:gateway:7e817e69-d869-4f8e-8d73-3db114d6a2e6/services/firewall
#                                                                                                                                                                                                                                                                                ^                to                ^
#Result will be written to csv 

import requests
import json
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VCD_HOST = "vcd10-6-1.rainpole.local"
API_VERSION = "40.0.0-alpha"

HARDCODED_TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhOTNjOWRiOS03NDcxLTMxOTItOGQwOS1hOGY3ZWVkYTg1ZjlAM2UxMGRjNzktM2M1NC00ZjNlLTkyMDEtNDY5NjM5NjhiYmZiIiwic3ViIjoiYWRtaW5pc3RyYXRvciIsImV4cCI6MTc2OTY3MTMyOCwidmVyc2lvbiI6InZjbG91ZF8xLjAiLCJqdGkiOiJkNzE5NzI3NGQ3NTE0MmNiOGRkYmE0YjViZjIwYWRjYyJ9.Cm4sXS6l8znpd-RKqEpGSytAjeFXE4mwXNo8XRH3CcXrvi_pN0uR4zXW4RANF9iwHHANgMpRQd54h0kTosXosmv0N6B90OnxqtMXE1GjqPxGRopRcy64qWKVWOA4XrXMnTHOLRcwGWhSa219dAoETCymurdmVdvF6Y7egFUWD7nMU0ZYODxgk8r3ygvZ11kuNHd6ZkdViwePWzjgzx_glsT80ihWc4FgICTRxn6wSXhkDhx3Dj_2CPIqhkvaud-mThyhAlFefpJALa8WwoYe6XuYoeUp2RzPdGAT-1lXxFgXCZac7CCUBuO7ujrlJ_FGBLIG_MnR_v5fZnY_8PqiIQ"

gateway_uuid = input("Enter Gateway UUID: ").strip()

def get_firewall_rules(uuid, token):
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
        
    gateway_urn = f"urn:vcloud:gateway:{uuid}"
    url = f"https://{VCD_HOST}/cloudapi/2.0.0/edgeGateways/{gateway_urn}/firewall/rules"
    
    headers = {
        "Accept": f"application/json;version={API_VERSION}",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"[*] Querying API: {url}")
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection Error: {e}")
        return None

def format_cell_data(key, value):
    if value is None:
        return ""
        
    if key == "applicationPortProfiles" and isinstance(value, list):
        names = [item.get('name', 'Unknown') for item in value if isinstance(item, dict)]
        return " | ".join(names)

    if isinstance(value, list):
        return " | ".join([str(v) for v in value])
        
    if isinstance(value, dict):
        return json.dumps(value)
        
    return value

def save_csv(json_data, filename="firewall_rules.csv"):
    all_rules = []

    sys_rules = json_data.get('systemRules') or []
    for r in sys_rules:
        r['Rule_Type'] = 'System'
        all_rules.append(r)

    user_rules = json_data.get('userDefinedRules') or []
    for r in user_rules:
        r['Rule_Type'] = 'User Defined'
        all_rules.append(r)

    def_rules = json_data.get('defaultRules') or []
    for r in def_rules:
        r['Rule_Type'] = 'Default'
        all_rules.append(r)
    
    if not all_rules:
        print("[-] CSV skipped: No rules found.")
        return

    all_keys = set().union(*(d.keys() for d in all_rules))
    
    priority_cols = ['Rule_Type', 'id', 'name', 'actionValue', 'direction', 'active']
    other_cols = [k for k in all_keys if k not in priority_cols]
    headers = priority_cols + sorted(other_cols)
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for rule in all_rules:
                row = []
                for header in headers:
                    val = rule.get(header, "")
                    formatted_val = format_cell_data(header, val)
                    row.append(formatted_val)
                writer.writerow(row)
                
        print(f"[+] CSV saved to file: {filename} ({len(all_rules)} rules total)")
    except IOError as e:
        print(f"[-] Error writing CSV file: {e}")

def save_json(json_data, filename="firewall_rules.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
        print(f"[+] JSON saved to file: {filename}")
    except IOError as e:
        print(f"[-] Error writing JSON file: {e}")

if __name__ == "__main__":
    if not gateway_uuid:
        print("[-] Error: Gateway UUID cannot be empty.")
    elif not HARDCODED_TOKEN:
        print("[-] Error: Token is missing.")
    else:
        data = get_firewall_rules(gateway_uuid, HARDCODED_TOKEN)
        
        if data:
            print("\n--- JSON OUTPUT START ---")
            print(json.dumps(data, indent=4))
            print("--- JSON OUTPUT END ---\n")
            
            save_json(data)
            save_csv(data)
