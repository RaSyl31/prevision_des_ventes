import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random

# --------------------------------------------------------------------
# Configuration de la page
# --------------------------------------------------------------------
st.set_page_config(page_title="Analyse des ventes", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé : fond noir, texte blanc, sidebar plus foncée, accents rouges
# --------------------------------------------------------------------
st.markdown("""
<style>
    /* Fond principal noir */
    .stApp {
        background-color: #000000;
    }

    /* Texte principal blanc */
    .stMarkdown, .stText, .stCaption, .stDataFrame, .stTable {
        color: #FFFFFF;
    }

    /* Titres en rouge */
    h1, h2, h3, h4, h5, h6 {
        color: #E63946;
    }

    /* Sidebar : fond noir plus foncé, texte blanc */
    .css-1d391kg, .css-1lcbmhc, .css-1out211 {
        background-color: #111111;
    }
    .css-1d391kg .stMarkdown, .css-1d391kg .stText, .css-1d391kg label {
        color: #FFFFFF;
    }

    /* Widgets (selectbox, multiselect, slider) : fond sombre, bordure rouge */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    .stSlider div[data-baseweb="slider"] {
        background-color: #1A1A1A;
        border: 1px solid #E63946;
        color: #FFFFFF;
    }

    /* Boutons rouges */
    .stButton > button, .stDownloadButton > button {
        background-color: #E63946;
        color: white;
        border: none;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #C1121F;
    }

    /* Liens en rouge */
    a {
        color: #E63946;
    }

    /* Tableaux : bordures rouges */
    .stDataFrame, .stTable {
        border: 1px solid #E63946;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTES DES AGENCES, SEGMENTS, MARQUES, ARTICLES
# --------------------------------------------------------------------
AGENCES = [
    "00-Siège",
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

# Table article : (segment, marque, article)
ARTICLES = [
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

# Conversion en DataFrame pour faciliter le filtrage
df_articles = pd.DataFrame(ARTICLES, columns=["segment", "marque", "article"])

# --------------------------------------------------------------------
# 2. GÉNÉRATION DE DONNÉES FICTIVES (à remplacer par vos vraies données)
# --------------------------------------------------------------------
@st.cache_data
def generate_dummy_data():
    """Génère 3 ans de données mensuelles pour toutes les combinaisons agence/article."""
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2023, 12, 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # début de mois

    data = []
    for agence in AGENCES:
        for _, row in df_articles.iterrows():
            segment, marque, article = row['segment'], row['marque'], row['article']
            # Tendance de base + saisonnalité + bruit
            base = random.uniform(50, 500)
            trend = random.uniform(0, 5)  # croissance mensuelle
            for i, date in enumerate(dates):
                # Saisonnalité : pic en été (décembre) et creux en hiver (juin)
                month = date.month
                seasonal = 1 + 0.3 * np.sin((month - 1) * 2 * np.pi / 12)
                # Bruit aléatoire
                noise = random.uniform(-0.2, 0.2)
                quantite = max(0, int(base * (1 + i * trend / 100) * seasonal * (1 + noise)))
                data.append({
                    "date": date,
                    "agence": agence,
                    "segment": segment,
                    "marque": marque,
                    "article": article,
                    "quantite": quantite
                })
    return pd.DataFrame(data)

# --------------------------------------------------------------------
# 3. CHARGEMENT DES DONNÉES
# --------------------------------------------------------------------
st.title("📊 Analyse des ventes par mois / par agence")

data_option = st.radio(
    "Source des données :",
    ["Utiliser des données fictives (démo)", "Importer un fichier CSV"]
)

if data_option == "Utiliser des données fictives (démo)":
    df = generate_dummy_data()
    st.success("Données fictives générées.")
else:
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Vérification des colonnes nécessaires
        required_cols = ['date', 'agence', 'segment', 'marque', 'article', 'quantite']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Le fichier CSV doit contenir les colonnes : {', '.join(required_cols)}")
            st.stop()
        df['date'] = pd.to_datetime(df['date'])
        st.success("Fichier chargé avec succès.")
    else:
        st.info("Veuillez téléverser un fichier CSV avec les colonnes : date, agence, segment, marque, article, quantite.")
        st.stop()

# --------------------------------------------------------------------
# 4. BARRE LATÉRALE : MODE D'AFFICHAGE ET FILTRES MULTIPLES
# --------------------------------------------------------------------
st.sidebar.header("Paramètres d'affichage")

# Choix du mode
mode_affichage = st.sidebar.radio("Affichage", ["Par mois", "Par Agence"])

# Filtres multiples
st.sidebar.subheader("Filtres (sélection multiple)")

# Année (multiselect)
annees_disponibles = sorted(df['date'].dt.year.unique())
selected_annees = st.sidebar.multiselect(
    "Année",
    options=annees_disponibles,
    default=annees_disponibles
)

# Segment (multiselect)
segments_disponibles = sorted(df['segment'].unique())
selected_segments = st.sidebar.multiselect(
    "Segment",
    options=segments_disponibles,
    default=segments_disponibles
)

# Marque (multiselect) - filtrée selon les segments sélectionnés
if selected_segments:
    marques_disponibles = sorted(df[df['segment'].isin(selected_segments)]['marque'].unique())
else:
    marques_disponibles = sorted(df['marque'].unique())
selected_marques = st.sidebar.multiselect(
    "Marque",
    options=marques_disponibles,
    default=marques_disponibles
)

# Article (multiselect) - filtré selon segments et marques
if selected_segments and selected_marques:
    articles_disponibles = sorted(df[(df['segment'].isin(selected_segments)) & 
                                     (df['marque'].isin(selected_marques))]['article'].unique())
else:
    articles_disponibles = sorted(df['article'].unique())
selected_articles = st.sidebar.multiselect(
    "Article",
    options=articles_disponibles,
    default=articles_disponibles
)

# --------------------------------------------------------------------
# 5. FILTRAGE DES DONNÉES
# --------------------------------------------------------------------
df_filtered = df[
    (df['date'].dt.year.isin(selected_annees)) &
    (df['segment'].isin(selected_segments)) &
    (df['marque'].isin(selected_marques)) &
    (df['article'].isin(selected_articles))
]

if df_filtered.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --------------------------------------------------------------------
# 6. CRÉATION DU TABLEAU CROISÉ DYNAMIQUE
# --------------------------------------------------------------------
if mode_affichage == "Par mois":
    # Extraire le mois (format 01, 02, ...)
    df_filtered['mois'] = df_filtered['date'].dt.month.astype(str).str.zfill(2)
    # Tableau croisé : index = hiérarchie segment > marque > article, colonnes = mois
    pivot = pd.pivot_table(
        df_filtered,
        values='quantite',
        index=['segment', 'marque', 'article'],
        columns='mois',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    # Réordonner les colonnes de 01 à 12 puis Total général
    mois_cols = [f"{i:02d}" for i in range(1, 13)]
    pivot = pivot.reindex(columns=mois_cols + ['Total général'], fill_value=0)
    # Titre du tableau
    st.subheader("Ventes par mois (toutes agences confondues)")
else:  # Par Agence
    pivot = pd.pivot_table(
        df_filtered,
        values='quantite',
        index=['segment', 'marque', 'article'],
        columns='agence',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    # Titre du tableau
    st.subheader("Ventes par agence (tous mois confondus)")

# --------------------------------------------------------------------
# 7. AFFICHAGE DU TABLEAU
# --------------------------------------------------------------------
# Réinitialiser l'index pour un affichage propre
pivot_reset = pivot.reset_index()
# Convertir les colonnes en chaînes pour éviter les problèmes d'affichage
pivot_reset.columns = [str(col) for col in pivot_reset.columns]

# Afficher le tableau avec mise en forme
st.dataframe(pivot_reset, use_container_width=True)

# --------------------------------------------------------------------
# 8. TÉLÉCHARGEMENT DU TABLEAU
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"ventes_{mode_affichage.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
