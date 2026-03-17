import dns.resolver
import requests
from datetime import datetime
from email_alert import send_email
import time
from route53_delete import delete_dns_record
import boto3
import os

client = boto3.client("route53")
HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")

domains = []
paginator = client.get_paginator("list_resource_record_sets")
for page in paginator.paginate(HostedZoneId=HOSTED_ZONE_ID):
    for record in page["ResourceRecordSets"]:
        if record["Type"] in ["A", "CNAME"]:
            name = record["Name"].rstrip(".")
            domains.append(name)

# Remove duplicates if any
domains = list(set(domains))
log_file = open("monitor_log.txt", "a")

working = []
failed = []

for domain in domains:

    print("\nChecking:", domain)
    log_file.write(f"\n[{datetime.now()}] Checking {domain}\n")

    # DNS CHECK
    try:
        result = dns.resolver.resolve(domain)
        ip = result[0].to_text()

        print("DNS OK:", ip)
        log_file.write(f"DNS OK: {ip}\n")

    except Exception as e:
        print("DNS FAILED:", e)
        log_file.write("DNS FAILED\n")

        failed.append(domain)
        continue


    # HTTP CHECK
    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(
            "http://" + domain,
            timeout=5,
            allow_redirects=True,
            headers=headers
        )

        print("HTTP STATUS ->", response.status_code)
        log_file.write(f"HTTP STATUS -> {response.status_code}\n")

        if 200 <= response.status_code < 400:
            working.append(domain)

        else:
            print("HTTP FAILED")
            log_file.write("HTTP FAILED\n")

            failed.append(domain)

    except Exception as e:
        print("HTTP FAILED:", e)
        log_file.write("HTTP FAILED\n")

        failed.append(domain)
print("\nWORKING DOMAINS:")
for d in working:
    print(d)


print("\nFAILED DOMAINS:")
for d in failed:
    print(d)

log_file.write("\n===================\n")
log_file.write("WORKING DOMAINS:\n")

for d in working:
    log_file.write(d + "\n")


log_file.write("\nFAILED DOMAINS:\n")

for d in failed:
    log_file.write(d + "\n")

log_file.close()

if failed:

    print("\nSending Email Alert...")
    send_email(failed)

    print("\nWaiting for 10 minutes before next check...")
    time.sleep(600)

    still_failed = []

    print("\nRECHECKING FAILED DOMAINS:")

    for domain in failed:

        try:

            dns.resolver.resolve(domain)

            headers = {"User-Agent": "Mozilla/5.0"}

            r = requests.get(
                "http://" + domain,
                timeout=5,
                allow_redirects=True,
                headers=headers
            )

            if 200 <= r.status_code < 400:
                print(f"{domain} is now working.")

            else:
                print(f"{domain} is still failing.")
                still_failed.append(domain)

        except Exception as e:
            print(f"{domain} ERROR:", e)
            still_failed.append(domain)



    print("\nStill failed domains:")
    print(still_failed)



    if still_failed:
        print("\nSummary before deletion:")
        print("WORKING DOMAINS:")
        for d in working:
            print(d)
        print("\nFAILED DOMAINS:")
        for d in still_failed:
            print(d)
        input("\nPress Enter to continue with deletion, or Ctrl+C to abort...")

        print("\nDeleting DNS records from Route53...")

        for domain in still_failed:
            delete_dns_record(domain)