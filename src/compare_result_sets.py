from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from domain_model import Result, Subject


@dataclass(frozen=True, slots=True)
class ComparisonReport:
    # Sizes
    expected_count: int
    actual_count: int
    intersection_count: int

    # Match / mismatch counts (by Subject key)
    identical_count: int
    differing_count: int
    missing_subjects: frozenset[Subject]
    unexpected_subjects: frozenset[Subject]

    # Percentages (0..100)
    identical_pct_of_expected: float
    differing_pct_of_expected: float
    missing_pct_of_expected: float

    identical_pct_of_intersection: float
    differing_pct_of_intersection: float

    # is_ccdc_event confusion (only for Subjects present in both sets)
    ccdc_false_negatives: frozenset[Subject]
    ccdc_false_positives: frozenset[Subject]

    # Channel deltas (only for Subjects present in both sets)
    # per subject: which expected channels were missed, and which extra channels were predicted
    channels_missed_by_subject: dict[Subject, frozenset[str]] = field(default_factory=dict)
    channels_falsely_added_by_subject: dict[Subject, frozenset[str]] = field(default_factory=dict)

    # Aggregate channel deltas
    channels_missed_counts: dict[str, int] = field(default_factory=dict)
    channels_falsely_added_counts: dict[str, int] = field(default_factory=dict)

    # Full per-subject diffs (only for differing subjects in intersection)
    per_subject_diff: dict[Subject, dict[str, object]] = field(default_factory=dict)


def compare_result_sets(
    *,
    expected: set[Result],
    actual: set[Result],
) -> ComparisonReport:
    """
    Compares two sets of Result and computes a delta report.

    Assumptions:
    - Each Subject appears at most once in each set. (If not, raises ValueError.)
    - Comparison is keyed by Subject.
    - For subjects present in both sets, "identical" means:
        expected.is_ccdc_event == actual.is_ccdc_event
        AND expected.detected_channels == actual.detected_channels
    """

    def _index_by_subject(results: Iterable[Result]) -> dict[Subject, Result]:
        index: dict[Subject, Result] = {}
        for r in results:
            if r.subject in index:
                raise ValueError(
                    "Duplicate Subject detected in a Result set. "
                    f"Subject={r.subject!r}"
                )
            index[r.subject] = r
        return index

    exp = _index_by_subject(expected)
    act = _index_by_subject(actual)

    exp_subjects = set(exp.keys())
    act_subjects = set(act.keys())
    intersection = exp_subjects & act_subjects

    missing_subjects = frozenset(exp_subjects - act_subjects)
    unexpected_subjects = frozenset(act_subjects - exp_subjects)

    identical_count = 0
    differing_count = 0

    ccdc_fn: set[Subject] = set()
    ccdc_fp: set[Subject] = set()

    channels_missed_by_subject: dict[Subject, frozenset[str]] = {}
    channels_falsely_added_by_subject: dict[Subject, frozenset[str]] = {}

    channels_missed_counts: dict[str, int] = {}
    channels_falsely_added_counts: dict[str, int] = {}

    per_subject_diff: dict[Subject, dict[str, object]] = {}

    for s in intersection:
        e = exp[s]
        a = act[s]

        same_ccdc = (e.is_ccdc_event == a.is_ccdc_event)
        same_channels = (e.detected_channels == a.detected_channels)

        if same_ccdc and same_channels:
            identical_count += 1
            continue

        differing_count += 1

        # ccdc confusion (only where expected/actual differ)
        if e.is_ccdc_event and not a.is_ccdc_event:
            ccdc_fn.add(s)
        elif not e.is_ccdc_event and a.is_ccdc_event:
            ccdc_fp.add(s)

        # channel deltas
        missed = frozenset(e.detected_channels - a.detected_channels)
        falsely_added = frozenset(a.detected_channels - e.detected_channels)

        if missed:
            channels_missed_by_subject[s] = missed
            for ch in missed:
                channels_missed_counts[ch] = channels_missed_counts.get(ch, 0) + 1

        if falsely_added:
            channels_falsely_added_by_subject[s] = falsely_added
            for ch in falsely_added:
                channels_falsely_added_counts[ch] = channels_falsely_added_counts.get(ch, 0) + 1

        per_subject_diff[s] = {
            "expected_is_ccdc_event": e.is_ccdc_event,
            "actual_is_ccdc_event": a.is_ccdc_event,
            "expected_channels": sorted(e.detected_channels),
            "actual_channels": sorted(a.detected_channels),
            "missed_channels": sorted(missed),
            "falsely_added_channels": sorted(falsely_added),
        }

    expected_count = len(exp_subjects)
    actual_count = len(act_subjects)
    intersection_count = len(intersection)

    def _pct(n: int, d: int) -> float:
        return 0.0 if d == 0 else (n / d) * 100.0

    # % based on expected set size (nice when "expected" is the benchmark)
    identical_pct_of_expected = _pct(identical_count, expected_count)
    differing_pct_of_expected = _pct(differing_count, expected_count)
    missing_pct_of_expected = _pct(len(missing_subjects), expected_count)

    # % based on overlap only (nice when actual has extras)
    identical_pct_of_intersection = _pct(identical_count, intersection_count)
    differing_pct_of_intersection = _pct(differing_count, intersection_count)

    return ComparisonReport(
        expected_count=expected_count,
        actual_count=actual_count,
        intersection_count=intersection_count,
        identical_count=identical_count,
        differing_count=differing_count,
        missing_subjects=missing_subjects,
        unexpected_subjects=unexpected_subjects,
        identical_pct_of_expected=identical_pct_of_expected,
        differing_pct_of_expected=differing_pct_of_expected,
        missing_pct_of_expected=missing_pct_of_expected,
        identical_pct_of_intersection=identical_pct_of_intersection,
        differing_pct_of_intersection=differing_pct_of_intersection,
        ccdc_false_negatives=frozenset(ccdc_fn),
        ccdc_false_positives=frozenset(ccdc_fp),
        channels_missed_by_subject=channels_missed_by_subject,
        channels_falsely_added_by_subject=channels_falsely_added_by_subject,
        channels_missed_counts=dict(
            sorted(channels_missed_counts.items(),
            key=lambda kv: (-kv[1], kv[0]))
        ),
        channels_falsely_added_counts=dict(
            sorted(channels_falsely_added_counts.items(),
            key=lambda kv: (-kv[1], kv[0]))
        ),
        per_subject_diff=per_subject_diff,
    )


def render_report(report: ComparisonReport) -> str:
    lines: list[str] = []
    line = "-" * 80

    def add(s: str = "") -> None:
        lines.append(s)

    add(line)
    add("RESULT SET COMPARISON REPORT")
    add(line)

    # --- Sizes ---
    add("Sizes")
    add(f"  Expected results : {report.expected_count}")
    add(f"  Actual results   : {report.actual_count}")
    add(f"  Intersection     : {report.intersection_count}")
    add()

    # --- Overall quality ---
    add("Overall match quality")
    add(
        f"  Identical (of expected)   : "
        f"{report.identical_count} "
        f"({report.identical_pct_of_expected:.2f}%)"
    )
    add(
        f"  Differing (of expected)   : "
        f"{report.differing_count} "
        f"({report.differing_pct_of_expected:.2f}%)"
    )
    add(
        f"  Missing (of expected)     : "
        f"{len(report.missing_subjects)} "
        f"({report.missing_pct_of_expected:.2f}%)"
    )
    add()

    add(
        f"  Identical (of intersection): "
        f"{report.identical_pct_of_intersection:.2f}%"
    )
    add(
        f"  Differing (of intersection): "
        f"{report.differing_pct_of_intersection:.2f}%"
    )
    add()

    # --- Missing / unexpected ---
    if report.missing_subjects:
        add("Missing Subjects (expected but not produced)")
        for s in sorted(
            report.missing_subjects,
            key=lambda s: (s.full_name_of_repo, s.path)
        ):
            add(f"  - {s.full_name_of_repo} @ {s.commit_sha} / {s.path}")
        add()

    if report.unexpected_subjects:
        add("Unexpected Subjects (produced but not expected)")
        for s in sorted(
            report.unexpected_subjects,
            key=lambda s: (s.full_name_of_repo, s.path)
        ):
            add(f"  - {s.full_name_of_repo} @ {s.commit_sha} / {s.path}")
        add()

    # --- CCDC confusion ---
    add("CCDC event classification")
    add(f"  False negatives : {len(report.ccdc_false_negatives)}")
    add(f"  False positives : {len(report.ccdc_false_positives)}")

    if report.ccdc_false_negatives:
        add("  FN Subjects:")
        for s in sorted(
            report.ccdc_false_negatives,
            key=lambda s: (s.full_name_of_repo, s.commit_sha, s.path)
        ):
            add(f"    - {s.full_name_of_repo} / {s.commit_sha} / {s.path}")

    if report.ccdc_false_positives:
        add("  FP Subjects:")
        for s in sorted(
            report.ccdc_false_positives,
            key=lambda s: (s.full_name_of_repo, s.commit_sha, s.path)
        ):
            add(f"    - {s.full_name_of_repo} / {s.commit_sha} / {s.path}")

    add()

    # --- Channel errors (aggregate) ---
    add("Channel detection errors (aggregate)")
    if report.channels_missed_counts:
        add("  Missed channels:")
        for ch, cnt in report.channels_missed_counts.items():
            add(f"    - {ch}: {cnt}")
    else:
        add("  Missed channels: none")

    if report.channels_falsely_added_counts:
        add("  Falsely added channels:")
        for ch, cnt in report.channels_falsely_added_counts.items():
            add(f"    - {ch}: {cnt}")
    else:
        add("  Falsely added channels: none")

    add()

    # --- Detailed diffs ---
    if report.per_subject_diff:
        add("Detailed per-subject differences")
        for s, diff in report.per_subject_diff.items():
            add(line)
            add(f"{s.full_name_of_repo} @ {s.commit_sha}")
            add(f"Path: {s.path}")
            add(
                f"  is_ccdc_event: "
                f"expected={diff['expected_is_ccdc_event']} | "
                f"actual={diff['actual_is_ccdc_event']}"
            )

            if diff["missed_channels"]:
                add(f"  Missed channels        : {', '.join(diff['missed_channels'])}")
            if diff["falsely_added_channels"]:
                add(f"  Falsely added channels : {', '.join(diff['falsely_added_channels'])}")

        add(line)

    add("End of report")
    add(line)

    return "\n".join(lines)


def print_report(report: ComparisonReport) -> None:
    print(render_report(report))


def write_report_to_file(
    report: ComparisonReport,
    path: Path,
    *,
    encoding: str = "utf-8",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(report), encoding=encoding)