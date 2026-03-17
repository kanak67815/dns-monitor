import time

def retry(func, *args, retries=3, delay=2, backoff=2, **kwargs):
    last_result = None

    for attempt in range(1, retries + 1):
        result = func(*args, **kwargs)

        # Expect function to return {"status": True/False}
        if result.get("status"):
            return result

        last_result = result

        if attempt < retries:
            time.sleep(delay)
            delay *= backoff

    return last_result