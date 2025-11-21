import time
from functools import wraps

from memory import reminders


def stop_the_clock(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds to execute.")
        return result
    return wrapper


def explain_why(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        reminder = f"Do not forget to explain why {func.__name__} does what it does."
        if reminder not in reminders:
            reminders.append(reminder)
        return result
    return wrapper


def back_up_with_literature(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        reminder = f"Back {func.__name__} up with literature."
        if reminder not in reminders:
            reminders.append(reminder)
        return result
    return wrapper


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()