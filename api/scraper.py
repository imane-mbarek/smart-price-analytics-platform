import requests
from bs4 import BeautifulSoup

CATEGORIES = {
    'telephones': ['iphone', 'samsung', 'redmi', 'huawei', 'xiaomi', 
                   'oppo', 'realme', 'phone', 'smartphone', 'mobile'],
    'laptops'   : ['laptop', 'pc portable', 'macbook', 'dell', 
                   'hp', 'lenovo', 'asus', 'acer', 'notebook', 'ordinateur']
}

# Produits variés à scraper périodiquement (page d'accueil)
PRODUITS_PERIODIQUES = [
    'iphone',
    'samsung galaxy',
    'redmi',
    'hp laptop',
    'lenovo',
    'asus laptop',
    'huawei',
    'macbook',
    'dell laptop',
    'xiaomi',
]

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

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

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
    
     # Tolérance : vérifier mot par mot si la query est un terme composé
    # ex: "pc portable" → "pc" ET "portable" dans les 4 premiers mots
    mots_query = query_lower.split()
    return all(m in zone_principale for m in mots_query)    

# ── JUMIA ─────────────────────────────────────────────────────
def scrape_jumia(produit, limit=20):
    url = f"https://www.jumia.ma/catalog/?q={produit.replace(' ', '+')}"
    resultats = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup  = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('article', class_='prd')
 
        for p in items[:limit]:
            try:
                nom  = p.find('h3', class_='name').text.strip()
                prix = p.find('div', class_='prc').text.strip()
                lien = "https://www.jumia.ma" + p.find('a')['href']
 
                # Image réelle Jumia
                img_tag = p.find('img')
                image   = img_tag.get('data-src') or img_tag.get('src') if img_tag else None
 
                if not est_produit_principal(nom, produit):
                    continue
 
                categorie = get_categorie(nom)
                rating    = p.find('div', class_='stars')
                reviews   = p.find('div', class_='rev')
                desc      = f"Catégorie : {categorie}"
                if rating:  desc += f" | Note : {rating.text.strip()}"
                if reviews: desc += f" | {reviews.text.strip()} avis"
 
                resultats.append({
                    'nom'        : nom,
                    'description': desc,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'Jumia',
                    'url'        : lien,
                    'image'      : image,
                })
            except:
                continue
    except Exception as e:
        print(f"Erreur Jumia : {e}")
    return resultats

# ── AVITO ─────────────────────────────────────────────────────
def scrape_avito(produit, limit=20):
    url = f"https://www.avito.ma/fr/maroc/{produit.replace(' ', '_')}"
    resultats = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup     = BeautifulSoup(r.text, 'html.parser')
        annonces = soup.find_all('a', class_='sc-iemWCZ')
 
        for a in annonces[:limit]:
            try:
                nom  = a.find('p', class_='sc-flUlpA').text.strip()
                prix = a.find('p', class_='sc-eDnWTT').text.strip()
                lien = "https://www.avito.ma" + a['href']
 
                # Image réelle Avito
                img_tag = a.find('img')
                image   = img_tag.get('src') or img_tag.get('data-src') if img_tag else None
                # Avito utilise parfois des URLs relatives
                if image and image.startswith('/'):
                    image = "https://www.avito.ma" + image
 
                if not est_produit_principal(nom, produit):
                    continue
 
                categorie    = get_categorie(nom)
                localisation = a.find('p', class_='sc-jTQCzO')
                date_pub     = a.find('p', class_='sc-jbKcbu')
                desc         = f"Catégorie : {categorie}"
                if localisation: desc += f" | {localisation.text.strip()}"
                if date_pub:     desc += f" | {date_pub.text.strip()}"
 
                resultats.append({
                    'nom'        : nom,
                    'description': desc,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'Avito',
                    'url'        : lien,
                    'image'      : image,
                })
            except:
                continue
    except Exception as e:
        print(f"Erreur Avito : {e}")
    return resultats
 
# ── EBAY ──────────────────────────────────────────────────────
def scrape_ebay(produit, limit=20):
    url = f"https://www.ebay.com/sch/i.html?_nkw={produit.replace(' ', '+')}"
    resultats = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup  = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('li', class_='s-item')
 
        for item in items[:limit]:
            try:
                nom_tag = item.find('div', class_='s-item__title')
                if not nom_tag: continue
                nom = nom_tag.text.strip()
                if nom == "Shop on eBay": continue
 
                prix_tag = item.find('span', class_='s-item__price')
                lien_tag = item.find('a', class_='s-item__link')
                if not prix_tag or not lien_tag: continue
 
                prix = prix_tag.text.strip()
                lien = lien_tag['href']
 
                # Image réelle eBay
                img_tag = item.find('img')
                image   = None
                if img_tag:
                    image = img_tag.get('src') or img_tag.get('data-src')
                    # eBay retourne parfois un pixel de tracking — on filtre
                    if image and 's.gif' in image:
                        image = None
 
                if not est_produit_principal(nom, produit):
                    continue
 
                categorie = get_categorie(nom)
                condition = item.find('span', class_='SECONDARY_INFO')
                livraison = item.find('span', class_='s-item__shipping')
                desc      = f"Catégorie : {categorie}"
                if condition: desc += f" | {condition.text.strip()}"
                if livraison: desc += f" | {livraison.text.strip()}"
 
                resultats.append({
                    'nom'        : nom,
                    'description': desc,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'eBay',
                    'url'        : lien,
                    'image'      : image,
                })
            except:
                continue
    except Exception as e:
        print(f"Erreur eBay : {e}")
    return resultats
    
# ── SCRAPE ALL ────────────────────────────────────────────────
def scrape_all(produit, plateformes=None):
    valide, message = valider_categorie(produit)
    if not valide:
        return []
    if plateformes is None:
        plateformes = ['jumia', 'avito', 'ebay']
    resultats = []
    if 'jumia' in plateformes: resultats += scrape_jumia(produit)
    if 'avito' in plateformes: resultats += scrape_avito(produit)
    if 'ebay'  in plateformes: resultats += scrape_ebay(produit)
    return resultats
