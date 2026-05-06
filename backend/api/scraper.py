import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

MOTS_PARASITES = [
    'coque','étui','etui','housse','protection','verre','film',
    'chargeur','câble','cable','adaptateur','support','dock',
    'écouteurs','ecouteurs','airpods','casque','batterie',
    'accessoire','kit','pack','lot','pochette','sac',
    'stylet','sleeve','cover','case','screen protector',
    'tempered glass','charger','earphones','headphones',
    'speaker','bag','backpack','compatible',
]

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

IMAGE_PLACEHOLDERS = (
    'data:image',
    'placeholder',
    'default',
    'blank.gif',
    's.gif',
    'no_photo',
    'nophoto',
    'spinner',
    'loading',
)


def _src_from_srcset(value):
    if not value:
        return None
    first = value.split(',')[0].strip()
    return first.split()[0] if first else None


def _clean_image_url(value, base_url):
    if not value:
        return None
    image = value.strip()
    lower = image.lower()
    if not image or any(token in lower for token in IMAGE_PLACEHOLDERS):
        return None
    return urljoin(base_url, image)


def extract_image(img_tag, base_url):
    if not img_tag:
        return None

    for attr in ('data-src', 'data-lazy-src', 'data-original', 'data-image', 'data-img', 'src'):
        image = _clean_image_url(img_tag.get(attr), base_url)
        if image:
            return image

    for attr in ('data-srcset', 'srcset'):
        image = _clean_image_url(_src_from_srcset(img_tag.get(attr)), base_url)
        if image:
            return image

    return None


def _titre_depuis_url(href):
    slug = href.rstrip('/').split('/')[-1].replace('.htm', '')
    slug = re.sub(r'_\d+$', '', slug)
    return re.sub(r'[_-]+', ' ', slug).strip()


def _prix_depuis_texte(text):
    match = re.search(r'([\d\s\u202f.,]+)\s*DH\b', text, re.IGNORECASE)
    return f"{match.group(1).strip()} DH" if match else None


def _image_avito(annonce):
    for img in annonce.find_all('img'):
        src = img.get('src') or ''
        alt = (img.get('alt') or '').lower()
        if 'avatar' in src.lower() or 'profile' in src.lower():
            continue
        if alt and alt not in ('avatar', 'photo'):
            image = extract_image(img, "https://www.avito.ma")
            if image:
                return image

    for img in annonce.find_all('img'):
        src = img.get('src') or ''
        if 'content.avito.ma/classifieds' in src:
            return extract_image(img, "https://www.avito.ma")

    return None


def get_categorie(produit):
    p = produit.lower()
    for cat, mots in CATEGORIES.items():
        if any(m in p for m in mots):
            return cat
    return 'non_specifie'


def valider_categorie(produit):
    cat = get_categorie(produit)
    if cat == 'non_specifie':
        return False, "Produit non supporté. Recherchez un téléphone ou un laptop."
    return True, cat


def est_produit_principal(nom, query):
    """Filtre strict : exclut les accessoires."""
    n = nom.lower().strip()
    q = query.lower().strip()
    premier = n.split()[0] if n.split() else ''
    if any(premier == p or n.startswith(p + ' ') for p in MOTS_PARASITES):
        return False
    zone = ' '.join(n.split()[:4])
    mots_query = q.split()
    return all(m in zone for m in mots_query)


# ── JUMIA ─────────────────────────────────────────────────────────────
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
                lien = urljoin("https://www.jumia.ma", p.find('a')['href'])

                # Image réelle Jumia
                img_tag = p.select_one('img.img') or p.find('img')
                image   = extract_image(img_tag, "https://www.jumia.ma")

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


# ── AVITO ─────────────────────────────────────────────────────────────
def scrape_avito(produit, limit=20):
    url = f"https://www.avito.ma/fr/maroc/{produit.replace(' ', '_')}"
    resultats = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        soup     = BeautifulSoup(r.text, 'html.parser')
        annonces = []
        seen     = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.htm' not in href:
                continue
            lien = urljoin("https://www.avito.ma", href)
            if lien in seen:
                continue
            seen.add(lien)
            annonces.append(a)

        for a in annonces:
            try:
                text = a.get_text(' ', strip=True)
                prix = _prix_depuis_texte(text)
                if not prix:
                    continue

                title_tag = a.find(attrs={'title': True})
                nom = title_tag.get('title').strip() if title_tag else _titre_depuis_url(a['href'])
                if not nom:
                    continue

                lien = urljoin("https://www.avito.ma", a['href'])

                # Image réelle Avito
                image = _image_avito(a)

                if not est_produit_principal(nom, produit):
                    continue

                categorie    = get_categorie(nom)
                desc         = f"Catégorie : {categorie}"
                details = text.replace(nom, '').replace(prix, '').strip()
                if details:
                    desc += f" | {details[:120]}"

                resultats.append({
                    'nom'        : nom,
                    'description': desc,
                    'prix'       : prix,
                    'categorie'  : categorie,
                    'plateforme' : 'Avito',
                    'url'        : lien,
                    'image'      : image,
                })
                if len(resultats) >= limit:
                    break
            except:
                continue
    except Exception as e:
        print(f"Erreur Avito : {e}")
    return resultats


# ── EBAY ──────────────────────────────────────────────────────────────
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
                image   = extract_image(img_tag, "https://www.ebay.com")

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
