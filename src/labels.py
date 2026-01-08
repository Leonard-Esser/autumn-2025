from enum import Enum


class TaskMode(Enum):
    TOPIC = 1
    INTENT = 2

HYPOTHESIS_TEMPLATES: dict[TaskMode, str] = {
    TaskMode.TOPIC: "This text is about {}.",
    TaskMode.INTENT: "The change {}.",
}

PROJECT_COMMUNICATION: dict[TaskMode, str] = {
    TaskMode.TOPIC: "project communication",
    TaskMode.INTENT: "modifies project communication documentation",
}

COMMUNICATION_CHANNEL_DOCUMENTATION: str = "communication channel documentation"

TOPICS_FOR_IDENTIFYING_CCDC_EVENT: list[str] = [
    COMMUNICATION_CHANNEL_DOCUMENTATION,
    "a communication channel",
    "communication channels",
]

TOPICS: list[str] = [
    PROJECT_COMMUNICATION[TaskMode.TOPIC],
    *TOPICS_FOR_IDENTIFYING_CCDC_EVENT,
]

INTENTIONS_FOR_IDENTIFYING_CCDC_EVENT: list[str] = [
    "modifies information about a communication channel",
    "adds a communication channel to the documentation",
    "removes a communication channel from the documentation",
    "explains why and how to use a communication channel",
]

INTENTIONS: list[str] = [
    PROJECT_COMMUNICATION[TaskMode.INTENT],
    *INTENTIONS_FOR_IDENTIFYING_CCDC_EVENT,
]

LABELS: dict[TaskMode, list[str]] = {
    TaskMode.TOPIC: TOPICS,
    TaskMode.INTENT: INTENTIONS,
}