from collections.abc import Callable

from config import CHUNKING


def apply_chunking_if_requested_and_necessary(
    text: str,
    cut_into_sufficiently_small_pieces: Callable[[str], list[str]]
) -> list[str]:
    if not CHUNKING:
        return [text]
    
    return cut_into_sufficiently_small_pieces(text)