from dns_check import dns_check
from http_check import http_check
from route53_fetch import get_route_53_domains

def run_monitor():
    domains = get_route_53_domains()

    print(f"\nTotal domains fetched: {len(domains)}\n")

    for domain in domains:
        print(f"Checking: {domain}")

        dns_result = dns_check(domain)

        if not dns_result["status"]:
            print(f" DNS FAILED: {dns_result}")
            continue

        print(f" DNS OK: {dns_result}")

        http_result = http_check(domain)

        if not http_result["status"]:
            print(f" HTTP FAILED: {http_result}")
        else:
            print(f" HTTP OK: {http_result}")

        print("-" * 50)


if __name__ == "__main__":
    run_monitor()