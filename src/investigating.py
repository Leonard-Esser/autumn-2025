import logging
from collections.abc import Callable

import pygit2
from typing import Any, Iterable

import config
import memory
from classifier import Classifier
from decorators import delete_sooner_or_later
from diffing import flatten, get_diff, get_patch, group_lines_by_origin
from model import CCDCEvent, Event, EventKey


classifier = Classifier()

logger = logging.getLogger(__name__)


@delete_sooner_or_later 
def naysayer(
    commit: pygit2.Commit,
    event_key: EventKey
) -> Event | CCDCEvent:
    if config.LOOK_FOR_BIGGEST_CHUNK:
        patch = get_patch(
            get_diff(
                commit,
                config.CONTEXT_LINES,
                True
            ),
            event_key.get_path
        )
        for hunk in patch.hunks:
            look_for_biggest_chunk(
                group_lines_by_origin(hunk),
                _let_classifier_count_tokens
            )
    return Event(event_key)


def _let_classifier_count_tokens(
    lines: Iterable[str]
) -> int:
    return classifier.count_tokens(flatten(lines))


def look_for_biggest_chunk(
    grouped_lines: dict[Any, Iterable[str]],
    take_measurements: Callable[[Iterable[str]], int]
):
    for key, chunk in grouped_lines.items():
        score = take_measurements(chunk)
        if not memory.biggest_chunk:
            memory.biggest_chunk = chunk
            memory.size_of_biggest_chunk = score
            continue
        if not memory.size_of_biggest_chunk:
            memory.size_of_biggest_chunk = take_measurements(memory.biggest_chunk)
        if score > memory.size_of_biggest_chunk:
            memory.biggest_chunk = chunk
            memory.size_of_biggest_chunk = score


def log_biggest_chunk():
    if memory.biggest_chunk:
        tc = _let_classifier_count_tokens(
            memory.biggest_chunk
        )
        logger.info(f"With {tc} tokens, this is the biggest chunk:\n{flatten(memory.biggest_chunk)}")