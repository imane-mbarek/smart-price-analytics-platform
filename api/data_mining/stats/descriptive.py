def calculer_statistiques(df):

    prix = df['prix']

    q1 = float(prix.quantile(0.25))
    q3 = float(prix.quantile(0.75))

    return {
        'min': round(float(prix.min()), 2),
        'max': round(float(prix.max()), 2),
        'moyenne': round(float(prix.mean()), 2),
        'mediane': round(float(prix.median()), 2),
        'ecart_type': round(float(prix.std()), 2),
        'q1': round(q1, 2),
        'q3': round(q3, 2),
        'iqr': round(q3 - q1, 2),
        'skewness': round(float(prix.skew()), 4),
        'kurtosis': round(float(prix.kurtosis()), 4),
        'total': len(df),
    }
