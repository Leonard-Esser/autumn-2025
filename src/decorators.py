import time
from functools import wraps

from get_logger import get_logger

logger = get_logger(__name__)

def stop_the_clock(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"{func.__name__} took {end - start:.6f} seconds to execute")
        return result
    return wrapper