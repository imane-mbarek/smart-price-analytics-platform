from django.db import models
from django.contrib.auth.models import User

class Produit(models.Model):
    nom           = models.CharField(max_length=255)
    description   = models.TextField(blank=True, null=True)
    prix          = models.FloatField()
    categorie     = models.CharField(max_length=100, default='non_specifie')
    plateforme    = models.CharField(max_length=100)
    url           = models.URLField()
    image         = models.URLField(blank=True, null=True)   # ← vraie image produit
    en_stock      = models.BooleanField(default=True)
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

class Notification(models.Model):
    TYPE_CHOICES = [
        ('baisse_prix',  'Baisse de prix'),
        ('hausse_prix',  'Hausse de prix'),
        ('rupture',      'Rupture de stock'),
        ('retour_stock', 'Retour en stock'),
    ]
 
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    produit     = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='notifications')
    type_notif  = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message     = models.TextField()
    ancien_prix = models.FloatField(null=True, blank=True)
    nouveau_prix= models.FloatField(null=True, blank=True)
    lue         = models.BooleanField(default=False)
    date        = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-date']
 
    def __str__(self):
        return f"{self.utilisateur.username} | {self.type_notif} | {self.produit.nom}"


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
    

