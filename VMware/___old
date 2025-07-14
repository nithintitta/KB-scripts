#written by Nithin Titta,
#APJ Cloud,  VCF Support. 
#Broadcom Inc, Bangalore.  IND. 

import requests
import json
import os
import sys

####inputs here
UUID = "__replace_with_VM_resource_id__" 
API_BASE = "https://__Aria_automation_FQDN___/api"
API_URL = f"{API_BASE}/{UUID}"

BEARER_TOKEN = "your_token_here"  
ENDPOINT_LINK = "/resources/endpoints/___________replace_endpoint_id_here___________"
ENDPOINT_TYPE = "vsphere"

###DO NOT MODIFY BELOW

OUTPUT_FILE = f"{UUID}-original.txt"


if os.path.exists(OUTPUT_FILE):
    print(f" File '{OUTPUT_FILE}' already exists. Exiting script.")
    sys.exit(1)


headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


response = requests.get(API_URL, headers=headers)

if response.status_code == 200:
    data = response.json()

  
    with open(OUTPUT_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f" Original GET response saved to '{OUTPUT_FILE}'")

    custom_properties = data.get("customProperties", {})

    needs_update = False

    if "__endpointType" not in custom_properties:
        custom_properties["__endpointType"] = ENDPOINT_TYPE
        print(" '__endpointType' will be added")
        needs_update = True

    if "__endpointLink" not in custom_properties:
        custom_properties["__endpointLink"] = ENDPOINT_LINK
        print(" '__endpointLink' will be added")
        needs_update = True

    if not needs_update:
        print(" Both '__endpointType' and '__endpointLink' already exist. No update needed.")
        sys.exit(0)

    data["customProperties"] = custom_properties

    put_response = requests.put(API_URL, headers=headers, data=json.dumps(data))

    if put_response.status_code in [200, 204]:
        print(" Successfully updated the resource with PUT.")
    else:
        print(f" PUT failed with status code {put_response.status_code}: {put_response.text}")

else:
    print(f" GET failed with status code {response.status_code}: {response.text}")
