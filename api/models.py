from django.db import models
from django.contrib.auth.models import User

class Produit(models.Model):
    nom           = models.CharField(max_length=255)
    description   = models.TextField(blank=True, null=True)
    prix          = models.FloatField()
    plateforme    = models.CharField(max_length=100)
    url           = models.URLField()
    date_collecte = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class HistoriquePrix(models.Model):
    """Sauvegarde le prix à chaque scraping pour détecter les variations."""
    produit    = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='historique_prix')
    prix       = models.FloatField()
    en_stock   = models.BooleanField(default=True)
    date       = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.produit.nom} — {self.prix} MAD"

class Panier(models.Model):
    """Produits sauvegardés par un utilisateur (surveillés)."""
    utilisateur    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='panier')
    produit        = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='dans_paniers')
    prix_au_moment = models.FloatField()   # prix quand ajouté au panier
    date_ajout     = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('utilisateur', 'produit')  # un produit une seule fois par panier
 
    def __str__(self):
        return f"{self.utilisateur.username} → {self.produit.nom}"



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
    
class Prix(models.Model):
    produit    = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='historique_prix')
    valeur     = models.FloatField()
    devise     = models.CharField(max_length=10, default='MAD')
    plateforme = models.CharField(max_length=100)
    date       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produit.nom} — {self.valeur} {self.devise}"

