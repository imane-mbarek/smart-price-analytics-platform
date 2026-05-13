import pandas as pd

from .preprocessing.pipeline import preprocess_pipeline

from .stats.descriptive import calculer_statistiques

from .clustering.kmeans_model import clustering_kmeans

from .clustering.dbscan_model import clustering_dbscan

from .clustering.pca_viz import appliquer_pca

from .anomalies.isolation_forest import detection_isolation_forest

from .anomalies.lof_model import detection_lof

from .association.rules import regles_association

def analyze(raw_data):

    df = pd.DataFrame(raw_data)

    # PREPROCESSING
    df, rapport, scaler = preprocess_pipeline(df)

    X_scaled = df[['prix_scaled']].values

    # STATS
    stats = calculer_statistiques(df)

    # KMEANS
    df, kmeans = clustering_kmeans(
        df,
        X_scaled
    )

    # DBSCAN
    df, dbscan = clustering_dbscan(
        df,
        X_scaled
    )

    # ISOLATION FOREST
    df = detection_isolation_forest(
        df,
        X_scaled
    )

    # LOF
    df = detection_lof(
        df,
        X_scaled
    )

    # CONSENSUS
    df['suspect'] = (
        df['anomalie_if']
        &
        df['anomalie_lof']
    )

    # PCA
    pca = appliquer_pca(df)

    # RULES
    rules = regles_association(df)

    return {

        'nettoyage': rapport,

        'stats': stats,

        'kmeans': kmeans,

        'dbscan': dbscan,

        'pca': pca,

        'rules': rules,

        'produits': df.to_dict(
            orient='records'
        )
    }