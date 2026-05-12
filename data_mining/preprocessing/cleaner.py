"""
cleaner.py  –  Prétraitement avancé des données scrappées
Module Data Mining | Licence IASD 2025/2026

Utilisation :
    from cleaner import charger_et_nettoyer, nettoyer

    # Charger depuis la BD + nettoyer en une seule ligne
    df_clean = charger_et_nettoyer(nom_produit='laptop')

    # OU : nettoyer un DataFrame déjà chargé
    df_clean = nettoyer(df_brut)
"""

import re
import pandas as pd
import numpy as np
from scipy import stats

# ─── Import du connecteur BD ──────────────────────────────────
from db_connector import get_data


# ══════════════════════════════════════════════════════════════
# 1.  MOTS-CLÉS POUR FILTRER LES FAUX PRODUITS (accessoires)
# ══════════════════════════════════════════════════════════════
MOTS_ACCESSOIRES = [
    'pochette', 'housse', 'coque', 'étui', 'protection', 'cover',
    'film', 'verre trempé', 'tempered glass', 'chargeur', 'câble',
    'cable', 'adaptateur', 'support', 'batterie externe', 'power bank',
    'écouteurs', 'écouteur', 'casque', 'airpods', 'tws',
    'chargeur sans fil', 'dock', 'stand', 'holder', 'sac',
    'sacoche', 'stylet', 'stylus', 'clavier', 'souris',
    'mouse', 'keyboard', 'sleeve', 'bag', 'strap', 'bracelet',
    'band', 'screen protector', 'protecteur', 'folio',
]

MOTS_PRODUIT_PRINCIPAL = [
    'laptop', 'pc portable', 'ordinateur portable', 'notebook',
    'macbook', 'iphone', 'samsung galaxy', 'smartphone', 'téléphone',
    'redmi', 'xiaomi', 'huawei', 'oppo', 'realme',
]

# ══════════════════════════════════════════════════════════════
# 2.  DÉTECTION DE CATÉGORIE (remplace la colonne BD manquante)
# ══════════════════════════════════════════════════════════════
CATEGORIES_MAPPING = {
    'iphone': 'telephone', 'samsung': 'telephone', 'redmi': 'telephone',
    'huawei': 'telephone', 'xiaomi': 'telephone', 'oppo': 'telephone',
    'realme': 'telephone', 'smartphone': 'telephone', 'mobile': 'telephone',
    'laptop': 'laptop', 'pc portable': 'laptop', 'macbook': 'laptop',
    'dell': 'laptop', 'hp': 'laptop', 'lenovo': 'laptop',
    'asus': 'laptop', 'acer': 'laptop', 'notebook': 'laptop',
    'ordinateur': 'laptop',
}

def detecter_categorie(nom: str) -> str:
    nom_lower = str(nom).lower().strip()
    for mot_cle, categorie in CATEGORIES_MAPPING.items():
        if mot_cle in nom_lower:
            return categorie
    return 'autre'


# ══════════════════════════════════════════════════════════════
# 3.  EXTRACTION DES CARACTÉRISTIQUES TECHNIQUES
# ══════════════════════════════════════════════════════════════

def extraire_marque(nom: str) -> str:
    marques = {
        'hp': 'HP', 'dell': 'Dell', 'lenovo': 'Lenovo', 'asus': 'Asus',
        'acer': 'Acer', 'apple': 'Apple', 'macbook': 'Apple',
        'samsung': 'Samsung', 'xiaomi': 'Xiaomi', 'redmi': 'Xiaomi',
        'huawei': 'Huawei', 'oppo': 'OPPO', 'realme': 'Realme',
        'iphone': 'Apple', 'victus': 'HP', 'omen': 'HP',
        'thinkpad': 'Lenovo', 'ideapad': 'Lenovo', 'inspiron': 'Dell',
        'latitude': 'Dell', 'vostro': 'Dell', 'zenbook': 'Asus',
        'vivobook': 'Asus', 'tuf': 'Asus', 'swift': 'Acer',
        'aspire': 'Acer', 'nitro': 'Acer', 'predator': 'Acer',
    }
    nom_lower = str(nom).lower()
    for mot, marque in marques.items():
        if mot in nom_lower:
            return marque
    return 'Autre'


def extraire_cpu(texte: str) -> str:
    texte = str(texte)
    patterns = [
        r'(i[3579][-\s]?\d{4,5}[A-Z]{0,2})',
        r'(core\s+i[3579][-\s]?\d{4,5}[A-Z]{0,2})',
        r'(i[3579]\s+\d{1,2}[A-Z]{2,3}\s+gen)',
        r'(i[3579]\s+\d{1,2}(?:eme|th|st|nd|rd)\s+gen)',
        r'(celeron\s+\w+)',
        r'(pentium\s+\w+)',
        r'(ryzen\s+[3579](?:\s+\d{4}[A-Z]{0,2})?)',
        r'(ryzen\s+[3579]\s+\d{1,2}[A-Z]{2,3}\s+gen)',
        r'(m[1-4](?:\s+(?:pro|max|ultra))?)',
        r'(snapdragon\s+\d{3,4}[A-Z]?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()
    return None


def extraire_ram(texte: str) -> float:
    texte = str(texte)
    patterns = [
        r'(\d+)\s*go\s+ram',
        r'(\d+)\s*gb\s+ram',
        r'ram\s*[:\-]?\s*(\d+)\s*(?:go|gb)',
        r'(\d+)\s*go\s*/\s*\d+',
        r'(\d+)\s*gb\s*/\s*\d+',
        r'/\s*(\d+)\s*(?:go|gb)',
        r'(\d+)\s*(?:go|gb)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            if val in [2, 4, 6, 8, 12, 16, 24, 32, 64]:
                return val
    return None


def extraire_stockage(texte: str) -> str:
    texte = str(texte)
    unites = {'go': 'Go', 'gb': 'Go', 'to': 'To', 'tb': 'To'}
    match_type = re.search(r'(ssd|nvme|hdd|emmc)', texte, re.IGNORECASE)
    type_str = match_type.group(1).upper() if match_type else 'Stockage'
    patterns = [
        r'(\d+)\s*(?:go|gb)\s*(?:ssd|nvme|hdd|emmc)',
        r'(\d+)\s*(?:to|tb)\s*(?:ssd|nvme|hdd)',
        r'(\d+)\s*(?:ssd|nvme)',
        r'(\d+)\s*(?:go|gb|to|tb)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            apres = texte[match.start():match.start()+20].lower()
            unite = 'Go'
            for u, label in unites.items():
                if u in apres:
                    unite = label
                    break
            if val >= 100 or unite == 'To':
                return f"{val}{unite} {type_str}"
    return None


def extraire_ecran(texte: str) -> str:
    texte = str(texte)
    patterns = [
        r'(\d{1,2}[,\.]\d)\s*["\']?\s*(?:pouces?|inch|")',
        r'ecran\s+(?:fhd|hd|uhd|4k)?\s*(\d{1,2}[,\.]\d)',
        r'(\d{1,2}[,\.]\d)\s*(?:fhd|hd|4k)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            taille = match.group(1).replace(',', '.')
            res_match = re.search(r'(fhd|hd\+?|uhd|4k|qhd|2k)', texte, re.IGNORECASE)
            res = res_match.group(1).upper() if res_match else ''
            return f'{taille}" {res}'.strip()
    return None


def extraire_etat(texte: str) -> str:
    texte = str(texte).lower()
    if any(w in texte for w in ['neuf', 'new', 'scellé', 'sealed', 'jamais utilisé']):
        return 'Neuf'
    if any(w in texte for w in ['occasion', 'used', 'reconditionné', 'reconditionne',
                                  'refurbished', 'très bon état', 'bon état',
                                  'grade a', 'grade b', '2ème main']):
        return 'Occasion'
    return 'Non précisé'


def extraire_generation(texte: str) -> str:
    texte = str(texte)
    patterns = [
        r'(\d{1,2})\s*(?:th|st|nd|rd|eme|ème)\s*gen(?:eration)?',
        r'gen(?:eration)?\s*(\d{1,2})',
        r'(\d{1,2})\s*eme\s+gen',
    ]
    for pattern in patterns:
        match = re.search(pattern, texte, re.IGNORECASE)
        if match:
            return f"{match.group(1)}ème Gen"
    return None


def nettoyer_description(desc: str) -> str:
    desc = str(desc)
    desc = re.sub(r'Cat[eé]gorie\s*:\s*\w+\s*\|?', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'il\s+y\s+a\s+\d+\s+(?:minute|heure|jour)s?', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'\b[A-Z]{3,}\s+V[eé]rifi[eé]\b', '', desc)
    desc = re.sub(r'INFORMATIQUE\s+ET\s+MULTIM[EÉ]DIA', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'\s*\|\s*', ' ', desc)
    desc = re.sub(r'\s{2,}', ' ', desc)
    return desc.strip()


# ══════════════════════════════════════════════════════════════
# 4.  FILTRAGE DES FAUX PRODUITS
# ══════════════════════════════════════════════════════════════

def est_faux_produit(nom: str, description: str) -> bool:
    texte     = (str(nom) + ' ' + str(description)).lower()
    nom_lower = str(nom).lower()
    for mot in MOTS_ACCESSOIRES:
        if mot in nom_lower[:40]:
            if not any(p in nom_lower for p in MOTS_PRODUIT_PRINCIPAL):
                return True
    count_accessoire = sum(1 for mot in MOTS_ACCESSOIRES if mot in texte)
    count_produit    = sum(1 for mot in MOTS_PRODUIT_PRINCIPAL if mot in texte)
    if count_accessoire >= 2 and count_produit == 0:
        return True
    return False


# ══════════════════════════════════════════════════════════════
# 5.  DÉTECTION DES OUTLIERS
# ══════════════════════════════════════════════════════════════

def detecter_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    df['prix_outlier']   = False
    df['raison_outlier'] = ''
    for categorie in df['categorie'].unique():
        mask = df['categorie'] == categorie
        prix = df.loc[mask, 'prix']
        Q1, Q3 = prix.quantile(0.25), prix.quantile(0.75)
        IQR = Q3 - Q1
        borne_basse = Q1 - 1.5 * IQR
        borne_haute = Q3 + 1.5 * IQR
        idx_bas  = df.index[mask & (df['prix'] < borne_basse)]
        idx_haut = df.index[mask & (df['prix'] > borne_haute)]
        df.loc[idx_bas | idx_haut, 'prix_outlier'] = True
        df.loc[idx_bas,  'raison_outlier'] = f'IQR : prix trop bas (< {borne_basse:.0f} MAD)'
        df.loc[idx_haut, 'raison_outlier'] = f'IQR : prix trop élevé (> {borne_haute:.0f} MAD)'
    return df


def detecter_outliers_zscore(df: pd.DataFrame, seuil: float = 3.0) -> pd.DataFrame:
    df['zscore_prix'] = 0.0
    for categorie in df['categorie'].unique():
        mask = df['categorie'] == categorie
        if mask.sum() < 3:
            continue
        z       = np.abs(stats.zscore(df.loc[mask, 'prix']))
        z_serie = pd.Series(z, index=df.loc[mask].index)
        df.loc[mask, 'zscore_prix'] = z_serie
        df.loc[mask & (z_serie > seuil), 'prix_outlier'] = True
    return df


# ══════════════════════════════════════════════════════════════
# 6.  RAPPORT QUALITÉ
# ══════════════════════════════════════════════════════════════

def generer_rapport(df_avant: pd.DataFrame, df_apres: pd.DataFrame,
                    n_faux: int, n_outliers: int) -> None:
    n_doublons = len(df_avant) - len(
        df_avant.drop_duplicates(subset=['nom', 'plateforme', 'prix'])
    )
    print("\n" + "═"*55)
    print("       RAPPORT DE PRÉTRAITEMENT – DATA MINING")
    print("═"*55)
    print(f"  Lignes initiales          : {len(df_avant)}")
    print(f"  Doublons supprimés        : {n_doublons}")
    print(f"  Faux produits filtrés     : {n_faux}")
    print(f"  Outliers détectés (prix)  : {n_outliers}")
    print(f"  Lignes après nettoyage    : {len(df_apres)}")
    print("─"*55)
    print("  Valeurs manquantes après nettoyage :")
    for col in ['marque', 'cpu', 'ram_go', 'stockage', 'ecran', 'etat', 'generation']:
        if col in df_apres.columns:
            n_null = df_apres[col].isna().sum()
            pct    = n_null / len(df_apres) * 100
            print(f"    {col:<20}: {n_null:>4} ({pct:.1f}%)")
    print("─"*55)
    print("  Catégories détectées :")
    for cat, count in df_apres['categorie'].value_counts().items():
        print(f"    {cat:<20}: {count}")
    print("═"*55 + "\n")


# ══════════════════════════════════════════════════════════════
# 7.  PIPELINE NETTOYAGE
# ══════════════════════════════════════════════════════════════

def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit un DataFrame brut issu de la BD."""
    df_avant = df.copy()

    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    df['description'] = df.get('description', pd.Series('')).fillna('').apply(nettoyer_description)

    # Faux produits
    masque_faux = df.apply(
        lambda row: est_faux_produit(row.get('nom', ''), row.get('description', '')), axis=1
    )
    n_faux = masque_faux.sum()
    if n_faux > 0:
        print(f"\n[FILTRE] {n_faux} faux produits retirés :")
        for nom in df.loc[masque_faux, 'nom'].tolist():
            print(f"    ✗ {nom}")
    df = df[~masque_faux].copy()

    # Doublons, nom, prix
    df = df.drop_duplicates(subset=['nom', 'plateforme', 'prix'])
    df = df.dropna(subset=['nom'])
    df['nom'] = df['nom'].str.strip()
    df['prix'] = pd.to_numeric(
        df['prix'].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce'
    )
    df = df.dropna(subset=['prix'])
    df = df[df['prix'] > 0]

    if 'plateforme' in df.columns:
        df['plateforme'] = df['plateforme'].str.lower().str.strip()
    df = df.dropna(subset=['url'])
    if 'date_collecte' in df.columns:
        df['date_collecte'] = pd.to_datetime(df['date_collecte'], errors='coerce')

    # ── Catégorie détectée depuis le nom ──────────────────────
    df['categorie'] = df['nom'].apply(detecter_categorie)

    # Extraction caractéristiques
    texte = df['nom'].fillna('') + ' ' + df['description'].fillna('')
    df['marque']     = df['nom'].apply(extraire_marque)
    df['cpu']        = texte.apply(extraire_cpu)
    df['ram_go']     = texte.apply(extraire_ram)
    df['stockage']   = texte.apply(extraire_stockage)
    df['ecran']      = texte.apply(extraire_ecran)
    df['etat']       = texte.apply(extraire_etat)
    df['generation'] = texte.apply(extraire_generation)

    # Outliers
    df = detecter_outliers_iqr(df)
    df = detecter_outliers_zscore(df)
    n_outliers = df['prix_outlier'].sum()

    generer_rapport(df_avant, df, n_faux, n_outliers)
    return df.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════
# 8.  FONCTION PRINCIPALE : charge BD + nettoie
# ══════════════════════════════════════════════════════════════

def charger_et_nettoyer(nom_produit: str = None,
                         plateforme: str = None,
                         limit: int = None) -> pd.DataFrame:
    """
    Charge les données depuis MySQL et les nettoie.

    Exemples :
        df = charger_et_nettoyer(nom_produit='iPhone')
        df = charger_et_nettoyer(plateforme='Jumia')
        df = charger_et_nettoyer()   # toute la base
    """
    print(f"\n[CLEANER] Chargement depuis la base de données...")
    df_brut = get_data(
        nom_produit=nom_produit,
        plateforme=plateforme,
        limit=limit,
    )

    if df_brut.empty:
        print("[CLEANER] ✗ Aucune donnée trouvée.")
        return df_brut

    print(f"[CLEANER] Prétraitement de {len(df_brut)} lignes...")
    df_clean = nettoyer(df_brut)
    print(f"[CLEANER] ✓ Terminé → {len(df_clean)} lignes propres.\n")
    return df_clean


# ══════════════════════════════════════════════════════════════
# TEST RAPIDE
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    df = charger_et_nettoyer()
    cols = ['nom', 'prix', 'categorie', 'marque', 'cpu', 'ram_go',
            'stockage', 'ecran', 'etat', 'prix_outlier', 'raison_outlier']
    cols_dispo = [c for c in cols if c in df.columns]
    print(df[cols_dispo].to_string())