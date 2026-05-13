import pandas as pd

from sklearn.preprocessing import StandardScaler

from data_mining.clustering.kmeans_model import (
    clustering_kmeans
)


def test_kmeans():

    df = pd.DataFrame({
        'prix': [100, 200, 300]
    })

    scaler = StandardScaler()

    X = scaler.fit_transform(
        df[['prix']]
    )

    df, result = clustering_kmeans(
        df,
        X
    )

    assert 'cluster_kmeans' in df.columns