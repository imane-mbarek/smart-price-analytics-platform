from .cleaner import nettoyer_dataframe

from .normalizer import normaliser_donnees


def preprocess_pipeline(df):

    # Nettoyage
    df, rapport = nettoyer_dataframe(df)

    # Normalisation
    df, scaler = normaliser_donnees(df)

    return df, rapport, scaler
