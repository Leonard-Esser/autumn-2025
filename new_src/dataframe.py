from __future__ import annotations

from collections.abc import Iterable
import pandas as pd


def dataframe(result_set: Iterable[Result]) -> pd.DataFrame:
    """
    Returns a DataFrame with:
      - one row per channel in Result.detected_channels
      - if detected_channels is empty: exactly one row with detected_channel=None
      - one column per field of Result
      - Subject expanded into its three fields
      - stable column order and explicit dtypes
    """
    rows: list[dict[str, object]] = []
    for result in result_set:
        base = {
            "full_name_of_repo": result.subject.full_name_of_repo,
            "commit_sha": result.subject.commit_sha,
            "path": result.subject.path,
            "is_ccdc_event": result.is_ccdc_event,
        }
        if result.detected_channels:
            for channel in result.detected_channels:
                rows.append({**base, "detected_channel": channel})
        else:
            rows.append({**base, "detected_channel": None})
    columns = [
        "full_name_of_repo",
        "commit_sha",
        "path",
        "is_ccdc_event",
        "detected_channel",
    ]
    df = pd.DataFrame.from_records(rows, columns=columns)
    df = df.astype(
        {
            "full_name_of_repo": "string",
            "commit_sha": "string",
            "path": "string",
            "is_ccdc_event": "bool",
            "detected_channel": "string",
        }
    )
    return df