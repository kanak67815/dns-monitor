import requests
from bs4 import BeautifulSoup

def crawl_domain(domain, timeout=5):
    url = f"http://{domain}"

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code >= 400:
            return {
                "status": False,
                "reason": f"HTTP {response.status_code}"
            }

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No Title"

        text = soup.get_text().strip()

        # Basic validation rules
        if len(text) < 50:
            return {
                "status": False,
                "reason": "Content too small",
                "title": title
            }

        if "error" in text.lower():
            return {
                "status": False,
                "reason": "Error page detected",
                "title": title
            }

        return {
            "status": True,
            "title": title,
            "length": len(text)
        }

    except Exception as e:
        return {
            "status": False,
            "reason": str(e)
        }