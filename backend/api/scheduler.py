"""
scheduler.py — Scraping périodique toutes les 24h.
Scrape une liste de produits variés (PRODUITS_PERIODIQUES)
pour alimenter la page d'accueil avec du contenu frais et diversifié.
"""
import threading
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

INTERVALLE_SECONDES = 24 * 60 * 60
_timer = None


def _scrape_periodique():
    from .models import Produit, Panier, Notification, HistoriquePrix
    from .scraper import scrape_jumia, scrape_avito, scrape_ebay, PRODUITS_PERIODIQUES
    from .views import clean_price

    logger.info(f"[Scheduler] Démarrage — {datetime.now():%H:%M %d/%m/%Y}")

    # Mélange aléatoire pour varier les produits affichés à chaque cycle
    termes = PRODUITS_PERIODIQUES.copy()
    random.shuffle(termes)

    for terme in termes:
        nouveaux = []
        # Alterner les plateformes pour avoir de la diversité
        for scraper in [scrape_jumia, scrape_avito, scrape_ebay]:
            try:
                nouveaux += scraper(terme, limit=5)  # 5 par plateforme max
            except Exception as e:
                logger.warning(f"[Scheduler] {scraper.__name__} : {e}")

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

                HistoriquePrix.objects.create(produit=existant, prix=prix_nouveau, en_stock=True)

                existant.prix     = prix_nouveau
                existant.en_stock = True
                # Mettre à jour l'image si elle était vide
                if r.get('image') and not existant.image:
                    existant.image = r['image']
                existant.save()

                _creer_notifications(existant, prix_ancien, prix_nouveau, stock_ancien, True)
            else:
                Produit.objects.create(
                    nom        = r['nom'],
                    description= r.get('description', ''),
                    prix       = prix_nouveau,
                    categorie  = r.get('categorie', 'non_specifie'),
                    plateforme = r['plateforme'],
                    url        = r['url'],
                    image      = r.get('image'),
                    en_stock   = True,
                )

    logger.info(f"[Scheduler] Terminé — {len(termes)} termes traités")
    _planifier_prochain()


def _creer_notifications(produit, prix_ancien, prix_nouveau, stock_ancien, stock_nouveau):
    from .models import Panier, Notification

    paniers = Panier.objects.filter(produit=produit).select_related('utilisateur')
    if not paniers.exists():
        return

    for panier in paniers:
        user = panier.utilisateur

        if prix_ancien > 0 and prix_nouveau < prix_ancien:
            variation = ((prix_ancien - prix_nouveau) / prix_ancien) * 100
            if variation >= 2:
                Notification.objects.create(
                    utilisateur=user, produit=produit,
                    type_notif='baisse_prix',
                    message=f"Prix réduit de {variation:.1f}% sur {produit.plateforme} !",
                    ancien_prix=prix_ancien, nouveau_prix=prix_nouveau,
                )
        elif prix_ancien > 0 and prix_nouveau > prix_ancien:
            variation = ((prix_nouveau - prix_ancien) / prix_ancien) * 100
            if variation >= 5:
                Notification.objects.create(
                    utilisateur=user, produit=produit,
                    type_notif='hausse_prix',
                    message=f"Prix augmenté de {variation:.1f}% sur {produit.plateforme}.",
                    ancien_prix=prix_ancien, nouveau_prix=prix_nouveau,
                )

        if stock_ancien and not stock_nouveau:
            Notification.objects.create(
                utilisateur=user, produit=produit,
                type_notif='rupture',
                message=f"{produit.nom} n'est plus disponible sur {produit.plateforme}.",
            )
        elif not stock_ancien and stock_nouveau:
            Notification.objects.create(
                utilisateur=user, produit=produit,
                type_notif='retour_stock',
                message=f"{produit.nom} est de nouveau disponible sur {produit.plateforme} !",
            )


def _planifier_prochain():
    global _timer
    _timer = threading.Timer(INTERVALLE_SECONDES, _scrape_periodique)
    _timer.daemon = True
    _timer.start()
    logger.info(f"[Scheduler] Prochain scraping dans {INTERVALLE_SECONDES // 3600}h")


def demarrer():
    global _timer
    if _timer is not None:
        return
    logger.info("[Scheduler] Démarrage scraping périodique (24h)")
    _planifier_prochain()


def arreter():
    global _timer
    if _timer:
        _timer.cancel()
        _timer = None
