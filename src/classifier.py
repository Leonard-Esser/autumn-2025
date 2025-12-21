from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class Classifier:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        device: str | None = None,
        max_length: int = 512,
    ) -> None:
        self.nli_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.nli_model.eval()

        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.device = torch.device(device)
        self.nli_model.to(self.device)

        self.max_length = max_length

        # BART MNLI label mapping (usually: 0=contradiction, 1=neutral, 2=entailment)
        id2label = self.nli_model.config.id2label
        self.entailment_id = next(i for i, v in id2label.items() if v.lower() == "entailment")

    @torch.inference_mode()
    def classify(
        self,
        text: str,
        labels: Sequence[str],
        hypothesis_template: str,
    ) -> dict[str, float]:
        if not labels:
            raise ValueError("labels must not be empty")
        if "{}" not in hypothesis_template:
            raise ValueError("hypothesis_template must contain '{}' placeholder")

        hypotheses = [hypothesis_template.format(lbl) for lbl in labels]

        # Encode pairs (premise, hypothesis) in batch
        enc = self.tokenizer(
            [text] * len(labels),
            hypotheses,
            truncation=True,
            max_length=self.max_length,
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        logits = self.nli_model(**enc).logits  # shape: (n_labels, 3)
        entail_logits = logits[:, self.entailment_id]  # shape: (n_labels,)

        # P(entailment) from 3-way softmax per label
        probs = torch.softmax(logits, dim=1)[:, self.entailment_id]
        scores = probs.detach().cpu().tolist()

        score_map = {lbl: float(sc) for lbl, sc in zip(labels, scores)}
        return score_map
    
    def count_tokens(
        self,
        text: str,
        *,
        add_special_tokens: bool = True,
    ) -> int:
        """
        Returns the number of tokens for `text` according to the tokenizer.

        Parameters
        ----------
        text : str
            Input text to tokenize.
        add_special_tokens : bool, default=True
            Whether to include special tokens like <s>, </s>.

        Returns
        -------
        int
            Number of tokens.
        """
        encoded = self.tokenizer(
            text,
            add_special_tokens=add_special_tokens,
            truncation=False,
            padding=False,
            return_attention_mask=False,
            return_token_type_ids=False,
        )
        return len(encoded["input_ids"])