from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


@dataclass(frozen=True, slots=True)
class _NliLabelIndices:
    contradiction: int
    neutral: int
    entailment: int


class Classifier:
    """
    Zero-shot classifier via NLI (e.g., facebook/bart-large-mnli).

    Usage pattern:
        scores = clf.classify(
            text=...,
            labels=[...],
            hypothesis_template="This text is about {}.",
        )
        # -> dict[label, score]

    Notes:
    - Scores are computed independently per label (no cross-label normalization).
    - Tokenization truncation strategy is "only_first" (truncate premise/text only).
    - Uses batching across all labels for the given text.
    """

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        max_length: int = 512,
    ) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

        if device is None:
            device = self._auto_device()

        self.device = torch.device(device)
        self.model.to(self.device)

        if max_length <= 0:
            raise ValueError("max_length must be > 0.")
        self.max_length = int(max_length)

        self._nli = self._resolve_nli_label_indices()

    @staticmethod
    def _auto_device() -> str:
        # Optimized for Apple Silicon (M1 Pro): prefer MPS when available.
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _resolve_nli_label_indices(self) -> _NliLabelIndices:
        """
        Resolve indices for contradiction/neutral/entailment robustly from HF config.
        Commonly for MNLI models: 0=contradiction, 1=neutral, 2=entailment
        but we don't assume ordering.
        """
        id2label: Mapping[int, str] = getattr(self.model.config, "id2label", {})
        if not id2label:
            # Fallback to MNLI typical ordering if missing (rare, but possible)
            return _NliLabelIndices(contradiction=0, neutral=1, entailment=2)

        norm = {i: str(lbl).strip().lower() for i, lbl in id2label.items()}

        def find_idx(target: str) -> int:
            for i, lbl in norm.items():
                # Covers "contradiction", "neutral", "entailment" and variants like "LABEL_0".
                if lbl == target:
                    return i
            # Some models use "LABEL_0/1/2" without names; assume MNLI order then.
            if set(norm.values()) <= {"label_0", "label_1", "label_2"} and len(norm) >= 3:
                if target == "contradiction":
                    return 0
                if target == "neutral":
                    return 1
                if target == "entailment":
                    return 2
            raise ValueError(
                f"Could not resolve MNLI label '{target}' from model.config.id2label={id2label}."
            )

        return _NliLabelIndices(
            contradiction=find_idx("contradiction"),
            neutral=find_idx("neutral"),
            entailment=find_idx("entailment"),
        )

    def classify(
        self,
        *,
        text: str,
        labels: Sequence[str],
        hypothesis_template: str
    ) -> dict[str, float]:
        """
        Classify a single text against multiple labels.

        Args:
            text: The premise.
            labels: Candidate labels (strings).
            hypothesis_template: Template with exactly one '{}' placeholder, e.g. "This text is about {}."

        Returns:
            dict[label, score] with one float score per label.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string.")
        if not labels:
            return {}
        if "{}" not in hypothesis_template:
            raise ValueError("hypothesis_template must contain '{}' placeholder for the label.")

        # Batch across all labels for this single text:
        premises = [text] * len(labels)
        hypotheses = [hypothesis_template.format(lbl) for lbl in labels]

        encoded = self.tokenizer(
            premises,
            hypotheses,
            padding=True,
            truncation="only_first",
            max_length=self.max_length,
            return_tensors="pt",
        )

        encoded = {k: v.to(self.device) for k, v in encoded.items()}

        with torch.inference_mode():
            logits = self.model(**encoded).logits  # shape: (num_labels, 3) for MNLI

        scores = self._scores_from_logits(logits)

        # Preserve label order (Python dicts preserve insertion order).
        return {label: float(score) for label, score in zip(labels, scores, strict=True)}

    def _scores_from_logits(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Convert MNLI logits -> per-row score in [0, 1] for entailment.
        """
        if logits.ndim != 2:
            raise ValueError(f"Expected logits to be 2D (batch, classes), got shape={tuple(logits.shape)}")

        c = self._nli.contradiction
        n = self._nli.neutral
        e = self._nli.entailment

        # Softmax over all 3 classes, then take entailment prob.
        probs = torch.softmax(logits, dim=1)
        return probs[:, e]