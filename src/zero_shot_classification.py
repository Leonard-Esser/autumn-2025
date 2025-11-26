from transformers import pipeline

from model import EventWhereCommunicationChannelDocumentationHasChanged, Event


classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

top_label = "documentation of communication channels"

candidate_labels = [
    top_label,
    "project description",
    "technical information",
    "user guide",
    "other",
]


def classify(
    repo: str,
    commit: str,
    path: str,
    flattened_changes: str
) -> EventWhereCommunicationChannelDocumentationHasChanged | Event:
    if is_ccd_event(flattened_changes):
        return EventWhereCommunicationChannelDocumentationHasChanged(
            repo,
            commit,
            path,
        )
    
    return Event(repo, commit, path)


def is_ccd_event(text: str) -> bool:
    if not text or not text.strip():
        return False
    result = classifier(text, candidate_labels)
    score = result["scores"][0]
    return result["labels"][0] is top_label and score > 0.50