```
from pygithub import PaginatedList
from pygit2 import Repository, Commit

from helpers import get_new_df, append
import ccd_event


def get_df_with_ccd_events_mapped_to_commits(classifier, repo, commits, paths):
    df = get_new_df()
    for commit in commits:
        for path in paths:
            for cdd_event in find_ccd_events(classifier, repo, commit, path):
                append(df, repo, commit.sha, path, ccd_event)
    return df


def find_ccd_events(classifier, repo, commit, path):
    return classifier.classify(commit, path, repo)


def main()
    return "Hello from mining.py!"


if __name__ == "__main__":
    main()
```