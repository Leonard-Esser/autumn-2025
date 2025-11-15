```
import os
import time

from pathlib import Path
from pygit2 import Repository
import pandas as pd

from decorators import timer
from sampling import get_sample
from helpers import *
from calling_github import get_github, get_repo, get_commits_dict_for_multiple_paths, clone
from mining import get_ccd_events_of_entire_repo, find_ccd_events
from investigation import analyze_data
import config


@timer
def main():
    sample = get_sample()
    export(sample)
    data = []
    for full_name in sample:
        github = get_github()
        repo = get_repo(github, full_name)
        commits_dict = get_commits_dict_for_multiple_paths(
            repo,
            config.PATHS_TO_CONSIDER,
            config.SINCE,
            config.UNTIL
        )
        export(sample)
        url = get_url(full_name)
        root = Path(__file__).resolve().parent.parent
        bare_clones_dir = make_directory_for_bare_clones(root)
        path = create_path_for_git_directory(parent_dir=bare_clones_dir, full_name_of_repo=full_name)
        if path.exists():
            print(f"Not cloning because the path already exists.")
        else:
            clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")
        repo = Repository(path)
        df = get_ccd_events_of_entire_repo(
            repo,
            commits_dict,
            get_finder(config.FINDER_TO_USE)
        ).assign(Repository=full_name)
        export(df)
        data.append(df)
        if config.DELETE_GIT_DIR_IMMEDIATELY:
            delete_git_dir(path)
    data = pd.concat(data, ignore_index=True)
    export(data)
    results = analyze_data(data)
    export(results)


if __name__ == "__main__":
    main()
```