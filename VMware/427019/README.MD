# VCD Edge Gateway Firewall Exporter

A Python utility to export all firewall rules—from a VMware Cloud Director (VCD) Edge Gateway into CSV and JSON formats.

## 📌 Why this script exists
In current versions of the Cloud Director UI, there is no option to export all firewall rules as CSV. This is an example script uses the VCD CloudAPI to retrieve the complete rule set and export it to a readable CSV format.

## 🚀 Features
* **Full Visibility:** Exports System, User, and Default rules.
* **Dual Output:** Generates both a readable CSV report and a raw JSON dump.
* **Dynamic Naming:** Automatically names output files using the Gateway UUID (e.g., `7e817e69-....csv`).
* **Data Formatting:** Flattens complex objects (like Application Port Profiles) into readable string values.

## 📋 Prerequisites
* **Python 3.x** installed on your machine.
* A valid **Bearer Token** (Access Token) from an active VCD session.

## ⚙️ Installation

1.  Clone this repository or download the script.
2.  Install the required Python library:
    ```bash
    pip install requests
    ```

## 🔧 Configuration

Open `export_firewall.py` in a text editor and update the following variables:

1.  **VCD_HOST:**
    Set this to your Cloud Director FQDN.
    ```python
    VCD_HOST = "vcd10-6-1.rainpole.local"
    ```

2.  **BEARER_TOKEN:**
    You must obtain a valid token from your browser session or Postman.
    * **How to get it:** Log into VCD UI > Press `F12` (Dev Tools) > Go to **Network** tab > Click any request > Copy the `Authorization` header value.
    * **Paste it:** Replace the placeholder string in the script.
    ```python
    BEARER_TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhOTNjOWR..."
    ```
    *(Note: Do not include the prefix "Bearer " in the variable, just the long alphanumeric string).*

## 🏃 Usage

1.  Run the script:
    ```bash
    python export_firewall.py
    ```

2.  When prompted, enter the **UUID** of the Edge Gateway you wish to query.
    * *Tip: You can find this UUID in the URL when viewing the Gateway in the VCD UI.*

    ```text
    Enter EDGE Gateway UUID: 7e817e69-d869-4f8e-8d73-3db114d6a2e6
    ```

## 📂 Output

The script will generate two files in the same directory, named after the Gateway UUID:

1.  **`<UUID>.csv`**
    * A flat-file spreadsheet containing all rules.
    * Includes a **Rule_Type** column to distinguish between `System`, `User Defined`, and `Default` rules.
2.  **`<UUID>.json`**
    * The raw JSON response from the API (useful for debugging or programmatic use).

## ❓ Troubleshooting

| Error | Cause | Resolution |
| :--- | :--- | :--- |
| **401 Unauthorized** | Token expired. | Get a fresh token from the browser (tokens typically expire after 30 mins) and update the script. |
| **406 Not Acceptable** | API Version mismatch. | Ensure `API_VERSION` in the script matches the version supported by your VCD cell (default is `40.0.0-alpha`). |
| **Connection Error** | Network issues. | Check that your machine can resolve and reach the `VCD_HOST` address. |

## ⚠️ Disclaimer
This script uses the `alpha` version of the VCD CloudAPI (`40.0.0-alpha`). you may tweak this based on what is avilable at https://{VCD_HOST}/api/versions
