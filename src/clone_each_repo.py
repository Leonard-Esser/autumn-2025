from pathlib import Path

from decorators import stop_the_clock
from get_repo import get_repo
from get_root import get_root
from play_sound import play_sound
from sample_provided_by_ebert_et_al import draw_repos

root: Path = get_root()


@stop_the_clock
def _clone_each_repo() -> None:
    for full_name_of_repo in draw_repos():
        get_repo(full_name_of_repo=full_name_of_repo, root=root)


if __name__ == "__main__":
    _clone_each_repo()
    play_sound()