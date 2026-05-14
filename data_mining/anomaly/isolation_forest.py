"""Detection d'anomalies avec Isolation Forest."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_isolation_forest(
    df: pd.DataFrame,
    features: list[str] | None = None,
    contamination: float = 0.05,
) -> list[dict]:
    if df is None or df.empty:
        return []

    cols = [c for c in (features or ["prix_standard", "prix_minmax"]) if c in df.columns]
    if not cols:
        return []

    x = df[cols].fillna(0)
    contamination = min(max(contamination, 0.01), 0.5)
    if len(x) < 5:
        contamination = min(0.4, 1 / max(len(x), 1))

    model = IsolationForest(contamination=contamination, random_state=42)
    labels = model.fit_predict(x)
    scores = model.decision_function(x)

    return [
        {
            "offre_id": int(row.get("id", idx + 1)),
            "anomalie_iso": int(labels[pos]),
            "is_anomaly": bool(labels[pos] == -1),
            "score_iso": float(scores[pos]),
        }
        for pos, (idx, row) in enumerate(df.iterrows())
    ]
