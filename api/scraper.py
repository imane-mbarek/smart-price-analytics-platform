import requests
from bs4 import BeautifulSoup

CATEGORIES = {
    'telephones': ['iphone', 'samsung', 'redmi', 'huawei', 'xiaomi', 
                   'oppo', 'realme', 'phone', 'smartphone', 'mobile'],
    'laptops'   : ['laptop', 'pc portable', 'macbook', 'dell', 
                   'hp', 'lenovo', 'asus', 'acer', 'notebook', 'ordinateur']
}

# Mots qui indiquent que le produit est un accessoire, pas le produit lui-même
MOTS_PARASITES = [
    'coque', 'étui', 'etui', 'housse', 'protection', 'verre', 'film',
    'chargeur', 'câble', 'cable', 'adaptateur', 'support', 'dock',
    'écouteurs', 'ecouteurs', 'airpods', 'casque', 'batterie',
    'accessoire', 'kit', 'pack', 'lot', 'pochette', 'sac',
    'stylet', 'stylo', 'manette', 'clavier', 'souris', 'webcam',
    'ventilateur', 'refroidisseur', 'sleeve', 'cover', 'case',
    'screen protector', 'tempered glass', 'charger', 'cable',
    'earphones', 'headphones', 'speaker', 'bag', 'backpack',
]

def get_categorie(produit):
    produit_lower = produit.lower()
    for cat, mots_cles in CATEGORIES.items():
        for mot in mots_cles:
            if mot in produit_lower:
                return cat
    return 'non_specifie'

def valider_categorie(produit):
    cat = get_categorie(produit)
    if cat == 'non_specifie':
        return False, "Produit non supporté. Recherchez un téléphone (iphone, samsung...) ou un laptop (hp, dell, lenovo...)"
    return True, cat


def est_produit_principal(nom, query):
    """
    Retourne True uniquement si le produit est le produit cherché,
    pas un accessoire ou un article lié.
 
    Règles :
    1. Le nom ne doit pas commencer par un mot parasite.
    2. Le nom doit contenir la requête comme élément principal
       (dans les 3 premiers mots du titre).
    """
    nom_lower   = nom.lower().strip()
    query_lower = query.lower().strip()
 
    # Règle 1 : premier mot = parasite → exclure
    premier_mot = nom_lower.split()[0] if nom_lower.split() else ''
    if any(premier_mot == p or nom_lower.startswith(p + ' ') for p in MOTS_PARASITES):
        return False
 
    # Règle 2 : le nom doit contenir la requête dans ses premiers mots
    # On prend les N premiers caractères proportionnels à la longueur de la query
    zone_principale = ' '.join(nom_lower.split()[:4])  # 4 premiers mots
    if query_lower not in zone_principale:
        # Tolérance : vérifier mot par mot si la query est un terme composé
        # ex: "pc portable" → "pc" ET "portable" dans les 4 premiers mots
        mots_query = query_lower.split()
        if not all(m in zone_principale for m in mots_query):
            return False
 
    return True
    

# ── JUMIA ─────────────────────────────────────────────────────
def scrape_jumia(produit):
    url     = f"https://www.jumia.ma/catalog/?q={produit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resultats = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Jumia inaccessible : {response.status_code}")
            return []

        soup     = BeautifulSoup(response.text, 'html.parser')
        produits = soup.find_all('article', class_='prd')

        if not produits:
            print("Jumia : aucun produit trouvé")
            return []

        for p in produits[:20]:  # on prend plus large pour compenser le filtrage
            try:
                nom  = p.find('h3', class_='name').text.strip()
                prix = p.find('div', class_='prc').text.strip()
                lien = "https://www.jumia.ma" + p.find('a')['href']

                  # ── Filtrage strict ──────────────────────────────
                if not est_produit_principal(nom, produit):
                    continue

                categorie = get_categorie(nom)
                rating    = p.find('div', class_='stars')
                reviews   = p.find('div', class_='rev')

                description = f"Catégorie : {categorie}"
                if rating:
                    description += f" | Note : {rating.text.strip()}"
                if reviews:
                    description += f" | {reviews.text.strip()} avis"

                resultats.append({
                    'nom'        : nom,
                    'description': description,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'Jumia',
                    'url'        : lien
                })
            except:
                continue

    except Exception as e:
        print(f"Erreur Jumia : {e}")

    return resultats

# ── AVITO ─────────────────────────────────────────────────────
def scrape_avito(produit):
    url     = f"https://www.avito.ma/fr/maroc/{produit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resultats = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Avito inaccessible : {response.status_code}")
            return []

        soup     = BeautifulSoup(response.text, 'html.parser')
        annonces = soup.find_all('a', class_='sc-iemWCZ')

        if not annonces:
            print("Avito : aucune annonce trouvée")
            return []

        for a in annonces[:20]:
            try:
                nom  = a.find('p', class_='sc-flUlpA').text.strip()
                prix = a.find('p', class_='sc-eDnWTT').text.strip()
                lien = "https://www.avito.ma" + a['href']

                 # ── Filtrage strict ──────────────────────────────
                if not est_produit_principal(nom, produit):
                    continue

                categorie    = get_categorie(nom)
                localisation = a.find('p', class_='sc-jTQCzO')
                date_pub     = a.find('p', class_='sc-jbKcbu')

                description = f"Catégorie : {categorie}"
                if localisation:
                    description += f" | Localisation : {localisation.text.strip()}"
                if date_pub:
                    description += f" | Publié : {date_pub.text.strip()}"

                resultats.append({
                    'nom'        : nom,
                    'description': description,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'Avito',
                    'url'        : lien
                })
            except:
                continue

    except Exception as e:
        print(f"Erreur Avito : {e}")

    return resultats

# ── EBAY ──────────────────────────────────────────────────────
def scrape_ebay(produit):
    url     = f"https://www.ebay.com/sch/i.html?_nkw={produit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resultats = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"eBay inaccessible : {response.status_code}")
            return []

        soup  = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='s-item__info')

        if not items:
            print("eBay : aucun produit trouvé")
            return []

        for item in items[:10]:
            try:
                nom  = item.find('div', class_='s-item__title').text.strip()
                prix = item.find('span', class_='s-item__price').text.strip()
                lien = item.find('a', class_='s-item__link')['href']

                if nom == "Shop on eBay":
                    continue

                 # ── Filtrage strict ──────────────────────────────
                if not est_produit_principal(nom, produit):
                    continue

                categorie = get_categorie(nom)
                condition = item.find('span', class_='SECONDARY_INFO')
                livraison = item.find('span', class_='s-item__shipping')

                description = f"Catégorie : {categorie}"
                if condition:
                    description += f" | Condition : {condition.text.strip()}"
                if livraison:
                    description += f" | Livraison : {livraison.text.strip()}"

                resultats.append({
                    'nom'        : nom,
                    'description': description,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'eBay',
                    'url'        : lien
                })
            except:
                continue

    except Exception as e:
        print(f"Erreur eBay : {e}")

    return resultats

# ── SCRAPE ALL ────────────────────────────────────────────────
def scrape_all(produit, plateformes=None):
    # Valider catégorie
    valide, message = valider_categorie(produit)
    if not valide:
        print(f"Catégorie non supportée : {message}")
        return []

    if plateformes is None:
        plateformes = ['jumia', 'avito', 'ebay']

    print(f"Recherche : {produit} | Catégorie : {message} | Plateformes : {plateformes}")

    resultats = []
    if 'jumia' in plateformes:
        resultats += scrape_jumia(produit)
    if 'avito' in plateformes:
        resultats += scrape_avito(produit)
    if 'ebay' in plateformes:
        resultats += scrape_ebay(produit)

    print(f"{len(resultats)} résultats trouvés !")
    return resultats
