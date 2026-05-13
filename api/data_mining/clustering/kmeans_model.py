from sklearn.cluster import KMeans


GAMMES = [
    'bas_de_gamme',
    'milieu_de_gamme',
    'haut_de_gamme'
]


def choisir_k(n):

    if n < 6:
        return min(2, n)

    return 3


def clustering_kmeans(df, X_scaled):

    k = choisir_k(len(df))

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    df = df.copy()

    df['cluster_kmeans'] = model.fit_predict(X_scaled)

    centres = sorted(
        enumerate(model.cluster_centers_.flatten()),
        key=lambda x: x[1]
    )

    gammes_k = GAMMES[-k:]

    label_map = {
        c[0]: gammes_k[i]
        for i, c in enumerate(centres)
    }

    df['gamme'] = df['cluster_kmeans'].map(label_map)

    return df, {
        'k': k,
        'inertie': round(float(model.inertia_), 2)
    }