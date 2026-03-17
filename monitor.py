from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route_53_domains
from email_alert import send_email
from route53_delete import delete_dns_record
from port_check import check_port
from retry_logic import retry
from dotenv import load_dotenv
load_dotenv()
import time
import os
print("HOSTED_ZONE_ID:", os.getenv("HOSTED_ZONE_ID"))
print("EMAIL_USER:", os.getenv("EMAIL_USER"))
# SAFETY SWITCH
ENABLE_DELETE = False

def run_monitor():
    domains = get_route_53_domains()

    print(f"\nTotal domains fetched: {len(domains)}\n")

    working = []
    failed = []

    # -------------------------
    # INITIAL CHECK
    # -------------------------
    for domain in domains:
        print(f"\nChecking: {domain}")

        dns_result = retry(dns_check, domain)

        if not dns_result["status"]:
            print(f" DNS FAILED: {dns_result}")
            failed.append(domain)
            continue

        print(f" DNS OK: {dns_result}")

        # ✅ PORT CHECK NEXT
        port_result = check_port(domain)

        if not port_result["status"]:
            print(f" PORT FAILED: {port_result}")
            failed.append(domain)
            continue

        print(f" PORT OK: {port_result}")

        # ✅ Mark as working (DNS + PORT passed)
        working.append(domain)

        # ✅ HTTP CHECK (ONLY FOR LOGGING)
        http_result = http_check(domain)

        if not http_result["status"]:
            print(f" HTTP WARNING (ignored): {http_result}")
        else:
            print(f" HTTP OK: {http_result}")

    # -------------------------
    # SUMMARY
    # -------------------------
    print("\nWORKING DOMAINS:")
    for d in working:
        print(d)

    print("\nFAILED DOMAINS:")
    for d in failed:
        print(d)

    # -------------------------
    # ALERT + RECHECK
    # -------------------------
    if failed:

        print("\nSending Email Alert...")
        send_email(failed)

        print("\nWaiting for 10 minutes before next check...")
        time.sleep(600)

        still_failed = []

        print("\nRECHECKING FAILED DOMAINS:")

        for domain in failed:
            # DNS recheck
            dns_result = retry(dns_check, domain)

            if not dns_result["status"]:
                print(f"{domain} still DNS FAILED")
                still_failed.append(domain)
                continue

            # PORT recheck
            port_result = check_port(domain)

            if not port_result["status"]:
                print(f"{domain} still PORT FAILED")
                still_failed.append(domain)
            else:
                print(f"{domain} is now healthy")

        print("\nStill failed domains:")
        print(still_failed)

        # -------------------------
        # DELETE (SAFE)
        # -------------------------
        if still_failed:

            print("\nSummary before deletion:")
            print("WORKING DOMAINS:", working)
            print("FAILED DOMAINS:", still_failed)

            if not ENABLE_DELETE:
                print("\n🚫 Deletion skipped (ENABLE_DELETE=False)")
            else:
                print("\nDeleting DNS records...")

                for domain in still_failed:

                    # EXTRA SAFETY CHECK
                    if not domain.endswith("mps-tis.com"):
                        print(f"Skipping unsafe domain: {domain}")
                        continue

                    delete_dns_record(domain)


if __name__ == "__main__":
    run_monitor()
