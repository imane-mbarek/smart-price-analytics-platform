"""Clustering DBSCAN, alternative a K-Means."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import DBSCAN


def run_dbscan(
    df: pd.DataFrame,
    features: list[str] | None = None,
    eps: float = 0.8,
    min_samples: int = 3,
) -> list[dict]:
    if df is None or df.empty:
        return []

    cols = [c for c in (features or ["prix_standard", "prix_minmax"]) if c in df.columns]
    if not cols:
        return []

    x = df[cols].fillna(0)
    min_samples = max(2, min(min_samples, len(x)))
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(x)

    return [
        {
            "offre_id": int(row.get("id", idx + 1)),
            "cluster": int(labels[idx]),
            "is_noise": bool(labels[idx] == -1),
            "prix": float(row.get("prix_mad", row.get("prix", 0))),
        }
        for idx, row in df.iterrows()
    ]
