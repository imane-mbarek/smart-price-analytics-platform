"""
normalizer.py  –  Normalisation & Encodage des données
Module Data Mining | Licence IASD 2025/2026

Chaîne complète :
    db_connector.py  →  cleaner.py  →  normalizer.py  →  pipeline.py
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

# ─── Liaison avec cleaner.py ──────────────────────────────────
try:
    from .cleaner import charger_et_nettoyer, nettoyer
except ImportError:  # execution directe depuis le dossier preprocessing
    from cleaner import charger_et_nettoyer, nettoyer


# ══════════════════════════════════════════════════════════════
# 1.  TAUX DE CONVERSION → MAD
# ══════════════════════════════════════════════════════════════
TAUX_CONVERSION = {
    'MAD': 1.0,
    'USD': 10.0,
    'EUR': 11.0,
    'GBP': 13.0,
    'AED': 2.7,
    'SAR': 2.7,
}


# ══════════════════════════════════════════════════════════════
# 2.  CONVERSION DES DEVISES
# ══════════════════════════════════════════════════════════════
def convertir_devise(df: pd.DataFrame,
                     colonne_prix: str = 'prix',
                     colonne_devise: str = 'devise') -> pd.DataFrame:
    """
    Convertit tous les prix en MAD.
    Si la colonne devise n'existe pas, suppose que tout est déjà en MAD.
    """
    def _convertir(row):
        devise = str(row.get(colonne_devise, 'MAD')).upper().strip()
        taux   = TAUX_CONVERSION.get(devise, 1.0)
        return row[colonne_prix] * taux

    if colonne_devise in df.columns:
        df['prix_mad'] = df.apply(_convertir, axis=1)
        print(f"[NORMALIZER] ✓ Devises converties en MAD")
    else:
        df['prix_mad'] = df[colonne_prix]
        print(f"[NORMALIZER] ✓ Prix déjà en MAD, colonne prix_mad créée")

    return df


# ══════════════════════════════════════════════════════════════
# 3.  NORMALISATION DES PRIX
# ══════════════════════════════════════════════════════════════
def normaliser_prix(df: pd.DataFrame,
                    colonne_prix: str = 'prix_mad') -> tuple:
    """
    Applique StandardScaler ET MinMaxScaler sur le prix.
    """
    std_scaler = StandardScaler()
    df['prix_standard'] = std_scaler.fit_transform(df[[colonne_prix]])

    minmax_scaler = MinMaxScaler()
    df['prix_minmax'] = minmax_scaler.fit_transform(df[[colonne_prix]])

    print(f"[NORMALIZER] ✓ Prix normalisés")
    print(f"             StandardScaler : moyenne={df['prix_standard'].mean():.3f}, "
          f"std={df['prix_standard'].std():.3f}")
    print(f"             MinMaxScaler   : min={df['prix_minmax'].min():.3f}, "
          f"max={df['prix_minmax'].max():.3f}")

    return df, std_scaler, minmax_scaler


# ══════════════════════════════════════════════════════════════
# 4.  ENCODAGE DES COLONNES TEXTE
# ══════════════════════════════════════════════════════════════
COLONNES_A_ENCODER = [
    'plateforme',
    'categorie',
    'marque',
    'etat',
    'generation',
]


def encoder_colonnes(df: pd.DataFrame) -> tuple:
    encoders = {}

    # ── 4a. LabelEncoder ──────────────────────────────────────
    for col in COLONNES_A_ENCODER:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = df[col].fillna('Inconnu')
            df[f'{col}_encode'] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
            mapping = dict(zip(le.classes_, le.transform(le.classes_)))
            print(f"[NORMALIZER] ✓ {col:<15} encodé → {mapping}")

    # ── 4b. RAM ───────────────────────────────────────────────
    if 'ram_go' in df.columns:
        df['ram_go'] = pd.to_numeric(df['ram_go'], errors='coerce')
        mediane_ram = df['ram_go'].median() if df['ram_go'].notna().any() else 0
        df['ram_go'] = df['ram_go'].fillna(mediane_ram)
        print(f"[NORMALIZER] ✓ ram_go          : NaN remplacés par médiane ({mediane_ram:.0f} Go)")

    # ── 4c. CPU → score ordinal ───────────────────────────────
    if 'cpu' in df.columns:
        df['cpu'] = df['cpu'].fillna('Inconnu')
        df['cpu_famille'] = df['cpu'].apply(_extraire_famille_cpu)
        print(f"[NORMALIZER] ✓ cpu             : famille extraite")

    # ── 4d. Stockage → Go ─────────────────────────────────────
    if 'stockage' in df.columns:
        df['stockage_go'] = df['stockage'].apply(_extraire_go_stockage)
        df['stockage_go'] = pd.to_numeric(df['stockage_go'], errors='coerce')
        mediane_stockage = df['stockage_go'].median() if df['stockage_go'].notna().any() else 0
        df['stockage_go'] = df['stockage_go'].fillna(mediane_stockage)
        print(f"[NORMALIZER] ✓ stockage        : valeur Go extraite, médiane={mediane_stockage:.0f}Go")

    # ── 4e. Écran → pouces ────────────────────────────────────
    if 'ecran' in df.columns:
        df['ecran_pouces'] = df['ecran'].apply(_extraire_pouces_ecran)
        df['ecran_pouces'] = pd.to_numeric(df['ecran_pouces'], errors='coerce')
        mediane_ecran = df['ecran_pouces'].median() if df['ecran_pouces'].notna().any() else 0
        df['ecran_pouces'] = df['ecran_pouces'].fillna(mediane_ecran)
        print(f"[NORMALIZER] ✓ ecran           : taille extraite, médiane={mediane_ecran:.1f}\"")

    return df, encoders


# ── Fonctions utilitaires ──────────────────────────────────────

def _extraire_famille_cpu(cpu_str: str) -> int:
    cpu_lower = str(cpu_str).lower()
    if 'celeron' in cpu_lower or 'pentium' in cpu_lower:
        return 1
    elif 'i3' in cpu_lower:
        return 3
    elif 'i5' in cpu_lower:
        return 5
    elif 'i7' in cpu_lower:
        return 7
    elif 'i9' in cpu_lower:
        return 9
    elif 'ryzen 3' in cpu_lower:
        return 4
    elif 'ryzen 5' in cpu_lower:
        return 6
    elif 'ryzen 7' in cpu_lower:
        return 8
    elif 'ryzen 9' in cpu_lower:
        return 10
    elif 'm1' in cpu_lower:
        return 7
    elif 'm2' in cpu_lower:
        return 8
    elif 'm3' in cpu_lower or 'm4' in cpu_lower:
        return 9
    else:
        return 0


def _extraire_go_stockage(stockage_str: str) -> float:
    import re
    if not stockage_str or str(stockage_str) == 'nan':
        return None
    match = re.search(r'(\d+)\s*(go|gb|to|tb)', str(stockage_str), re.IGNORECASE)
    if match:
        val   = float(match.group(1))
        unite = match.group(2).lower()
        if unite in ['to', 'tb']:
            val *= 1000
        return val
    return None


def _extraire_pouces_ecran(ecran_str: str) -> float:
    import re
    if not ecran_str or str(ecran_str) == 'nan':
        return None
    match = re.search(r'(\d{1,2}[.,]\d)', str(ecran_str))
    if match:
        return float(match.group(1).replace(',', '.'))
    return None


# ══════════════════════════════════════════════════════════════
# 5.  PIPELINE COMPLET NORMALIZER
# ══════════════════════════════════════════════════════════════
def normaliser(df: pd.DataFrame) -> tuple:
    """
    Applique toute la normalisation sur un DataFrame déjà nettoyé.

    Retourne : df, std_scaler, minmax_scaler, encoders
    """
    print("\n[NORMALIZER] Début de la normalisation...")

    df = convertir_devise(df)
    df, std_scaler, minmax_scaler = normaliser_prix(df)
    df, encoders = encoder_colonnes(df)

    print("[NORMALIZER] ✓ Normalisation terminée\n")
    return df, std_scaler, minmax_scaler, encoders


# ══════════════════════════════════════════════════════════════
# 6.  PIPELINE COMPLET : BD → Nettoyage → Normalisation
# ══════════════════════════════════════════════════════════════
def charger_nettoyer_normaliser(nom_produit: str = None,
                                 plateforme: str = None,
                                 limit: int = None) -> tuple:
    """
    Pipeline complet en une seule fonction :
        Base de données → cleaner.py → normalizer.py

    Exemple :
        df, std_sc, mm_sc, encoders = charger_nettoyer_normaliser()
        df, std_sc, mm_sc, encoders = charger_nettoyer_normaliser(nom_produit='iPhone')
    """
    df_clean = charger_et_nettoyer(
        nom_produit=nom_produit,
        plateforme=plateforme,
        limit=limit,
    )

    if df_clean.empty:
        print("[NORMALIZER] ✗ Aucune donnée à normaliser.")
        return df_clean, None, None, {}

    df_norm, std_scaler, minmax_scaler, encoders = normaliser(df_clean)
    return df_norm, std_scaler, minmax_scaler, encoders


# ══════════════════════════════════════════════════════════════
# 7.  TEST RAPIDE
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Pipeline complet : BD → nettoyage → normalisation
    df, std_sc, mm_sc, encoders = charger_nettoyer_normaliser()

    print("\n=== Aperçu des colonnes numériques pour clustering ===")
    cols_clustering = [
        'nom', 'prix_mad', 'prix_standard', 'prix_minmax',
        'ram_go', 'stockage_go', 'ecran_pouces',
        'cpu_famille', 'marque_encode', 'etat_encode',
        'plateforme_encode', 'prix_outlier'
    ]
    cols_dispo = [c for c in cols_clustering if c in df.columns]
    print(df[cols_dispo].head(10).to_string())

    print(f"\n=== Colonnes disponibles pour clustering ({len(cols_dispo)}) ===")
    for c in cols_dispo:
        print(f"  • {c}")
