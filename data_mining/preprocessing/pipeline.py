"""
pipeline.py  –  Pipeline complet de prétraitement
Module Data Mining | Licence IASD 2025/2026

Chaîne complète :
    db_connector.py → cleaner.py → normalizer.py → pipeline.py
                                                        ↓
                                            prêt pour clustering / anomalies
"""

import sys
sys.path.append('.')

import pandas as pd

# ─── Imports depuis les modules ───────────────────────────────
from db_connector import get_data
from cleaner      import nettoyer
from normalizer   import normaliser


# ══════════════════════════════════════════════════════════════
# COLONNES NUMÉRIQUES UTILISÉES PAR LE CLUSTERING / ANOMALIES
# ══════════════════════════════════════════════════════════════
FEATURES_CLUSTERING = [
    'prix_mad',
    'prix_standard',
    'prix_minmax',
    'ram_go',
    'stockage_go',
    'ecran_pouces',
    'cpu_famille',
    'marque_encode',
    'etat_encode',
    'plateforme_encode',
    'categorie_encode',
]


# ══════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════
def build_pipeline(nom_produit: str = None,
                   plateforme: str = None,
                   limit: int = None) -> tuple:
    """
    Pipeline complet :
        Base de données → Nettoyage → Normalisation → Prêt pour DM

    Paramètres
    ----------
    nom_produit : filtre par nom (ex: 'iPhone', 'laptop')
    plateforme  : filtre par plateforme (ex: 'Jumia', 'Avito')
    limit       : nombre max de lignes à charger

    Retourne
    --------
    df_clean      : DataFrame nettoyé (avant normalisation)
    df_scaled     : DataFrame normalisé + encodé (prêt pour DM)
    std_scaler    : StandardScaler fitté (pour inverse_transform)
    minmax_scaler : MinMaxScaler fitté
    encoders      : dict des LabelEncoders fittés
    features      : liste des colonnes numériques disponibles pour DM
    """

    _header("PIPELINE PRÉTRAITEMENT DATA MINING")

    # ── Étape 1 : Récupération depuis la base de données ──────
    _step(1, "Récupération des données depuis MySQL...")
    df_raw = get_data(
        nom_produit=nom_produit,
        plateforme=plateforme,
        limit=limit,
    )
    print(f"   Données brutes chargées : {len(df_raw)} lignes")

    if df_raw.empty or len(df_raw) < 3:
        print("   ✗ Pas assez de données !")
        return None, None, None, None, {}, []

    # ── Étape 2 : Nettoyage (cleaner.py) ──────────────────────
    _step(2, "Nettoyage des données...")
    n_avant  = len(df_raw)
    df_clean = nettoyer(df_raw.copy())
    n_apres  = len(df_clean)
    print(f"   Lignes avant nettoyage  : {n_avant}")
    print(f"   Lignes après nettoyage  : {n_apres}")
    print(f"   Lignes supprimées       : {n_avant - n_apres}")
    print(f"   Outliers prix détectés  : {df_clean['prix_outlier'].sum()}")

    if df_clean.empty or len(df_clean) < 3:
        print("   ✗ Pas assez de données après nettoyage !")
        return None, None, None, None, {}, []

    # ── Étape 3 : Normalisation & Encodage (normalizer.py) ────
    _step(3, "Normalisation et encodage...")
    df_scaled, std_scaler, minmax_scaler, encoders = normaliser(df_clean.copy())

    # ── Étape 4 : Sélection des features pour DM ──────────────
    _step(4, "Sélection des features pour le Data Mining...")
    features = [f for f in FEATURES_CLUSTERING if f in df_scaled.columns]
    features_manquantes = [f for f in FEATURES_CLUSTERING if f not in df_scaled.columns]

    print(f"   Features disponibles    : {len(features)}")
    for f in features:
        n_null = df_scaled[f].isna().sum()
        print(f"     ✓ {f:<25} ({n_null} NaN)")

    if features_manquantes:
        print(f"   Features manquantes     :")
        for f in features_manquantes:
            print(f"     ✗ {f}")

    # ── Rapport final ──────────────────────────────────────────
    _rapport(df_scaled, features)

    return df_clean, df_scaled, std_scaler, minmax_scaler, encoders, features


# ══════════════════════════════════════════════════════════════
# HELPERS D'AFFICHAGE
# ══════════════════════════════════════════════════════════════
def _header(titre: str) -> None:
    print("\n" + "═"*55)
    print(f"   {titre}")
    print("═"*55)


def _step(n: int, texte: str) -> None:
    print(f"\n  Étape {n} : {texte}")


def _rapport(df: pd.DataFrame, features: list) -> None:
    print("\n" + "─"*55)
    print("  RAPPORT FINAL")
    print("─"*55)

    if 'categorie' in df.columns:
        print(f"  Catégories  : {df['categorie'].value_counts().to_dict()}")
    if 'plateforme' in df.columns:
        print(f"  Plateformes : {df['plateforme'].value_counts().to_dict()}")
    if 'prix_mad' in df.columns:
        print(f"  Prix MAD    : min={df['prix_mad'].min():.0f} | "
              f"max={df['prix_mad'].max():.0f} | "
              f"moy={df['prix_mad'].mean():.0f}")
    if 'prix_outlier' in df.columns:
        print(f"  Outliers    : {df['prix_outlier'].sum()} détectés "
              f"({df['prix_outlier'].mean()*100:.1f}%)")
    if 'marque' in df.columns:
        print(f"  Marques     : {df['marque'].value_counts().to_dict()}")

    print(f"\n  {len(features)} features numériques prêtes pour le clustering :")
    print(f"  {features}")
    print("\n  ✓ Pipeline terminé avec succès !")
    print("═"*55 + "\n")


# ══════════════════════════════════════════════════════════════
# TEST DIRECT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    df_clean, df_scaled, std_sc, mm_sc, encoders, features = \
        build_pipeline()

    if df_scaled is not None:
        print("\nAperçu des données prêtes pour le Data Mining :")
        cols_apercu = [
            'nom', 'marque', 'prix_mad', 'prix_standard', 'prix_minmax',
            'ram_go', 'stockage_go', 'ecran_pouces', 'cpu_famille',
            'etat', 'plateforme', 'prix_outlier'
        ]
        cols_dispo = [c for c in cols_apercu if c in df_scaled.columns]
        print(df_scaled[cols_dispo].head(10).to_string())

        print(f"\nDataFrame prêt pour clustering — shape : {df_scaled[features].shape}")
        print(df_scaled[features].describe().round(2).to_string())