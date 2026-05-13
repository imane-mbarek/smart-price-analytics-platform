import pandas as pd

from mlxtend.preprocessing import TransactionEncoder

from mlxtend.frequent_patterns import (
    apriori,
    association_rules
)


def construire_transactions(df):

    transactions = []

    for _, row in df.iterrows():

        items = []

        items.append(
            f"plateforme_{row['plateforme']}"
        )

        if 'gamme' in row:
            items.append(row['gamme'])

        transactions.append(items)

    return transactions


def regles_association(df):

    transactions = construire_transactions(df)

    te = TransactionEncoder()

    te_array = te.fit_transform(
        transactions
    )

    df_trans = pd.DataFrame(
        te_array,
        columns=te.columns_
    )

    itemsets = apriori(
        df_trans,
        min_support=0.1,
        use_colnames=True
    )

    rules = association_rules(
        itemsets,
        metric='confidence',
        min_threshold=0.5
    )

    return rules.to_dict('records')