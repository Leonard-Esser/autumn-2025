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
        data = process_each_sample(sample, root, version, classify)
        export_ccd_events(data, "all_events", root, version)
        filtered = data[data["Affects CCD"] == 1]
        export_ccd_events(filtered, "ccd_events_only", root, version)


if __name__ == "__main__":
    main()
    if reminders:
        print("----------")
        print("Reminders:")
        print_reminders()