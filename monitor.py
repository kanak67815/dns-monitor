from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route53_domains
from route53_delete import delete_dns_record
from email_alert import send_email
import os

import time

HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")

client = boto3.client("route53")
HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")

def evaluate_domain(domain):
    """
    Decide if domain is healthy or suspicious
    """

    dns_result = dns_check(domain)
    http_result = http_check(domain)

    print(f"\nChecking: {domain}")
    print("DNS:", dns_result)
    print("HTTP:", http_result)

    # 🚨 CASE 1: Domain does not exist
    if not dns_result["status"] and dns_result.get("reason") == "NXDOMAIN":
        return "DELETE"

    # ⚠️ CASE 2: DNS OK but HTTP failed
    if dns_result["status"] and not http_result["status"]:
        return "SUSPICIOUS"

    # ⚠️ CASE 3: Everything failed
    if not dns_result["status"] and not http_result["status"]:
        return "SUSPICIOUS"

    # ✅ CASE 4: Working
    return "HEALTHY"


def monitor():

    domains_data = get_route53_domains(HOSTED_ZONE_ID)

    healthy = []
    suspicious = []
    to_delete = []

    # 🔍 First Pass
    for item in domains_data:
        domain = item["domain"]

        status = evaluate_domain(domain)

        if status == "HEALTHY":
            healthy.append(domain)

        elif status == "SUSPICIOUS":
            suspicious.append(domain)

        elif status == "DELETE":
            to_delete.append(domain)

    # 📧 Alert suspicious domains
    if suspicious:
        print("\nSending alert for suspicious domains...")
        send_email(suspicious)

    # ⏳ WAIT before recheck
    print("\nWaiting 10 minutes before recheck...")
    time.sleep(600)

    still_suspicious = []

    # 🔁 Second Pass (Recheck)
    for domain in suspicious:
        status = evaluate_domain(domain)

        if status != "HEALTHY":
            still_suspicious.append(domain)

    print("\nStill suspicious:", still_suspicious)

    # 🚨 FINAL DELETE DECISION
    final_delete = to_delete + still_suspicious

    if final_delete:
        print("\nDomains marked for deletion:")
        print(final_delete)

        # ⚠️ Ideally require manual approval here
        confirm = input("Type YES to delete: ")

        if confirm == "YES":
            for domain in final_delete:
                delete_dns_record(domain)
        else:
            print("Deletion cancelled.")


if __name__ == "__main__":
    monitor()
