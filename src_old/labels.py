from enum import Enum
class TaskMode(Enum):
    TOPIC = 1
    INTENT = 2

HYPOTHESIS_TEMPLATES = {
    TaskMode.TOPIC: "This text is about {}.",
    TaskMode.INTENT: "The change {}.",
}

PROJECT_COMMUNICATION = {
    TaskMode.TOPIC: "project communication",
    TaskMode.INTENT: "modifies project communication documentation",
}

COMMUNICATION_CHANNEL_DOCUMENTATION = "communication channel documentation"

TOPICS_FOR_IDENTIFYING_CCDC_EVENT = [
    COMMUNICATION_CHANNEL_DOCUMENTATION,
    "a communication channel",
    "communication channels",
]

TOPICS = [
    PROJECT_COMMUNICATION[TaskMode.TOPIC],
    *TOPICS_FOR_IDENTIFYING_CCDC_EVENT,
]

INTENTIONS_FOR_IDENTIFYING_CCDC_EVENT = [
    "modifies information about a communication channel",
    "adds a communication channel to the documentation",
    "removes a communication channel from the documentation",
    "explains why and how to use a communication channel",
]

INTENTIONS = [
    PROJECT_COMMUNICATION[TaskMode.INTENT],
    *INTENTIONS_FOR_IDENTIFYING_CCDC_EVENT,
]

LABELS_REPRESENTING_ADD = [
    "added",
]

LABELS_REPRESENTING_UPDATE = [
    "updated",
    "updated regardings its documentation",
]

LABELS_REPRESENTING_REMOVE = [
    "removed",
]

LABELS_FOR_IDENTIFYING_TYPE_OF_CHANGE = [
    *LABELS_REPRESENTING_ADD,
    *LABELS_REPRESENTING_UPDATE,
    *LABELS_REPRESENTING_REMOVE,
]