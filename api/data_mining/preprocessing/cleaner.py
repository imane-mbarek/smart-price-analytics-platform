import pandas as pd


def nettoyer_dataframe(df: pd.DataFrame):
    rapport = {}

    avant = len(df)

    # Supprimer doublons
    df = df.drop_duplicates(subset=['nom', 'prix'])

    rapport['doublons_supprimes'] = avant - len(df)

    # Supprimer prix invalides
    df = df.dropna(subset=['prix'])

    df = df[df['prix'] > 0]

    rapport['prix_invalides_supprimes'] = (
        avant - rapport['doublons_supprimes'] - len(df)
    )

    # Supprimer outliers extrêmes
    mediane = df['prix'].median()

    seuil_haut = mediane * 10

    avant_outliers = len(df)

    df = df[df['prix'] <= seuil_haut]

    rapport['outliers_extremes_supprimes'] = (
        avant_outliers - len(df)
    )

    rapport['avant'] = avant
    rapport['apres'] = len(df)

    return df.reset_index(drop=True), rapport