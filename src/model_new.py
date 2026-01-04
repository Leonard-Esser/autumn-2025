from dataclasses import dataclass, field

from typing import Optional

import pygit2


@dataclass(frozen=True, slots=True)
class Subject:
    full_name_of_repo: str
    commit_sha: str
    path: str


CommunicationChannel = str


@dataclass
class Result:
    subject: Subject
    detected_channels: set[CommunicationChannel] = field(default_factory=set)
    is_ccdc_event: bool = False


@dataclass
class PartialResult(Result):
    hunk: pygit2.DiffHunk
    text: Optional[str] = None