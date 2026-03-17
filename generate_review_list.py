import json
from datetime import datetime
from email_alert import send_email

REVIEW_FILE = "review_list.json"
LOG_FILE = "monitor_log.json"

# -------------------------
# LOAD DATA
# -------------------------
with open(LOG_FILE) as f:
    monitor_data = json.load(f)

try:
    with open(REVIEW_FILE) as f:
        existing = json.load(f)
except:
    existing = []

existing_domains = {item["domain"] for item in existing}

new_flagged = []

# -------------------------
# FLAG FAILED DOMAINS
# -------------------------
for d in monitor_data:
    domain = d.get("domain")

    final_status = d.get("final_status")

    # Only flag FAILED domains
    if final_status == "failed":
        if domain not in existing_domains:
            new_flagged.append({
                "domain": domain,
                "approve": None,   # human decision
                "flagged_on": datetime.utcnow().isoformat()
            })

# -------------------------
# MERGE OLD + NEW
# -------------------------
final_list = existing + new_flagged

# -------------------------
# SAVE FILE
# -------------------------
with open(REVIEW_FILE, "w") as f:
    json.dump(final_list, f, indent=2)

# -------------------------
# ALERT ONLY NEW
# -------------------------
if new_flagged:
    send_email([d["domain"] for d in new_flagged])
    print(f"{len(new_flagged)} new domains flagged.")
else:
    print("No new domains flagged.")