import logging
from functools import lru_cache
from typing import Iterable, Callable

import pygit2
from transformers import AutoTokenizer, PreTrainedTokenizerBase

import labels
from aggregate import any_result_is_ccdc_event
from classifier import Classifier
from domain_model import PartialResult, Subject
from labels import TaskMode
from pygit2_helpers import flatten_hunk, flatten_lines, group_lines_by_origin
from slice_text_by_token_limit import slice_text_by_token_limit

logger = logging.getLogger(__name__)


# -------------------------
# Hot-path caches
# -------------------------

@lru_cache(maxsize=8)
def _get_tokenizer(model_id: str) -> PreTrainedTokenizerBase:
    # tokenizer init is expensive -> cache it
    return AutoTokenizer.from_pretrained(model_id)


@lru_cache(maxsize=8)
def _get_classifier(model_id: str, token_limit: int) -> Classifier:
    # model init is very expensive -> cache it
    return Classifier(model_name=model_id, max_length=token_limit)


@lru_cache(maxsize=64)
def _max_hypothesis_len(
    model_id: str,
    mode: TaskMode,
) -> int:
    """
    Compute the maximum token length of the hypothesis across all labels for a given mode.
    This allows an O(1) exact 'fits' check:
        len(premise_tokens) + max_hypothesis_tokens + special_tokens <= token_limit
    """
    tok = _get_tokenizer(model_id)
    template = labels.HYPOTHESIS_TEMPLATES[mode]

    max_len = 0
    for lab in labels.LABELS[mode]:
        hyp = template.format(lab)
        # add_special_tokens=False: we account for special tokens via build_inputs_with_special_tokens
        hyp_ids = tok(hyp, add_special_tokens=False, truncation=False, verbose=False)["input_ids"]
        if len(hyp_ids) > max_len:
            max_len = len(hyp_ids)
    return max_len


def _text_fits_fast(
    *,
    tokenizer: PreTrainedTokenizerBase,
    model_id: str,
    text: str,
    mode: TaskMode,
    token_limit: int,
) -> bool:
    """
    Exact check whether *all* (text, hypothesis(label)) pairs fit into token_limit,
    without re-tokenizing the text for every label.
    """
    if not text:
        return False

    premise_ids = tokenizer(text, add_special_tokens=False, truncation=False, verbose=False)["input_ids"]
    hyp_max = _max_hypothesis_len(model_id, mode)

    # Account for special tokens added by the model (e.g., <s> premise </s></s> hypothesis </s>)
    # build_inputs_with_special_tokens returns the final ids with special tokens.
    # We only need its length, so we can pass dummy lists of the right sizes.
    final_ids = tokenizer.build_inputs_with_special_tokens(
        premise_ids,
        [0] * hyp_max,
    )
    return len(final_ids) <= token_limit


def is_ccdc_event(
    *,
    subject: Subject,
    hunk: pygit2.DiffHunk,
    model_id: str,
    token_limit: int,
    task_mode: TaskMode,
    tries_to_classify_flattened_hunk: bool,
    returns_asap: bool,
    logs_scores: bool,
) -> bool:
    tokenizer = _get_tokenizer(model_id)
    classifier = _get_classifier(model_id, token_limit)

    # Fast path: whole flattened hunk
    if tries_to_classify_flattened_hunk:
        text = flatten_hunk(hunk, origin_included=True)
        if _text_fits_fast(
            tokenizer=tokenizer,
            model_id=model_id,
            text=text,
            mode=TaskMode.INTENT,
            token_limit=token_limit,
        ):
            return _text_is_ccdc_event(
                text,
                classifier=classifier,
                task_mode=TaskMode.INTENT,
                logs_scores=logs_scores,
            )

    # Only allocate PartialResults if we actually need them (i.e., no ASAP return)
    partial_results: list[PartialResult] | None = None
    any_positive = False

    def _evaluate(text: str, *, mode: TaskMode) -> bool:
        nonlocal any_positive, partial_results

        # Avoid work for blank strings
        if not text or not text.strip():
            return False

        is_pos = _text_is_ccdc_event(
            text,
            classifier=classifier,
            task_mode=mode,
            logs_scores=logs_scores,
        )

        if returns_asap:
            return is_pos

        # Only build PartialResult list if we must aggregate at end
        if partial_results is None:
            partial_results = []
        partial_results.append(
            PartialResult(
                subject=subject,
                hunk=hunk,
                text=text,
                is_ccdc_event=is_pos,
            )
        )
        any_positive = any_positive or is_pos
        return is_pos

    def _fits(text: str, *, mode: TaskMode) -> bool:
        return _text_fits_fast(
            tokenizer=tokenizer,
            model_id=model_id,
            text=text,
            mode=mode,
            token_limit=token_limit,
        )

    def _iter_slices(text: str) -> Iterable[str]:
        """
        Yield either the full text (if it fits) or token-limit slices.
        Robust fallback: if slicer fails, yield nothing and let caller fallback further.
        """
        if _fits(text, mode=task_mode):
            yield text
            return
        try:
            yield from slice_text_by_token_limit(text, text_fits=lambda s: _fits(s, mode=task_mode))
        except Exception:
            return

    # Main loop: origin -> lines
    grouped = group_lines_by_origin(hunk)
    for _origin, lines in grouped.items():
        block = flatten_lines(lines)

        # 1) Try block (and/or its slices)
        found = False
        for candidate in _iter_slices(block):
            found = True
            if _evaluate(candidate, mode=task_mode) and returns_asap:
                return True

        if found:
            continue  # block handled (either fit or successfully sliced)

        # 2) Fallback: per-line (and/or slices)
        for line in lines:
            line_text = line.content.rstrip()
            for candidate in _iter_slices(line_text):
                if _evaluate(candidate, mode=task_mode) and returns_asap:
                    return True

    # If returns_asap=True, we'd have returned already when positive.
    if returns_asap:
        return False

    # If we never created partial_results, nothing was evaluated as "valid candidate"
    if partial_results is None:
        return False

    # You can skip this call and return `any_positive` if you trust it’s equivalent.
    # Keeping it preserves semantics if any_result_is_ccdc_event does more later.
    return any_result_is_ccdc_event(partial_results)


def _text_is_ccdc_event(
    text: str,
    *,
    classifier: Classifier,
    task_mode: TaskMode,
    logs_scores: bool,
) -> bool:
    # Fast blank check
    if not text or not text.strip():
        return False

    scores = classifier.classify(
        text=text,
        labels=labels.LABELS[task_mode],
        hypothesis_template=labels.HYPOTHESIS_TEMPLATES[task_mode],
    )

    if logs_scores:
        logger.info(text)
        logger.info(scores)

    return _interpret_scores(scores)


def _interpret_scores(labels_and_their_scores: dict[str, float]) -> bool:
    threshold = 0.5
    return any(score > threshold for score in labels_and_their_scores.values())