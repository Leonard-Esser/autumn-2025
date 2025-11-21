from pathlib import Path

from batching import process_each_sample
from decorators import stop_the_clock, explain_why, back_up_with_literature
from helpers import get_version
from io_helpers import export_sample, export_ccd_events
from memory import reminders
from sampling import get_sample
import config
import helpers


def get_root() -> Path:
    return Path(__file__).resolve().parent.parent


@explain_why
@back_up_with_literature
def is_ccd_event(text: str) -> bool:
    return False


def print_reminders():
    for reminder in reminders:
        print(reminder)


@stop_the_clock
def main():
    root = get_root()
    version = get_version(root)
    
    sample = get_sample()
    export_sample(sample, root, version)
    
    data = process_each_sample(sample, root, version, is_ccd_event)
    export_ccd_events(data, root, version)


if __name__ == "__main__":
    main()
    print("---")
    print("Reminders:")
    print_reminders()