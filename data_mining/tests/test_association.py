from data_mining.api.dm_service import analyze
from data_mining.association import extract_rules
from data_mining.preprocessing.pipeline import build_pipeline


def test_association_rules_and_dm_service_shape():
    data = [
        {"nom": "HP laptop i5", "prix": 4000, "devise": "MAD", "plateforme": "Avito", "etat": "occasion"},
        {"nom": "HP laptop i7", "prix": 9000, "devise": "MAD", "plateforme": "Amazon", "etat": "neuf"},
        {"nom": "Dell laptop i5", "prix": 5000, "devise": "MAD", "plateforme": "Avito", "etat": "occasion"},
        {"nom": "Macbook M2", "prix": 14000, "devise": "MAD", "plateforme": "Amazon", "etat": "neuf"},
    ]
    _clean, df, _std, _mm, _encoders, _features = build_pipeline(data)
    rules = extract_rules(df, min_support=0.2, min_confidence=0.5)
    result = analyze(data)

    assert rules
    assert {"stats", "clusters", "anomalies", "rules", "pca"}.issubset(result.keys())
