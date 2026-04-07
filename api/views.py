from rest_framework import viewsets
from .models import Produit
from .serializers import ProduitSerializer

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