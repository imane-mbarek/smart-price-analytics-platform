"""
0005_produit_categorie.py
Migration : ajout du champ `categorie` sur le modèle Produit.

Ce champ est requis par datamining.py et views.py mais absent du models.py initial.
Valeur par défaut : 'non_specifie' pour les produits existants.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_produit_description_prix'),
    ]

    operations = [
        migrations.AddField(
            model_name='produit',
            name='categorie',
            field=models.CharField(
                max_length=100,
                default='non_specifie',
                blank=True,
            ),
        ),
    ]