import logging

import pygit2
from transformers import pipeline

import config
import labels
from classifier import Classifier
from decorators import delete_sooner_or_later
from diffing import flatten, get_changes, get_changes_of_hunk, get_diff, get_flattened_changes_grouped_by_line_origin, get_patch
from labels import TaskMode
from model import CCDCEvent, Event, EventKey, TypeOfChange


logger = logging.getLogger(__name__)


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
classifier = Classifier()


def classify_thoroughly(
    event_key: EventKey,
    commit: pygit2.Commit
) -> Event | CCDCEvent:
    logger.info(f"Classifying commit {commit.id}")
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
    is_ccdc_event =  _patch_is_ccdc_event(
        patch_without_context,
        classify_additions_and_deletions_separately=True
    )
    if is_ccdc_event:
        return CCDCEvent(event_key)
    
    return Event(event_key)


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


def _patch_is_ccdc_event(
    patch: pygit2.Patch,
    classify_additions_and_deletions_separately: bool
) -> bool:
    for hunk in patch.hunks:
        hunk_is_ccdc_event = _hunk_is_ccdc_event(
            hunk,
            classify_additions_and_deletions_separately
        )
        if hunk_is_ccdc_event:
            return True
    
    return False


def _hunk_is_ccdc_event(
    hunk: pygit2.DiffHunk,
    classify_additions_and_deletions_separately: bool
) -> bool:
    if not classify_additions_and_deletions_separately:
        return _hunk_as_a_whole_hints_at_ccdc_event(hunk)
    
    grouped_changes = get_flattened_changes_grouped_by_line_origin(hunk)
    origins = set(grouped_changes.keys())
    if "+" in origins and "-" in origins:
        return _hunk_as_a_whole_hints_at_ccdc_event(hunk)
    else:
        for origin in origins:
            if origin in ("+", "-"):
                return _text_hints_at_ccdc_event(grouped_changes[origin])
    
    return False


def _hunk_as_a_whole_hints_at_ccdc_event(
    hunk: pygit2.DiffHunk
):
    return _text_hints_at_ccdc_event(
        flatten(
            get_changes_of_hunk(hunk)
        ),
        TaskMode.INTENT
    )


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

    if not line_origins:
        return set(TypeOfChange)

    # Only additions
    if line_origins == {'+'}:
        return {TypeOfChange.UPDATE, TypeOfChange.REMOVE}

    # Only deletions
    if line_origins == {'-'}:
        return {TypeOfChange.ADD, TypeOfChange.UPDATE}

    return set()


def _identify_types_of_changes_based_on_patch(patch_to_investigate: pygit2.Patch) -> set[TypeOfChange]:
    types = set()
    for hunk in patch_to_investigate.hunks:
        flattened_changes = flatten(
            get_changes_of_hunk(hunk)
        )
        types = types | _identify_types_of_changes(flattened_changes)
    return types


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
        project_communication_label = labels.PROJECT_COMMUNICATION_LABELS[task_mode]
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