```
import os

from pathlib import Path

from helpers import export, get_url, create_path, run_git_gc, delete_local_repo_clone
from sampling import get_sample
from calling_github import clone, get_commits
from mining import classify_commits
from investigation import analyze_data
import config


def main():
    sample = get_sample()
    export(sample)
    data = get_new_df()
    for id in sample:
        commits = get_commits(full_name=id, files=config.FILES_TO_BE_STUDIED, since=config.SINCE, until=config.UNTIL)
        export(commits)
        url = get_url(full_name=id)
        path = create_path(full_name=id)
        if os.path.exists(path):
            print(f"Not cloning because the path already exists.")
        else:
            repo = clone(url=url, path=path, depth=1)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")
        df = classify_commits(repo=repo, commits=relevant_commits)
        export(df)
        data = combine(df1=data, df2=df)
        delete_local_repo_clone(path=path)
    export(data)
    results = analyze_data(data=data)
    export(results)


if __name__ == "__main__":
    main()
```
