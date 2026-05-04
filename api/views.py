from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Produit, Recherche, SurveillancePrix
from .serializers import (
    ProduitSerializer, RechercheSerializer,
    SurveillancePrixSerializer, RegisterSerializer
)
from .scraper import scrape_jumia, scrape_avito, scrape_ebay, valider_categorie
from .datamining import analyser_produits
import re, csv, threading, uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

_progression = {}

def clean_price(prix_str):
    prix_clean = re.sub(r'[^\d.]', '', str(prix_str))
    try:
        return float(prix_clean)
    except:
        return 0.0

def _scrape_background(task_id, query, plateformes_list):
    _progression[task_id] = {
        'statut'     : 'en_cours',
        'progression': 0,
        'message'    : 'Démarrage...',
        'resultats'  : []
    }

    try:
        resultats = []
        total     = len(plateformes_list)
        fait      = 0

        if 'jumia' in plateformes_list:
            _progression[task_id]['message'] = 'Scraping Jumia...'
            resultats += scrape_jumia(query)
            fait += 1
            _progression[task_id]['progression'] = int((fait / total) * 100)

        if 'avito' in plateformes_list:
            _progression[task_id]['message'] = 'Scraping Avito...'
            resultats += scrape_avito(query)
            fait += 1
            _progression[task_id]['progression'] = int((fait / total) * 100)

        if 'ebay' in plateformes_list:
            _progression[task_id]['message'] = 'Scraping eBay...'
            resultats += scrape_ebay(query)
            fait += 1
            _progression[task_id]['progression'] = int((fait / total) * 100)

        # Sauvegarder en base
        _progression[task_id]['message'] = 'Sauvegarde en base...'
        saved = []
        for r in resultats:
            p = Produit.objects.create(
                nom         = r['nom'],
                description = r.get('description', ''),
                prix        = clean_price(r['prix']),
                categorie   = r.get('categorie', 'non_specifie'),
                plateforme  = r['plateforme'],
                url         = r['url']
            )
            saved.append(p)

        _progression[task_id]['statut']      = 'termine'
        _progression[task_id]['progression'] = 100
        _progression[task_id]['message']     = f'{len(saved)} résultats trouvés'
        _progression[task_id]['resultats']   = ProduitSerializer(saved, many=True).data

    except Exception as e:
        _progression[task_id]['statut']  = 'erreur'
        _progression[task_id]['message'] = str(e)


class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.all()
    serializer_class = ProduitSerializer

    # GET /api/produits/search_async/?q=iphone&plateformes=jumia,ebay
    @action(detail=False, methods=['get'])
    def search_async(self, request):
        query       = request.query_params.get('q', '')
        plateformes = request.query_params.get('plateformes', 'jumia,avito,ebay')

        if not query:
            return Response({'error': 'Paramètre q manquant'}, status=400)

        # Valider catégorie téléphone ou laptop
        valide, message = valider_categorie(query)
        if not valide:
            return Response({'error': message}, status=400)

        plateformes_list = [p.strip().lower() for p in plateformes.split(',')]

        # Historique
        user = request.user if request.user.is_authenticated else None
        Recherche.objects.create(utilisateur=user, produit=query)

        # Lancer en background
        task_id = str(uuid.uuid4())
        thread  = threading.Thread(
            target = _scrape_background,
            args   = (task_id, query, plateformes_list)
        )
        thread.daemon = True
        thread.start()

        return Response({
            'task_id'    : task_id,
            'message'    : f'Scraping lancé pour : {query}',
            'plateformes': plateformes_list
        })

    # GET /api/produits/progression/?task_id=xxx
    @action(detail=False, methods=['get'])
    def progression(self, request):
        task_id = request.query_params.get('task_id', '')
        if not task_id or task_id not in _progression:
            return Response({'error': 'Task ID invalide'}, status=404)

        data = _progression[task_id]
        return Response({
            'task_id'    : task_id,
            'statut'     : data['statut'],
            'progression': data['progression'],
            'message'    : data['message'],
            'resultats'  : data.get('resultats', [])
        })

    # GET /api/produits/analyser/?q=iphone
    @action(detail=False, methods=['get'])
    def analyser(self, request):
        query    = request.query_params.get('q', '')
        cat      = request.query_params.get('categorie', '')
        produits = Produit.objects.all()

        if query:
            produits = produits.filter(nom__icontains=query)
        if cat:
            produits = produits.filter(categorie=cat)

        if not produits.exists():
            return Response({'error': 'Aucun produit à analyser'}, status=404)

        resultats = analyser_produits(produits)
        return Response(resultats)

    # GET /api/produits/by_platform/?platform=Jumia
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        platform = request.query_params.get('platform', '')
        produits = Produit.objects.filter(plateforme=platform)
        return Response(ProduitSerializer(produits, many=True).data)

    # GET /api/produits/by_categorie/?cat=telephones
    @action(detail=False, methods=['get'])
    def by_categorie(self, request):
        cat      = request.query_params.get('cat', '')
        produits = Produit.objects.filter(categorie=cat)
        return Response({
            'categorie': cat,
            'count'    : produits.count(),
            'results'  : ProduitSerializer(produits, many=True).data
        })

    # GET /api/produits/export_csv/?q=iphone
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.filter(nom__icontains=query) if query else Produit.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="produits.csv"'
        writer   = csv.writer(response)
        writer.writerow(['ID', 'Nom', 'Description', 'Prix', 'Catégorie', 'Plateforme', 'URL', 'Date'])
        for p in produits:
            writer.writerow([p.id, p.nom, p.description, p.prix, p.categorie, p.plateforme, p.url, p.date_collecte])
        return response

    # GET /api/produits/export_pdf/?q=iphone
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.filter(nom__icontains=query) if query else Produit.objects.all()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="produits.pdf"'
        p    = canvas.Canvas(response, pagesize=A4)
        w, h = A4

        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, h - 50, f"Résultats : {query}")
        p.setFont("Helvetica", 10)
        y = h - 80

        for prod in produits:
            if y < 50:
                p.showPage()
                y = h - 50
            p.drawString(50, y, f"{prod.nom[:40]} | {prod.prix} MAD | {prod.plateforme} | {prod.categorie}")
            y -= 18

        p.save()
        return response

    # POST /api/produits/check_alerts/
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        alertes    = SurveillancePrix.objects.filter(notifie=False)
        declenchee = []
        for alerte in alertes:
            offres = Produit.objects.filter(
                nom__icontains = alerte.produit,
                prix__lte      = alerte.prix_cible
            )
            if offres.exists():
                alerte.notifie = True
                alerte.save()
                declenchee.append({
                    'produit'   : alerte.produit,
                    'prix_cible': alerte.prix_cible,
                    'offres'    : ProduitSerializer(offres, many=True).data
                })
        return Response({
            'alertes_declenchees': len(declenchee),
            'details'            : declenchee
        })

# ── Panier ────────────────────────────────────────────────────────────
class PanierViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
 
    # GET /api/panier/
    def list(self, request):
        items = Panier.objects.filter(utilisateur=request.user).select_related('produit')
        return Response(PanierSerializer(items, many=True).data)
 
    # POST /api/panier/   body: { "produit": <id> }
    def create(self, request):
        produit_id = request.data.get('produit')
        try:
            produit = Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            return Response({'error': 'Produit introuvable'}, status=404)
 
        item, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            produit=produit,
            defaults={'prix_au_moment': produit.prix}
        )
        if not created:
            return Response({'message': 'Produit déjà dans le panier'}, status=200)
        return Response(PanierSerializer(item).data, status=201)
 
    # DELETE /api/panier/<produit_id>/
    def destroy(self, request, pk=None):
        deleted, _ = Panier.objects.filter(utilisateur=request.user, produit_id=pk).delete()
        if not deleted:
            return Response({'error': 'Produit non trouvé dans le panier'}, status=404)
        return Response(status=204)
 
    # GET /api/panier/count/
    @action(detail=False, methods=['get'])
    def count(self, request):
        return Response({'count': Panier.objects.filter(utilisateur=request.user).count()})
 

class RechercheViewSet(viewsets.ModelViewSet):
    queryset         = Recherche.objects.all().order_by('-date')
    serializer_class = RechercheSerializer

class SurveillancePrixViewSet(viewsets.ModelViewSet):
    queryset         = SurveillancePrix.objects.all()
    serializer_class = SurveillancePrixSerializer

class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]
