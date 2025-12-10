import pygit2
from transformers import pipeline

import config
import labels
from decorators import delete_sooner_or_later
from diffing import flatten, get_changes, get_changes_of_hunk, get_diff, get_patch
from model import CCDCEvent, Event, EventKey, TypeOfChange


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def classify_thoroughly(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    diff, diff_without_context = _get_diff_with_and_without_context(commit)
    
    def _get_patch_with_and_without_context() -> tuple[pygit2.Patch, pygit2.Patch]:
        path = event_key.get_path
        patch = get_patch(
            diff,
            path
        )
        patch_without_context = get_patch(
            diff_without_context,
            path
        )
        return (patch, patch_without_context)
    
    patch, patch_without_context = _get_patch_with_and_without_context()

    if not _is_ccdc_event_based_on_patch(patch_without_context):
        if config.CONTEXT_LINES <= 0 or not _is_ccdc_event_based_on_patch(patch):
            return Event(event_key)
    
    return CCDCEvent(event_key)


def _get_diff_with_and_without_context(
    commit: pygit2.Commit
) -> tuple[pygit2.Diff, pygit2.Diff]:
    if config.CONTEXT_LINES > 0:
        diff = get_diff(
            commit,
            config.CONTEXT_LINES,
            True
        )
        diff_without_context = get_diff(
            commit,
            0,
            True
        )
    else:
        diff = get_diff(
            commit,
            0,
            True
        )
        diff_without_context = diff
    
    return (diff, diff_without_context)


def _is_ccdc_event_based_on_patch(patch_to_investigate: pygit2.Patch) -> bool:
    for hunk in patch_to_investigate.hunks:
        flattened_changes = flatten(
            get_changes_of_hunk(hunk)
        )
        if _is_ccdc_event(flattened_changes):
            return True
    
    return False


def _is_ccdc_event(text: str) -> bool:
    if not text or not text.strip():
        return False
    
    result = classifier(text, labels.LABELS_IDENTIFYING_CCDC_EVENT, multi_label=True)
    for label, score in zip(result["labels"], result["scores"]):
        if label in labels.LABELS_REPRESENTING_CCDC_EVENT and score > 0.80:
            return True
    return False


def naysayer(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    return Event(event_key)


@delete_sooner_or_later
def classify(
    event_key: EventKey,
    patch: pygit2.Patch
) -> CCDCEvent | Event:
    flattened_changes = flatten(
        get_changes(patch)
    )
    
    if _is_ccdc_event(flattened_changes):
        return CCDCEvent(
            event_key,
            types_of_changes=_identify_types_of_changes(flattened_changes)
        )
    
    return Event(event_key)


def _identify_types_of_changes(text: str) -> set[TypeOfChange]:
    if not text or not text.strip():
        return set()
    
    result = classifier(text, labels.LABELS_IDENTIFYING_TYPES_OF_CHANGES, multi_label=True)
    types_of_changes = set()
    for label, score in zip(result["labels"], result["scores"]):
        if label in labels.LABELS_REPRESENTING_ADD and score > 0.55:
            types_of_changes.add(TypeOfChange.ADD)
        elif label in labels.LABELS_REPRESENTING_UPDATE and score > 0.55:
            types_of_changes.add(TypeOfChange.UPDATE)
        elif label in labels.LABELS_REPRESENTING_REMOVE and score > 0.55:
            types_of_changes.add(TypeOfChange.REMOVE)
    
    return types_of_changes