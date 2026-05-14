"""Reduction PCA 2D pour visualisation frontend."""

from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA


def compute_pca(df: pd.DataFrame, features: list[str] | None = None, labels=None) -> list[dict]:
    if df is None or df.empty:
        return []

    cols = [c for c in (features or ["prix_standard", "prix_minmax"]) if c in df.columns]
    if not cols:
        return []

    x = df[cols].fillna(0)
    if len(cols) == 1:
        coords = pd.DataFrame({"x": x.iloc[:, 0], "y": 0.0})
    else:
        coords_array = PCA(n_components=2, random_state=42).fit_transform(x)
        coords = pd.DataFrame(coords_array, columns=["x", "y"], index=df.index)

    labels = labels if labels is not None else [None] * len(df)
    return [
        {
            "offre_id": int(row.get("id", idx + 1)),
            "x": float(coords.loc[idx, "x"]),
            "y": float(coords.loc[idx, "y"]),
            "cluster": None if labels[pos] is None else int(labels[pos]),
            "prix": float(row.get("prix_mad", row.get("prix", 0))),
            "nom": row.get("nom"),
        }
        for pos, (idx, row) in enumerate(df.iterrows())
    ]
