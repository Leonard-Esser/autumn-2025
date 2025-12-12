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
class HypothesisTemplateIdentifier(Enum):
    TOPIC = 1
    INTENT = 2

HYPOTHESIS_TEMPLATES = {
    HypothesisTemplateIdentifier.TOPIC: "This change is about {}.",
    HypothesisTemplateIdentifier.INTENT: "The change {}.",
}

TOPICS_IDENTIFYING_CCDC_EVENTS = [
    "communication",
    "communication channels",
    "communication channel documentation",
    "project communication",
    "how to communicate",
    "where to communicate",
    "exchanging information",
]

TOPICS = [
    *TOPICS_IDENTIFYING_CCDC_EVENTS,
]

INTENTIONS_IDENTIFYING_CCDC_EVENTS = [
    "adds a communication channel to the documentation",
    "updates the documentation of a communication channel",
    "removes a communication channel from the documentation",
    "updates information regarding communication",
    "explains why and how to use a communication channel",
]

INTENTIONS = [
    *INTENTIONS_IDENTIFYING_CCDC_EVENTS,
]
