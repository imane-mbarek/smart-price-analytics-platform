"""Statistiques descriptives retournees au backend."""

from __future__ import annotations

import pandas as pd


def _to_float(value):
    if pd.isna(value):
        return None
    return float(value)


def compute_stats(df: pd.DataFrame, price_col: str = "prix_mad") -> dict:
    """Calcule min, max, moyenne, mediane, variance, quartiles et plateformes."""
    if df is None or df.empty:
        return {}

    col = price_col if price_col in df.columns else "prix"
    prices = pd.to_numeric(df[col], errors="coerce").dropna()
    if prices.empty:
        return {}

    q1 = prices.quantile(0.25)
    q2 = prices.quantile(0.50)
    q3 = prices.quantile(0.75)

    stats = {
        "count": int(prices.count()),
        "min": _to_float(prices.min()),
        "max": _to_float(prices.max()),
        "mean": _to_float(prices.mean()),
        "median": _to_float(prices.median()),
        "std": _to_float(prices.std(ddof=1)) if len(prices) > 1 else 0.0,
        "variance": _to_float(prices.var(ddof=1)) if len(prices) > 1 else 0.0,
        "q1": _to_float(q1),
        "q2": _to_float(q2),
        "q3": _to_float(q3),
        "iqr": _to_float(q3 - q1),
    }

    if "plateforme" in df.columns:
        stats["distribution_plateforme"] = (
            df["plateforme"].fillna("inconnu").astype(str).value_counts().to_dict()
        )
    if "categorie" in df.columns:
        stats["distribution_categorie"] = (
            df["categorie"].fillna("inconnu").astype(str).value_counts().to_dict()
        )
    return stats
