"""Service unique appele par le backend Django apres scraping."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from data_mining.anomaly import detect_anomalies
from data_mining.association import extract_rules
from data_mining.clustering import compute_pca, run_dbscan, run_kmeans
from data_mining.preprocessing.pipeline import build_pipeline
from data_mining.stats import compute_stats


def analyze(raw_data: Iterable[dict] | pd.DataFrame) -> dict:
    """
    Point d'entree unique appele par Django.

    Input  : liste de produits scrapes (JSON) ou DataFrame.
    Output : dict JSON-ready avec statistiques, clusters, anomalies et regles.
    """
    df_clean, df_scaled, _std, _mm, _encoders, features = build_pipeline(raw_data)
    if df_scaled is None or df_scaled.empty:
        return {
            "stats": {},
            "clusters": [],
            "dbscan": [],
            "anomalies": [],
            "rules": [],
            "pca": [],
            "metadata": {"rows": 0, "features": []},
        }

    kmeans = run_kmeans(df_scaled, features)
    labels = [item["cluster"] for item in kmeans["items"]]
    pca = compute_pca(df_scaled, features, labels=labels)

    pca_by_id = {item["offre_id"]: item for item in pca}
    clusters = []
    for item in kmeans["items"]:
        p = pca_by_id.get(item["offre_id"], {})
        clusters.append(
            {
                **item,
                "pca_x": p.get("x"),
                "pca_y": p.get("y"),
            }
        )

    return {
        "stats": compute_stats(df_scaled),
        "kmeans": {
            "centroids": kmeans.get("centroids", []),
            "elbow": kmeans.get("elbow", []),
        },
        "clusters": clusters,
        "dbscan": run_dbscan(df_scaled, features),
        "anomalies": detect_anomalies(df_scaled, features),
        "rules": extract_rules(df_scaled),
        "pca": pca,
        "metadata": {
            "rows": int(len(df_scaled)),
            "features": features,
            "clean_rows": int(len(df_clean)) if df_clean is not None else 0,
        },
    }
