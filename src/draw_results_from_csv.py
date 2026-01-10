import csv
import random
from pathlib import Path

from domain_model import Result, Subject


def draw_results_from_csv(
    path: Path,
    *,
    k: int | None = None,
    random_state: int | None = None,
) -> set[Result]:
    # subject -> (channels_set, is_ccdc_event)
    grouped: dict[Subject, tuple[set[str], bool]] = {}

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subject = Subject(
                full_name_of_repo=row["full_name_of_repo"],
                commit_sha=row["commit_sha"],
                path=row["path"],
            )

            raw_channel = row["detected_channel"]
            channel = raw_channel.strip() if raw_channel else None

            is_ccdc = _to_bool(row["is_ccdc_event"])

            if subject not in grouped:
                channels: set[str] = set()
                if channel is not None:
                    channels.add(channel)
                grouped[subject] = (channels, is_ccdc)
            else:
                channels, prev_is_ccdc = grouped[subject]
                if channel is not None:
                    channels.add(channel)
                grouped[subject] = (channels, prev_is_ccdc or is_ccdc)

    results_list: list[Result] = [
        Result(
            subject=s,
            detected_channels=frozenset(channels),
            is_ccdc_event=is_ccdc,
        )
        for s, (channels, is_ccdc) in grouped.items()
    ]

    if k is not None and k > 0 and k < len(results_list):
        if random_state is not None:
            random.seed(random_state)
        results_list = random.sample(results_list, k)

    return set(results_list)


def _to_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    return s in {"1", "true", "t", "yes", "y"}