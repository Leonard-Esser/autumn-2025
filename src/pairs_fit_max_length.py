from typing import Sequence

from transformers import PreTrainedTokenizerBase


def pairs_fit_max_length(
    *,
    tokenizer: PreTrainedTokenizerBase,
    text: str,
    labels: Sequence[str],
    hypothesis_template: str,
    max_length: int,
    add_special_tokens: bool = True,
) -> bool:
    """
    Check whether all (premise, hypothesis) pairs fit within a given token limit.

    This function is intended to live in a standalone utility module
    (e.g. ``token_utils.py``) and is independent of any classifier class.

    For each label in ``labels``, a hypothesis is created using
    ``hypothesis_template.format(label)``. The function then tokenizes the
    corresponding (premise, hypothesis) pair **without truncation** and checks
    whether the resulting token sequence length exceeds ``max_length``.

    If at least one pair would exceed the limit, the function returns ``False``.
    Otherwise, it returns ``True``.

    Parameters
    ----------
    tokenizer : PreTrainedTokenizerBase
        HuggingFace tokenizer used to tokenize the premise–hypothesis pairs.
    text : str
        The premise text.
    labels : Sequence[str]
        Labels used to generate hypotheses.
    hypothesis_template : str
        Template for hypothesis generation. Must contain a ``{}`` placeholder.
    max_length : int
        Maximum allowed number of tokens for a single (premise, hypothesis) pair.
    add_special_tokens : bool, default=True
        Whether to include special tokens (e.g. ``<s>``, ``</s>``) in the count.

    Returns
    -------
    bool
        ``True`` if all (premise, hypothesis) pairs fit within ``max_length``
        tokens without truncation, otherwise ``False``.

    Raises
    ------
    ValueError
        If ``labels`` is empty or ``hypothesis_template`` does not contain a
        ``{}`` placeholder.
    """
    if not labels:
        raise ValueError("labels must not be empty")
    if "{}" not in hypothesis_template:
        raise ValueError("hypothesis_template must contain '{}' placeholder")

    for label in labels:
        hypothesis = hypothesis_template.format(label)

        encoded = tokenizer(
            text,
            hypothesis,
            add_special_tokens=add_special_tokens,
            truncation=False,
            padding=False,
            return_attention_mask=False,
            return_token_type_ids=False,
            verbose=False,
        )

        if len(encoded["input_ids"]) > max_length:
            return False

    return True