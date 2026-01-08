import re
import unicodedata
from difflib import SequenceMatcher

import pygit2

import communication_channels
from domain_model import Subject

# ---------------------------------------------------------------------------
# Tunables (recall-first defaults)
# ---------------------------------------------------------------------------

# For multi-word phrases and longer keywords.
FUZZY_THRESHOLD_PHRASE = 84

# For very short tokens like "pr" / "irc" / "xmpp", fuzzy can explode with false positives.
# We keep fuzzy very strict for short keywords (but still enabled for recall).
FUZZY_THRESHOLD_SHORT = 96

# Keywords shorter than this are treated as "short".
SHORT_KEYWORD_LEN = 5

# Build n-grams up to this size (helps with phrases like "github pull request").
MAX_NGRAM = 5


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_channels(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    """
    Detect communication channels mentioned in a DiffHunk.

    Recall-first approach:
    - Normalize markdown/text aggressively
    - Exact/regex matches first
    - Fuzzy fallback against token n-grams

    Returns:
        set[str]: detected channel keys (as in communication_channels.KEYWORDS).
    """
    text = _extract_hunk_text(hunk)
    if not text.strip():
        return set()

    normalized = _normalize_text(text)
    if not normalized:
        return set()

    tokens = _tokenize(normalized)
    ngrams = _make_ngrams(tokens, max_n=MAX_NGRAM)

    detected: set[str] = set()

    for channel, keywords in communication_channels.KEYWORDS.items():
        if _channel_matches(normalized, tokens, ngrams, keywords):
            detected.add(channel)

    return detected


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _extract_hunk_text(hunk: pygit2.DiffHunk) -> str:
    """
    Extracts text from the hunk lines.
    For recall, we include additions, deletions, and context lines.
    """
    parts: list[str] = []

    # pygit2.DiffLine has .content; origin is a single-character code.
    for line in getattr(hunk, "lines", []):
        content = getattr(line, "content", "")
        if not content:
            continue

        # Strip typical diff prefixes if present in content
        # (some representations include + / - / space).
        content = content.lstrip("\ufeff")  # BOM safety
        if content and content[0] in {"+", "-", " "}:
            content = content[1:]

        parts.append(content.rstrip("\n"))

    # Fallback: hunk.header sometimes carries useful context, include lightly.
    header = getattr(hunk, "header", "")
    if header:
        parts.insert(0, header.strip())

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Normalization (Markdown-aware, English-focused)
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")  # [text](url) -> text
_URL_RE = re.compile(r"https?://\S+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CODE_FENCE_RE = re.compile(r"```.*?```", flags=re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")  # `code` -> code
_MD_PUNCT_RE = re.compile(r"[>*_~]+")  # markdown adornments
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_MULTI_WS_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    # Unicode normalize (handles weird hyphens etc.)
    text = unicodedata.normalize("NFKC", text)

    # Lowercase for case-insensitive matching
    text = text.lower()

    # Remove fenced code blocks (often noisy for channel detection in docs)
    text = _CODE_FENCE_RE.sub(" ", text)

    # Convert markdown links to visible anchor text
    text = _LINK_RE.sub(r" \1 ", text)

    # Remove raw URLs (anchor text was kept above)
    text = _URL_RE.sub(" ", text)

    # Strip inline code markers but keep content
    text = _INLINE_CODE_RE.sub(r" \1 ", text)

    # Remove HTML tags
    text = _HTML_TAG_RE.sub(" ", text)

    # Remove common markdown punctuation
    text = _MD_PUNCT_RE.sub(" ", text)

    # Normalize separators (hyphens, slashes, etc.) into spaces
    text = _NON_ALNUM_RE.sub(" ", text)

    # Collapse whitespace
    text = _MULTI_WS_RE.sub(" ", text).strip()

    return text


def _tokenize(normalized_text: str) -> list[str]:
    if not normalized_text:
        return []
    return normalized_text.split()


def _make_ngrams(tokens: list[str], *, max_n: int) -> list[str]:
    if not tokens:
        return []
    max_n = max(1, max_n)
    out: list[str] = []
    n_tokens = len(tokens)
    for n in range(1, max_n + 1):
        if n > n_tokens:
            break
        for i in range(0, n_tokens - n + 1):
            out.append(" ".join(tokens[i : i + n]))
    return out


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def _channel_matches(
    normalized_text: str,
    tokens: list[str],
    ngrams: list[str],
    keywords: list[str],
) -> bool:
    """
    Returns True if any keyword hits via:
    1) exact/regex word-boundary match
    2) phrase regex match (whitespace tolerant)
    3) fuzzy match against n-grams (recall-first)
    """
    for kw in keywords:
        kw_norm = _normalize_text(kw)
        if not kw_norm:
            continue

        # 1) Exact / boundary regex
        if _regex_hit(normalized_text, kw_norm):
            return True

        # 2) Phrase regex (tolerant whitespace)
        if _phrase_regex_hit(normalized_text, kw_norm):
            return True

        # 3) Fuzzy fallback
        if _fuzzy_hit(tokens, ngrams, kw_norm):
            return True

    return False


def _regex_hit(text: str, kw_norm: str) -> bool:
    """
    Word-boundary match.
    - For single tokens: \bdiscord\b
    - For multi-word: still works but less tolerant than phrase regex
    """
    pattern = r"\b" + re.escape(kw_norm) + r"\b"
    return re.search(pattern, text) is not None


def _phrase_regex_hit(text: str, kw_norm: str) -> bool:
    """
    For phrases: "github pull request" matches "github   pull   request".
    Also helps for cases where normalization collapsed separators.
    """
    parts = kw_norm.split()
    if len(parts) <= 1:
        return False
    pattern = r"\b" + r"\s+".join(map(re.escape, parts)) + r"\b"
    return re.search(pattern, text) is not None


def _fuzzy_hit(tokens: list[str], ngrams: list[str], kw_norm: str) -> bool:
    """
    Recall-first fuzzy:
    - For short keywords (<= SHORT_KEYWORD_LEN): very strict threshold
    - For phrases: compare against n-grams of similar length
    """
    kw_len = len(kw_norm)
    kw_tokens = kw_norm.split()

    if kw_len <= SHORT_KEYWORD_LEN and len(kw_tokens) == 1:
        # Compare against tokens only
        for tok in tokens:
            if _similarity(tok, kw_norm) >= FUZZY_THRESHOLD_SHORT:
                return True
        return False

    # For phrases, compare against n-grams with comparable token length
    target_n = len(kw_tokens)
    if target_n <= 0:
        return False

    # Limit comparisons for speed and precision: only n-grams of same length ±1
    candidate_lengths = {target_n}
    if target_n > 1:
        candidate_lengths.add(target_n - 1)
    candidate_lengths.add(target_n + 1)

    for ng in ngrams:
        ng_n = len(ng.split())
        if ng_n not in candidate_lengths:
            continue
        if _similarity(ng, kw_norm) >= FUZZY_THRESHOLD_PHRASE:
            return True

    return False


def _similarity(a: str, b: str) -> int:
    """
    Returns similarity as an integer percentage [0..100].
    """
    if not a or not b:
        return 0
    return int(round(100 * SequenceMatcher(None, a, b).ratio()))