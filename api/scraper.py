import requests
from bs4 import BeautifulSoup
def scrape_jumia(produit):
    url = f"https://www.jumia.ma/catalog/?q={produit}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resultats = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        produits = soup.find_all('article', class_='prd')
        
        for p in produits[:10]:  # top 10
            try:
                nom  = p.find('h3', class_='name').text.strip()
                prix = p.find('div', class_='prc').text.strip()
                lien = "https://www.jumia.ma" + p.find('a')['href']
                
                resultats.append({
                    'nom'        : nom,
                    'prix'       : prix,
                    'plateforme' : 'Jumia',
                    'url'        : lien
                })
            except:
                continue
                
    except Exception as e:
        print(f"Erreur Jumia : {e}")
    
    return resultats

def scrape_avito(produit):
    url = f"https://www.avito.ma/fr/maroc/{produit}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resultats = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        annonces = soup.find_all('a', class_='sc-iemWCZ')
        
        for a in annonces[:10]:
            try:
                nom  = a.find('p', class_='sc-flUlpA').text.strip()
                prix = a.find('p', class_='sc-eDnWTT').text.strip()
                lien = "https://www.avito.ma" + a['href']
                
                resultats.append({
                    'nom'        : nom,
                    'prix'       : prix,
                    'plateforme' : 'Avito',
                    'url'        : lien
                })
            except:
                continue
                
    except Exception as e:
        print(f"Erreur Avito : {e}")
    
    return resultats
 
def scrape_ebay(produit):
    url = f"https://www.ebay.com/sch/i.html?_nkw={produit}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resultats = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup     = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='s-item__info')
        
        for item in items[:10]:
            try:
                nom  = item.find('div', class_='s-item__title').text.strip()
                prix = item.find('span', class_='s-item__price').text.strip()
                lien = item.find('a', class_='s-item__link')['href']
                
                if nom == "Shop on eBay":  # ignorer le premier résultat
                    continue
                
                resultats.append({
                    'nom'        : nom,
                    'prix'       : prix,
                    'plateforme' : 'eBay',
                    'url'        : lien
                })
            except:
                continue
                
    except Exception as e:
        print(f"Erreur eBay : {e}")
    
    return resultats
def scrape_all(produit):
    print(f"🔍 Recherche : {produit}")
    
    resultats = []
    resultats += scrape_jumia(produit)
    resultats += scrape_avito(produit)
    resultats += scrape_ebay(produit)
    
    print(f"✅ {len(resultats)} résultats trouvés !")
    return resultats
if __name__ == "__main__":
    resultats = scrape_all("iphone")
    for r in resultats:
        print(r)
