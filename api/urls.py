from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProduitViewSet, RechercheViewSet, SurveillancePrixViewSet,
    PanierViewSet, NotificationViewSet
)

router = DefaultRouter()
router.register(r'produits',       ProduitViewSet,          basename='produit')
router.register(r'recherches',     RechercheViewSet,        basename='recherche')
router.register(r'surveillances',  SurveillancePrixViewSet, basename='surveillance')
router.register(r'panier',         PanierViewSet,           basename='panier')
router.register(r'notifications',  NotificationViewSet,     basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
