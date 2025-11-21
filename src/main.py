import os
import time

from pathlib import Path
from pygit2 import Repository
import pandas as pd

from batching import process_each_sample
from decorators import stop_the_clock
from helpers import get_version
from io_helpers import export_sample, export_ccd_events
from sampling import get_sample
import config
import helpers


def get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_ccd_event(text: str) -> bool:
    return false


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