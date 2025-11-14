import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds to execute.")
        return result
    return wrapper


@timer
def main():
    print("Hello from timer.py!")


if __name__ == "__main__":
    main()