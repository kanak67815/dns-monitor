import json
from datetime import datetime

REVIEW_FILE = "review_list.json"

def create_review_list(domains):
    data = []

    for domain in domains:
        data.append({
            "domain": domain,
            "first_detected": str(datetime.now()),
            "approve": None  # human fills this
        })

    with open(REVIEW_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Review list created: {REVIEW_FILE}")


def load_review_list():
    try:
        with open(REVIEW_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def get_approved_domains():
    data = load_review_list()

    approved = []

    for entry in data:
        if entry.get("approve") is True:
            approved.append(entry["domain"])

    return approved