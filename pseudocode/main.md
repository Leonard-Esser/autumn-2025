```
from auth import authenticate
from sampling import get_sample
from util import export, get_url, create_path, combine
from calling_github import clone, get_commits
from mining import classify_commits
from investigation import analyze_data
import config

def main():
    authenticate()
    sample = get_sample(size=config.SAMPLE_SIZE)
    export(sample)
    data = get_new_df()
    for id in sample:
        url = get_url(id=id)
        path = create_path(id=id)
        repo = clone(url=url, path=path, bare=True, run_git_gc=True)
        relevant_commits = get_commits(url=url, files=config.FILES_TO_BE_STUDIED)
        export(relevant_commits)
        df = classify_commits(repo=repo, commits=relevant_commits)
        export(df)
        data = combine(df1=data, df2=df)
    export(data)
    results = analyze_data(data=data)
    export(results)
```
