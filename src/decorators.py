import logging
import time
from functools import wraps
from threading import Lock

logger = logging.getLogger(__name__)


def stop_the_clock(func):
    total_time = 0.0
    call_count = 0
    lock = Lock()

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal total_time, call_count
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start

        with lock:
            call_count += 1
            total_time += duration
            avg_time = total_time / call_count

        logger.info(
            "%s took %.6f seconds (avg over %d calls: %.6f seconds)",
            func.__name__,
            duration,
            call_count,
            avg_time,
        )
        return result

    return wrapper