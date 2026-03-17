import json
from datetime import datetime
from alert_service import send_alert

REVIEW_FILE = "review_list.json"
LOG_FILE = "monitor_log.json"

# Load monitor log
with open(LOG_FILE) as f:
    monitor_data = json.load(f)

# Load existing review list (if exists)
try:
    with open(REVIEW_FILE) as f:
        existing = json.load(f)
except:
    existing = []

existing_domains = {item["domain"] for item in existing}

new_flagged = []

for d in monitor_data:
    domain = d.get("domain")

    dns_status = d.get("dns", {}).get("status", False)
    http_status = d.get("http", {}).get("status", False)
    crawl_score = d.get("crawl_score", 0)

    if not dns_status or not http_status or crawl_score < 0.3:
        if domain not in existing_domains:
            new_flagged.append({
                "domain": domain,
                "delete": False,
                "flagged_on": datetime.utcnow().isoformat()
            })

# Merge old + new
final_list = existing + new_flagged

# Save
with open(REVIEW_FILE, "w") as f:
    json.dump(final_list, f, indent=2)

# Send alert only for new domains
if new_flagged:
    send_alert([d["domain"] for d in new_flagged])
    print(f"{len(new_flagged)} new domains flagged.")
else:
    print("No new domains flagged.")