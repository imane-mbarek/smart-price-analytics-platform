from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Produit, Recherche, SurveillancePrix, Panier, Notification, HistoriquePrix


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Produit
        fields = '__all__'


class HistoriquePrixSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HistoriquePrix
        fields = '__all__'


class PanierSerializer(serializers.ModelSerializer):
    produit_detail = ProduitSerializer(source='produit', read_only=True)
    variation_prix = serializers.SerializerMethodField()

    class Meta:
        model  = Panier
        fields = ['id', 'produit', 'produit_detail', 'prix_au_moment', 'date_ajout', 'variation_prix']
        read_only_fields = ['prix_au_moment', 'date_ajout']

    def get_variation_prix(self, obj):
        """Calcule la variation de prix depuis l'ajout au panier."""
        prix_actuel = obj.produit.prix
        if obj.prix_au_moment and obj.prix_au_moment > 0:
            variation = ((prix_actuel - obj.prix_au_moment) / obj.prix_au_moment) * 100
            return round(variation, 2)
        return 0


class NotificationSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model  = Notification
        fields = ['id', 'produit', 'produit_nom', 'type_notif', 'message',
                  'ancien_prix', 'nouveau_prix', 'lue', 'date']


class RechercheSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Recherche
        fields = '__all__'


class SurveillancePrixSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SurveillancePrix
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email']