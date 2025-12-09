from transformers import pipeline

import labels
from model import CCDCEvent, Event, TypeOfChange


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def classify(
    repo: str,
    commit: str,
    path: str,
    flattened_changes: str,
    simply_create_bare_events: bool = False
) -> CCDCEvent | Event:
    if simply_create_bare_events:
        return Event(repo, commit, path)
    
    if _is_ccdc_event(flattened_changes):
        return CCDCEvent(
            repo,
            commit,
            path,
            types_of_changes=_identify_types_of_changes(flattened_changes)
        )
    
    return Event(repo, commit, path)


def _is_ccdc_event(text: str) -> bool:
    if not text or not text.strip():
        return False
    
    result = classifier(text, labels.LABELS_IDENTIFYING_CCDC_EVENT, multi_label=True)
    for label, score in zip(result["labels"], result["scores"]):
        if label in labels.LABELS_REPRESENTING_CCDC_EVENT and score > 0.55:
            return True
    return False


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