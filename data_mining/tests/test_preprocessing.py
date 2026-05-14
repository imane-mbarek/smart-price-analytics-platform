from data_mining.preprocessing.pipeline import build_pipeline


def sample_data():
    return [
        {"nom": "iPhone 15", "prix": 8500, "devise": "MAD", "plateforme": "Jumia", "etat": "neuf"},
        {"nom": "iPhone 15", "prix": 8500, "devise": "MAD", "plateforme": "Jumia", "etat": "neuf"},
        {"nom": "iPhone 14 occasion", "prix": 5000, "devise": "MAD", "plateforme": "Avito", "etat": "occasion"},
        {"nom": "iPhone cable", "prix": 100, "devise": "MAD", "plateforme": "Avito", "etat": "neuf"},
        {"nom": "Samsung Galaxy S24", "prix": 9000, "devise": "MAD", "plateforme": "Amazon", "etat": "neuf"},
    ]


def test_preprocessing_cleans_and_scales_backend_json():
    df_clean, df_scaled, _std, _mm, _encoders, features = build_pipeline(sample_data())

    assert df_clean is not None
    assert df_scaled is not None
    assert "prix_mad" in df_scaled.columns
    assert "prix_standard" in df_scaled.columns
    assert "plateforme_encode" in df_scaled.columns
    assert "prix_mad" in features
    assert len(df_scaled) == 4
