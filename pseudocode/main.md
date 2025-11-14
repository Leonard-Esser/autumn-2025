```
def main():
    files_to_be_studied = config.FILE_TO_BE_STUDIED
    sample = get_sample()
    export(sample)
    data = []
    for full_name in sample:
        commits = get_commits(
            full_name,
            files_to_be_studied,
            config.SINCE,
            config.UNTIL
        )
        export(commits)
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
        df = get_ccd_events(
            repo,
            full_name,
            commits,
            file_to_be_studied,
            get_classifier(config.CLASSIFIER)
        )
        export(df)
        data.append(df)
        if config.DELETE_GIT_DIR_IMMEDIATELY:
            delete_git_dir(path)
    data = pd.concat(data, ignore_index=True)
    export(data)
    results = analyze_data(data=data)
    export(results)
```