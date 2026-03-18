import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def http_check(domain, retries=3, timeout=5):

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; HealthCheckBot/1.0)"
    }

    urls = [
        f"https://{domain}",
        f"http://{domain}"
    ]

    last_error = None

    for attempt in range(1, retries + 1):
        for url in urls:
            try:
                response = requests.head(
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    headers=headers,
                    verify=False   # ✅ IMPORTANT FIX
                )

                if response.status_code >= 400:
                    response = requests.get(
                        url,
                        timeout=timeout,
                        allow_redirects=True,
                        headers=headers,
                        verify=False   # ✅ IMPORTANT FIX
                    )

                # ✅ SUCCESS CASE
                if 200 <= response.status_code < 400:
                    return {
                        "status": True,
                        "url": url,
                        "status_code": response.status_code
                    }

                # 🟡 BOT BLOCK
                elif response.status_code == 403:
                    return {
                        "status": True,
                        "warning": "Forbidden (possible bot block)",
                        "url": url,
                        "status_code": 403
                    }

                # 🟡 SERVER ERROR BUT ALIVE
                elif response.status_code >= 500:
                    return {
                        "status": True,
                        "warning": "Server error but alive",
                        "url": url,
                        "status_code": response.status_code
                    }

            # 🔥 FIXED SSL HANDLING
            except requests.exceptions.SSLError as e:
                return {
                    "status": True,   # ✅ KEY CHANGE
                    "warning": "SSL issue",
                    "error": str(e),
                    "url": url
                }

            except requests.exceptions.Timeout:
                last_error = "Timeout"

            except requests.exceptions.ConnectionError:
                last_error = "Connection Error"

            except requests.exceptions.RequestException as e:
                last_error = str(e)

        time.sleep(2 ** attempt)

    return {
        "status": False,
        "url": None,
        "status_code": None,
        "error": last_error or "HTTP check failed after retries"
    }