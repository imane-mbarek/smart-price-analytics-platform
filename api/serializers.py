from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Produit, Recherche, SurveillancePrix

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Produit
        fields = '__all__' 
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
        user = User.objects.create_user(
            username = validated_data['username'],
            email    = validated_data.get('email', ''),
            password = validated_data['password']
        )
        return user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email']