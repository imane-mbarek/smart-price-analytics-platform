import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def appliquer_pca(df):

    df_feat = df[['prix']].copy()

    plat_dummies = pd.get_dummies(
        df['plateforme'],
        prefix='plat'
    )

    df_feat = pd.concat(
        [df_feat, plat_dummies],
        axis=1
    )

    scaler = StandardScaler()

    X = scaler.fit_transform(
        df_feat.fillna(0)
    )

    pca = PCA(n_components=2)

    coords = pca.fit_transform(X)

    points = []

    for i, row in df.iterrows():

        points.append({
            'nom': row['nom'],
            'prix': row['prix'],
            'x': float(coords[i, 0]),
            'y': float(coords[i, 1]),
        })

    return {
        'points': points
    }