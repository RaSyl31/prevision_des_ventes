import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import random
from io import StringIO

# --------------------------------------------------------------------
# Configuration de la page
# --------------------------------------------------------------------
st.set_page_config(page_title="Analyse et Prévision des ventes", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé : fond gris clair, texte noir, tableau agrandi, titres ajustés
# --------------------------------------------------------------------
st.markdown("""
<style>
    /* Fond principal gris clair */
    .stApp {
        background-color: #F0F2F6;
    }

    /* Texte principal noir */
    .stMarkdown, .stText, .stCaption, .stDataFrame, .stTable, label {
        color: #000000;
    }

    /* Titres : plus grands, moins d'espace au-dessus */
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

    /* Sidebar : fond gris clair, texte noir */
    .css-1d391kg, .css-1lcbmhc, .css-1out211 {
        background-color: #E0E2E6;
    }
    .css-1d391kg .stMarkdown, .css-1d391kg .stText, .css-1d391kg label {
        color: #000000;
    }

    /* Widgets : fond blanc, bordure grise, texte noir */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stSlider div[data-baseweb="slider"] {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        color: #000000;
    }

    /* Boutons */
    .stButton > button, .stDownloadButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #45a049;
    }

    /* Liens */
    a {
        color: #0000EE;
    }

    /* Tableaux : agrandir et mettre en avant */
    .stDataFrame {
        width: 100%;
        border: 1px solid #CCCCCC;
    }
    div[data-testid="stDataFrame"] {
        height: 800px !important;  /* hauteur plus grande */
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. TABLEAU DES PRODUITS (fourni par l'utilisateur)
# --------------------------------------------------------------------
PRODUCT_TABLE = """
... (votre tableau complet, identique au précédent) ...
"""

# Parser le tableau produits
df_products = pd.read_csv(StringIO(PRODUCT_TABLE), sep='\t')
df_products = df_products[df_products['Référence'].notna() & ~df_products['Référence'].str.contains('Total', na=False)]

def extraire_contenance(contenances):
    m = re.search(r'(\d+)\s*cl', contenances)
    return int(m.group(1)) if m else None

df_products['contenance_cl'] = df_products['contenances'].apply(extraire_contenance)

# --------------------------------------------------------------------
# 2. GÉNÉRATION DE DONNÉES FICTIVES (de 2017 à 2031)
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
    for _, prod in df_products.iterrows():
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
                    'reference': prod['Référence'],
                    'quantite': quantite
                })
    return pd.DataFrame(data)

# --------------------------------------------------------------------
# 3. CHARGEMENT DES DONNÉES
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
            required_cols = ['date', 'agence', 'reference', 'quantite']
            if not all(col in df_ventes.columns for col in required_cols):
                st.error(f"Le fichier CSV doit contenir les colonnes : {', '.join(required_cols)}")
                st.stop()
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            st.success("Fichier chargé avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
            st.stop()
    else:
        st.info("Veuillez téléverser un fichier CSV avec les colonnes : date, agence, reference, quantite.")
        st.stop()

# Fusionner avec le tableau produits
df_ventes = df_ventes.merge(df_products, left_on='reference', right_on='Référence', how='left')

# --------------------------------------------------------------------
# 4. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité d'affichage", ["Quantité (bouteilles)", "Volume (hectolitres)"])
df_ventes['valeur'] = df_ventes['quantite'] if unite == "Quantité (bouteilles)" else df_ventes['quantite'] * df_ventes['contenance_cl'] / 10000.0

# --------------------------------------------------------------------
# 5. FILTRES MULTIPLES (cases à cocher)
# --------------------------------------------------------------------
st.sidebar.header("Filtres (sélection multiple)")

mode_affichage = st.sidebar.radio("Affichage", ["Par mois", "Par agence", "Par année"])

# Années : de 2017 à 2031 avec indicateur pour les prévisions
annees_options = list(range(2017, 2032))

# Fonction d'affichage avec point bleu pour prévisions
def format_annee(annee):
    if annee >= 2027:
        return f"{annee} 🔵 (prévision)"
    else:
        return str(annee)

selected_annees = st.sidebar.multiselect(
    "Année",
    options=annees_options,
    default=annees_options,
    format_func=format_annee
)

st.sidebar.markdown("**Note** : 🔵 = années de prévision (2027-2031).")

# Filtrer par années
df_temp = df_ventes[df_ventes['date'].dt.year.isin(selected_annees)]

# Segment
segments_options = sorted(df_temp['segment'].dropna().unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)
df_temp = df_temp[df_temp['segment'].isin(selected_segments)]

# Marque
marques_options = sorted(df_temp['marque_1'].dropna().unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)
df_temp = df_temp[df_temp['marque_1'].isin(selected_marques)]

# Format
formats_options = sorted(df_temp['format'].dropna().unique())
selected_formats = st.sidebar.multiselect("Format", options=formats_options, default=formats_options)
df_temp = df_temp[df_temp['format'].isin(selected_formats)]

# Contenance
contenances_options = sorted(df_temp['contenances'].dropna().unique())
selected_contenances = st.sidebar.multiselect("Contenance", options=contenances_options, default=contenances_options)
df_temp = df_temp[df_temp['contenances'].isin(selected_contenances)]

# Agence (seulement pour le mode "Par mois")
if mode_affichage == "Par mois":
    agences_options = sorted(df_temp['agence'].unique())
    selected_agences = st.sidebar.multiselect("Agence", options=agences_options, default=agences_options)
    df_temp = df_temp[df_temp['agence'].isin(selected_agences)]

# --------------------------------------------------------------------
# 6. TABLEAU CROISÉ DYNAMIQUE
# --------------------------------------------------------------------
index_cols = ['segment', 'marque_1', 'format', 'contenances', 'Référence']

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
    st.subheader(f"Ventes par mois - Années : {', '.join(map(str, selected_annees))}")
    styled = None

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
    st.subheader(f"Ventes par agence - Années : {', '.join(map(str, selected_annees))}")
    styled = None

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
    st.subheader("Ventes par année (colonnes bleues = prévisions 2027-2031)")
    # Fonction de coloration pour les colonnes années >=2027
    def color_blue(val, col_name):
        if col_name in ['Total général']:
            return ''
        try:
            year = int(col_name)
            if year >= 2027:
                return 'color: blue; font-weight: bold'
        except:
            pass
        return ''
    styled = pivot.style.apply(lambda col: [color_blue(v, col.name) for v in col], axis=0)

# --------------------------------------------------------------------
# 7. AFFICHAGE DU TABLEAU
# --------------------------------------------------------------------
pivot_reset = pivot.reset_index()
pivot_reset.columns = [str(col) for col in pivot_reset.columns]

if unite == "Volume (hectolitres)":
    for col in pivot_reset.columns[1:]:
        pivot_reset[col] = pivot_reset[col].round(2)

# Si style appliqué (mode année), on le réapplique sur le DataFrame reset
if mode_affichage == "Par année":
    def color_year_cols(val, col_name):
        if col_name in ['Total général', 'segment', 'marque_1', 'format', 'contenances', 'Référence']:
            return ''
        try:
            year = int(col_name)
            if year >= 2027:
                return 'color: blue; font-weight: bold'
        except:
            pass
        return ''
    styled = pivot_reset.style.apply(lambda col: [color_year_cols(v, col.name) for v in col], axis=0)
    st.dataframe(styled, use_container_width=True, height=800)
else:
    st.dataframe(pivot_reset, use_container_width=True, height=800)

# --------------------------------------------------------------------
# 8. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"ventes_{mode_affichage.lower().replace(' ', '_')}_{unite.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
