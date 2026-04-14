import requests
import json
import os
import urllib3

# SSL xəbərdarlıqlarını söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_HOST = "13.63.163.57" # Sənin Splunk IP-n
SPLUNK_PORT = "8089"
SPLUNK_USER = "admin"
SPLUNK_PASS = os.getenv("SPLUNK_PASSWORD") # Şifrəni gizli yerdən götürəcəyik

URL = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/saved/searches"

def sync():
    with open('splunk/rules.json', 'r') as f:
        rules = json.load(f)

    for rule in rules:
        print(f"Syncing: {rule['rule_name']}")
        payload = {
            "name": rule['rule_name'],
            "search": rule['query'],
            "description": rule['description'],
            "is_scheduled": 1,
            "cron_schedule": "*/5 * * * *",
            "actions": "webhook,email"
        }
        
        # API vasitəsilə Splunk-a göndəririk
        response = requests.post(URL, data=payload, auth=(SPLUNK_USER, SPLUNK_PASS), verify=False)
        
        if response.status_code == 201:
            print(f"✅ {rule['rule_name']} yaradıldı.")
        elif response.status_code == 409:
            print(f"ℹ️ {rule['rule_name']} artıq var, update edilir...")
            # Update üçün URL-ə rule adını əlavə edirik
            update_url = f"{URL}/{rule['rule_name']}"
            requests.post(update_url, data={"search": rule['query']}, auth=(SPLUNK_USER, SPLUNK_PASS), verify=False)
        else:
            print(f"❌ Xəta: {response.status_code}")

if __name__ == "__main__":
    sync()
