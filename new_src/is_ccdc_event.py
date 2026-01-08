import pygit2
from aggregate import any_result_is_ccdc_event
from domain_model import PartialResult, Subject
from get_logger import get_logger
from pairs_fit_max_length import pairs_fit_max_length
from pygit2_helpers import flatten_hunk, flatten_lines, group_lines_by_origin
from transformers import AutoTokenizer

import labels
from classifier import Classifier
from labels import TaskMode
from slice_text_by_token_limit import slice_text_by_token_limit

logger = get_logger(__name__)


def is_ccdc_event(
    *,
    subject: Subject,
    hunk: pygit2.DiffHunk,
    model_id: str,
    token_limit: int,
    tries_to_classify_flattened_hunk: bool,
    logs_scores: bool,
) -> bool:
    classifier = Classifier(
        model_name=model_id,
        max_length=token_limit,
    )

    def _text_fits(
        text: str,
        *,
        task_mode: TaskMode
    ) -> bool:
        return pairs_fit_max_length(
            tokenizer=AutoTokenizer.from_pretrained(model_id),
            text=text,
            labels=labels.LABELS[task_mode],
            hypothesis_template=labels.HYPOTHESIS_TEMPLATES[task_mode],
            max_length=token_limit,
        )
    
    if tries_to_classify_flattened_hunk:
        text = flatten_hunk(hunk, origin_included=True)
        task_mode = TaskMode.INTENT
        if _text_fits(text, task_mode=task_mode):
            return _text_is_ccdc_event(
                text,
                classifier=classifier,
                task_mode=task_mode,
                logs_scores=logs_scores,
            )
    
    task_mode = TaskMode.TOPIC
    partial_results: list[PartialResult] = []
    for origin, lines in group_lines_by_origin(hunk).items():
        text = flatten_lines(lines)
        if _text_fits(text, task_mode=task_mode):
            partial_results.append(
                _partial_result(
                    subject=subject,
                    hunk=hunk,
                    text=text,
                    classifier=classifier,
                    task_mode=task_mode,
                    logs_scores=logs_scores,
                )
            )
            continue
        
        for line in lines:
            text = line.content.rstrip()
            if _text_fits(text, task_mode=task_mode):
                partial_results.append(
                    _partial_result(
                        subject=subject,
                        hunk=hunk,
                        text=text,
                        classifier=classifier,
                        task_mode=task_mode,
                        logs_scores=logs_scores,
                    )
                )
            else:
                def _slice_fits(slc: str):
                    return _text_fits(slc, task_mode=task_mode)
                
                for text_slice in slice_text_by_token_limit(
                    text,
                    text_fits=_slice_fits,
                ):    
                    partial_results.append(
                        _partial_result(
                            subject=subject,
                            hunk=hunk,
                            text=text_slice,
                            classifier=classifier,
                            task_mode=task_mode,
                            logs_scores=logs_scores,
                        )
                    )
    return any_result_is_ccdc_event(partial_results)
    
    return False


def _partial_result(
    *,
    subject: Subject,
    hunk: pygit2.DiffHunk,
    text: str,
    classifier: Classifier,
    task_mode: TaskMode,
    logs_scores: bool,
) -> PartialResult:
    return PartialResult(
        subject=subject,
        hunk=hunk,
        text=text,
        is_ccdc_event=_text_is_ccdc_event(
            text,
            classifier=classifier,
            task_mode=task_mode,
            logs_scores=logs_scores,
        )
    )


def _text_is_ccdc_event(
    text: str,
    *,
    classifier: Classifier,
    task_mode: TaskMode,
    logs_scores: bool,
) -> bool:
    if not text or not text.strip():
        return False
    
    labels_and_their_scores = classifier.classify(
        text=text,
        labels=labels.LABELS[task_mode],
        hypothesis_template=labels.HYPOTHESIS_TEMPLATES[task_mode],
    )

    if logs_scores:
        logger.info(labels_and_their_scores)
    
    return _interpret_scores(labels_and_their_scores, task_mode=task_mode)


def _interpret_scores(
    labels_and_their_scores: dict[str, float],
    *,
    task_mode: TaskMode,
) -> bool:
    threshold = 0.5
    project_communication_label = labels.PROJECT_COMMUNICATION[task_mode]
    if task_mode is TaskMode.INTENT:
        if labels_and_their_scores[project_communication_label] < 0.1:
            return False
    if labels_and_their_scores[project_communication_label] > threshold:
        labels_and_their_scores.pop(project_communication_label)
    
    for label, score in labels_and_their_scores.items():
        if score > threshold:
            return True
    
    return False