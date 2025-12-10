import pygit2
from transformers import pipeline

import labels
from decorators import delete_sooner_or_later
from diffing import flatten, get_changes
from model import CCDCEvent, Event, EventKey, TypeOfChange


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


@delete_sooner_or_later
def classifier_pipeline_callable(
    event_key: EventKey,
    patch: pygit2.Patch
) -> Event | CCDCEvent:
    pass


@delete_sooner_or_later
def naysayer(
    event_key: EventKey,
    patch: pygit2.Patch
) -> Event | CCDCEvent:
    return Event(event_key)


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


def _is_ccdc_event(text: str) -> bool:
    if not text or not text.strip():
        return False
    
    result = classifier(text, labels.LABELS_IDENTIFYING_CCDC_EVENT, multi_label=True)
    for label, score in zip(result["labels"], result["scores"]):
        if label in labels.LABELS_REPRESENTING_CCDC_EVENT and score > 0.75:
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