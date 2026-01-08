from github import Commit, Repository
import pandas as pd


def create_df_for_repo(repo: Repository) -> pd.DataFrame:
    row = {
        # Identity
        "ID": repo.id,
        "Full Name": repo.full_name,

        # URLs
        "Homepage": repo.homepage,
        "Clone URL": repo.clone_url,
        "Git URL": repo.git_url,
        "Teams URL": repo.teams_url,

        # Time
        "Created At": repo.created_at,
        "Pushed At": repo.pushed_at,
        "Updated At": repo.updated_at,

        # Features
        "Has Discussions": repo.has_discussions,
        "Has Issues": repo.has_issues,
        "Has Pages": repo.has_pages,
        "Has Projects": repo.has_projects,
        "Has Wiki": repo.has_wiki,

        # Counts
        "Forks Count": repo.forks_count,
        "Open Issues Count": repo.open_issues_count,
        "Stargazers Count": repo.stargazers_count,
        "Subscribers Count": repo.subscribers_count,
        "Size": repo.size,
    }

    return create_single_row_df(row, "Repository")


def create_single_row_df(
    row: dict[str, any],
    column_name_prefix: str
) -> pd.DataFrame:
    row = {f"{column_name_prefix} {key}": value for key, value in row.items()}
    return pd.DataFrame([row])


def create_df_for_commits(commits: list[str]) -> pd.DataFrame:
    if not commits:
        return pd.DataFrame()
    
    frames = [create_df_for_commit(commit) for commit in commits]
    if not frames:
        return pd.DataFrame()
    
    return pd.concat(frames, ignore_index=True)



def create_df_for_commit(commit: Commit) -> pd.DataFrame:
    row = {
        "SHA": commit.sha,
        "URL": commit.url,
        "HTML URL": commit.html_url,
        "Date": commit.commit.committer.date,
    }
    
    return create_single_row_df(row, "Commit")