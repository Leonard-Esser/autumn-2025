import pygit2
from aggregate import any_result_is_ccdc_event
from domain_model import PartialResult, Subject
from get_logger import get_logger
from pairs_fit_max_length import pairs_fit_max_length
from pygit2_helpers import flatten_hunk, flatten_lines, group_lines_by_origin
from transformers import AutoTokenizer

import config
import labels
from classifier import Classifier
from labels import TaskMode

logger = get_logger(__name__)


def is_ccdc_event(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    if config.TRIES_TO_CLASSIFY_HUNK_WITH_ONLY_ONE_CALL:
        text = flatten_hunk(hunk, origin_included=True)
        task_mode = TaskMode.INTENT
        if _text_under_token_limit(text, task_mode):
            logger.info("Can classify hunk with only one call")
            return _ask_classifier(text, task_mode)
    
    partial_results: list[PartialResult] = []
    for origin, lines in group_lines_by_origin(hunk).items():
        text = flatten_lines(lines)
        task_mode = TaskMode.TOPIC
        if _text_under_token_limit(text, task_mode):
            logger.info("Can classify group of lines with only one call")
            partial_results.append(
                PartialResult(
                    subject=subject,
                    hunk=hunk,
                    text=text,
                    is_ccdc_event=_ask_classifier(text, task_mode)
                )
            )
            continue
        
        for line in lines:
            text = line.content.rstrip()
            if _text_under_token_limit(text, task_mode):
                logger.info("Can classify single line with only one call")
                partial_results.append(
                    PartialResult(
                        subject=subject,
                        hunk=hunk,
                        text=text,
                        is_ccdc_event=_ask_classifier(text, task_mode)
                    )
                )
                continue
            
            # TODO apply further segmentation
            # for now, we simply let the classifier truncate the text
            logger.warning(f"Further segmentation needed")
            partial_results.append(
                PartialResult(
                    subject=subject,
                    hunk=hunk,
                    text=text,
                    is_ccdc_event=_ask_classifier(text, task_mode)
                )
            )
    return any_result_is_ccdc_event(partial_results)


def _text_under_token_limit(text: str, task_mode: TaskMode) -> bool:
    return pairs_fit_max_length(
        tokenizer=AutoTokenizer.from_pretrained(config.MODEL_ID),
        text=text,
        labels=labels.LABELS[task_mode],
        hypothesis_template=labels.HYPOTHESIS_TEMPLATES[task_mode],
        max_length=config.MAX_NUMBER_OF_TOKENS,
    )


def _ask_classifier(text: str, task_mode: TaskMode) -> bool:
    if not text or not text.strip():
        return False
    classifier = Classifier(
        model_name=config.MODEL_ID,
        max_length=config.MAX_NUMBER_OF_TOKENS
    )
    labels_and_their_scores = classifier.classify(
        text=text,
        labels=labels.LABELS[task_mode],
        hypothesis_template=labels.HYPOTHESIS_TEMPLATES[task_mode]
    )
    logger.info(labels_and_their_scores)
    
    if _should_return_false_early(
        labels_and_their_scores,
        task_mode
    ):
        return False
    
    for label, score in labels_and_their_scores.items():
        if score > 0.5:
            return True
    
    return False


def _should_return_false_early(
    labels_and_their_scores: dict[str, float],
    task_mode: TaskMode
) -> bool:
    project_communication_label = labels.PROJECT_COMMUNICATION[task_mode]
    if task_mode is TaskMode.INTENT:
        return labels_and_their_scores[project_communication_label] < 0.01
    if labels_and_their_scores[project_communication_label] >= 0.009:
        labels_and_their_scores.pop(project_communication_label)
        return False
    return labels_and_their_scores[labels.COMMUNICATION_CHANNEL_DOCUMENTATION] < 0.171