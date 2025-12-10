LABELS_REPRESENTING_CCDC_EVENT = [
    "communication channels",
    "github issues",
]

LABELS_IDENTIFYING_CCDC_EVENT = [
    *LABELS_REPRESENTING_CCDC_EVENT,
    "installation",
    "requirements"
    "usage",
    "examples"
    "contribution",
    "project description",
    "maintenance notes",
    "legal and licensing",
    "sponsors",
    "other",
]

LABELS_REPRESENTING_ADD = [
    "communication channel added",
]

LABELS_REPRESENTING_UPDATE = [
    "description modified",
]

LABELS_REPRESENTING_REMOVE = [
    "communication channel removed",
]

LABELS_IDENTIFYING_TYPES_OF_CHANGES = [
    *LABELS_REPRESENTING_ADD,
    *LABELS_REPRESENTING_UPDATE,
    *LABELS_REPRESENTING_REMOVE,
    "communication channel referenced by name",
]
