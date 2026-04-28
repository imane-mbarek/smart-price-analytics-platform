import sqlite3
import pandas as pd

def get_data(nom_produit=None):
    conn = sqlite3.connect('db.sqlite3')
    
    if nom_produit:
        query = f"""
            SELECT id, nom, description, prix, plateforme, url
            FROM api_produit
            WHERE nom LIKE '%{nom_produit}%'
        """
    else:
        query = "SELECT id, nom, description, prix, plateforme, url FROM api_produit"
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df