#!/bin/bash
# ==============================================================================
# Written by Nithin Titta, VCF-GS Support.
# Script to automate Broadcom KB 380251 (Extended)
# Fixes broken Orchestrator Integrations with Aria Automation 8.x after certificate replacement
# Supports both Embedded and External VRO.
# Run this on an Aria Automation appliance node.
# Needs a Bearer token, Grab it from browser  (log in to the impacted tenant vRA UI > Dev tools > request header > authorization. must only contain the Bearer Token witout the "Bearer"
# ==============================================================================

# Prompt for the Bearer Token
read -s -p "Enter your Aria Automation Bearer Token: " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo "Error: Token cannot be empty."
    exit 1
fi

echo "[*] Retrieving Aria Automation Load Balancer hostname..."
VRA=$(vracli load-balancer)

if [ -z "$VRA" ]; then
    echo "Error: Could not retrieve load balancer FQDN using 'vracli'. Are you running this on an Aria Automation appliance?"
    exit 1
fi
echo "    -> Aria Load Balancer: $VRA"
echo ""

# Fetch and display available VRO integrations
echo "[*] Finding all Orchestrator integrations (Embedded and External)..."
echo "----------------------------------------------------------------------"
curl -s -k "https://$VRA/iaas/api/integrations/?apiVersion=2021-07-15" -H "Authorization: Bearer $TOKEN" | \
jq -r '.content[] | select(.integrationType == "embedded-VRO" or .integrationType == "vro") | "Name: \(.name)\nType: \(.integrationType)\nID:   \(.id)\n----------------------------------------------------------------------"'

echo ""
read -p "Copy and paste the ID of the integration you want to update: " INTEGRATION_ID

if [ -z "$INTEGRATION_ID" ]; then
    echo "Error: Integration ID cannot be empty."
    exit 1
fi

# Determine where to pull the certificate from
echo ""
echo "If this is an external VRO, we need to pull the certificate from that specific appliance."
echo "If this is the embedded VRO, we pull it from the Aria Automation Load Balancer ($VRA)."
read -p "Enter the FQDN of the Orchestrator appliance (Press Enter to default to $VRA): " VRO_FQDN

VRO_FQDN=${VRO_FQDN:-$VRA}

echo ""
echo "[*] Extracting and formatting the new certificate chain from $VRO_FQDN:443..."
CERT_CONTENT=$(openssl s_client -connect "$VRO_FQDN:443" -showcerts < /dev/null 2>/dev/null | sed -ne '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' | awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}')

if [ -z "$CERT_CONTENT" ]; then
    echo "Error: Failed to retrieve the certificate from $VRO_FQDN:443"
    exit 1
fi

# Print summary and prompt for confirmation
echo ""
echo "======================================================================"
echo "                       PRE-FLIGHT CONFIRMATION                        "
echo "======================================================================"
echo "Target Orchestrator FQDN : $VRO_FQDN"
echo "Target Integration ID    : $INTEGRATION_ID"
echo "Certificate to apply     :"
echo -e "$CERT_CONTENT" | sed 's/\\n/\n/g' # Renders the literal \n as actual newlines for readability in the prompt
echo "======================================================================"
echo ""

read -p "Does the endpoint and certificate look correct? Proceed with patching? (y/n): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Operation cancelled by user. No changes were made."
    exit 0
fi

echo ""
echo "[*] Patching the integration with the new certificate..."
PATCH_CERT_PAYLOAD=$(cat <<EOF
{
  "integrationProperties": {
    "certificate": "$CERT_CONTENT"
  },
  "customProperties": {
    "certificate": "$CERT_CONTENT"
  }
}
EOF
)

# Apply the certificate patch
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -k -X PATCH "https://$VRA/iaas/api/integrations/$INTEGRATION_ID?apiVersion=2021-07-15" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  --data-raw "$PATCH_CERT_PAYLOAD")

if [[ "$HTTP_STATUS" -ge 200 && "$HTTP_STATUS" -lt 300 ]]; then
    echo "    -> Certificate patch applied successfully (HTTP $HTTP_STATUS)."
else
    echo "    -> Error: Failed to patch certificate (HTTP $HTTP_STATUS)."
    echo "    -> Note: If it fails because properties are read-only, please contact Broadcom Support as per the KB."
    exit 1
fi

echo "[*] Patching the integration to clear 'vroUnresponsiveReason' state..."
PATCH_STATE_PAYLOAD=$(cat <<EOF
{
  "customProperties": {
    "vroUnresponsiveReason": ""
  }
}
EOF
)

# Apply the unresponsive reason patch
HTTP_STATUS_STATE=$(curl -s -o /dev/null -w "%{http_code}" -k -X PATCH "https://$VRA/iaas/api/integrations/$INTEGRATION_ID?apiVersion=2021-07-15" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  --data-raw "$PATCH_STATE_PAYLOAD")

if [[ "$HTTP_STATUS_STATE" -ge 200 && "$HTTP_STATUS_STATE" -lt 300 ]]; then
    echo "    -> State patch applied successfully (HTTP $HTTP_STATUS_STATE)."
else
    echo "    -> Warning: Failed to clear unresponsive state (HTTP $HTTP_STATUS_STATE). You may need to manually verify in the UI."
fi

echo ""
echo "[+] Done! The Orchestrator trust should now be restored."
