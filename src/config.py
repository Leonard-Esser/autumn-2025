from labels import TaskMode


# section: program behavior
RETURNS_CACHED_DATA_IF_ANY = True
UPDATES_CACHE = True
CANNOT_DETECT_ANYTHING = False
IS_NAYSAYER = False
DELETES_GIT_DIR_IMMEDIATELY = True
# end of section

# section: diffing options
ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 0
FINDS_SIMILAR = False
# end of section

# section: RE the Zero-shot classifier via NLI
# The model id of a predefined tokenizer hosted inside a model repo on huggingface.co.
MODEL_ID = "facebook/bart-large-mnli"
# Maximum allowed number of tokens for a single (premise, hypothesis) pair.
TOKEN_LIMIT = 256
TASK_MODE: TaskMode = TaskMode.TOPIC
TRIES_TO_CLASSIFY_FLATTENED_HUNK = False
RETURNS_ASAP = True
# end of section

# section: logging
LOGS_PROGRESS = True
LOGS_SCORES = False
LOGS_EACH_PARTIAL_RESULT_CREATED = False
# end of section

# section: manual verification
RANDOM_STATE = 42
NUMBER_OF_POSITIVE_EVENTS_TO_DRAW = 10
NUMBER_OF_NEGATIVE_EVENTS_TO_DRAW = 10
# end of section