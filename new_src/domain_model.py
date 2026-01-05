import json
from dataclasses import dataclass, field

import pygit2
from typing import Optional

import config
from get_logger import get_logger
from pygit2_helpers import flatten_hunk


@dataclass(frozen=True, slots=True)
class Subject:
    full_name_of_repo: str
    commit_sha: str
    path: str


@dataclass(frozen=True, slots=True)
class Result:
    subject: Subject
    detected_channels: frozenset[str] = field(default_factory=frozenset)
    is_ccdc_event: bool = False


@dataclass
class PartialResult:
    subject: Subject
    hunk: pygit2.DiffHunk
    text: Optional[str] = None
    detected_channels: frozenset[str] = field(default_factory=frozenset)
    is_ccdc_event: bool = False
    
    def __post_init__(self) -> None:
        if config.LOGS_EACH_PARTIAL_RESULT_CREATED:
            get_logger(__name__).info(
                "PartialResult created: %s",
                self._log_repr(),
            )
    

    def _log_repr(self) -> str:
        """
        Returns a compact JSON string representation of this PartialResult.
        Avoids serializing the full pygit2.DiffHunk (can be huge / not JSON-serializable).
        """
        hunk = self.hunk
        text = self.text
        if not text:
            text = flatten_hunk(hunk, origin_included=True)
        payload = {
            "type": self.__class__.__name__,
            "subject": {
                "full_name_of_repo": self.subject.full_name_of_repo,
                "commit_sha": self.subject.commit_sha,
                "path": self.subject.path,
            },
            "hunk": {
                "header": hunk.header,
                "new_lines": hunk.new_lines,
                "new_start": hunk.new_start,
                "old_lines": hunk.old_lines,
                "old_start": hunk.old_start,
            },
            "text": self.text,
            "detected_channels": sorted(self.detected_channels),
            "is_ccdc_event": self.is_ccdc_event,
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))