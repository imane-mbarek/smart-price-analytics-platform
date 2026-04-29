import pymysql
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def get_data(nom_produit=None):
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        ssl={'ssl-mode': 'REQUIRED'}
    )
    
    if nom_produit:
        query = f"SELECT * FROM api_produit WHERE nom LIKE '%{nom_produit}%'"
    else:
        query = "SELECT * FROM api_produit"
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def nettoyer(df):
    # Supprimer doublons
    df = df.drop_duplicates(subset=['nom', 'prix'])
    # Supprimer valeurs manquantes
    df = df.dropna(subset=['prix'])
    # Supprimer prix invalides
    df = df[df['prix'] > 0]
    return df