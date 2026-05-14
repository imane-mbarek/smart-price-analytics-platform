import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder


def normaliser_donnees(df: pd.DataFrame):

    scaler = StandardScaler()

    df = df.copy()

    # Standardisation prix
    df['prix_scaled'] = scaler.fit_transform(
        df[['prix']]
    )

    # Encodage plateforme
    plateforme_encoder = LabelEncoder()

    df['plateforme_encoded'] = plateforme_encoder.fit_transform(
        df['plateforme']
    )

    # Encodage catégorie
    if 'categorie' in df.columns:

        categorie_encoder = LabelEncoder()

        df['categorie_encoded'] = categorie_encoder.fit_transform(
            df['categorie']
        )

    return df, scaler
