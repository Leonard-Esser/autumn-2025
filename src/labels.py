COMMUNICATION_CHANNELS = [
    "pull request",
    "fork",
    "ping",
    "wiki",
    "issues",
    "rss feed",
    "medium",
    "website",
    "blog",
    "gitter",
    "discord",
    "slack",
    "patreon",
    "zulip",
    "icq",
    "telegram",
    "irc",
    "forum",
    "stack overflow",
    "reddit",
    "meetup",
    "skype",
    "newsletter",
    "mailing list",
    "mail",
    "form",
    "google group",
    "youtube",
    "facebook",
    "twitter",
    "linkedin",
    "jira",
]

LABELS_REPRESENTING_CCDC_EVENT = [
    "communication channels",
    "a communication channel",
    "project communication",
]

LABELS_IDENTIFYING_CCDC_EVENT = [
    *LABELS_REPRESENTING_CCDC_EVENT,
    "installation",
    "requirements"
    "usage",
    "examples",
    "project description",
    "maintenance notes",
    "licensing",
    "sponsors",
    "copyright",
    "version management",
    "project history",
    "implementation details",
]

LABELS_REPRESENTING_ADD = [
    "communication channel addition",
]

LABELS_REPRESENTING_UPDATE = [
    "communication channel documentation update",
]

LABELS_REPRESENTING_REMOVE = [
    "communication channel removal",
]

LABELS_IDENTIFYING_TYPES_OF_CHANGES = [
    *LABELS_REPRESENTING_ADD,
    *LABELS_REPRESENTING_UPDATE,
    *LABELS_REPRESENTING_REMOVE,
]

from enum import Enum
class TaskMode(Enum):
    TOPIC = 1
    INTENT = 2

HYPOTHESIS_TEMPLATES = {
    TaskMode.TOPIC: "This text is about {}.",
    TaskMode.INTENT: "The change {}.",
}

PROJECT_COMMUNICATION_LABELS = {
    TaskMode.TOPIC: "project communication",
    TaskMode.INTENT: "modifies project communication documentation",
}

COMMUNICATION_CHANNEL_DOCUMENTATION = "communication channel documentation"

TOPICS_IDENTIFYING_CCDC_EVENTS = [
    COMMUNICATION_CHANNEL_DOCUMENTATION,
    "a communication channel",
    "communication channels",
]

TOPICS = [
    PROJECT_COMMUNICATION_LABELS[TaskMode.TOPIC],
    *TOPICS_IDENTIFYING_CCDC_EVENTS,
]

INTENTIONS_IDENTIFYING_CCDC_EVENTS = [
    "modifies information about a communication channel",
    "adds a communication channel to the documentation",
    "removes a communication channel from the documentation",
    "explains why and how to use a communication channel",
]

INTENTIONS = [
    PROJECT_COMMUNICATION_LABELS[TaskMode.INTENT],
    *INTENTIONS_IDENTIFYING_CCDC_EVENTS,
]
