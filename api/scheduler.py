"""
scheduler.py
Scraping périodique automatique toutes les 24h.
Lancé au démarrage de Django via apps.py (ready()).
"""
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

INTERVALLE_SECONDES = 24 * 60 * 60   # 24 heures
_timer = None


def _scrape_periodique():
    """
    Relance le scraping pour toutes les recherches récentes (dernières 7 jours),
    met à jour les prix en base, détecte les variations et crée les notifications.
    """
    # Import ici pour éviter les imports circulaires au démarrage
    from .models import Produit, Panier, Notification, HistoriquePrix
    from .scraper import scrape_jumia, scrape_avito, scrape_ebay, valider_categorie
    from .views import clean_price
    from django.db.models import Min
    from django.utils import timezone
    from datetime import timedelta

    logger.info(f"[Scheduler] Scraping périodique démarré — {datetime.now():%H:%M %d/%m/%Y}")

    # Récupérer les termes uniques recherchés dans les 7 derniers jours
    from .models import Recherche
    depuis = timezone.now() - timedelta(days=7)
    termes = (
        Recherche.objects
        .filter(date__gte=depuis)
        .values_list('produit', flat=True)
        .distinct()
    )

    for terme in termes:
        valide, _ = valider_categorie(terme)
        if not valide:
            continue

        nouveaux = []
        for scraper in [scrape_jumia, scrape_avito, scrape_ebay]:
            try:
                nouveaux += scraper(terme)
            except Exception as e:
                logger.warning(f"[Scheduler] Erreur scraper {scraper.__name__} : {e}")

        for r in nouveaux:
            prix_nouveau = clean_price(r['prix'])
            if prix_nouveau <= 0:
                continue

            # Chercher si le produit existe déjà (même nom + plateforme)
            existant = Produit.objects.filter(
                nom__iexact=r['nom'],
                plateforme=r['plateforme']
            ).first()

            if existant:
                prix_ancien  = existant.prix
                stock_ancien = existant.en_stock

                # Sauvegarder dans l'historique
                HistoriquePrix.objects.create(
                    produit=existant,
                    prix=prix_nouveau,
                    en_stock=True
                )

                # Mettre à jour le produit
                existant.prix     = prix_nouveau
                existant.en_stock = True
                existant.save()

                # Notifier les utilisateurs qui ont ce produit dans leur panier
                _creer_notifications(existant, prix_ancien, prix_nouveau, stock_ancien, True)

            else:
                # Nouveau produit → créer
                Produit.objects.create(
                    nom        = r['nom'],
                    description= r.get('description', ''),
                    prix       = prix_nouveau,
                    categorie  = r.get('categorie', 'non_specifie'),
                    plateforme = r['plateforme'],
                    url        = r['url'],
                    en_stock   = True
                )

    logger.info(f"[Scheduler] Scraping périodique terminé — {len(list(termes))} termes traités")
    _planifier_prochain()


def _creer_notifications(produit, prix_ancien, prix_nouveau, stock_ancien, stock_nouveau):
    """Crée les notifications pour tous les utilisateurs ayant ce produit dans leur panier."""
    from .models import Panier, Notification

    paniers = Panier.objects.filter(produit=produit).select_related('utilisateur')
    if not paniers.exists():
        return

    for panier in paniers:
        user = panier.utilisateur

        # Baisse de prix ≥ 2%
        if prix_ancien > 0 and prix_nouveau < prix_ancien:
            variation = ((prix_ancien - prix_nouveau) / prix_ancien) * 100
            if variation >= 2:
                Notification.objects.create(
                    utilisateur = user,
                    produit     = produit,
                    type_notif  = 'baisse_prix',
                    message     = f"Prix réduit de {variation:.1f}% sur {produit.plateforme} !",
                    ancien_prix = prix_ancien,
                    nouveau_prix= prix_nouveau,
                )

        # Hausse de prix ≥ 5%
        elif prix_ancien > 0 and prix_nouveau > prix_ancien:
            variation = ((prix_nouveau - prix_ancien) / prix_ancien) * 100
            if variation >= 5:
                Notification.objects.create(
                    utilisateur = user,
                    produit     = produit,
                    type_notif  = 'hausse_prix',
                    message     = f"Prix augmenté de {variation:.1f}% sur {produit.plateforme}.",
                    ancien_prix = prix_ancien,
                    nouveau_prix= prix_nouveau,
                )

        # Rupture de stock
        if stock_ancien and not stock_nouveau:
            Notification.objects.create(
                utilisateur = user,
                produit     = produit,
                type_notif  = 'rupture',
                message     = f"{produit.nom} n'est plus disponible sur {produit.plateforme}.",
            )

        # Retour en stock
        elif not stock_ancien and stock_nouveau:
            Notification.objects.create(
                utilisateur = user,
                produit     = produit,
                type_notif  = 'retour_stock',
                message     = f"{produit.nom} est de nouveau disponible sur {produit.plateforme} !",
            )


def _planifier_prochain():
    """Replanifie le prochain scraping dans 24h."""
    global _timer
    _timer = threading.Timer(INTERVALLE_SECONDES, _scrape_periodique)
    _timer.daemon = True
    _timer.start()
    logger.info(f"[Scheduler] Prochain scraping dans {INTERVALLE_SECONDES // 3600}h")


def demarrer():
    """Point d'entrée appelé depuis apps.py ready()."""
    global _timer
    if _timer is not None:
        return  # déjà démarré
    logger.info("[Scheduler] Démarrage du scraping périodique (toutes les 24h)")
    _planifier_prochain()


def arreter():
    """Annule le timer (utilisé en tests)."""
    global _timer
    if _timer:
        _timer.cancel()
        _timer = None
