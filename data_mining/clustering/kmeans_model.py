"""Clustering K-Means des offres par gamme de prix."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans


def _feature_frame(df: pd.DataFrame, features: list[str] | None = None) -> pd.DataFrame:
    if features:
        cols = [c for c in features if c in df.columns]
    else:
        cols = [c for c in ["prix_standard", "prix_minmax", "prix_mad"] if c in df.columns]
    return df[cols].fillna(0) if cols else pd.DataFrame(index=df.index)


def elbow_scores(df: pd.DataFrame, features: list[str] | None = None, max_k: int = 6) -> list[dict]:
    x = _feature_frame(df, features)
    if x.empty:
        return []
    scores = []
    for k in range(1, min(max_k, len(x)) + 1):
        model = KMeans(n_clusters=k, n_init=10, random_state=42)
        model.fit(x)
        scores.append({"k": k, "inertia": float(model.inertia_)})
    return scores


def run_kmeans(df: pd.DataFrame, features: list[str] | None = None, n_clusters: int = 3) -> dict:
    """Retourne les labels K-Means, les gammes et les centroides."""
    if df is None or df.empty:
        return {"items": [], "centroids": [], "elbow": []}

    x = _feature_frame(df, features)
    if x.empty:
        return {"items": [], "centroids": [], "elbow": []}

    k = max(1, min(n_clusters, len(x)))
    labels = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(x)

    result_df = df.copy()
    result_df["cluster"] = labels
    price_col = "prix_mad" if "prix_mad" in result_df.columns else "prix"
    means = result_df.groupby("cluster")[price_col].mean().sort_values()
    gamme_by_cluster = {
        cluster: gamme
        for cluster, gamme in zip(means.index.tolist(), ["bas", "milieu", "haut"][: len(means)])
    }

    items = []
    for idx, row in result_df.iterrows():
        cluster = int(row["cluster"])
        items.append(
            {
                "offre_id": int(row.get("id", idx + 1)),
                "cluster": cluster,
                "gamme": gamme_by_cluster.get(cluster, "milieu"),
                "prix": float(row.get(price_col, 0)),
                "nom": row.get("nom"),
                "plateforme": row.get("plateforme"),
            }
        )

    centroids = [
        {
            "cluster": int(cluster),
            "gamme": gamme_by_cluster.get(cluster, "milieu"),
            "prix_moyen": float(mean),
        }
        for cluster, mean in means.items()
    ]
    return {"items": items, "centroids": centroids, "elbow": elbow_scores(df, features)}
