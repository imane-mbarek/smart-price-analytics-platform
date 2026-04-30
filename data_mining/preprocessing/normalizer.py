import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ── Taux de conversion vers MAD (taux fixes) ──────────────────
TAUX_CONVERSION = {
    'MAD': 1.0,
    'USD': 10.0,   # 1 USD = 10 MAD
    'EUR': 11.0,   # 1 EUR = 11 MAD
    'GBP': 13.0,   # 1 GBP = 13 MAD
    'AED': 2.7,    # 1 AED = 2.7 MAD
    'SAR': 2.7,    # 1 SAR = 2.7 MAD
}

# ── 1. Conversion des devises ──────────────────────────────────
def convertir_devise(df, colonne_prix='prix', colonne_devise='devise'):
    def convertir(row):
        devise = str(row.get(colonne_devise, 'MAD')).upper().strip()
        taux = TAUX_CONVERSION.get(devise, 1.0)
        return row[colonne_prix] * taux
    
    if colonne_devise in df.columns:
        df['prix_mad'] = df.apply(convertir, axis=1)
    else:
        df['prix_mad'] = df[colonne_prix]
    
    return df

# ── 2. Normalisation des prix avec StandardScaler ─────────────
def normaliser_prix(df, colonne_prix='prix_mad'):
    scaler = StandardScaler()
    df['prix_normalise'] = scaler.fit_transform(df[[colonne_prix]])
    return df, scaler

# ── 3. Encodage des colonnes texte avec LabelEncoder ──────────
def encoder_colonnes(df, colonnes=['plateforme', 'categorie']):
    encoders = {}
    for col in colonnes:
        if col in df.columns:
            le = LabelEncoder()
            df[f'{col}_encode'] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
            print(f"{col} : {dict(zip(le.classes_, le.transform(le.classes_)))}")
    return df, encoders

# ── 4. Pipeline complet ───────────────────────────────────────
def normaliser(df):
    # Étape 1 : conversion devises
    df = convertir_devise(df)
    print(f" Devises converties en MAD")
    
    # Étape 2 : normalisation prix
    df, scaler = normaliser_prix(df)
    print(f"Prix normalisés")
    
    # Étape 3 : encodage colonnes texte
    df, encoders = encoder_colonnes(df)
    print(f"Colonnes encodées")
    
    return df, scaler, encoders