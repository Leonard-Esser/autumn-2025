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
    "communication",
]

LABELS_IDENTIFYING_CCDC_EVENT = [
    *LABELS_REPRESENTING_CCDC_EVENT,
    "installation",
    "requirements"
    "usage",
    "examples",
    "project description",
    "maintenance notes",
    "legal",
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
