import pandas as pd
from pathlib import Path

from batching import process_each_sample
from decorators import stop_the_clock
from helpers import get_version
from io_helpers import export_ccd_events, export_sample
from memory import reminders
from sampling import read_full_names_from_sample_provided_by_ebert_et_al
from zero_shot_classification import classify
import config
import helpers


def _get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_sample(
    root: str | Path,
    version: str,
    export_the_sample_right_away: bool = True
) -> list[int] | list[str]:
    
    sample = read_full_names_from_sample_provided_by_ebert_et_al(
        _get_path_of_sample(root)
    )
    
    if not sample:
        return
    
    sample = sample[:config.SAMPLE_SIZE]
    
    if export_the_sample_right_away:
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
            process_each_sample(sample, root, version, classify),
            root,
            version
        )


if __name__ == "__main__":
    main()
    if reminders:
        print("----------")
        print("Reminders:")
        print_reminders()