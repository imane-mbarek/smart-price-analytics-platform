from data_mining.anomaly import detect_anomalies
from data_mining.preprocessing.pipeline import build_pipeline


def test_anomaly_returns_alert_levels():
    data = [
        {"nom": "iPhone 15", "prix": 8500, "devise": "MAD", "plateforme": "Jumia"},
        {"nom": "iPhone 15 Pro", "prix": 12000, "devise": "MAD", "plateforme": "Amazon"},
        {"nom": "iPhone 14", "prix": 7000, "devise": "MAD", "plateforme": "Avito"},
        {"nom": "iPhone suspect", "prix": 1, "devise": "MAD", "plateforme": "Avito"},
        {"nom": "iPhone 13", "prix": 6000, "devise": "MAD", "plateforme": "Jumia"},
    ]
    _clean, df, _std, _mm, _encoders, features = build_pipeline(data)

    anomalies = detect_anomalies(df, features)

    assert len(anomalies) == len(df)
    assert all(item["niveau"] in {"rouge", "orange", "vert"} for item in anomalies)
