import pandas as pd

from api.data_mining.preprocessing.cleaner import (
    nettoyer_dataframe
)


def test_cleaner():

    data = {
        'nom': ['iphone', 'iphone'],
        'prix': [1000, 1000]
    }

    df = pd.DataFrame(data)

    cleaned, rapport = nettoyer_dataframe(df)

    assert len(cleaned) == 1
