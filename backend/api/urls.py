from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProduitViewSet, RechercheViewSet, SurveillancePrixViewSet,
    PanierViewSet, NotificationViewSet, RegisterView
)

router = DefaultRouter()
router.register(r'produits',       ProduitViewSet,          basename='produit')
router.register(r'recherches',     RechercheViewSet,        basename='recherche')
router.register(r'surveillances',  SurveillancePrixViewSet, basename='surveillance')
router.register(r'panier',         PanierViewSet,           basename='panier')
router.register(r'notifications',  NotificationViewSet,     basename='notification')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
