import random

import pandas as pd
from pathlib import Path

import config
import helpers
from batching import process_each_sample
from classifying import is_ccdc_event, identify_types_of_changes
from decorators import stop_the_clock
from helpers import get_version
from io_helpers import export_ccd_events, export_sample
from memory import reminders
from model import CCDCEvent, Event
from sampling import get_sample_provided_by_ebert_et_al


def _get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_sample(
    root: str | Path,
    version: str,
    export_the_sample_right_away: bool = True
) -> list[str]:
    
    sample = get_sample_provided_by_ebert_et_al(
        _get_path_of_sample(root),
        config.SAMPLE_SIZE
    )
    
    if sample and export_the_sample_right_away:
        export_sample(sample, root, version)
    
    return sample


def _get_path_of_sample(root: str | Path) -> Path:
    return Path(root) / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv"


def export_selected_information(
    data: pd.DataFrame,
    root: str | Path,
    version: str
):
    columns_of_interest = [
        "Repository Full Name",
        "Commit SHA",
        "Path",
        "Affects CCD",
        "Type of Change",
        "Commit Date",
        "Repository Has Discussions",
        "Repository Has Issues",
        "Repository Has Wiki",
        "Repository Open Issues Count",
        "Repository Stargazers Count",
        "Repository Subscribers Count",
        "Repository Size",
    ]
    data = data[columns_of_interest]
    export_ccd_events(data, "events", root, version)


def _print_reminders():
    for reminder in reminders:
        print(reminder)


def _classify(
    repo: str,
    commit: str,
    path: str,
    flattened_changes: str
) -> CCDCEvent | Event:
    if is_ccdc_event(flattened_changes):
        return CCDCEvent(
            repo,
            commit,
            path,
            types_of_changes=identify_types_of_changes(flattened_changes)
        )
    
    return Event(repo, commit, path)


@stop_the_clock
def main():
    root = _get_root()
    version = get_version(root)
    print(f"Data will be saved to a directory named {version} within data/output/")
    
    sample = _get_sample(
        root,
        version
    )
    
    if not sample:
        pass
    else:
        export_selected_information(
            process_each_sample(sample, root, version, _classify),
            root,
            version
        )


if __name__ == "__main__":
    main()
    if reminders:
        print("----------")
        print("Reminders:")
        print_reminders()