from collections.abc import Callable
from pathlib import Path

import pygit2

from analyze import analyze
from compare_result_sets import compare_result_sets, print_report, write_report_to_file
from data_access import get_test_results_dir, get_truth_dir
from dataframes import dataframe
from domain_model import Result, Subject
from draw_results_from_csv import draw_results_from_csv
from export import export_df


def test_each_truth_file(
    root: Path,
    *,
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool],
    logs_progress: bool,
    deletes_git_dir_immediately: bool,
    program_version: str,
    prints_report_too: bool = False,
) -> None:
    truth_dir = get_truth_dir(root)
    csv_paths = sorted(p for p in truth_dir.rglob("*.csv") if p.is_file())
    for path in csv_paths:
        test(
            root,
            expected=path,
            channel_detector=channel_detector,
            classifier=classifier,
            logs_progress=logs_progress,
            deletes_git_dir_immediately=deletes_git_dir_immediately,
            program_version=program_version,
            prints_report_too=prints_report_too,
        )


def test(
    root: Path,
    *,
    expected: Path,
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool],
    logs_progress: bool,
    deletes_git_dir_immediately: bool,
    program_version: str,
    actual: Path | None = None,
    prints_report_too: bool = False,
    overwrites_existing_results: bool = True,
) -> None:
    test: str = expected.stem
    test_results_dir = get_test_results_dir(
        root,
        test=test,
        program_version=program_version,
    )
    expected: set[Result] = draw_results_from_csv(expected)
    if actual is not None:
        actual = draw_results_from_csv(actual)
    else:
        file_name = f"results_{test}_{program_version}.csv"
        path = test_results_dir / file_name
        if not overwrites_existing_results and path.exists():
            actual = draw_results_from_csv(path)
        else:
            actual = analyze(
                {r.subject for r in expected},
                root=root,
                channel_detector=channel_detector,
                classifier=classifier,
                logs_progress=logs_progress,
                deletes_git_dir_immediately=deletes_git_dir_immediately,
            )
            export_df(
                dataframe(actual),
                file_name,
                test_results_dir,
            )
    
    report = compare_result_sets(
        expected=expected,
        actual=actual,
    )
    path_to_report = test_results_dir / f"test_report_{test}_{program_version}.txt"
    write_report_to_file(report, path_to_report)
    if prints_report_too:
        print_report(report)