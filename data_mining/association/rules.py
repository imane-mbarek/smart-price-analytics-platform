"""Extraction de regles d'association type Apriori."""

from __future__ import annotations

import pandas as pd


def _price_band(series: pd.Series) -> pd.Series:
    if series.nunique(dropna=True) < 3:
        return pd.Series(["prix_moyen"] * len(series), index=series.index)
    labels = ["prix_bas", "prix_moyen", "prix_eleve"]
    return pd.qcut(series.rank(method="first"), q=3, labels=labels).astype(str)


def extract_rules(df: pd.DataFrame, min_support: float = 0.1, min_confidence: float = 0.5) -> list[dict]:
    """
    Genere les top regles simples plateforme/marque/etat/categorie -> tranche prix.
    Utilise une logique transactionnelle compatible avec le besoin backend meme si
    mlxtend n'est pas installe dans l'environnement local.
    """
    if df is None or df.empty:
        return []

    work = df.copy()
    price_col = "prix_mad" if "prix_mad" in work.columns else "prix"
    if price_col not in work.columns:
        return []
    work["prix_tranche"] = _price_band(pd.to_numeric(work[price_col], errors="coerce").fillna(0))

    candidate_cols = [c for c in ["plateforme", "marque", "etat", "categorie"] if c in work.columns]
    rules = []
    total = len(work)

    for col in candidate_cols:
        for value, group in work.groupby(col, dropna=True):
            support = len(group) / total
            if support < min_support:
                continue
            target = group["prix_tranche"].value_counts(normalize=True).idxmax()
            confidence = float((group["prix_tranche"] == target).mean())
            if confidence >= min_confidence:
                rules.append(
                    {
                        "antecedent": f"{col}={value}",
                        "consequent": target,
                        "support": round(float(support), 4),
                        "confidence": round(confidence, 4),
                    }
                )

    rules.sort(key=lambda item: (item["confidence"], item["support"]), reverse=True)
    return rules[:10]
