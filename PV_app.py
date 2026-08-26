import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import random

# --------------------------------------------------------------------
# Configuration de la page
# --------------------------------------------------------------------
st.set_page_config(page_title="Analyse et Prévision des ventes", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé : fond gris clair, texte noir, tableau agrandi, titres ajustés
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
# 1. LISTE DES ARTICLES ACTIFS (segment, marque, article)
# --------------------------------------------------------------------
ACTIVE_ARTICLES = [
    ("ALCOMIX", "Booster", "Booster Appel-Mix 50CL VER"),
    ("ALCOMIX", "Booster", "Booster Tornado 50CL VER VER"),
    ("BG", "Caprice", "Caprice Ananas 100 cl VER"),
    ("BG", "Caprice", "Caprice Ananas 150 cl PET"),
    ("BG", "Caprice", "Caprice Ananas 30 cl VER"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 100 cl VER"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 150 cl PET"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 20L FUT"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 30 cl VER"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 30L FUT"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 33 cl CAN"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 35 cl PET"),
    ("BG", "Caprice", "Caprice Bonbon Anglais 50 cl PET"),
    ("BG", "Caprice", "Caprice Grenadine 100 cl VER"),
    ("BG", "Caprice", "Caprice Grenadine 150 cl PET"),
    ("BG", "Caprice", "Caprice Grenadine 30 cl VER"),
    ("BG", "Caprice", "Caprice Grenadine 33 cl CAN"),
    ("BG", "Caprice", "Caprice Grenadine 35 cl PET"),
    ("BG", "Caprice", "Caprice Grenadine 50 cl PET"),
    ("BG", "Caprice", "Caprice Orange 100 cl VER"),
    ("BG", "Caprice", "Caprice Orange 150 cl PET"),
    ("BG", "Caprice", "Caprice Orange 20L FUT"),
    ("BG", "Caprice", "Caprice Orange 30 cl VER"),
    ("BG", "Caprice", "Caprice Orange 33 cl CAN"),
    ("BG", "Caprice", "Caprice Orange 35 cl PET"),
    ("BG", "Caprice", "Caprice Orange 50 cl PET"),
    ("BG", "Tonic", "Tonic 100 cl VER"),
    ("BG", "Tonic", "Tonic 30 cl VER"),
    ("BG", "World Cola", "World Cola 100cl VER"),
    ("BG", "World Cola", "World Cola 100cl WOCO VER"),
    ("BG", "World Cola", "World Cola 150cl PET"),
    ("BG", "World Cola", "World Cola 20L FUT"),
    ("BG", "World Cola", "World Cola 30cl VER"),
    ("BG", "World Cola", "World Cola 30cl WOCO VER"),
    ("BG", "World Cola", "World Cola 33 cl CAN"),
    ("BG", "World Cola", "World Cola 35cl PET"),
    ("BG", "World Cola", "World Cola 50cl PET"),
    ("BI", "Beaufort", "Beaufort 33 CL CAN"),
    ("BI", "Beaufort", "Beaufort 33CL VER"),
    ("BI", "FRESH", "FRESH 33 cl CAN"),
    ("BI", "FRESH", "THB Fresh 33 cl VER"),
    ("BI", "FRESH", "THB Fresh 65 cl VER"),
    ("BI", "Gold", "Gold 8 50 cl CAN"),
    ("BI", "Gold", "Gold 8 50 cl VER"),
    ("BI", "Gold", "Gold Blanche 20L FUT"),
    ("BI", "Gold", "Gold Blanche 33cl VER"),
    ("BI", "Gold", "Gold Blanche 50 cl CAN"),
    ("BI", "Gold", "Gold Blanche 50 cl VER"),
    ("BI", "Gold", "Gold Blonde 33 cl VER"),
    ("BI", "Gold", "Gold Blonde 50 cl CAN"),
    ("BI", "Gold", "Gold Blonde 50 cl VER"),
    ("BI", "Gold", "Gold Blonde 65 cl VER"),
    ("BI", "Queen", "Queen s 65 cl VER"),
    ("BI", "THB", "THB BLanche 20L FUT"),
    ("BI", "THB", "THB Pilsener 20L Export FUT"),
    ("BI", "THB", "THB Pilsener 20L FUT"),
    ("BI", "THB", "THB Pilsener 30L Export FUT"),
    ("BI", "THB", "THB Pilsener 30L FUT"),
    ("BI", "THB", "THB Pilsener 33 cl VER"),
    ("BI", "THB", "THB Pilsener 50 cl CAN"),
    ("BI", "THB", "THB Pilsener 65 cl VER"),
    ("EAUX", "Cristal", "Cristal 100 cl VER"),
    ("EAUX", "Cristal", "Cristal 150 cl PET"),
    ("EAUX", "Cristal", "Cristal 30 cl VER"),
    ("EAUX", "Cristal", "Cristal 50 cl VER"),
    ("EAUX", "Cristalline", "Cristalline 100 cl PET"),
    ("EAUX", "Cristalline", "Cristalline 200 cl PET"),
    ("EAUX", "Eau", "Eau vive 150 cl PET"),
    ("EAUX", "Eau", "Eau vive 50 cl PET"),
    ("EAUX", "Eau", "Eau vive 50 cl VER"),
    ("Energy", "FOSA", "FOSA 50 cl CAN"),
    ("Energy", "XXL", "XXL 30cl BOB VER"),
    ("Energy", "XXL", "XXL 30cl VER"),
    ("Energy", "XXL", "XXL 33 cl CAN"),
    ("Energy", "XXL", "XXL 35cl PET"),
]

# Création du DataFrame des articles actifs
df_articles = pd.DataFrame(ACTIVE_ARTICLES, columns=["segment", "marque", "article"])

# --------------------------------------------------------------------
# 2. EXTRACTION DE LA CONTENANCE EN CL POUR LE CALCUL EN HECTOLITRES
# --------------------------------------------------------------------
def extract_contenance(article):
    """Extrait la contenance en cl à partir du libellé de l'article."""
    # Patterns : 50CL, 50 cl, 50cl, 20L, 20 l, 2000 cl, etc.
    # On convertit tout en cl.
    # Recherche d'un nombre suivi de CL (insensible à la casse)
    m = re.search(r'(\d+)\s*(?:CL|cl)', article)
    if m:
        return int(m.group(1))
    # Recherche d'un nombre suivi de L (litres)
    m = re.search(r'(\d+)\s*(?:L|l)', article)
    if m:
        return int(m.group(1)) * 100  # 1 L = 100 cl
    # Si non trouvé, on retourne None (ne sera pas utilisé pour le volume)
    return None

df_articles['contenance_cl'] = df_articles['article'].apply(extract_contenance)

# --------------------------------------------------------------------
# 3. GÉNÉRATION DE DONNÉES FICTIVES (historique 2017-2026 + prévisions 2027-2031)
# --------------------------------------------------------------------
@st.cache_data
def generate_dummy_data():
    start_date = datetime(2017, 1, 1)
    end_date = datetime(2031, 12, 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    agences = [
        "00-Siège", "01-Tanjombato", "03-Usine-Diego", "04-Tulear",
        "05-Fianarantsoa", "06-Ihosy", "07-Majunga", "08-Manakara",
        "09-Tamatave", "11-Andranomahery", "12-Antsirabe", "18-Ambanja",
        "19-Sambava", "21-Nosy-Be", "23-Morondava", "24-Fort-Dauphin"
    ]
    data = []
    for _, art in df_articles.iterrows():
        for agence in agences:
            base = random.uniform(10, 500)
            trend = random.uniform(-0.02, 0.05)
            for i, date in enumerate(dates):
                if date.year < 2027:
                    seasonal = 1 + 0.3 * np.sin((date.month - 1) * 2 * np.pi / 12)
                    noise = random.uniform(-0.2, 0.2)
                    quantite = max(0, int(base * (1 + i * trend) * seasonal * (1 + noise)))
                else:
                    seasonal = 1 + 0.1 * np.sin((date.month - 1) * 2 * np.pi / 12)
                    noise = random.uniform(-0.05, 0.05)
                    quantite = max(0, int(base * (1 + i * trend) * seasonal * (1 + noise)))
                data.append({
                    'date': date,
                    'agence': agence,
                    'article': art['article'],
                    'quantite': quantite
                })
    return pd.DataFrame(data)

# --------------------------------------------------------------------
# 4. CHARGEMENT DES DONNÉES
# --------------------------------------------------------------------
st.title("📈 Analyse et Prévision des ventes")

data_option = st.radio(
    "Source des données :",
    ["Utiliser des données fictives (démo)", "Importer un fichier CSV"]
)

if data_option == "Utiliser des données fictives (démo)":
    df_ventes = generate_dummy_data()
    st.success("Données fictives générées (2017-2031).")
else:
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    if uploaded_file is not None:
        try:
            df_ventes = pd.read_csv(uploaded_file)
            required_cols = ['date', 'agence', 'article', 'quantite']
            if not all(col in df_ventes.columns for col in required_cols):
                st.error(f"Le fichier CSV doit contenir les colonnes : {', '.join(required_cols)}")
                st.stop()
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            st.success("Fichier chargé avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
            st.stop()
    else:
        st.info("Veuillez téléverser un fichier CSV avec les colonnes : date, agence, article, quantite.")
        st.stop()

# Fusionner avec le tableau des articles pour obtenir segment, marque et contenance
df_ventes = df_ventes.merge(df_articles, on='article', how='left')

# --------------------------------------------------------------------
# 5. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité d'affichage", ["Quantité (bouteilles)", "Volume (hectolitres)"])
if unite == "Quantité (bouteilles)":
    df_ventes['valeur'] = df_ventes['quantite']
else:
    # Volume en hectolitres : quantite * contenance_cl / 10000
    df_ventes['valeur'] = df_ventes['quantite'] * df_ventes['contenance_cl'] / 10000.0

# --------------------------------------------------------------------
# 6. FILTRES MULTIPLES (cases à cocher)
#    Filtre année restreint aux prévisions 2027-2031
# --------------------------------------------------------------------
st.sidebar.header("Filtres (sélection multiple)")

mode_affichage = st.sidebar.radio("Affichage", ["Par mois", "Par agence", "Par année"])

annees_options = [2027, 2028, 2029, 2030, 2031]
selected_annees = st.sidebar.multiselect(
    "Année (prévisions)",
    options=annees_options,
    default=annees_options
)

# Filtrer directement sur les années sélectionnées
df_temp = df_ventes[df_ventes['date'].dt.year.isin(selected_annees)]

# Segment
segments_options = sorted(df_temp['segment'].dropna().unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)
df_temp = df_temp[df_temp['segment'].isin(selected_segments)]

# Marque
marques_options = sorted(df_temp['marque'].dropna().unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)
df_temp = df_temp[df_temp['marque'].isin(selected_marques)]

# Article
articles_options = sorted(df_temp['article'].dropna().unique())
selected_articles = st.sidebar.multiselect("Article", options=articles_options, default=articles_options)
df_temp = df_temp[df_temp['article'].isin(selected_articles)]

# Agence (seulement pour le mode "Par mois")
if mode_affichage == "Par mois":
    agences_options = sorted(df_temp['agence'].unique())
    selected_agences = st.sidebar.multiselect("Agence", options=agences_options, default=agences_options)
    df_temp = df_temp[df_temp['agence'].isin(selected_agences)]

# --------------------------------------------------------------------
# 7. TABLEAU CROISÉ DYNAMIQUE
# --------------------------------------------------------------------
index_cols = ['segment', 'marque', 'article']

if df_temp.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

if mode_affichage == "Par mois":
    df_temp['mois'] = df_temp['date'].dt.month.astype(str).str.zfill(2)
    pivot = pd.pivot_table(
        df_temp,
        values='valeur',
        index=index_cols,
        columns='mois',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    mois_cols = [f"{i:02d}" for i in range(1, 13)]
    pivot = pivot.reindex(columns=mois_cols + ['Total général'], fill_value=0)
    st.subheader("Prévisions par mois (années 2027-2031)")

elif mode_affichage == "Par agence":
    pivot = pd.pivot_table(
        df_temp,
        values='valeur',
        index=index_cols,
        columns='agence',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    st.subheader("Prévisions par agence (années 2027-2031)")

else:  # Par année
    df_temp['annee'] = df_temp['date'].dt.year
    pivot = pd.pivot_table(
        df_temp,
        values='valeur',
        index=index_cols,
        columns='annee',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    st.subheader("Prévisions par année (2027-2031)")

# --------------------------------------------------------------------
# 8. AFFICHAGE DU TABLEAU
# --------------------------------------------------------------------
pivot_reset = pivot.reset_index()
pivot_reset.columns = [str(col) for col in pivot_reset.columns]

if unite == "Volume (hectolitres)":
    for col in pivot_reset.columns[1:]:
        pivot_reset[col] = pivot_reset[col].round(2)

st.dataframe(pivot_reset, use_container_width=True, height=800)

# --------------------------------------------------------------------
# 9. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"previsions_{mode_affichage.lower().replace(' ', '_')}_{unite.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
