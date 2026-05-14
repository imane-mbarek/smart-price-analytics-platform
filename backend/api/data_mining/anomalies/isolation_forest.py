from sklearn.ensemble import IsolationForest


def detection_isolation_forest(df, X_scaled):

    n = len(X_scaled)

    contamination = max(
        0.05,
        min(0.15, 3 / n)
    )

    model = IsolationForest(
        contamination=contamination,
        random_state=42
    )

    preds = model.fit_predict(X_scaled)

    df = df.copy()

    df['anomalie_if'] = (
        preds == -1
    )

    df['score_if'] = model.score_samples(
        X_scaled
    )

    return df
