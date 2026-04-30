import pymysql
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
CATEGORIES_MAPPING = {
    # Téléphones
    'iphone'     : 'telephone',
    'samsung'    : 'telephone',
    'redmi'      : 'telephone',
    'huawei'     : 'telephone',
    'xiaomi'     : 'telephone',
    'oppo'       : 'telephone',
    'realme'     : 'telephone',
    'phone'      : 'telephone',
    'smartphone' : 'telephone',
    'mobile'     : 'telephone',
    'phone'       : 'telephone',
    'phones'      : 'telephone',
    'smartphone'  : 'telephone',
    'smartphones' : 'telephone',
    'mobile'      : 'telephone',
    'mobiles'     : 'telephone',
    # Laptops
    'laptop'     : 'laptop',
    'pc portable': 'laptop',
    'macbook'    : 'laptop',
    'dell'       : 'laptop',
    'hp'         : 'laptop',
    'lenovo'     : 'laptop',
    'asus'       : 'laptop',
    'acer'       : 'laptop',
    'notebook'   : 'laptop',
    'ordinateur' : 'laptop',
    'laptop'      : 'ordinateur',
    'laptops'     : 'ordinateur',
    'pc'          : 'ordinateur',
    'ordinateur'  : 'ordinateur',
    'computer'    : 'ordinateur',
}

def get_data(nom_produit=None):
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', '26130')),
        ssl={'ssl-mode': 'REQUIRED'}
    )
    if nom_produit:
        query = f"SELECT * FROM api_produit WHERE nom LIKE '%{nom_produit}%'"
    else:
        query = "SELECT * FROM api_produit"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def detecter_categorie(nom):
    nom = str(nom).lower().strip()
    for mot_cle, categorie in CATEGORIES_MAPPING.items():
        if mot_cle in nom:
            return categorie
    return 'autre'

def nettoyer(df):
    # ── 1. Standardiser les noms de colonnes ──────────────────
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

    # ── 2. Supprimer les doublons ──────────────────────────────
    df = df.drop_duplicates(subset=['nom', 'plateforme', 'prix'])

    # ── 3. Nom ────────────────────────────────────────────────
    df = df.dropna(subset=['nom'])           # supprimer si vide
    df['nom'] = df['nom'].str.lower().str.strip()  # uniformiser

    # ── 4. Prix ───────────────────────────────────────────────
    df = df.dropna(subset=['prix'])          # supprimer si vide
    df['prix'] = df['prix'].astype(str)\
                            .str.replace('[^0-9.]', '', regex=True)
    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    df = df.dropna(subset=['prix'])          # supprimer après conversion
    df = df[df['prix'] > 0]                  # supprimer prix invalides

    # ── 5. Description ────────────────────────────────────────
    df['description'] = df['description'].fillna('')
    df['description'] = df['description'].str.strip()

    # ── 6. Catégorie ──────────────────────────────────────────
    df['categorie'] = df['nom'].apply(detecter_categorie)

    # ── 7. Plateforme ─────────────────────────────────────────
    df['plateforme'] = df['plateforme'].str.lower().str.strip()

    # ── 8. URL ────────────────────────────────────────────────
    df = df.dropna(subset=['url'])

    # ── 9. Date ───────────────────────────────────────────────
    if 'date_collecte' in df.columns:
        df['date_collecte'] = pd.to_datetime(
            df['date_collecte'], errors='coerce'
        )

    # ── 10. Réinitialiser l'index ─────────────────────────────
    df = df.reset_index(drop=True)
    print(f"Catégories détectées : {df['categorie'].value_counts().to_dict()}")

    return df