from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route_53_domains
from email_alert import send_email
from port_check import check_port
from retry_logic import retry
from crawler import crawl_domain
from approval_system import create_review_list

import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor

# -------------------------
# CONFIG
# -------------------------
MAX_WORKERS = 10

logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------
# DOMAIN CHECK FUNCTION
# -------------------------
def check_domain(domain):
    logging.info(f"Checking {domain}")

    result = {
        "domain": domain,
        "dns": {},
        "port": {},
        "http": {},
        "crawl": {}
    }

    # DNS
    dns_result = retry(dns_check, domain)
    result["dns"] = dns_result

    if not dns_result["status"]:
        logging.error(f"DNS failed for {domain}")
        result["final_status"] = "failed"
        return result

    # PORT
    port_result = check_port(domain)
    result["port"] = port_result

    if not port_result["status"]:
        logging.error(f"Port failed for {domain}")
        result["final_status"] = "failed"
        return result

    # HTTP (non-blocking warning)
    http_result = http_check(domain)
    result["http"] = http_result

    if not http_result["status"]:
        logging.warning(f"HTTP issue for {domain}: {http_result}")

    # CRAWLER (non-blocking warning)
    crawl_result = crawl_domain(domain)
    result["crawl"] = crawl_result

    if not crawl_result["status"]:
        logging.warning(f"Crawler issue for {domain}: {crawl_result}")

    result["final_status"] = "working"
    return result


# -------------------------
# MAIN MONITOR
# -------------------------
def run_monitor():
    domains = get_route_53_domains()
    logging.info(f"Total domains fetched: {len(domains)}")

    # -------------------------
    # PARALLEL EXECUTION
    # -------------------------
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(check_domain, domains))

    # -------------------------
    # SAVE RESULTS
    # -------------------------
    with open("monitor_log.json", "w") as f:
        json.dump(results, f, indent=2)

    # -------------------------
    # SEPARATE STATUS
    # -------------------------
    working = [r["domain"] for r in results if r["final_status"] == "working"]
    failed = [r["domain"] for r in results if r["final_status"] == "failed"]

    logging.info(f"Working domains: {len(working)}")
    logging.info(f"Failed domains: {len(failed)}")

    # -------------------------
    # ALERT + RECHECK
    # -------------------------
    if failed:
        logging.warning(f"Sending alert for failed domains: {failed}")
        send_email(failed)

        logging.info("Waiting 10 minutes before recheck...")
        time.sleep(600)

        still_failed = []

        for domain in failed:
            dns_result = retry(dns_check, domain)

            if not dns_result["status"]:
                still_failed.append(domain)
                continue

            port_result = check_port(domain)

            if not port_result["status"]:
                still_failed.append(domain)

        logging.warning(f"Still failed domains: {still_failed}")

        # -------------------------
        # HUMAN APPROVAL FLOW
        # -------------------------
        if still_failed:
            create_review_list(still_failed)


if __name__ == "__main__":
    run_monitor()