import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO

# --------------------------------------------------------------------
# Configuration de la page
# --------------------------------------------------------------------
st.set_page_config(page_title="Analyse et Prévision des ventes", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé : fond gris clair, texte noir, tableau agrandi
# --------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F0F2F6;
    }
    .stMarkdown, .stText, .stCaption, .stDataFrame, .stTable, label {
        color: #000000;
    }
    h1 {
        font-size: 2.5rem !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        color: #000000;
    }
    h2, h3, h4 {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    .css-1d391kg, .css-1lcbmhc, .css-1out211 {
        background-color: #E0E2E6;
    }
    .css-1d391kg .stMarkdown, .css-1d391kg .stText, .css-1d391kg label {
        color: #000000;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stSlider div[data-baseweb="slider"] {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        color: #000000;
    }
    .stButton > button, .stDownloadButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #45a049;
    }
    a {
        color: #0000EE;
    }
    .stDataFrame {
        width: 100%;
        border: 1px solid #CCCCCC;
    }
    div[data-testid="stDataFrame"] {
        height: 800px !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTE DES ARTICLES ACTIFS (segment, Marque, Article)
# --------------------------------------------------------------------
ACTIVE_ARTICLES = [
    ("ALCOMIX", "Booster", "Booster Appel-Mix 50CL VER"),
    ("ALCOMIX", "Booster", "Booster Tornado 50CL VER VER"),
    # ... insérez ici la liste complète des articles actifs (identique à vos données)
]

df_active = pd.DataFrame(ACTIVE_ARTICLES, columns=["segment_actif", "marque_actif", "article_actif"])

# --------------------------------------------------------------------
# 2. TABLE DE CORRESPONDANCE RÉFÉRENCE -> ARTICLE (complète)
# --------------------------------------------------------------------
REFERENCE_TO_ARTICLE = {
    # ... insérez ici le dictionnaire complet fourni précédemment
}

# --------------------------------------------------------------------
# 3. LISTE DES AGENCES (par défaut)
# --------------------------------------------------------------------
AGENCES = [
    "00-Siège", "01-Tanjombato", "03-Usine-Diego", "04-Tulear",
    "05-Fianarantsoa", "06-Ihosy", "07-Majunga", "08-Manakara",
    "09-Tamatave", "11-Andranomahery", "12-Antsirabe", "18-Ambanja",
    "19-Sambava", "21-Nosy-Be", "23-Morondava", "24-Fort-Dauphin"
]

# --------------------------------------------------------------------
# 4. FONCTIONS UTILITAIRES
# --------------------------------------------------------------------
MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

def parse_mois(mois_str):
    if isinstance(mois_str, str):
        mois_str = mois_str.lower().strip()
        return MOIS_FR.get(mois_str)
    return None

def nettoyer_nombre(val):
    if isinstance(val, str):
        val = val.replace(' ', '').replace(',', '.')
    try:
        return float(val)
    except:
        return 0.0

def extraire_contenance_cl(article_str):
    m = re.search(r'(\d+)\s*CL', article_str, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)\s*L', article_str, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 100
    return None

def extraire_format(article_str):
    m = re.search(r'\b(VER|PET|CAN|FUT|BOI)\b', article_str)
    if m:
        return m.group(1)
    return None

# --------------------------------------------------------------------
# 5. FONCTION DE CHARGEMENT ET NETTOYAGE
# --------------------------------------------------------------------
@st.cache_data
def traiter_fichier(file_bytes, filename):
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))

    required_cols = ['Année', 'Mois', 'segment', 'marque_1', 'format', 'Nom agence', 'contenances', 'Référence', 'ventes hecto']
    if not all(col in df_raw.columns for col in required_cols):
        raise ValueError(f"Colonnes manquantes. Requises : {required_cols}")

    # Filtrer les lignes de détail
    df = df_raw[df_raw['Référence'].notna() & ~df_raw['Référence'].astype(str).str.contains('Total', na=False)].copy()

    # Mapper la référence vers l'article standardisé
    df['Référence'] = df['Référence'].map(REFERENCE_TO_ARTICLE).fillna(df['Référence'])

    # Convertir la colonne Année en numérique
    df['Année'] = pd.to_numeric(df['Année'].astype(str).str.replace(' ', ''), errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)

    # Convertir la colonne "ventes hecto" en numérique (directement sans créer de nouvelle colonne)
    df['ventes hecto'] = df['ventes hecto'].apply(nettoyer_nombre)

    # Créer la date
    df['mois_num'] = df['Mois'].apply(parse_mois)
    df = df[df['mois_num'].notna()]
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(int).astype(str) + '-01')

    # Extraire la contenance en cl
    df['contenance_cl'] = df['contenances'].apply(extraire_contenance_cl)

    # Renommer les colonnes
    df.rename(columns={'Nom agence': 'agence', 'marque_1': 'marque'}, inplace=True)

    # Filtrer pour ne garder que les articles actifs présents
    df = df[df['Référence'].isin(df_active['article_actif'])]

    # Gestion des articles actifs manquants (similarité)
    # ... (même logique que précédemment)

    return df

# --------------------------------------------------------------------
# 6. FONCTION DE CALCUL DES COEFFICIENTS SAISONNIERS
# --------------------------------------------------------------------
def calculer_saisonnalite(serie_mensuelle):
    if len(serie_mensuelle) < 12:
        return None
    moyennes_par_mois = serie_mensuelle.groupby(serie_mensuelle.index.month).mean()
    moyenne_globale = serie_mensuelle.mean()
    if moyenne_globale == 0:
        return None
    coeffs = (moyennes_par_mois / moyenne_globale).to_dict()
    return coeffs

def obtenir_saisonnalite_segment(df_hist, segment):
    df_segment = df_hist[df_hist['segment'] == segment]
    if df_segment.empty:
        return None
    serie_agregee = df_segment.groupby('date')['valeur'].sum()
    if len(serie_agregee) < 12:
        return None
    return calculer_saisonnalite(serie_agregee)

# --------------------------------------------------------------------
# 7. FONCTION DE CALCUL DES PRÉVISIONS AVEC SAISONNALITÉ
# --------------------------------------------------------------------
@st.cache_data
def calculer_previsions_saisonnalite(df_hist, annees_prev):
    # ... (même code que précédemment, avec resample('YE') corrigé)
    pass

# --------------------------------------------------------------------
# 8. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.title("📈 Analyse et Prévision des ventes")

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois, segment, marque_1, format, Nom agence, contenances, Référence, ventes hecto.")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

try:
    df = traiter_fichier(file_bytes, filename)
except Exception as e:
    st.error(f"Erreur lors du traitement du fichier : {e}")
    st.stop()

# --------------------------------------------------------------------
# 9. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité d'affichage", ["Hectolitres (ventes hecto)", "Bouteilles (ventes cols)"])

if unite == "Hectolitres (ventes hecto)":
    df['valeur'] = df['ventes hecto']   # Utilisation de la colonne d'origine
else:
    df['valeur'] = df['ventes hecto'] * 10000 / df['contenance_cl']
    df['valeur'] = df['valeur'].round(0)

# --------------------------------------------------------------------
# 10. GÉNÉRATION DES PRÉVISIONS (2027-2031)
# --------------------------------------------------------------------
df_hist = df[df['date'].dt.year <= 2026].copy()
annees_prev = [2027, 2028, 2029, 2030, 2031]

df_prev = calculer_previsions_saisonnalite(df_hist, annees_prev)

# ... la suite (dernier recours, filtres, tableau croisé, affichage) identique
