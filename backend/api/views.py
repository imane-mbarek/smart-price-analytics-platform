from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Produit, Recherche, SurveillancePrix, Panier, Notification, HistoriquePrix
from .serializers import (
    ProduitSerializer, RechercheSerializer, SurveillancePrixSerializer,
    RegisterSerializer, PanierSerializer, NotificationSerializer
)
from .scraper import scrape_jumia, scrape_avito, valider_categorie
from data_mining.api.dm_service import analyze
import re, csv, threading, uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

_progression = {}

TAUX_CONVERSION = {'USD': 10.0, 'EUR': 10.8, 'GBP': 12.5, 'MAD': 1.0}
PLATFORM_NAMES = {'jumia': 'Jumia', 'avito': 'Avito'}


def clean_price(prix_str):
    """Nettoie et convertit un prix en MAD. Gère USD, EUR, GBP, fourchettes eBay."""
    s = str(prix_str).strip()

    if ' to ' in s.lower():
        s = s.lower().split(' to ')[0]

    devise = 'MAD'
    if '$' in s or 'USD' in s.upper():   devise = 'USD'
    elif '€' in s or 'EUR' in s.upper(): devise = 'EUR'
    elif '£' in s or 'GBP' in s.upper(): devise = 'GBP'

    s_clean = re.sub(r'[^\d,.]', '', s)

    if ',' in s_clean and '.' in s_clean:
        if s_clean.index('.') < s_clean.index(','):
            s_clean = s_clean.replace('.', '').replace(',', '.')
        else:
            s_clean = s_clean.replace(',', '')
    elif ',' in s_clean:
        s_clean = s_clean.replace(',', '.')

    try:
        valeur = float(s_clean)
    except (ValueError, AttributeError):
        return 0.0

    return round(valeur * TAUX_CONVERSION.get(devise, 1.0), 2)


def _creer_notifications_panier(produit, prix_ancien, prix_nouveau, stock_ancien, stock_nouveau):
    paniers = Panier.objects.filter(produit=produit).select_related('utilisateur')
    if not paniers.exists():
        return

    for panier in paniers:
        user = panier.utilisateur

        if prix_ancien > 0 and prix_nouveau < prix_ancien:
            variation = ((prix_ancien - prix_nouveau) / prix_ancien) * 100
            if variation >= 2:
                Notification.objects.create(
                    utilisateur=user,
                    produit=produit,
                    type_notif='baisse_prix',
                    message=f"Prix réduit de {variation:.1f}% sur {produit.plateforme} !",
                    ancien_prix=prix_ancien,
                    nouveau_prix=prix_nouveau,
                )
        elif prix_ancien > 0 and prix_nouveau > prix_ancien:
            variation = ((prix_nouveau - prix_ancien) / prix_ancien) * 100
            if variation >= 5:
                Notification.objects.create(
                    utilisateur=user,
                    produit=produit,
                    type_notif='hausse_prix',
                    message=f"Prix augmenté de {variation:.1f}% sur {produit.plateforme}.",
                    ancien_prix=prix_ancien,
                    nouveau_prix=prix_nouveau,
                )

        if stock_ancien and not stock_nouveau:
            Notification.objects.create(
                utilisateur=user,
                produit=produit,
                type_notif='rupture',
                message=f"{produit.nom} n'est plus disponible sur {produit.plateforme}.",
            )
        elif not stock_ancien and stock_nouveau:
            Notification.objects.create(
                utilisateur=user,
                produit=produit,
                type_notif='retour_stock',
                message=f"{produit.nom} est de nouveau disponible sur {produit.plateforme} !",
            )


def _trouver_produit_panier(resultat):
    plateforme = resultat['plateforme']
    url = resultat.get('url')
    nom = resultat['nom']

    produit = Produit.objects.filter(
        url=url,
        plateforme=plateforme,
        dans_paniers__isnull=False,
    ).first()
    if produit:
        return produit

    return Produit.objects.filter(
        nom__iexact=nom,
        plateforme=plateforme,
        dans_paniers__isnull=False,
    ).first()


def _scrape_background(task_id, query, plateformes_list):
    _progression[task_id] = {
        'statut': 'en_cours', 'progression': 0,
        'message': 'Démarrage...', 'resultats': []
    }
    try:
        resultats = []
        total = len(plateformes_list)
        fait  = 0

        for plateforme, scraper in [
            ('jumia', scrape_jumia),
            ('avito', scrape_avito),
        ]:
            if plateforme in plateformes_list:
                _progression[task_id]['message'] = f'Scraping {plateforme.capitalize()}...'
                resultats += scraper(query)
                fait += 1
                _progression[task_id]['progression'] = int((fait / total) * 80)

        _progression[task_id]['message']     = 'Sauvegarde en base...'
        _progression[task_id]['progression'] = 90

        plateformes_db = [PLATFORM_NAMES[p] for p in plateformes_list if p in PLATFORM_NAMES]
        Produit.objects.filter(
            nom__icontains=query,
            plateforme__in=plateformes_db,
            dans_paniers__isnull=True,
        ).delete()

        saved = []
        for r in resultats:
            prix_mad = clean_price(r['prix'])
            if prix_mad <= 0:
                continue

            p = _trouver_produit_panier(r)
            if p:
                prix_ancien = p.prix
                stock_ancien = p.en_stock
                p.nom = r['nom']
                p.description = r.get('description', '')
                p.prix = prix_mad
                p.categorie = r.get('categorie', 'non_specifie')
                p.plateforme = r['plateforme']
                p.url = r['url']
                p.en_stock = True
                if r.get('image'):
                    p.image = r.get('image')
                p.save()
                _creer_notifications_panier(p, prix_ancien, prix_mad, stock_ancien, True)
            else:
                p = Produit.objects.create(
                    nom        = r['nom'],
                    description= r.get('description', ''),
                    prix       = prix_mad,
                    categorie  = r.get('categorie', 'non_specifie'),
                    plateforme = r['plateforme'],
                    url        = r['url'],
                    en_stock   = True,
                    image      = r.get('image'),
                )

            HistoriquePrix.objects.create(produit=p, prix=prix_mad, en_stock=True)
            saved.append(p)

        _progression[task_id].update({
            'statut': 'termine', 'progression': 100,
            'message': f'{len(saved)} résultats trouvés',
            'resultats': ProduitSerializer(saved, many=True).data,
        })

    except Exception as e:
        _progression[task_id].update({'statut': 'erreur', 'message': str(e)})


# ── Produits ──────────────────────────────────────────────────────────
class ProduitViewSet(viewsets.ModelViewSet):
    queryset         = Produit.objects.all().order_by('-date_collecte')
    serializer_class = ProduitSerializer

    @action(detail=False, methods=['get'])
    def accueil(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 12)), 40)
        except ValueError:
            limit = 12

        produits = Produit.objects.filter(en_stock=True).exclude(plateforme='eBay').order_by('?')[:limit]
        return Response(ProduitSerializer(produits, many=True).data)

    @action(detail=False, methods=['get'])
    def search_async(self, request):
        query       = request.query_params.get('q', '').strip()
        plateformes = request.query_params.get('plateformes', 'jumia,avito')

        if not query:
            return Response({'error': 'Paramètre q manquant'}, status=400)

        valide, message = valider_categorie(query)
        if not valide:
            return Response({'error': message}, status=400)

        plateformes_list = [p.strip().lower() for p in plateformes.split(',') if p.strip().lower() in PLATFORM_NAMES]
        if not plateformes_list:
            return Response({'error': 'Aucune plateforme valide selectionnee'}, status=400)
        user = request.user if request.user.is_authenticated else None
        Recherche.objects.create(utilisateur=user, produit=query)

        task_id = str(uuid.uuid4())
        t = threading.Thread(target=_scrape_background, args=(task_id, query, plateformes_list))
        t.daemon = True
        t.start()

        return Response({'task_id': task_id, 'message': f'Scraping lancé pour : {query}', 'plateformes': plateformes_list})

    @action(detail=False, methods=['get'])
    def progression(self, request):
        task_id = request.query_params.get('task_id', '')
        if not task_id or task_id not in _progression:
            return Response({'error': 'Task ID invalide'}, status=404)
        data = _progression[task_id]
        return Response({
            'task_id': task_id, 'statut': data['statut'],
            'progression': data['progression'], 'message': data['message'],
            'resultats': data.get('resultats', []),
        })

    @action(detail=False, methods=['get'])
    def analyser(self, request):
        query    = request.query_params.get('q', '')
        cat      = request.query_params.get('categorie', '')
        produits = Produit.objects.exclude(plateforme='eBay')
        if query: produits = produits.filter(nom__icontains=query)
        if cat:   produits = produits.filter(categorie=cat)
        if not produits.exists():
            return Response({'error': 'Aucun produit à analyser'}, status=404)
        raw_data = list(produits.values())
        return Response(analyze(raw_data))

    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        platform = request.query_params.get('platform', '')
        if platform == 'eBay':
            return Response([])
        return Response(ProduitSerializer(Produit.objects.filter(plateforme=platform), many=True).data)

    @action(detail=False, methods=['get'])
    def by_categorie(self, request):
        cat      = request.query_params.get('cat', '')
        produits = Produit.objects.filter(categorie=cat)
        return Response({'categorie': cat, 'count': produits.count(), 'results': ProduitSerializer(produits, many=True).data})

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.exclude(plateforme='eBay')
        if query:
            produits = produits.filter(nom__icontains=query)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="produits.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Nom', 'Description', 'Prix (MAD)', 'Catégorie', 'Plateforme', 'URL', 'Date'])
        for p in produits:
            writer.writerow([p.id, p.nom, p.description, p.prix, p.categorie, p.plateforme, p.url, p.date_collecte])
        return response

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        query    = request.query_params.get('q', '')
        produits = Produit.objects.exclude(plateforme='eBay')
        if query:
            produits = produits.filter(nom__icontains=query)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="produits.pdf"'
        c    = canvas.Canvas(response, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, h - 50, f"Résultats : {query}")
        c.setFont("Helvetica", 10)
        y = h - 80
        for p in produits:
            if y < 50: c.showPage(); y = h - 50
            c.drawString(50, y, f"{p.nom[:40]} | {p.prix} MAD | {p.plateforme}")
            y -= 18
        c.save()
        return response

    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        alertes    = SurveillancePrix.objects.filter(notifie=False)
        declenchee = []
        for alerte in alertes:
            offres = Produit.objects.filter(nom__icontains=alerte.produit, prix__lte=alerte.prix_cible)
            if offres.exists():
                alerte.notifie = True
                alerte.save()
                declenchee.append({
                    'produit': alerte.produit, 'prix_cible': alerte.prix_cible,
                    'offres': ProduitSerializer(offres, many=True).data,
                })
        return Response({'alertes_declenchees': len(declenchee), 'details': declenchee})


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


# ── Notifications ─────────────────────────────────────────────────────
class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # GET /api/notifications/
    def list(self, request):
        notifs = Notification.objects.filter(utilisateur=request.user)
        return Response(NotificationSerializer(notifs, many=True).data)

    # POST /api/notifications/<id>/lire/
    @action(detail=True, methods=['post'])
    def lire(self, request, pk=None):
        updated = Notification.objects.filter(utilisateur=request.user, id=pk).update(lue=True)
        if not updated:
            return Response({'error': 'Notification introuvable'}, status=404)
        return Response({'message': 'Notification marquée comme lue'})

    # POST /api/notifications/tout_lire/
    @action(detail=False, methods=['post'])
    def tout_lire(self, request):
        count = Notification.objects.filter(utilisateur=request.user, lue=False).update(lue=True)
        return Response({'message': f'{count} notification(s) marquée(s) comme lues'})

    # GET /api/notifications/non_lues/
    @action(detail=False, methods=['get'])
    def non_lues(self, request):
        notifs = Notification.objects.filter(utilisateur=request.user, lue=False)
        return Response({'count': notifs.count(), 'notifications': NotificationSerializer(notifs, many=True).data})


# ── Autres ViewSets ───────────────────────────────────────────────────
class RechercheViewSet(viewsets.ModelViewSet):
    serializer_class = RechercheSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recherche.objects.filter(utilisateur=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)


class SurveillancePrixViewSet(viewsets.ModelViewSet):
    queryset         = SurveillancePrix.objects.all()
    serializer_class = SurveillancePrixSerializer


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]
