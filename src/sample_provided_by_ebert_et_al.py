import csv
import random
from pathlib import Path
from urllib.parse import urlparse

import subjects_config
from auth import get_github
from calling_github import name_check
from export import export_set_of_names
from get_root import get_root
from play_sound import play_sound

root: Path = get_root()

base_path: Path = root / "data" / "samples" / "ebert_et_al_2022"
path_to_original_sample: Path = base_path / "sample_1000.csv"
path_to_updated_sample: Path = base_path / "sample_1000_updated.csv"


def draw_repos(
    *,
    k: int | None = None,
    random_state: int | None = None,
) -> set[str]:
    population = sorted(_full_name_of_each_repo())
    if not population:
        return set()
    if k is not None and k > 0:
        k = min(k, len(population))
        if random_state is not None:
            random.seed(random_state)
        return set(random.sample(population, k))
    return set(population)


def _full_name_of_each_repo(
    *,
    path: Path | None = None,
    original_format: bool = False,
) -> set[str]:
    if path is not None:
        results: set[str] = set()
        with path.open("r", encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None) # skip header
            for row in reader:
                if not row:
                    continue
                if original_format:
                    url = row[1]
                    parsed = urlparse(url)
                    parts = parsed.path.strip("/").split("/")
                    if len(parts) >= 2:
                        full_name = f"{parts[-2]}/{parts[-1]}"
                        results.add(full_name)
                else:
                    results.add(row[0])
        return results
    
    if not path_to_updated_sample.exists():
        return _fix_sample()
    
    return _full_name_of_each_repo(
        path=path_to_updated_sample
    )


def _fix_sample() -> set[str]:
    repos: set[str] = set()
    gh = get_github()
    for full_name_of_repo in _full_name_of_each_repo(
        path=path_to_original_sample,
        original_format=True,
    ):
        repos.add(
            name_check(
                full_name_of_repo,
                gh=gh,
                swallows_archived_repos=subjects_config.EXCLUDES_RETIRED_REPOS,
            )
        )
    if repos:
        export_set_of_names(
            repos,
            csv_path=path_to_updated_sample,
            col_name="full_name_of_repo"
        )
    return repos


if __name__ == "__main__":
    _fix_sample()
    play_sound()