from django.db import models
from django.contrib.auth.models import User

class Produit(models.Model):
    nom           = models.CharField(max_length=255)
    prix          = models.FloatField()
    plateforme    = models.CharField(max_length=100)
    url           = models.URLField()
    date_collecte = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Recherche(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    produit     = models.CharField(max_length=255)
    date        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.produit

class SurveillancePrix(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit     = models.CharField(max_length=255)
    prix_cible  = models.FloatField()
    notifie     = models.BooleanField(default=False)
    date_ajout  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produit} < {self.prix_cible}"


