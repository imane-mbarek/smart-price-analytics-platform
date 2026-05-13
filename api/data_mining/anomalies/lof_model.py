from sklearn.neighbors import LocalOutlierFactor


def detection_lof(df, X_scaled):

    n = len(X_scaled)

    n_neighbors = max(
        2,
        min(20, n // 5)
    )

    model = LocalOutlierFactor(
        n_neighbors=n_neighbors
    )

    preds = model.fit_predict(X_scaled)

    df = df.copy()

    df['anomalie_lof'] = (
        preds == -1
    )

    df['score_lof'] = (
        -model.negative_outlier_factor_
    )

    return df