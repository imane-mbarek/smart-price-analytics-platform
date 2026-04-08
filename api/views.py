from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Produit, Recherche, SurveillancePrix
from .serializers import (
    ProduitSerializer, RechercheSerializer,
    SurveillancePrixSerializer, RegisterSerializer, UserSerializer
)
from .scraper import scrape_all
import re, csv, threading
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.all()
    serializer_class = ProduitSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Produit
from .serializers import ProduitSerializer
from .scraper import scrape_all
import re

# ── Clean price helper ───────────────────────
def clean_price(prix_str):
    prix_clean = re.sub(r'[^\d.]', '', str(prix_str))
    try:
        return float(prix_clean)
    except:
        return 0.0

# ── ViewSet ──────────────────────────────────
class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.all()
    serializer_class = ProduitSerializer

    # GET /api/produits/search/?q=iphone
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')

        # 1. Validate query
        if not query:
            return Response(
                {'error': 'Please provide a search term ?q='},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Scrape all platforms
        print(f"🔍 Scraping for : {query}")
        resultats = scrape_all(query)

        if not resultats:
            return Response(
                {'error': 'No results found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Save to database
        saved = []
        for r in resultats:
            produit = Produit.objects.create(
                nom        = r['nom'],
                prix       = clean_price(r['prix']),
                plateforme = r['plateforme'],
                url        = r['url']
            )
            saved.append(produit)

        # 4. Return results
        serializer = ProduitSerializer(saved, many=True)
        return Response({
            'query'    : query,
            'count'    : len(saved),
            'results'  : serializer.data
        })

    # GET /api/produits/by_platform/
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        platform = request.query_params.get('platform', '')
        produits = Produit.objects.filter(plateforme=platform)
        serializer = ProduitSerializer(produits, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.filter(nom__icontains=query) if query else Produit.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="produits.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Nom', 'Prix', 'Plateforme', 'URL', 'Date'])
        for p in produits:
            writer.writerow([p.id, p.nom, p.prix, p.plateforme, p.url, p.date_collecte])

        return response
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.filter(nom__icontains=query) if query else Produit.objects.all()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="produits.pdf"'

        p   = canvas.Canvas(response, pagesize=A4)
        w, h = A4
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, h - 50, f"Résultats : {query}")
        p.setFont("Helvetica", 10)

        y = h - 80
        for prod in produits:
            if y < 50:
                p.showPage()
                y = h - 50
            ligne = f"{prod.nom[:50]}  |  {prod.prix} MAD  |  {prod.plateforme}"
            p.drawString(50, y, ligne)
            y -= 18

        p.save()
        return response

# ── Recherche ViewSet ─────────────────────────────────────────
class RechercheViewSet(viewsets.ModelViewSet):
    queryset         = Recherche.objects.all().order_by('-date')
    serializer_class = RechercheSerializer

# ── Surveillance Prix ViewSet ─────────────────────────────────
class SurveillancePrixViewSet(viewsets.ModelViewSet):
    queryset         = SurveillancePrix.objects.all()
    serializer_class = SurveillancePrixSerializer

    # POST /api/surveillance/check_alerts/
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        alertes    = SurveillancePrix.objects.filter(notifie=False)
        declenchee = []

        for alerte in alertes:
            prix_actuels = Produit.objects.filter(
                nom__icontains = alerte.produit,
                prix__lte      = alerte.prix_cible
            )
            if prix_actuels.exists():
                alerte.notifie = True
                alerte.save()
                declenchee.append({
                    'produit'   : alerte.produit,
                    'prix_cible': alerte.prix_cible,
                    'offres'    : ProduitSerializer(prix_actuels, many=True).data
                })

        return Response({
            'alertes_declenchees': len(declenchee),
            'details'            : declenchee
        })

# ── Auth : Register ───────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    queryset         = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]