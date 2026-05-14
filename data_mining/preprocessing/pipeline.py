"""Pipeline complet de pretraitement pour le module Data Mining."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

try:
    from .cleaner import nettoyer
    from .db_connector import get_data
    from .normalizer import normaliser
except ImportError:  # execution directe
    from cleaner import nettoyer
    from db_connector import get_data
    from normalizer import normaliser


FEATURES_CLUSTERING = [
    "prix_mad",
    "prix_standard",
    "prix_minmax",
    "ram_go",
    "stockage_go",
    "ecran_pouces",
    "cpu_famille",
    "marque_encode",
    "etat_encode",
    "plateforme_encode",
    "categorie_encode",
]


def _as_dataframe(raw_data: Iterable[dict] | pd.DataFrame | None) -> pd.DataFrame:
    if raw_data is None:
        return pd.DataFrame()
    if isinstance(raw_data, pd.DataFrame):
        return raw_data.copy()
    return pd.DataFrame(list(raw_data))


def preprocess(raw_data: Iterable[dict] | pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Nettoie, enrichit et normalise les donnees brutes du backend."""
    df_raw = _as_dataframe(raw_data)
    if df_raw.empty:
        return df_raw, []

    df_clean = nettoyer(df_raw)
    if df_clean.empty:
        return df_clean, []

    df_scaled, _std_scaler, _minmax_scaler, _encoders = normaliser(df_clean)
    features = [col for col in FEATURES_CLUSTERING if col in df_scaled.columns]
    return df_scaled, features


def build_pipeline(
    raw_data: Iterable[dict] | pd.DataFrame | str | None = None,
    plateforme: str | None = None,
    limit: int | None = None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, object, object, dict, list[str]]:
    """
    Pipeline compatible avec deux usages :
    - build_pipeline(raw_data) pour les donnees JSON du backend ;
    - build_pipeline("iphone", plateforme="Jumia") pour charger depuis la BD.
    """
    if raw_data is None or isinstance(raw_data, str):
        df_raw = get_data(nom_produit=raw_data, plateforme=plateforme, limit=limit)
    else:
        df_raw = _as_dataframe(raw_data)

    if df_raw.empty:
        return None, None, None, None, {}, []

    df_clean = nettoyer(df_raw)
    if df_clean.empty:
        return df_clean, None, None, None, {}, []

    df_scaled, std_scaler, minmax_scaler, encoders = normaliser(df_clean)
    features = [col for col in FEATURES_CLUSTERING if col in df_scaled.columns]
    return df_clean, df_scaled, std_scaler, minmax_scaler, encoders, features
