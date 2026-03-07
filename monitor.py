import dns.resolver
import requests
from datetime import datetime
from email_alert import send_email

domains = [
    "app1.mps-tis.com",
    "app2.mps-tis.com",
    "app3.mps-tis.com",
    "app4.mps-tis.com",
    "app5.mps-tis.com",
    "web1.mps-tis.com",
    "web2.mps-tis.com",
    "web3.mps-tis.com",
    "web4.mps-tis.com",
    "web5.mps-tis.com"
]

log_file = open("monitor_log.txt", "a")

working = []
failed = []

for domain in domains:

    print("\nChecking:", domain)
    log_file.write(f"\n[{datetime.now()}] Checking {domain}\n")

    # DNS CHECK
    try:
        result = dns.resolver.resolve(domain, "A")
        ip = result[0].to_text()
        print("DNS OK:", ip)
        log_file.write(f"DNS OK: {ip}\n")

    except:
        print("DNS FAILED")
        log_file.write("DNS FAILED\n")
        failed.append(domain)
        continue

    # HTTP CHECK
    try:
        response = requests.get("http://" + domain, timeout=5)
        print("HTTP STATUS ->", response.status_code)
        log_file.write(f"HTTP STATUS -> {response.status_code}\n")

        working.append(domain)

    except:
        print("HTTP FAILED")
        log_file.write("HTTP FAILED\n")
        failed.append(domain)

print("\n===================")

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

# EMAIL ALERT
if failed:
    print("\nSending Email Alert...")
    send_email(failed)