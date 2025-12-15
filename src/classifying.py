import logging

import pygit2
from transformers import pipeline
from typing import Iterable

import config
import labels
from classifier import Classifier
from diffing import flatten, get_changes_of_hunk, get_diff, get_flattened_changes_grouped_by_line_origin, get_patch
from labels import TaskMode
from model import CCDCEvent, Event, EventKey, TypeOfChange


logger = logging.getLogger(__name__)


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
classifier = Classifier()


def classify_commit(
    commit: pygit2.Commit,
    event_key: EventKey
) -> Event | CCDCEvent:
    diff = get_diff(
        commit,
        config.CONTEXT_LINES,
        True
    )
    patch = get_patch(
        diff,
        event_key.get_path
    )
    return _classify_patch(
        patch,
        event_key,
        classify_additions_and_deletions_separately=True
    )


def _classify_patch(
    patch: pygit2.Patch,
    event_key: EventKey,
    classify_additions_and_deletions_separately: bool
) -> Event | CCDCEvent:
    return _merge_ccdc_events(
        _get_ccdc_event_for_each_hunk(
            patch,
            event_key,
            classify_additions_and_deletions_separately
        ),
        event_key
    )


def _get_ccdc_event_for_each_hunk(
    patch: pygit2.Patch,
    event_key: EventKey,
    classify_additions_and_deletions_separately: bool
) -> list[CCDCEvent]:
    events = []
    for hunk in patch.hunks:
        events.append(
            _classify_hunk(
                hunk,
                event_key,
                classify_additions_and_deletions_separately,
            )
        )
    return [event for event in events if isinstance(event, CCDCEvent)]


def _merge_ccdc_events(
    events: Iterable[CCDCEvent],
    event_key: EventKey
) -> Event | CCDCEvent:
    if not events:
        return Event(event_key)
    
    types_of_change = set()
    for event in events:
        types_of_change |= set(event.get_types_of_change)
    return CCDCEvent(
        event_key,
        types_of_change
    )


def _classify_hunk(
    hunk: pygit2.DiffHunk,
    event_key: EventKey,
    classify_additions_and_deletions_separately: bool = False
) -> Event | CCDCEvent:
    if not classify_additions_and_deletions_separately:
        text = flatten(
            get_changes_of_hunk(hunk)
        )
        if not _text_hints_at_ccdc_event(
            text,
            TaskMode.INTENT
        ):
            return Event(event_key)
        
        return CCDCEvent(
            event_key,
            _identify_types_of_change(text) - _rule_out_illogical_types_of_change(hunk)
        )
    
    grouped_changes = get_flattened_changes_grouped_by_line_origin(hunk)
    origins = set(grouped_changes.keys())
    if "+" in origins and "-" in origins:
        return _classify_hunk(hunk, event_key)
    else:
        for origin in origins:
            if origin in ("+", "-"):
                if _text_hints_at_ccdc_event(grouped_changes[origin]):
                    types_of_change = [TypeOfChange.ADD]
                    if origin == "-":
                        types_of_change = [TypeOfChange.REMOVE]
                    return CCDCEvent(
                        event_key,
                        types_of_change
                    )
                else:
                    return Event(event_key)


def _rule_out_illogical_types_of_change(hunk: pygit2.DiffHunk,) -> set[TypeOfChange]:
    """Returns the types of change that are `impossible` or illogical based on the given DiffHunk."""

    # Collect the set of line origins in the patch: {'+', '-', ' '}
    line_origins = set()
    for line in hunk.lines:
        line_origins.add(line.origin)

    if not line_origins:
        return set(TypeOfChange)

    # Only additions
    if line_origins == {'+'}:
        return {TypeOfChange.UPDATE, TypeOfChange.REMOVE}

    # Only deletions
    if line_origins == {'-'}:
        return {TypeOfChange.ADD, TypeOfChange.UPDATE}

    return set()


def _text_hints_at_ccdc_event(
    text: str,
    task_mode: TaskMode = TaskMode.TOPIC
) -> bool:
    if not text or not text.strip():
        return False
    logger.info(text)
    
    lbls = labels.TOPICS
    if task_mode == TaskMode.INTENT:
        lbls = labels.INTENTIONS
    hypothesis = labels.HYPOTHESIS_TEMPLATES[task_mode]
    labels_and_their_scores = classifier.classify(
        text,
        lbls,
        hypothesis
    )
    logger.info(labels_and_their_scores)

    def _should_return_false_early() -> bool:
        project_communication_label = labels.PROJECT_COMMUNICATION[task_mode]
        if task_mode is TaskMode.INTENT:
            return labels_and_their_scores[project_communication_label] < 0.01
        if labels_and_their_scores[project_communication_label] >= 0.009:
            labels_and_their_scores.pop(project_communication_label)
            return False
        return labels_and_their_scores[labels.COMMUNICATION_CHANNEL_DOCUMENTATION] < 0.171
    
    if _should_return_false_early():
        return False
    
    for label, score in labels_and_their_scores.items():
        if score > 0.5:
            return True
    return False


def _identify_types_of_change(text: str) -> set[TypeOfChange]:
    if not text or not text.strip():
        return set()
    lbls = labels.LABELS_FOR_IDENTIFYING_TYPE_OF_CHANGE
    hypothesis = "At least one communication channel was {}."
    labels_and_their_scores = classifier.classify(
        text,
        lbls,
        hypothesis
    )
    logger.info(labels_and_their_scores)

    types_of_change = set()
    for label, score in labels_and_their_scores.items():
        if label in labels.LABELS_REPRESENTING_ADD and score > 0.50:
            types_of_change.add(TypeOfChange.ADD)
        elif label in labels.LABELS_REPRESENTING_UPDATE and score > 0.50:
            types_of_change.add(TypeOfChange.UPDATE)
        elif label in labels.LABELS_REPRESENTING_REMOVE and score > 0.50:
            types_of_change.add(TypeOfChange.REMOVE)
    
    return types_of_change


def naysayer(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    return Event(event_key)