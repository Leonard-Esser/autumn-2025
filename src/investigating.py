from collections.abc import Callable

import pygit2
from typing import Any, Iterable

import config
import memory
from decorators import delete_sooner_or_later
from diffing import flatten, get_diff, get_patch, group_lines_by_origin
from model import CCDCEvent, Event, EventKey


@delete_sooner_or_later 
def naysayer(
    commit: pygit2.Commit,
    event_key: EventKey
) -> Event | CCDCEvent:
    if config.REMEMBER_THE_BIGGEST_CHUNK:
        patch = get_patch(
            get_diff(
                commit,
                config.CONTEXT_LINES,
                True
            ),
            event_key.get_path
        )
        for hunk in patch.hunks:
            look_for_the_biggest_chunk_yet(
                group_lines_by_origin(hunk),
                _take_measurements
            )
    return Event(event_key)


def _take_measurements(
    lines: Iterable[str]
) -> int:
    return len(flatten(lines))


def look_for_the_biggest_chunk_yet(
    grouped_lines: dict[Any, Iterable[str]],
    take_measurements: Callable[[Iterable[str]], int]
):
    for key, chunk in grouped_lines.items():
        if not memory.the_biggest_chunk_yet:
            memory.the_biggest_chunk_yet = chunk
            continue
        if take_measurements(chunk) > take_measurements(memory.the_biggest_chunk_yet):
            memory.the_biggest_chunk_yet = chunk