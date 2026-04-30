import sys
import sys
sys.path.append('.')
from data_mining.preprocessing.pipeline import build_pipeline

# Lancer le pipeline complet
df_clean, df_scaled, scaler, encoders = build_pipeline("iPhone")

if df_scaled is not None:
    print("\nAperçu des données prêtes pour DM :")
    print(df_scaled[[
        'nom', 'prix_mad', 'prix_normalise',
        'plateforme', 'plateforme_encode',
        'categorie', 'categorie_encode'
    ]].to_string())