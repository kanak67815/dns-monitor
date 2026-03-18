from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route_53_domains
from email_alert import send_email
from port_check import check_port
from retry_logic import retry
from crawler import crawl_domain

import logging
import json
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 10
LOG_FILE = "monitor_log.json"

logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def safe_check(domain):
    try:
        return check_domain(domain)
    except Exception as e:
        logging.error(f"Crash on {domain}: {e}")
        return {
            "domain": domain,
            "final_status": "failed",
            "error": str(e)
        }

def check_domain(domain):
    logging.info(f"Checking {domain}")

    result = {
        "domain": domain,
        "dns": {},
        "port": {},
        "http": {},
        "crawl": {},
        "failure_reason": []
    }

    dns_result = retry(dns_check, domain)
    result["dns"] = dns_result

    if not dns_result.get("status"):
        result["failure_reason"].append("DNS")
        result["final_status"] = "failed"
        return result

    port_result = check_port(domain)
    result["port"] = port_result

    if not port_result.get("status"):
        result["failure_reason"].append("PORT")
        result["final_status"] = "failed"
        return result

    http_result = http_check(domain)
    result["http"] = http_result

    if not http_result.get("status"):
        result["failure_reason"].append("HTTP")

    crawl_result = crawl_domain(domain)
    result["crawl"] = crawl_result

    if not crawl_result.get("status"):
        result["failure_reason"].append("CRAWL")

    if not http_result.get("status") and not crawl_result.get("status"):
        result["final_status"] = "failed"
    else:
        result["final_status"] = "working"

    return result

def load_previous_failed():
    try:
        with open(LOG_FILE) as f:
            old_data = json.load(f)
            return {d["domain"] for d in old_data if d.get("final_status") == "failed"}
    except:
        return set()

def run_monitor():
    domains = get_route_53_domains()
    logging.info(f"Total domains fetched: {len(domains)}")

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(domains))) as executor:
        results = list(executor.map(safe_check, domains))

    old_failed = load_previous_failed()

    with open(LOG_FILE, "w") as f:
        json.dump(results, f, indent=2)

    working = [r["domain"] for r in results if r.get("final_status") == "working"]
    failed = [r["domain"] for r in results if r.get("final_status") == "failed"]

    logging.info(f"Working domains: {len(working)}")
    logging.info(f"Failed domains: {len(failed)}")

    new_failed = [d for d in failed if d not in old_failed]

    if new_failed:
        logging.warning(f"New failed domains detected: {new_failed}")
        send_email(new_failed)

if __name__ == "__main__":
    run_monitor()