"""
db_connector.py  –  Connexion à la base de données MySQL
Module Data Mining | Licence IASD 2025/2026

Rôle : fichier unique de connexion, importé par cleaner.py et dm_service.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()


# ══════════════════════════════════════════════════════════════
# 1.  CONNEXION VIA SQLALCHEMY (compatible pandas)
# ══════════════════════════════════════════════════════════════

def get_engine():
    """
    Retourne un engine SQLAlchemy.
    Utilisé par pd.read_sql() pour éviter le warning pandas.
    """
    try:
        url = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '26130')}"
            f"/{os.getenv('DB_NAME')}?ssl_disabled=false"
        )
        engine = create_engine(url)
        # Test rapide de connexion
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DB] ✓ Connexion établie avec succès")
        return engine
    except Exception as e:
        print(f"[DB] ✗ Erreur de connexion : {e}")
        raise


# ══════════════════════════════════════════════════════════════
# 2.  CHARGEMENT DES DONNÉES
# ══════════════════════════════════════════════════════════════

def get_data(nom_produit: str = None,
             plateforme: str = None,
             limit: int = None) -> pd.DataFrame:
    """
    Charge les données depuis la table api_produit.

    Paramètres
    ----------
    nom_produit : filtre sur le nom (recherche partielle)
    plateforme  : filtre sur la plateforme (ex: 'Jumia', 'Avito')
    limit       : nombre maximum de lignes

    Note : pas de colonne 'categorie' dans la BD,
           elle est détectée automatiquement par cleaner.py

    Retourne
    --------
    pd.DataFrame : id, nom, description, prix, plateforme, url, date_collecte
    """
    engine = get_engine()

    # Construction des filtres
    conditions = []
    params     = {}

    if nom_produit:
        conditions.append("nom LIKE :nom")
        params['nom'] = f"%{nom_produit}%"

    if plateforme:
        conditions.append("plateforme = :plateforme")
        params['plateforme'] = plateforme

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    limit_clause = f"LIMIT {limit}" if limit else ""

    query = f"""
        SELECT
            id,
            nom,
            description,
            prix,
            plateforme,
            url,
            date_collecte
        FROM api_produit
        {where_clause}
        {limit_clause}
    """

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params if params else None)
        print(f"[DB] ✓ {len(df)} produits chargés"
              + (f" pour '{nom_produit}'" if nom_produit else ""))
        return df
    except Exception as e:
        print(f"[DB] ✗ Erreur lors du chargement : {e}")
        raise


def get_stats_base() -> dict:
    """Retourne des stats rapides sur la base."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("""
                SELECT
                    COUNT(*)                   AS total_produits,
                    COUNT(DISTINCT plateforme) AS nb_plateformes,
                    MIN(prix)                  AS prix_min,
                    MAX(prix)                  AS prix_max,
                    AVG(prix)                  AS prix_moyen
                FROM api_produit
            """), conn)
        return df.iloc[0].to_dict()
    except Exception as e:
        print(f"[DB] ✗ Erreur stats : {e}")
        raise


def get_plateformes_disponibles() -> list:
    """Retourne la liste des plateformes présentes dans la base."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text("SELECT DISTINCT plateforme FROM api_produit"), conn
            )
        return df['plateforme'].tolist()
    except Exception as e:
        print(f"[DB] ✗ Erreur : {e}")
        raise


# ══════════════════════════════════════════════════════════════
# 3.  TEST RAPIDE
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=== Test de connexion ===")
    stats = get_stats_base()
    print(f"  Total produits  : {int(stats['total_produits'])}")
    print(f"  Plateformes     : {int(stats['nb_plateformes'])}")
    print(f"  Prix min / max  : {stats['prix_min']} / {stats['prix_max']} MAD")
    print(f"  Prix moyen      : {round(stats['prix_moyen'], 2)} MAD")

    print("\n=== Plateformes disponibles ===")
    plateformes = get_plateformes_disponibles()
    for p in plateformes:
        print(f"  • {p}")

    print("\n=== Test chargement 5 produits ===")
    df = get_data(limit=5)
    print(df[['nom', 'prix', 'plateforme']].to_string())