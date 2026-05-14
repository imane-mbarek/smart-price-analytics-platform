# Module Data Mining

Ce dossier contient le module analytique de la plateforme Smart Price Analytics.
Il reçoit les offres brutes du scraping ou du backend Django, nettoie les données,
calcule les statistiques, détecte les gammes de prix, signale les anomalies et
retourne un résultat JSON exploitable par l'API REST.

## Installation

```bash
pip install -r data_mining/requirements.txt
```

## Point d'entree backend

```python
from data_mining.api.dm_service import analyze

resultats = analyze([
    {
        "nom": "iPhone 15",
        "prix": 8500,
        "devise": "MAD",
        "plateforme": "Jumia.ma",
        "vendeur": "Store_XY",
        "note_vendeur": 4.2,
        "etat": "neuf",
    }
])
```

La fonction retourne un dictionnaire avec les cles `stats`, `clusters`,
`anomalies`, `rules`, `pca` et `metadata`.

## Tests

```bash
pytest data_mining/tests/
```
