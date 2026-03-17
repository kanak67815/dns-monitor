import json
from datetime import datetime
from email_alert import send_email

REVIEW_FILE = "review_list.json"
LOG_FILE = "monitor_log.json"

# Load monitor data
try:
    with open(LOG_FILE) as f:
        monitor_data = json.load(f)
except Exception as e:
    print(f"Error reading {LOG_FILE}: {e}")
    monitor_data = []

# Load existing review list
try:
    with open(REVIEW_FILE) as f:
        existing = json.load(f)
except Exception:
    existing = []

existing_domains = {item.get("domain") for item in existing if "domain" in item}

new_flagged = []

# Process domains
for d in monitor_data:
    domain = d.get("domain")
    final_status = d.get("final_status")

    if not domain:
        continue

    if final_status == "failed" and domain not in existing_domains:
        new_flagged.append({
            "domain": domain,
            "approve": None,
            "flagged_on": datetime.utcnow().isoformat()
        })

# Merge and save
final_list = existing + new_flagged

with open(REVIEW_FILE, "w") as f:
    json.dump(final_list, f, indent=2)

# Send alert
if new_flagged:
    send_email([d["domain"] for d in new_flagged])
    print(f"{len(new_flagged)} new domains flagged.")
else:
    print("No new domains flagged.")