import random

import pandas as pd
from pathlib import Path

import config
import helpers
from batching import process_each_sample
from classifying import classify, naysayer
from decorators import stop_the_clock
from helpers import get_version
from io_helpers import export_ccd_events, export_sample, get_output_dir
from memory import reminders
from sampling import draw_k_random_distinct_rows_from_sample, get_sample_provided_by_ebert_et_al


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
    
    if config.DO_NOT_CLASSIFY_AT_ALL:
        data = process_each_sample(sample, root, version, naysayer)
    else:
        data = process_each_sample(sample, root, version, classify)
    
    _export_selected_information(
        data,
        root,
        version
    )


def _get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_sample(
    root: str | Path,
    version: str,
    export_the_sample_right_away: bool = True
) -> list[str]:
    
    sample = get_sample_provided_by_ebert_et_al(
        _get_path_of_sample(root),
        config.SAMPLE_SIZE,
        config.RANDOM_STATE
    )
    
    if sample and export_the_sample_right_away:
        export_sample(sample, root, version)
    
    return sample


def _get_path_of_sample(root: str | Path) -> Path:
    return Path(root) / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv"


def _export_selected_information(
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


def _read_events_csv_and_draw_random_events():
    root = _get_root()
    version = get_version(root)
    path = get_output_dir(root, config.NAME_OF_FRAMES_DIR, version=version)
    path = path / "events.csv"
    _draw_random_events(
        pd.read_csv(path),
        root,
        version
    )


def _draw_random_events(
    events: pd.DataFrame,
    root: str | Path,
    version: str
) -> pd.DataFrame:
    columns_of_interest = [
        "Repository Full Name",
        "Commit SHA",
        "Path"
    ]
    
    output_dir = get_output_dir(root, config.NAME_OF_SAMPLES_DIR, version=version)
    export_path = output_dir / f"{config.EVENTS_SAMPLE_SIZE}_random_events.csv"
    
    return draw_k_random_distinct_rows_from_sample(
        events,
        columns_of_interest,
        config.EVENTS_SAMPLE_SIZE,
        export_path,
        config.RANDOM_STATE_FOR_DRAWING_EVENTS
    )


def _print_reminders():
    for reminder in reminders:
        print(reminder)


if __name__ == "__main__":
    main()
    _read_events_csv_and_draw_random_events()
    if reminders:
        print("----------")
        print("Reminders:")
        _print_reminders()