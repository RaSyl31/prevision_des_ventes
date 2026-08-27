import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO
import plotly.graph_objects as go

# --------------------------------------------------------------------
# Configuration de la page
# --------------------------------------------------------------------
st.set_page_config(page_title="Coefficients de Saisonnalité", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé
# --------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    .stMarkdown, .stText, .stCaption, .stDataFrame, .stTable, label { color: #000000; }
    
    .titre-rouge {
        background-color: #CC0000;
        color: white !important;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: block;
        margin: 10px 0;
    }
    
    .stDataFrame { width: 100%; border: 1px solid #CCCCCC; }
    div[data-testid="stDataFrame"] { height: 600px !important; }
    .stButton > button, .stDownloadButton > button { background-color: #4CAF50; color: white; border: none; }
    .stButton > button:hover, .stDownloadButton > button:hover { background-color: #45a049; }
    
    .ia-box {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTE DES AGENCES
# --------------------------------------------------------------------
AGENCES = [
    "00-",
    "01-Tanjombato",
    "03-Usine-Diego",
    "04-Tulear",
    "05-Fianarantsoa",
    "06-Ihosy",
    "07-Majunga",
    "08-Manakara",
    "09-Tamatave",
    "11-Andranomahery",
    "12-Antsirabe",
    "18-Ambanja",
    "19-Sambava",
    "21-Nosy-Be",
    "23-Morondava",
    "24-Fort-Dauphin"
]

# --------------------------------------------------------------------
# 2. BASE DE RÉFÉRENCE DES ARTICLES ACTIFS
# --------------------------------------------------------------------
BASE_ARTICLES = [
    ("1-BIERES", "1-Queen s", "VER", "33cl", "Queen s 33 cl VER"),
    ("1-BIERES", "1-Queen s", "VER", "65cl", "Queen s 65 cl VER"),
    ("1-BIERES", "3-Fresh", "CAN", "33cl", "FRESH 33 cl CAN"),
    ("1-BIERES", "3-Fresh", "CAN", "33cl", "FRESH 33 cl EXPORT CAN"),
    ("1-BIERES", "3-Fresh", "VER", "33cl", "THB Fresh 33 cl VER"),
    ("1-BIERES", "3-Fresh", "VER", "50cl", "THB Fresh 50 cl VER"),
    ("1-BIERES", "3-Fresh", "VER", "65cl", "THB Fresh 65 cl VER"),
    ("1-BIERES", "4-THB", "CAN", "33cl", "THB Pilsener 33 cl CAN"),
    ("1-BIERES", "4-THB", "CAN", "50cl", "THB Pilsener 50 cl CAN"),
    ("1-BIERES", "4-THB", "FUT", "2000cl", "THB Pilsener 20L Export FUT"),
    ("1-BIERES", "4-THB", "FUT", "2000cl", "THB Pilsener 20L FUT"),
    ("1-BIERES", "4-THB", "FUT", "3000cl", "THB Pilsener 30L Export FUT"),
    ("1-BIERES", "4-THB", "FUT", "3000cl", "THB Pilsener 30L FUT"),
    ("1-BIERES", "4-THB", "VER", "33cl", "THB Pilsener 33 cl VER"),
    ("1-BIERES", "4-THB", "VER", "33cl", "THB Speciale NOEL 33 cl VER"),
    ("1-BIERES", "4-THB", "VER", "50cl", "THB Pilsener 50 cl VER"),
    ("1-BIERES", "4-THB", "VER", "65cl", "THB Pilsener 65 cl VER"),
    ("1-BIERES", "5-Gold", "CAN", "50cl", "Gold 8 50 cl CAN"),
    ("1-BIERES", "5-Gold", "CAN", "50cl", "Gold Blanche 50 cl CAN"),
    ("1-BIERES", "5-Gold", "CAN", "50cl", "Gold Blonde 50 cl CAN"),
    ("1-BIERES", "5-Gold", "FUT", "2000cl", "Gold Blanche 20L FUT"),
    ("1-BIERES", "5-Gold", "FUT", "3000cl", "Gold Blanche 30L FUT"),
    ("1-BIERES", "5-Gold", "VER", "33cl", "Gold Amigo 33cl VER"),
    ("1-BIERES", "5-Gold", "VER", "33cl", "Gold Blanche 33cl VER"),
    ("1-BIERES", "5-Gold", "VER", "33cl", "Gold Blonde 33 cl VER"),
    ("1-BIERES", "5-Gold", "VER", "33cl", "Gold Rosee 33cl VER"),
    ("1-BIERES", "5-Gold", "VER", "50cl", "Gold 8 50 cl VER"),
    ("1-BIERES", "5-Gold", "VER", "50cl", "Gold Blanche 50 cl VER"),
    ("1-BIERES", "5-Gold", "VER", "50cl", "Gold Blonde 50 cl VER"),
    ("1-BIERES", "5-Gold", "VER", "65cl", "Gold Blonde 65 cl VER"),
    ("1-BIERES", "6-Beaufort", "CAN", "33cl", "Beaufort 33 cl CAN"),
    ("1-BIERES", "6-Beaufort", "CAN", "50cl", "Beaufort 50 CL CAN"),
    ("1-BIERES", "6-Beaufort", "VER", "33cl", "Beaufort 33CL VER"),
    ("1-BIERES", "7-Autres bieres", "FUT", "2000cl", "THB Blanche 20L Export FUT"),
    ("1-BIERES", "7-Autres bieres", "VER", "50cl", "THB 8% 50 cl VER"),
    ("1-BIERES", "7-Autres bieres", "VER", "50cl", "THB Blanche 50 cl VER"),
    ("2-BG", "1-Caprice", "CAN", "33cl", "Caprice Bonbon Anglais 33 cl CAN"),
    ("2-BG", "1-Caprice", "CAN", "33cl", "Caprice Grenadine 33 cl CAN"),
    ("2-BG", "1-Caprice", "CAN", "33cl", "Caprice Orange 33 cl CAN"),
    ("2-BG", "1-Caprice", "FUT", "2000cl", "Caprice Bonbon Anglais 20L FUT"),
    ("2-BG", "1-Caprice", "FUT", "2000cl", "Caprice Orange 20L FUT"),
    ("2-BG", "1-Caprice", "FUT", "3000cl", "Caprice Bonbon Anglais 30L FUT"),
    ("2-BG", "1-Caprice", "PET", "150cl", "Caprice Ananas 150 cl PET"),
    ("2-BG", "1-Caprice", "PET", "150cl", "Caprice Bonbon Anglais 150 cl PET"),
    ("2-BG", "1-Caprice", "PET", "150cl", "Caprice Grenadine 150 cl PET"),
    ("2-BG", "1-Caprice", "PET", "150cl", "Caprice Orange 150 cl PET"),
    ("2-BG", "1-Caprice", "PET", "150cl", "Caprice Pomme 150 cl PET"),
    ("2-BG", "1-Caprice", "PET", "35cl", "Caprice Bonbon Anglais 35 cl PET"),
    ("2-BG", "1-Caprice", "PET", "35cl", "Caprice Grenadine 35 cl PET"),
    ("2-BG", "1-Caprice", "PET", "35cl", "Caprice Orange 35 cl PET"),
    ("2-BG", "1-Caprice", "PET", "50cl", "Caprice Ananas 50 cl PET"),
    ("2-BG", "1-Caprice", "PET", "50cl", "Caprice Bonbon Anglais 50 cl PET"),
    ("2-BG", "1-Caprice", "PET", "50cl", "Caprice Grenadine 50 cl PET"),
    ("2-BG", "1-Caprice", "PET", "50cl", "Caprice Orange 50 cl PET"),
    ("2-BG", "1-Caprice", "PET", "50cl", "Caprice Pomme 50 cl PET"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Ananas 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Bonbon Anglais 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Citron 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Grenadine 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Orange 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "100cl", "Caprice Pomme 100 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Ananas 30 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Bonbon Anglais 30 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Citron 30 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Grenadine 30 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Orange 30 cl VER"),
    ("2-BG", "1-Caprice", "VER", "30cl", "Caprice Pomme 30 cl VER"),
    ("2-BG", "1-XXL", "CAN", "33cl", "XXL 33 cl CAN"),
    ("2-BG", "1-XXL", "PET", "35cl", "XXL 35cl PET"),
    ("2-BG", "1-XXL", "VER", "30cl", "XXL 30cl BOB VER"),
    ("2-BG", "1-XXL", "VER", "30cl", "XXL 30cl VER"),
    ("2-BG", "2-FOSA", "CAN", "50cl", "FOSA 50 cl CAN"),
    ("2-BG", "2-Tonic", "VER", "100cl", "Tonic 100 cl VER"),
    ("2-BG", "2-Tonic", "VER", "30cl", "Tonic 30 cl VER"),
    ("2-BG", "3-D jino", "PET", "125cl", "D Jino Cola 125cl PET"),
    ("2-BG", "3-D jino", "PET", "125cl", "D Jino tropical 125cl PET"),
    ("2-BG", "3-D jino", "PET", "35cl", "D Jino Cola 35cl PET"),
    ("2-BG", "3-D jino", "PET", "35cl", "D Jino Limonady 35cl PET"),
    ("2-BG", "3-D jino", "PET", "35cl", "D Jino Tropical 35cl PET"),
    ("2-BG", "4-Youzou", "PET", "150cl", "Youzou 150 cl PET"),
    ("2-BG", "4-Youzou", "PET", "50cl", "Youzou 50cl PET"),
    ("2-BG", "4-Youzou", "VER", "100cl", "Youzou 100 cl VER"),
    ("2-BG", "4-Youzou", "VER", "30cl", "Youzou 30 cl VER"),
    ("2-BG", "5-World Cola", "CAN", "33cl", "World Cola 33 cl CAN"),
    ("2-BG", "5-World Cola", "FUT", "2000cl", "World Cola 20L FUT"),
    ("2-BG", "5-World Cola", "PET", "150cl", "World Cola 150cl PET"),
    ("2-BG", "5-World Cola", "PET", "35cl", "World Cola 35cl PET"),
    ("2-BG", "5-World Cola", "PET", "50cl", "World Cola 50cl PET"),
    ("2-BG", "5-World Cola", "VER", "100cl", "World Cola 100cl VER"),
    ("2-BG", "5-World Cola", "VER", "100cl", "World Cola 100cl WOCO VER"),
    ("2-BG", "5-World Cola", "VER", "30cl", "World Cola 30cl VER"),
    ("2-BG", "5-World Cola", "VER", "30cl", "World Cola 30cl WOCO VER"),
    ("3-EAUX", "1-Cristalline", "PET", "100cl", "Cristalline 100 cl PET"),
    ("3-EAUX", "1-Cristalline", "PET", "200cl", "Cristalline 200 cl PET"),
    ("3-EAUX", "2-Eau vive", "PET", "150cl", "Eau vive 150 cl PET"),
    ("3-EAUX", "2-Eau vive", "PET", "50cl", "Eau vive 50 cl PET"),
    ("3-EAUX", "2-Eau vive", "VER", "50cl", "Eau vive 50 cl VER"),
    ("3-EAUX", "3-Cristal", "PET", "150cl", "Cristal 150 cl PET"),
    ("3-EAUX", "3-Cristal", "VER", "100cl", "Cristal 100 cl VER"),
    ("3-EAUX", "3-Cristal", "VER", "30cl", "Cristal 30 cl VER"),
    ("3-EAUX", "3-Cristal", "VER", "50cl", "Cristal 50 cl VER"),
    ("5-ALCOMIX", "1-Booster", "PET", "35cl", "Booster Tornado 35CL PET"),
    ("5-ALCOMIX", "1-Booster", "VER", "50cl", "Booster Appel-Mix 50CL VER"),
    ("5-ALCOMIX", "1-Booster", "VER", "50cl", "Booster CUBA LIBRE 50CL VER"),
    ("5-ALCOMIX", "1-Booster", "VER", "50cl", "Booster Tornado 50CL VER VER"),
    ("5-ALCOMIX", "2-Alcomix Divers", "VER", "33cl", "Racines 33 cl VER"),
    ("5-ALCOMIX", "2-Alcomix Divers", "VER", "50cl", "BOTA Fresh 50 cl VER"),
    ("7-VIN", "Vin", "0cl", "50cl", "Valmont 50cl"),
]

df_base_articles = pd.DataFrame(BASE_ARTICLES, columns=["segment", "marque", "format", "contenances", "Référence"])
ARTICLES_ACTIFS = df_base_articles['Référence'].unique().tolist()

# --------------------------------------------------------------------
# 3. FONCTIONS UTILITAIRES
# --------------------------------------------------------------------
def nettoyer_nombre(val):
    if isinstance(val, str):
        val = val.replace(' ', '').replace(',', '.')
    try:
        return float(val)
    except:
        return 0.0

# --------------------------------------------------------------------
# 4. FONCTION D'INTERPRÉTATION IA
# --------------------------------------------------------------------
def interpreter_resultats(df_coefficients, df_filtre):
    if df_filtre.empty:
        return "Aucune donnée à interpréter."
    
    interpretations = []
    noms_mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    moyennes_par_mois = df_filtre.groupby('mois')['coefficient'].mean()
    mois_tres_forts = moyennes_par_mois[moyennes_par_mois > 1.2].index.tolist()
    mois_forts = moyennes_par_mois[(moyennes_par_mois > 1.05) & (moyennes_par_mois <= 1.2)].index.tolist()
    mois_normaux = moyennes_par_mois[(moyennes_par_mois >= 0.95) & (moyennes_par_mois <= 1.05)].index.tolist()
    mois_faibles = moyennes_par_mois[(moyennes_par_mois >= 0.8) & (moyennes_par_mois < 0.95)].index.tolist()
    mois_tres_faibles = moyennes_par_mois[moyennes_par_mois < 0.8].index.tolist()
    
    interpretations.append("### 📊 Analyse Globale de la Saisonnalité")
    
    if mois_tres_forts:
        interpretations.append(f"🔴 **Pics majeurs** : {', '.join([noms_mois[m-1] for m in mois_tres_forts])}")
    if mois_forts:
        interpretations.append(f"🟠 **Mois dynamiques** : {', '.join([noms_mois[m-1] for m in mois_forts])}")
    if mois_normaux:
        interpretations.append(f"🟢 **Mois stables** : {', '.join([noms_mois[m-1] for m in mois_normaux])}")
    if mois_faibles:
        interpretations.append(f"🟡 **Mois calmes** : {', '.join([noms_mois[m-1] for m in mois_faibles])}")
    if mois_tres_faibles:
        interpretations.append(f"🔵 **Creux majeurs** : {', '.join([noms_mois[m-1] for m in mois_tres_faibles])}")
    
    interpretations.append("\n### 🏭 Analyse par Segment")
    for segment in sorted(df_filtre['segment'].unique()):
        df_seg = df_filtre[df_filtre['segment'] == segment]
        moy_seg = df_seg.groupby('mois')['coefficient'].mean()
        pic = moy_seg.idxmax()
        creux = moy_seg.idxmin()
        amplitude = moy_seg.max() - moy_seg.min()
        interpretations.append(f"**{segment}** : Pic en {noms_mois[pic-1]} (coef {moy_seg[pic]:.2f}), Creux en {noms_mois[creux-1]} (coef {moy_seg[creux]:.2f}), Amplitude {amplitude:.2f}")
    
    interpretations.append("\n### 🏷️ Analyse par Marque")
    for marque in sorted(df_filtre['marque'].unique()):
        df_marque = df_filtre[df_filtre['marque'] == marque]
        moy_marque = df_marque.groupby('mois')['coefficient'].mean()
        pic = moy_marque.idxmax()
        taux_variation = (moy_marque.max() - moy_marque.min()) / moy_marque.min() * 100 if moy_marque.min() > 0 else 0
        interpretations.append(f"**{marque}** : Pic en {noms_mois[pic-1]}, Variation saisonnière de {taux_variation:.0f}%")
    
    interpretations.append("\n### 🔍 Articles les Plus Saisonniers")
    variabilite = df_filtre.groupby('Référence')['coefficient'].std().sort_values(ascending=False).head(3)
    for i, (article, std) in enumerate(variabilite.items(), 1):
        df_article = df_filtre[df_filtre['Référence'] == article]
        moy_article = df_article.groupby('mois')['coefficient'].mean()
        pic = moy_article.idxmax()
        creux = moy_article.idxmin()
        interpretations.append(f"{i}. **{article}** : Pic en {noms_mois[pic-1]}, Creux en {noms_mois[creux-1]}")
    
    interpretations.append("\n### 💡 Recommandations Stratégiques")
    interpretations.append("**📦 Gestion des Stocks :**")
    if mois_tres_forts:
        interpretations.append(f"   - Augmenter les stocks de sécurité avant : {', '.join([noms_mois[m-1] for m in mois_tres_forts])}")
    if mois_tres_faibles:
        interpretations.append(f"   - Réduire les commandes pendant : {', '.join([noms_mois[m-1] for m in mois_tres_faibles])}")
    
    interpretations.append("**📣 Actions Marketing :**")
    if mois_tres_faibles:
        interpretations.append(f"   - Promotions pour stimuler la demande en : {', '.join([noms_mois[m-1] for m in mois_tres_faibles])}")
    if mois_tres_forts:
        interpretations.append(f"   - Capitaliser sur la demande naturelle en : {', '.join([noms_mois[m-1] for m in mois_tres_forts])}")
    
    interpretations.append("**💰 Gestion de Trésorerie :**")
    interpretations.append("   - Prévoir des besoins en fonds de roulement plus élevés pendant les pics")
    interpretations.append("   - Optimiser les délais de paiement selon la saisonnalité")
    
    return "\n".join(interpretations)

# --------------------------------------------------------------------
# 5. CHARGEMENT ET TRAITEMENT
# --------------------------------------------------------------------
@st.cache_data
def charger_et_calculer(file_bytes, filename):
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))
    
    # Vérifier les colonnes requises
    required_cols = ['Année', 'Mois année', 'Segments', 'Marque', 'Format', 'Agences', 'Contenance', 'Articles', 'Vente hl direct']
    missing_cols = [col for col in required_cols if col not in df_raw.columns]
    if missing_cols:
        st.error(f"Colonnes manquantes : {missing_cols}")
        st.stop()
    
    df = df_raw.copy()
    
    # Filtrer les lignes de détail
    df = df[df['Articles'].notna()]
    df = df[~df['Articles'].astype(str).str.contains('Total', case=False, na=False)]
    df = df[~df['Articles'].astype(str).str.contains('vide', case=False, na=False)]
    df = df[df['Articles'].astype(str).str.strip() != '']
    df = df[df['Mois année'].notna()]
    df = df[~df['Mois année'].astype(str).str.contains('Total', case=False, na=False)]
    df = df[df['Agences'].notna()]
    df = df[~df['Agences'].astype(str).str.contains('Total', case=False, na=False)]
    
    # Renommer les colonnes
    df.rename(columns={
        'Segments': 'segment',
        'Marque': 'marque',
        'Format': 'format',
        'Agences': 'agence',
        'Contenance': 'contenances',
        'Articles': 'Référence',
        'Vente hl direct': 'ventes_hecto'
    }, inplace=True)
    
    # Convertir Année directement en int (c'est déjà un nombre)
    df['Année'] = pd.to_numeric(df['Année'], errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)
    
    # Convertir ventes
    df['ventes_hecto'] = df['ventes_hecto'].apply(nettoyer_nombre)
    
    # Extraire le mois depuis "Mois année" (ex: "01 2024" -> 1)
    df['mois_num'] = df['Mois année'].astype(str).str.strip().str.split(' ').str[0]
    df['mois_num'] = pd.to_numeric(df['mois_num'], errors='coerce')
    df = df.dropna(subset=['mois_num'])
    df['mois_num'] = df['mois_num'].astype(int)
    
    # Créer la date
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(str) + '-01')
    
    # Filtrer agences valides
    df = df[df['agence'].isin(AGENCES)]
    
    # Filtrer articles actifs
    df = df[df['Référence'].isin(ARTICLES_ACTIFS)]
    
    # Utiliser les deux années les plus récentes disponibles
    annees_disponibles = sorted(df['Année'].unique())
    if len(annees_disponibles) >= 2:
        annee_fin = annees_disponibles[-1]
        annee_debut = annees_disponibles[-2]
    elif len(annees_disponibles) == 1:
        annee_debut = annees_disponibles[0]
        annee_fin = annees_disponibles[0]
    else:
        return pd.DataFrame()
    
    st.info(f"Années utilisées pour le calcul : {annee_debut} - {annee_fin}")
    
    df_periode = df[(df['Année'] >= annee_debut) & (df['Année'] <= annee_fin)]
    
    if df_periode.empty:
        return pd.DataFrame()
    
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    moyenne_generale = df_periode.groupby(group_cols)['ventes_hecto'].mean()
    moyenne_par_mois = df_periode.groupby(group_cols + [df_periode['mois_num']])['ventes_hecto'].mean()
    
    resultats = []
    
    for (keys, moyenne_gen) in moyenne_generale.items():
        if moyenne_gen <= 0:
            continue
        
        coeffs = {}
        for mois in range(1, 13):
            key_with_month = keys + (mois,)
            moyenne_mois = moyenne_par_mois.get(key_with_month, 0)
            coeffs[mois] = moyenne_mois / moyenne_gen if moyenne_gen > 0 else 0
        
        somme_coeffs = sum(coeffs.values())
        if somme_coeffs > 0:
            coeffs_norm = {m: (c / somme_coeffs) * 12 for m, c in coeffs.items()}
            coeffs_arrondis = {}
            somme_arrondie = 0
            for mois in range(1, 12):
                coeff = round(coeffs_norm[mois], 2)
                coeffs_arrondis[mois] = coeff
                somme_arrondie += coeff
            coeffs_arrondis[12] = round(12 - somme_arrondie, 2)
            somme_finale = sum(coeffs_arrondis.values())
            if abs(somme_finale - 12) > 0.01:
                coeffs_arrondis[12] = round(coeffs_arrondis[12] + (12 - somme_finale), 2)
            
            for mois in range(1, 13):
                resultats.append({
                    'segment': keys[0],
                    'marque': keys[1],
                    'format': keys[2],
                    'contenances': keys[3],
                    'Référence': keys[4],
                    'agence': keys[5],
                    'mois': mois,
                    'coefficient': coeffs_arrondis[mois]
                })
    
    return pd.DataFrame(resultats)

# --------------------------------------------------------------------
# 6. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📊 Coefficients de Saisonnalité par Article et Agence</span>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois année, Segments, Marque, Format, Agences, Contenance, Articles, Vente hl direct")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

df_coefficients = charger_et_calculer(file_bytes, filename)

if df_coefficients.empty:
    st.warning("Aucune donnée disponible pour calculer les coefficients.")
    st.stop()

st.success(f"Calcul terminé : {len(df_coefficients)} coefficients")

# --------------------------------------------------------------------
# 7. FILTRES
# --------------------------------------------------------------------
st.sidebar.header("Filtres")

articles_options = sorted(df_coefficients['Référence'].unique())
selected_articles = st.sidebar.multiselect("Article", options=articles_options, default=articles_options)

if selected_articles:
    marques_options = sorted(df_coefficients[df_coefficients['Référence'].isin(selected_articles)]['marque'].unique())
else:
    marques_options = sorted(df_coefficients['marque'].unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)

if selected_articles and selected_marques:
    segments_options = sorted(df_coefficients[
        (df_coefficients['Référence'].isin(selected_articles)) & 
        (df_coefficients['marque'].isin(selected_marques))
    ]['segment'].unique())
else:
    segments_options = sorted(df_coefficients['segment'].unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)

df_filtre = df_coefficients[
    (df_coefficients['Référence'].isin(selected_articles)) &
    (df_coefficients['marque'].isin(selected_marques)) &
    (df_coefficients['segment'].isin(selected_segments))
]

if df_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --------------------------------------------------------------------
# 8. TABLEAU PIVOT
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">Coefficients de saisonnalité mensuels</span>', unsafe_allow_html=True)

pivot = df_filtre.pivot_table(
    index=['segment', 'marque', 'format', 'contenances', 'Référence', 'agence'],
    columns='mois',
    values='coefficient',
    aggfunc='first'
)

mois_cols = list(range(1, 13))
pivot = pivot.reindex(columns=mois_cols)

noms_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
pivot.columns = noms_mois

pivot['Total'] = pivot.sum(axis=1)

st.dataframe(pivot, width='stretch', height=600)

# --------------------------------------------------------------------
# 9. GRAPHIQUE
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📈 Variation mensuelle des coefficients</span>', unsafe_allow_html=True)

coeffs_globaux_par_mois = df_filtre.groupby('mois')['coefficient'].mean()

somme_coeffs_graph = coeffs_globaux_par_mois.sum()
if somme_coeffs_graph > 0:
    coeffs_globaux_normalises = (coeffs_globaux_par_mois / somme_coeffs_graph) * 12
else:
    coeffs_globaux_normalises = coeffs_globaux_par_mois

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=noms_mois,
    y=coeffs_globaux_normalises.reindex(mois_cols),
    mode='lines+markers',
    name='Coefficient global',
    line=dict(color='blue', width=2),
    marker=dict(size=8)
))
fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Moyenne = 1.0")
fig.update_layout(
    title="Coefficients de saisonnalité globaux par mois (toutes agences confondues)",
    xaxis_title="Mois",
    yaxis_title="Coefficient",
    height=500,
    showlegend=True,
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='lightgray'),
    yaxis=dict(showgrid=True, gridcolor='lightgray')
)
st.plotly_chart(fig, width='stretch')

# --------------------------------------------------------------------
# 10. INTERPRÉTATION IA
# --------------------------------------------------------------------
st.markdown("### 🤖 Interprétation et Recommandations")
st.markdown('<div class="ia-box">' + interpreter_resultats(df_coefficients, df_filtre).replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------
# 11. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot.reset_index().to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les coefficients (CSV)",
    data=csv,
    file_name="coefficients_saisonnalite.csv",
    mime="text/csv"
)
