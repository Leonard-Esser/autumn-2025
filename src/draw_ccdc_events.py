import random
from collections import defaultdict
from typing import Iterable

from domain_model import Result, Subject


def draw_ccdc_events(
    *,
    results: Iterable[Result],
    k: int,
    logical_negation: bool = False,
    random_state: int | None = None,
) -> set[Result]:
    if k <= 0:
        return set()
    # group Result objects by Subject (only for subjects matching the CCDC criterion)
    grouped: dict[Subject, list[Result]] = defaultdict(list)
    for r in results:
        # if logical_negation=True -> select non-CCDC events (is_ccdc_event == False)
        # else -> select CCDC events (is_ccdc_event == True)
        matches = (not r.is_ccdc_event) if logical_negation else r.is_ccdc_event
        if matches:
            grouped[r.subject].append(r)
    subjects = list(grouped.keys())
    if not subjects:
        return set()
    k = min(k, len(subjects))
    if random_state is not None:
        random.seed(random_state)
    drawn_subjects = random.sample(subjects, k)
    # return all Result objects belonging to the drawn subjects
    drawn_results: set[Result] = set()
    for s in drawn_subjects:
        drawn_results.update(grouped[s])
    return drawn_results