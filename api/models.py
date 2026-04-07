from django.db import models
class Produit(models.Model):
    nom           = models.CharField(max_length=255)
    prix          = models.FloatField()
    plateforme    = models.CharField(max_length=100)
    url           = models.URLField()
    date_collecte = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


