import sys
sys.path.append('.')
from data_mining.preprocessing.cleaner import get_data, nettoyer

# Récupérer données
df = get_data("iPhone")
print("Données brutes :", len(df))

# Nettoyer
df_clean = nettoyer(df)
print("Données nettoyées :", len(df_clean))
print(df_clean)