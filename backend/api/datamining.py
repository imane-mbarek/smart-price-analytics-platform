import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

def analyser_produits(produits_qs):
    df = pd.DataFrame(list(produits_qs.values(
        'id', 'nom', 'description', 'prix', 'plateforme', 'categorie'
    )))

    if df.empty or len(df) < 3:
        return {'erreur': 'Pas assez de données pour analyser'}

    resultats = {}

    # ── 1. Nettoyage ──────────────────────────────────────
    avant       = len(df)
    df          = df.drop_duplicates(subset=['nom', 'prix'])
    df          = df.dropna(subset=['prix'])
    df          = df[df['prix'] > 0]
    apres       = len(df)
    resultats['nettoyage'] = {
        'avant'    : avant,
        'apres'    : apres,
        'supprimes': avant - apres
    }

    # ── 2. Statistiques descriptives ──────────────────────
    resultats['statistiques'] = {
        'min'       : round(float(df['prix'].min()), 2),
        'max'       : round(float(df['prix'].max()), 2),
        'moyenne'   : round(float(df['prix'].mean()), 2),
        'mediane'   : round(float(df['prix'].median()), 2),
        'ecart_type': round(float(df['prix'].std()), 2),
        'q1'        : round(float(df['prix'].quantile(0.25)), 2),
        'q3'        : round(float(df['prix'].quantile(0.75)), 2),
        'total'     : len(df)
    }

    # ── 3. Clustering K-Means ─────────────────────────────
    X        = df[['prix']].values
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_clusters = min(3, len(df))
    kmeans     = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    centres   = sorted(enumerate(kmeans.cluster_centers_.flatten()), key=lambda x: x[1])
    gammes    = ['bas_de_gamme', 'milieu_de_gamme', 'haut_de_gamme']
    label_map = {c[0]: gammes[i] for i, c in enumerate(centres)}
    df['gamme'] = df['cluster'].map(label_map)

    resultats['clusters'] = []
    for gamme in gammes:
        subset = df[df['gamme'] == gamme]
        if not subset.empty:
            resultats['clusters'].append({
                'gamme'  : gamme,
                'min'    : round(float(subset['prix'].min()), 2),
                'max'    : round(float(subset['prix'].max()), 2),
                'moyenne': round(float(subset['prix'].mean()), 2),
                'count'  : len(subset)
            })

    # ── 4. Détection anomalies Isolation Forest ───────────
    iso = IsolationForest(contamination=0.1, random_state=42)
    df['anomalie'] = iso.fit_predict(X_scaled)
    df['anomalie'] = df['anomalie'].map({1: False, -1: True})

    resultats['anomalies'] = df[df['anomalie'] == True][
        ['nom', 'prix', 'plateforme']
    ].to_dict('records')

    # ── 5. Meilleure offre recommandée ────────────────────
    normaux = df[df['anomalie'] == False]
    if not normaux.empty:
        meilleure = normaux.nsmallest(1, 'prix').iloc[0]
        resultats['meilleure_offre'] = {
            'nom'       : meilleure['nom'],
            'prix'      : round(float(meilleure['prix']), 2),
            'plateforme': meilleure['plateforme'],
            'gamme'     : meilleure['gamme'],
            'description': meilleure['description']
        }

    # ── 6. Données pour graphiques React ─────────────────
    resultats['par_plateforme'] = []
    for plat in df['plateforme'].unique():
        subset = df[df['plateforme'] == plat]
        resultats['par_plateforme'].append({
            'plateforme': plat,
            'min'       : round(float(subset['prix'].min()), 2),
            'max'       : round(float(subset['prix'].max()), 2),
            'moyenne'   : round(float(subset['prix'].mean()), 2),
            'count'     : len(subset)
        })

    resultats['par_categorie'] = []
    for cat in df['categorie'].unique():
        subset = df[df['categorie'] == cat]
        resultats['par_categorie'].append({
            'categorie': cat,
            'min'      : round(float(subset['prix'].min()), 2),
            'max'      : round(float(subset['prix'].max()), 2),
            'moyenne'  : round(float(subset['prix'].mean()), 2),
            'count'    : len(subset)
        })

    resultats['distribution'] = [round(float(p), 2) for p in df['prix'].tolist()]
    resultats['produits']     = df[[
        'id', 'nom', 'prix', 'plateforme', 'categorie', 'gamme', 'anomalie', 'description'
    ]].to_dict('records')

    return resultats