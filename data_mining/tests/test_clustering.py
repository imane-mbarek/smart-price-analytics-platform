from data_mining.clustering import compute_pca, run_dbscan, run_kmeans
from data_mining.preprocessing.pipeline import build_pipeline


def test_clustering_outputs_labels_and_pca_2d():
    data = [
        {"nom": "HP laptop i5 8Go", "prix": 4500, "devise": "MAD", "plateforme": "Jumia"},
        {"nom": "Dell laptop i7 16Go", "prix": 9000, "devise": "MAD", "plateforme": "Amazon"},
        {"nom": "Lenovo laptop i3 8Go", "prix": 3500, "devise": "MAD", "plateforme": "Avito"},
        {"nom": "Macbook M2", "prix": 14000, "devise": "MAD", "plateforme": "Jumia"},
    ]
    _clean, df, _std, _mm, _encoders, features = build_pipeline(data)

    kmeans = run_kmeans(df, features)
    pca = compute_pca(df, features, labels=[item["cluster"] for item in kmeans["items"]])
    dbscan = run_dbscan(df, features)

    assert len(kmeans["items"]) == len(df)
    assert len(kmeans["centroids"]) <= 3
    assert {"x", "y"}.issubset(pca[0].keys())
    assert len(dbscan) == len(df)
