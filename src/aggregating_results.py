from collections.abc import Iterable

from model_new import Result


def aggregate_results(results: Iterable[Result]) -> Result:
    results_list = list(results)
    if not results_list:
        raise ValueError("aggregate_results() requires at least one Result.")
    subject = results_list[0].subject
    if any(r.subject != subject for r in results_list[1:]):
        raise ValueError("All Result objects must have the same subject/key.")
    all_channels = set().union(*(r.detected_channels for r in results_list))
    is_ccdc = any(r.is_ccdc_event for r in results_list)
    return Result(subject=subject, detected_channels=all_channels, is_ccdc_event=is_ccdc)