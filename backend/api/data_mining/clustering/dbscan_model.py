from sklearn.cluster import DBSCAN


def clustering_dbscan(df, X_scaled):

    n = len(X_scaled)

    eps = 0.5 if n > 20 else 0.8

    min_samples = max(2, n // 10)

    model = DBSCAN(
        eps=eps,
        min_samples=min_samples
    )

    df = df.copy()

    df['cluster_dbscan'] = model.fit_predict(
        X_scaled
    )

    return df, {
        'eps': eps,
        'min_samples': min_samples
    }
