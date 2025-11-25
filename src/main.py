from pathlib import Path

from batching import process_each_sample
from decorators import stop_the_clock
from helpers import get_version
from io_helpers import export_sample, export_ccd_events
from memory import reminders
from random_dummy_classifier import classify
from sampling import get_sample
import config
import helpers


def get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_reminders():
    for reminder in reminders:
        print(reminder)


@stop_the_clock
def main():
    root = get_root()
    version = get_version(root)
    print(f"Data will be saved to a directory named {version} within data/output/")
    
    sample = get_sample()
    export_sample(sample, root, version)
    
    data = process_each_sample(sample, root, version, classify)
    export_ccd_events(data, root, version)


if __name__ == "__main__":
    main()
    if reminders:
        print("----------")
        print("Reminders:")
        print_reminders()