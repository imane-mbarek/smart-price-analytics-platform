"""Detection d'anomalies avec LOF et combinaison des alertes."""

from __future__ import annotations

import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

from .isolation_forest import detect_isolation_forest


def detect_lof(df: pd.DataFrame, features: list[str] | None = None, n_neighbors: int = 20) -> list[dict]:
    if df is None or df.empty:
        return []

    cols = [c for c in (features or ["prix_standard", "prix_minmax"]) if c in df.columns]
    if not cols:
        return []

    x = df[cols].fillna(0)
    if len(x) < 3:
        labels = [1] * len(x)
        scores = [0.0] * len(x)
    else:
        n_neighbors = max(2, min(n_neighbors, len(x) - 1, 50))
        model = LocalOutlierFactor(n_neighbors=n_neighbors)
        labels = model.fit_predict(x)
        scores = model.negative_outlier_factor_

    return [
        {
            "offre_id": int(row.get("id", idx + 1)),
            "anomalie_lof": int(labels[pos]),
            "is_anomaly": bool(labels[pos] == -1),
            "score_lof": float(scores[pos]),
        }
        for pos, (idx, row) in enumerate(df.iterrows())
    ]


def detect_anomalies(df: pd.DataFrame, features: list[str] | None = None) -> list[dict]:
    """Combine Isolation Forest et LOF selon les niveaux rouge/orange/vert."""
    if df is None or df.empty:
        return []

    iso = detect_isolation_forest(df, features)
    lof = detect_lof(df, features)
    iso_by_id = {item["offre_id"]: item for item in iso}
    lof_by_id = {item["offre_id"]: item for item in lof}

    output = []
    for idx, row in df.iterrows():
        offre_id = int(row.get("id", idx + 1))
        iso_flag = iso_by_id.get(offre_id, {}).get("anomalie_iso", 1) == -1
        lof_flag = lof_by_id.get(offre_id, {}).get("anomalie_lof", 1) == -1
        if iso_flag and lof_flag:
            niveau = "rouge"
        elif iso_flag or lof_flag:
            niveau = "orange"
        else:
            niveau = "vert"

        output.append(
            {
                "offre_id": offre_id,
                "nom": row.get("nom"),
                "plateforme": row.get("plateforme"),
                "prix": float(row.get("prix_mad", row.get("prix", 0))),
                "suspect": bool(iso_flag and lof_flag),
                "niveau": niveau,
                "anomalie_iso": bool(iso_flag),
                "anomalie_lof": bool(lof_flag),
                "score_iso": iso_by_id.get(offre_id, {}).get("score_iso"),
                "score_lof": lof_by_id.get(offre_id, {}).get("score_lof"),
            }
        )
    return output
