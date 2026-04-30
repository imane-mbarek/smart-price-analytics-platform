import sys
sys.path.append('.')
import pandas as pd
from data_mining.preprocessing.cleaner import get_data, nettoyer
from data_mining.preprocessing.normalizer import normaliser

def build_pipeline(nom_produit=None):
    """
    Pipeline complet :
    raw data → nettoyage → normalisation → encodage → prêt pour DM
    """
    
    print("=" * 50)
    print("   PIPELINE PRETRAITEMENT DATA MINING")
    print("=" * 50)

    # ── Étape 1 : Récupération des données ────────────────────
    print("\n Étape 1 : Récupération des données...")
    df_raw = get_data(nom_produit)
    print(f"   Données brutes : {len(df_raw)} lignes")

    if df_raw.empty or len(df_raw) < 3:
        print("Pas assez de données !")
        return None, None, None, None

    # ── Étape 2 : Nettoyage ───────────────────────────────────
    print("\n Étape 2 : Nettoyage...")
    avant = len(df_raw)
    df_clean = nettoyer(df_raw.copy())
    apres = len(df_clean)
    print(f"   Lignes avant    : {avant}")
    print(f"   Lignes après    : {apres}")
    print(f"   Supprimées      : {avant - apres}")

    if df_clean.empty or len(df_clean) < 3:
        print("Pas assez de données après nettoyage !")
        return None, None, None, None

    # ── Étape 3 : Normalisation et encodage ───────────────────
    print("\n Étape 3 : Normalisation et encodage...")
    df_scaled, scaler, encoders = normaliser(df_clean.copy())

    # ── Étape 4 : Rapport final ───────────────────────────────
    print("\n Rapport final :")
    print(f"   Colonnes dispo  : {list(df_scaled.columns)}")
    print(f"   Catégories      : {df_scaled['categorie'].value_counts().to_dict()}")
    print(f"   Plateformes     : {df_scaled['plateforme'].value_counts().to_dict()}")
    print(f"   Prix min (MAD)  : {df_scaled['prix_mad'].min()}")
    print(f"   Prix max (MAD)  : {df_scaled['prix_mad'].max()}")
    print(f"   Prix moyen(MAD) : {round(df_scaled['prix_mad'].mean(), 2)}")
    print("\nPipeline terminé avec succès !")
    print("=" * 50)

    return df_clean, df_scaled, scaler, encoders


# ── Test direct ───────────────────────────────────────────────
if __name__ == "__main__":
    df_clean, df_scaled, scaler, encoders = build_pipeline("iPhone")

    if df_scaled is not None:
        print("\nAperçu des données prêtes pour DM :")
        print(df_scaled[[
            'nom', 'prix_mad', 'prix_normalise',
            'plateforme', 'plateforme_encode',
            'categorie', 'categorie_encode'
        ]].to_string())