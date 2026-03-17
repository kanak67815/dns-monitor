from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route_53_domains
from email_alert import send_email
from route53_delete import delete_dns_record
from check_port import check_port
from retry_logic import retry
from crawler import crawl_domain
from approval_system import create_review_list
from dotenv import load_dotenv

import time

load_dotenv()

# SAFETY SWITCH
ENABLE_DELETE = False

def run_monitor():
    domains = get_route_53_domains()

    print(f"\nTotal domains fetched: {len(domains)}\n")

    working = []
    failed = []

<<<<<<< HEAD
    # -------------------------
    # INITIAL CHECK
    # -------------------------
=======
   
>>>>>>> 787d94f (generate list)
    for domain in domains:
        print(f"\nChecking: {domain}")

        # DNS
        dns_result = retry(dns_check, domain)
        if not dns_result["status"]:
            print(f" DNS FAILED: {dns_result}")
            failed.append(domain)
            continue

        print(f" DNS OK: {dns_result}")

        # PORT
        port_result = check_port(domain)
        if not port_result["status"]:
            print(f" PORT FAILED: {port_result}")
            failed.append(domain)
            continue

        print(f" PORT OK: {port_result}")

        # HTTP
        http_result = http_check(domain)
        if not http_result["status"]:
            print(f" HTTP WARNING (ignored): {http_result}")
        else:
            print(f" HTTP OK: {http_result}")

        # CRAWLER
        crawl_result = crawl_domain(domain)
        if not crawl_result["status"]:
            print(f" CRAWLER WARNING: {crawl_result}")
        else:
            print(f" CRAWLER OK: {crawl_result}")

        # If DNS + PORT passed → working
        working.append(domain)

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
            dns_result = retry(dns_check, domain)

            if not dns_result["status"]:
                print(f"{domain} still DNS FAILED")
                still_failed.append(domain)
                continue

            port_result = check_port(domain)

            if not port_result["status"]:
                print(f"{domain} still PORT FAILED")
                still_failed.append(domain)
            else:
                print(f"{domain} is now healthy")

        print("\nStill failed domains:")
        print(still_failed)

<<<<<<< HEAD
        # -------------------------
        # APPROVAL SYSTEM (instead of delete)
        # -------------------------
=======
>>>>>>> 787d94f (generate list)
        if still_failed:
            print("\nCreating review list for manual approval...")
            create_review_list(still_failed)


if __name__ == "__main__":
    run_monitor()
