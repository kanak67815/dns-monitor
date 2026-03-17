import json
import os
import logging
from datetime import datetime, timedelta
from route53_delete import delete_dns_record

REVIEW_FILE = "review_list.json"
DAYS_WAIT = 5

ENABLE_DELETE = os.getenv("ENABLE_DELETE", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)

# LOAD REVIEW LIST
try:
    with open(REVIEW_FILE) as f:
        review_data = json.load(f)
except FileNotFoundError:
    logging.error("review_list.json not found")
    exit()
except Exception as e:
    logging.error(f"Error reading review_list.json: {e}")
    exit()

# PROCESS EACH DOMAIN
for item in review_data:
    domain = item.get("domain")
    flagged_on = item.get("flagged_on")
    approve = item.get("approve")

    if not domain or not flagged_on:
        logging.warning(f"Skipping invalid entry: {item}")
        continue

    try:
        flagged_date = datetime.fromisoformat(flagged_on)
    except Exception:
        logging.error(f"Invalid date format for {domain}: {flagged_on}")
        continue

    # WAITING PERIOD CHECK
    if (datetime.utcnow() - flagged_date) < timedelta(days=DAYS_WAIT):
        logging.info(f"{domain}: Waiting period not completed")
        continue

    # APPROVAL CHECK
    if approve is True:

        if not ENABLE_DELETE:
            logging.warning(f"[DRY RUN] Would delete {domain}")
            continue

        try:
            result = delete_dns_record(domain)
        except Exception as e:
            logging.error(f"Error deleting {domain}: {e}")
            continue

        if result:
            logging.info(f"Deleted: {domain}")
        else:
            logging.error(f"Failed to delete: {domain}")

    elif approve is False:
        logging.info(f"{domain}: Explicitly NOT approved for deletion")

    else:
        logging.info(f"{domain}: Waiting for human approval")