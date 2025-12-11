import logging

import pygit2
from transformers import pipeline

import config
import labels
from decorators import delete_sooner_or_later
from diffing import flatten, get_changes, get_changes_of_hunk, get_diff, get_patch
from model import CCDCEvent, Event, EventKey, TypeOfChange


logger = logging.getLogger(__name__)


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def classify_thoroughly(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    logger.info(f"Classifying commit {commit.short_id}")
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
        if not config.CONTEXT_LINES > 0 or not _is_ccdc_event_based_on_patch(patch):
            return Event(event_key)
    
    illogical_types_of_changes = _rule_out_illogical_types_of_changes(patch_without_context)
    types_of_changes = _identify_types_of_changes_based_on_patch(patch_without_context)
    types_of_changes -= illogical_types_of_changes
    
    return CCDCEvent(event_key, types_of_changes)


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


def _rule_out_illogical_types_of_changes(patch_to_investigate: pygit2.Patch) -> set[TypeOfChange]:
    """Returns the types of changes that are `impossible` or illogical based on the patch."""

    def _get_line_origin_set() -> set:
        line_origin_set = set()
        for hunk in patch_to_investigate.hunks:
            for line in hunk.lines:
                line_origin_set.add(line.origin)
        return line_origin_set

    # Collect the set of line origins in the patch: {'+', '-', ' '}
    line_origins = _get_line_origin_set()

    # No line origins → no meaningful changes → rule out all types.
    if not line_origins:
        return set(TypeOfChange)

    # Only additions
    if line_origins == {'+'}:
        return {TypeOfChange.UPDATE, TypeOfChange.REMOVE}

    # Only deletions
    if line_origins == {'-'}:
        return {TypeOfChange.ADD, TypeOfChange.UPDATE}

    # Mixed changes → nothing can be ruled out
    return set()


def _identify_types_of_changes_based_on_patch(patch_to_investigate: pygit2.Patch) -> set[TypeOfChange]:
    types = set()
    for hunk in patch_to_investigate.hunks:
        flattened_changes = flatten(
            get_changes_of_hunk(hunk)
        )
        types = types | _identify_types_of_changes(flattened_changes)
    return types


def _is_ccdc_event(text: str) -> bool:
    if not text or not text.strip():
        return False
    
    result = classifier(text, labels.LABELS_IDENTIFYING_CCDC_EVENT, multi_label=False)
    logger.info(result)
    labels_and_their_scores = zip(result["labels"], result["scores"])
    tendency = False
    for label, score in labels_and_their_scores:
        if label in labels.LABELS_REPRESENTING_CCDC_EVENT:
            if score > 0.50:
                return True
            elif score > 0.30 and not tendency:
                tendency = True
    result = classifier(text, labels.COMMUNICATION_CHANNELS, multi_label=True)
    logger.info(result)
    labels_and_their_scores = zip(result["labels"], result["scores"])
    for label, score in labels_and_their_scores:
        if score > 0.90 or (tendency and score > 0.50):
            return True
    return False


def _identify_types_of_changes(text: str) -> set[TypeOfChange]:
    if not text or not text.strip():
        return set()
    
    result = classifier(text, labels.LABELS_IDENTIFYING_TYPES_OF_CHANGES, multi_label=True)
    types_of_changes = set()
    for label, score in zip(result["labels"], result["scores"]):
        if label in labels.LABELS_REPRESENTING_ADD and score > 0.50:
            types_of_changes.add(TypeOfChange.ADD)
        elif label in labels.LABELS_REPRESENTING_UPDATE and score > 0.50:
            types_of_changes.add(TypeOfChange.UPDATE)
        elif label in labels.LABELS_REPRESENTING_REMOVE and score > 0.50:
            types_of_changes.add(TypeOfChange.REMOVE)
    
    return types_of_changes


def naysayer(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    return Event(event_key)