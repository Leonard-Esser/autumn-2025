# section: program behavior
RETURNS_CACHED_DATA_IF_ANY = True
UPDATES_CACHE = True
CANNOT_DETECT_ANYTHING = True
IS_NAYSAYER = False
DELETES_GIT_DIR_IMMEDIATELY = False
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
TOKEN_LIMIT = 512
TRIES_TO_CLASSIFY_FLATTENED_HUNK = False
# end of section

# section: logging
LOGS_PROGRESS = True
LOGS_SCORES = False
LOGS_EACH_PARTIAL_RESULT_CREATED = False
# end of section

# section: output
PARTS_OF_BASE_OUTPUT_DIR = [
    "data",
    "output"
]
SUBJECTS_CSV = "subjects.csv"
REPOS_CSV = "all_repos.csv"
COMMITS_CSV = "commits.csv"
RESULTS_CSV = "results.csv"
# end of section