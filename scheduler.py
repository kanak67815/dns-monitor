import time

def run_with_intervals(task, intervals=[600, 3600, 86400]):
    """
    intervals in seconds:
    600 = 10 min
    3600 = 1 hr
    86400 = 24 hr
    """

    for interval in intervals:
        print(f"\nRunning check... next run in {interval} seconds\n")
        task()
        time.sleep(interval)