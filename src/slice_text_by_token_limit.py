from __future__ import annotations

from collections import deque
from typing import Callable


def slice_text_by_token_limit(
    text: str,
    *,
    count_tokens: Callable[[str], int],
    max_tokens: int = 512,
    prefer_split_chars: tuple[str, ...] = ("\n\n", "\n", ". ", " ", ""),
) -> list[str]:
    """
    Split `text` into slices so that each slice has < `max_tokens` tokens.

    Strategy:
    - Uses a queue (iterative, no recursion depth issues).
    - If a chunk is too large, tries to split near the middle at a "nice" boundary
      (paragraph -> newline -> sentence -> space). Falls back to hard midpoint split.
    - Filters out empty/whitespace-only results.

    Notes:
    - Assumes `count_tokens` is monotonic-ish with text length (true for common tokenizers).
    """
    if max_tokens <= 1:
        raise ValueError("max_tokens must be > 1")

    def under_limit(s: str) -> bool:
        return count_tokens(s) < max_tokens

    def split_once(s: str) -> tuple[str, str]:
        s = s.strip()
        if not s:
            return "", ""

        mid = len(s) // 2

        # Try to split near the midpoint using progressively weaker boundaries.
        for sep in prefer_split_chars:
            if sep == "":
                break
            left_idx = s.rfind(sep, 0, mid)
            right_idx = s.find(sep, mid)

            # pick the closest split to the middle (but valid)
            candidates = [i for i in (left_idx, right_idx) if i != -1]
            if not candidates:
                continue

            split_at = min(candidates, key=lambda i: abs(i - mid))
            a = s[:split_at].strip()
            b = s[split_at + len(sep) :].strip()
            if a and b:
                return a, b

        # Fallback: hard split at midpoint, but avoid empty halves when possible.
        a = s[:mid].strip()
        b = s[mid:].strip()
        if not a:  # extremely short or lots of whitespace
            a = s[: max(1, len(s) // 3)].strip()
            b = s[len(a) :].strip()
        if not b:
            b = s[len(a) :].strip()
        return a, b

    # Fast-path
    text = text.strip()
    if not text:
        return []
    if under_limit(text):
        return [text]

    # Work queue
    q: deque[str] = deque([text])
    out: list[str] = []

    while q:
        chunk = q.popleft()
        chunk = chunk.strip()
        if not chunk:
            continue

        if under_limit(chunk):
            out.append(chunk)
            continue

        a, b = split_once(chunk)

        # Safety: if we failed to meaningfully split, return as-is to avoid infinite loops.
        # (Should be rare; mostly protects against pathological token counters.)
        if not a or not b or (a == chunk and b == chunk):
            out.append(chunk)
            continue

        q.append(a)
        q.append(b)

    return out