from collections.abc import Iterable

from domain_model import PartialResult, Result


def aggregate(results: Iterable[PartialResult]) -> Result:
    results_list = list(results)
    if not results_list:
        raise ValueError("aggregate() requires at least one Result.")
    subject = results_list[0].subject
    if any(r.subject != subject for r in results_list[1:]):
        raise ValueError("All Result objects must have the same subject/key.")
    all_channels = frozenset().union(*(r.detected_channels for r in results_list))
    is_ccdc = any_result_is_ccdc_event(results)
    return Result(subject=subject, detected_channels=all_channels, is_ccdc_event=is_ccdc)


def any_result_is_ccdc_event(results: Iterable[PartialResult]) -> bool:
    results_list = list(results)
    return any(r.is_ccdc_event for r in results_list)