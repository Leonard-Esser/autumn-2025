import pandas as pd
import pygit2
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import config
from classifying import classify, classify_thoroughly, naysayer
from decorators import stop_the_clock
from helpers import clone_if_necessary, get_version
from io_helpers import get_output_dir, export_df
from mining import get_ccd_events_of_single_commit
from model import CCDCEvent, convert_to_type_of_change, Event, EventKey


@stop_the_clock
def main():
    root = _get_root()
    version = get_version(root)
    print(f"Data will be saved to a directory named {version} within data/output/")
    
    if config.DO_NOT_CLASSIFY_AT_ALL:
        delta = _test_classifier(
            root,
            _get_the_truth(root),
            naysayer
        )
    else:
        delta = _test_classifier(
            root,
            _get_the_truth(root),
            classify_thoroughly
        )
    
    file_name = f"test_result_delta_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    export_df(
        delta,
        file_name,
        get_output_dir(root, config.NAME_OF_TEST_RESULTS_DIR, version=version)
    )


def _get_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_the_truth(root: Path):
    return _read_clean_csv(path=root / "data" / "labeled_events" / "labeled_events.csv")


def _read_clean_csv(path: str, required_columns: list[str] | None = None) -> pd.DataFrame:
    """
    Reads a CSV file into a pandas DataFrame and removes all rows where 
    any of the specified required columns contain missing or empty values.

    Parameters
    ----------
    path : str
        Path to the CSV file.
    required_columns : list[str] | None
        Columns that must contain values. If None, all columns are required.

    Returns
    -------
    pd.DataFrame
        A cleaned DataFrame containing only rows where all required columns 
        have non-null and non-empty values.
    """

    # Read CSV normally
    df = pd.read_csv(path)

    # Determine which columns must not contain empty values
    if required_columns is None:
        required_columns = df.columns.tolist()

    # Treat empty strings as NaN
    df = df.replace("", pd.NA)

    # Drop rows with missing values in required columns
    df = df.dropna(subset=required_columns)

    return df


mykey = tuple[str, str, str]


def _test_classifier(
    root: Path,
    truth: pd.DataFrame,
    classifier_pipeline: Callable[[EventKey, pygit2.Patch], CCDCEvent | Event],
) -> pd.DataFrame:
    key_cols: list[str] = ["Repository Full Name", "Commit SHA", "Path"]
    
    def _get_expected_results() -> dict[mykey, dict[str, Any]]:
        expected_results = {}
        for key, rows in truth.groupby(key_cols):
            full_name_of_repo, commit_sha, path = key
            affects_ccd_col = rows["Affects CCD"].dropna().unique()
            if len(affects_ccd_col) != 1:
                raise ValueError(
                    f"Expected exactly one 'Affects CCD' value per key, "
                    f"but found {affects_ccd_col} for "
                    f"{full_name_of_repo} @ {commit_sha} / {path}"
                )
            affects_ccd = int(affects_ccd_col[0])

            # Collect all distinct types of changes for this triple.
            # Assumption: a value of 0 is a sentinel meaning "no type of change".
            type_of_change_col = rows["Type of Change"].dropna().tolist()
            
            expected_types_of_changes = sorted(
                {
                    convert_to_type_of_change(t)
                    for t in type_of_change_col
                    if t not in (0, "0")
                },
                key=lambda x: x.name
            )

            expected_results[key] = {
                "Affects CCD": affects_ccd,
                "Types of Changes": expected_types_of_changes,
            }
        return expected_results
    
    repo_cache: dict[str, pygit2.Repository] = {}

    def _clone_if_necessary(
        full_name_of_repo: str
    ) -> pygit2.Repository:
        if not full_name_of_repo in repo_cache:
            repo_cache[full_name_of_repo] = clone_if_necessary(
                root,
                full_name_of_repo
            )
        
        return repo_cache[full_name_of_repo]
    
    commit_cache: dict[tuple[str, str], pygit2.Commit] = {}

    def _get_commit(
        full_name_of_repo: str,
        sha: str
    ) -> pygit2.Commit:
        key = (full_name_of_repo, sha)
        if key in commit_cache:
            return commit_cache[key]
        
        repo = _clone_if_necessary(full_name_of_repo)
        commit = repo.revparse_single(sha)
        commit_cache[key] = commit
        return commit
    
    def _get_actual_results() -> dict[mykey, dict[str, Any]]:
        actual_results = {}
        for _, row in truth[key_cols].drop_duplicates().iterrows():
            full_name_of_repo = str(row[key_cols[0]])
            commit_sha = str(row[key_cols[1]])
            path = str(row[key_cols[2]])
            key = (full_name_of_repo, commit_sha, path)
            commit = _get_commit(full_name_of_repo, commit_sha)
            events = get_ccd_events_of_single_commit(
                full_name_of_repo,
                commit,
                [path],
                classifier_pipeline
            )
            affects_ccd_col = events["Affects CCD"].dropna().unique()
            if len(affects_ccd_col) != 1:
                raise ValueError(
                    f"Classifier produced multiple 'Affects CCD' values for "
                    f"{full_name_of_repo} @ {commit_sha} / {path}: {affects_ccd_col}"
                )
            affects_ccd = int(affects_ccd_col[0])

            # Collect all distinct types of changes for this triple.
            # Assumption: a value of 0 is a sentinel meaning "no type of change".
            type_of_change_col = events["Type of Change"].dropna().tolist()
            actual_types_of_changes = sorted(
                {t for t in type_of_change_col if t not in (0, "0")},
                key=lambda x: x.name
            )

            actual_results[key] = {
                "Affects CCD": affects_ccd,
                "Types of Changes": actual_types_of_changes,
            }
        return actual_results

    def _get_delta_by_comparing_results(
        expected_results: dict[mykey, dict[str, Any]],
        actual_results: dict[mykey, dict[str, Any]]
    ) -> pd.DataFrame:
        error_rows = []
        for key, exp_res in expected_results.items():
            full_name_of_repo, commit_sha, path = key
            act_res = actual_results.get(key)
            
            exp_aff = exp_res["Affects CCD"]
            act_aff = act_res["Affects CCD"]
            exp_types = sorted(
                exp_res["Types of Changes"],
                key=lambda x: x.name
            )
            act_types = sorted(
                act_res["Types of Changes"],
                key=lambda x: x.name
            )

            # No error?
            if exp_aff == act_aff:
                if exp_aff == 0:
                    # Both say "does not affect CCD", and we ignore types of change.
                    continue

                # Both say "affects CCD" -> check types of change
                if set(exp_types) == set(act_types):
                    continue  # perfect match

                # Only types of change differ
                error_type = "Confusion"
            else:
                # Affects CCD mismatch
                if act_aff == 1 and exp_aff == 0:
                    error_type = "False Positive"
                elif act_aff == 0 and exp_aff == 1:
                    error_type = "False Negative"
                else:
                    # Should not really happen for binary labels, but handle gracefully.
                    error_type = "Unknown"

            error_rows.append(
                {
                    "Repository Full Name": full_name_of_repo,
                    "Commit SHA": commit_sha,
                    "Path": path,
                    "Expected Affects CCD": exp_aff,
                    "Actual Affects CCD": act_aff,
                    "Expected Types of Change": exp_types,
                    "Actual Types of Change": act_types,
                    "Error Type": error_type,
                }
            )
        
        if not error_rows:
            return pd.DataFrame()
        
        return pd.DataFrame(error_rows)
    
    return _get_delta_by_comparing_results(
        _get_expected_results(),
        _get_actual_results()
    )


if __name__ == "__main__":
    main()