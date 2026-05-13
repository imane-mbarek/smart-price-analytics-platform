from django.contrib import admin
from .models import Produit, Recherche, SurveillancePrix, Prix

admin.site.register(Produit)
admin.site.register(Recherche)
admin.site.register(SurveillancePrix)
admin.site.register(Prix)