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
    h1, h2, h3, h4, h5, h6 {
        color: #000000;
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
        height: 700px !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. TABLEAU DES PRODUITS (fourni par l'utilisateur)
# --------------------------------------------------------------------
PRODUCT_TABLE = """
segment	marque_1	format	contenances	Référence
1-BIERES	1-Queen s	VER	50 cl	159-Queen s 50 cl VER
1-BIERES	1-Queen s	VER	65 cl	103-Queen s 65 cl VER
1-BIERES	1-Queen s	VER	65 cl	103VER-Queen s 65 cl VER
1-BIERES	3-Fresh	VER	50 cl	199-THB Fresh 50 cl VER
1-BIERES	3-Fresh	VER	65 cl	127-THB Fresh 65 cl VER
1-BIERES	4-Castel	VER	50 cl	143-Castel beer 50cl VER
1-BIERES	4-Castel	VER	65 cl	165-Castel beer 65cl VER
1-BIERES	4-THB	CAN	33 cl	105-THB Pilsener 33 cl CAN
1-BIERES	4-THB	CAN	50 cl	186-THB Pilsener 50 cl CAN
1-BIERES	4-THB	FUT	2000 cl	110EXP-THB Pilsener 20L FUT
1-BIERES	4-THB	FUT	2000 cl	110-THB Pilsener 20L FUT
1-BIERES	4-THB	FUT	3000 cl	150EXP-THB Pilsener 30L FUT
1-BIERES	4-THB	FUT	3000 cl	150-THB Pilsener 30L FUT
1-BIERES	4-THB	VER	33 cl	102-THB Pilsener 33 cl VER
1-BIERES	4-THB	VER	50 cl	184-THB Pilsener 50 cl VER
1-BIERES	4-THB	VER	65 cl	101-THB Pilsener 65 cl VER
1-BIERES	5-Gold	CAN	50 cl	173CAN-Gold 8 50 cl CAN
1-BIERES	5-Gold	CAN	50 cl	252-Gold Blonde 50 cl CAN
1-BIERES	5-Gold	CAN	50 cl	260-Gold Blanche 50 cl CAN
1-BIERES	5-Gold	FUT	2000 cl	151-Gold Blanche 20L FUT
1-BIERES	5-Gold	FUT	2000 cl	154-Gold Blonde 20L FUT
1-BIERES	5-Gold	VER	33 cl	129-Gold Blonde 33 cl VER
1-BIERES	5-Gold	VER	33 cl	153-Gold Blanche 33cl VER
1-BIERES	5-Gold	VER	50 cl	158-Gold Blonde 50 cl VER
1-BIERES	5-Gold	VER	50 cl	173-Gold 8 50 cl VER
1-BIERES	5-Gold	VER	50 cl	258-Gold Amigo Tequila 50cl VER
1-BIERES	5-Gold	VER	50 cl	263-Gold Amigo Red 50cl VER
1-BIERES	5-Gold	VER	50 cl	280-Gold Blanche 50 cl VER
1-BIERES	5-Gold	VER	65 cl	130-Gold Blonde 65 cl VER
1-BIERES	6-Beaufort	CAN	50 cl	264CAN-Beaufort 50 CL CAN
1-BIERES	6-Beaufort	FUT	2000 cl	264FUT-Beaufort 20L FUT
1-BIERES	6-Beaufort	VER	33 cl	264-Beaufort 33CL VER
1-BIERES	6-Beaufort	VER	50 cl	264VER-Beaufort 50CL VER
1-BIERES	7-Autres bieres	FUT	2000 cl	110TBL-THB Blanche 20L Export FUT
1-BIERES	7-Autres bieres	FUT	2000 cl	179-Skol 20L FUT
1-BIERES	7-Autres bieres	VER	33 cl	281-Chill 33cl VER
1-BIERES	7-Autres bieres	VER	50 cl	176-Skol 50cl VER
1-BIERES	7-Autres bieres	VER	50 cl	182-Libertalia 50cl VER
1-BIERES	7-Autres bieres	VER	50 cl	184TBL-THB Blanche 50 cl VER
1-BIERES	7-Autres bieres	VER	50 cl	184TH8-THB 8% 50 cl VER
1-BIERES	7-Autres bieres	VER	50 cl	271-Chill 50cl VER
1-BIERES	7-Autres bieres	VER	50 cl	272-Doppel Munich 50CL VER
1-BIERES	7-Autres bieres	VER	65 cl	177-Skol 65cl VER
2-BG	1-Caprice	FUT	2000 cl	110CBB-Caprice Bonbon Anglais 20L FUT
2-BG	1-Caprice	FUT	2000 cl	110COR-Caprice Orange 20L FUT
2-BG	1-Caprice	PET	150 cl	132ANN-Caprice Ananas 150 cl PET
2-BG	1-Caprice	PET	150 cl	132BBA-Caprice Bonbon Anglais 150 cl PET
2-BG	1-Caprice	PET	150 cl	132GRE-Caprice Grenadine 150 cl PET
2-BG	1-Caprice	PET	150 cl	132LET-Caprice Letchi 150 cl PET
2-BG	1-Caprice	PET	150 cl	132POM-Caprice Pomme 150 cl PET
2-BG	1-Caprice	PET	150 cl	135-Caprice Orange 150 cl PET
2-BG	1-Caprice	PET	35 cl	168BBA-Caprice Bonbon Anglais 35 cl PET
2-BG	1-Caprice	PET	50 cl	136-Caprice Orange 50 cl PET
2-BG	1-Caprice	PET	50 cl	139ANN-Caprice Ananas 50 cl PET
2-BG	1-Caprice	PET	50 cl	139BBA-Caprice Bonbon Anglais 50 cl PET
2-BG	1-Caprice	PET	50 cl	139GRE-Caprice Grenadine 50 cl PET
2-BG	1-Caprice	PET	50 cl	139POM-Caprice Pomme 50 cl PET
2-BG	1-Caprice	VER	100 cl	111BBA-Caprice Bonbon Anglais 100 cl VER
2-BG	1-Caprice	VER	100 cl	111COL-Caprice Cola 100 cl VER
2-BG	1-Caprice	VER	100 cl	111GRE-Caprice Grenadine 100 cl VER
2-BG	1-Caprice	VER	100 cl	111LET-Caprice Letchi 100 cl VER
2-BG	1-Caprice	VER	100 cl	131-Caprice Orange 100 cl VER
2-BG	1-Caprice	VER	30 cl	114BBA-Caprice Bonbon Anglais 30 cl VER
2-BG	1-Caprice	VER	30 cl	114COL-Caprice Cola 30 cl VER
2-BG	1-Caprice	VER	30 cl	114GRE-Caprice Grenadine 30 cl VER
2-BG	1-Caprice	VER	30 cl	114LET-Caprice Letchi 30 cl VER
2-BG	1-Caprice	VER	30 cl	122-Caprice Orange 30 cl VER
2-BG	1-XXL	PET	35 cl	170-XXL 35cl PET
2-BG	1-XXL	PET	50 cl	163-XXL 50cl PET
2-BG	1-XXL	VER	30 cl	161-XXL 30cl VER
2-BG	2-Tonic	PET	125 cl	212TON-Tonic 125 cl PET
2-BG	2-Tonic	PET	35 cl	168TON-Tonic 35 cl PET
2-BG	2-Tonic	VER	100 cl	123-Tonic 100 cl VER
2-BG	2-Tonic	VER	30 cl	113-Tonic 30 cl VER
2-BG	3-D jino	PET	125 cl	212COK-D Jino tropical 125cl PET
2-BG	3-D jino	PET	125 cl	212COL-D Jino Cola 125cl PET
2-BG	3-D jino	PET	125 cl	212IPT-D Jino Ice Tea Petillant 125cl PET
2-BG	3-D jino	PET	150 cl	284COK-D Jino Tropical 150cl PET
2-BG	3-D jino	PET	150 cl	284COL-D Jino Cola 150cl PET
2-BG	3-D jino	PET	35 cl	274COK-D Jino Tropical 35cl PET
2-BG	3-D jino	PET	35 cl	274COL-D Jino Cola 35cl PET
2-BG	3-D jino	PET	35 cl	274IPT-D Jino Ice Tea Petillant 35cl PET
2-BG	3-D jino	PET	35 cl	274LIM-D Jino Limonady 35cl PET
2-BG	3-D jino	VER	30 cl	282COL-D Jino Cola 30cl VER
2-BG	3-D jino	VER	30 cl	282IPE-D Jino Ice Tea 30cl VER
2-BG	3-D jino	VER	50 cl	273COK-D Jino Tropical 50cl VER
2-BG	3-D jino	VER	50 cl	273COL-D Jino Cola 50cl VER
2-BG	3-D jino	VER	50 cl	273IPE-D Jino Ice Tea 50cl VER
2-BG	3-D jino	VER	50 cl	273LIM-D Jino Limonady 50cl VER
2-BG	4-Youzou	PET	125 cl	212YOU-Youzou 125cl PET
2-BG	4-Youzou	PET	150 cl	284YOU-Youzou 150 cl PET
2-BG	4-Youzou	PET	35 cl	274YOU-Youzou 35cl PET
2-BG	4-Youzou	PET	50 cl	225YOU-Youzou 50cl PET
2-BG	4-Youzou	VER	100 cl	222YOU-Youzou 100 cl VER
2-BG	4-Youzou	VER	30 cl	282YOU-Youzou 30 cl VER
2-BG	4-Youzou	VER	50 cl	273YOU-Youzou 50cl VER
2-BG	5-World Cola	FUT	2000 cl	110WOR-World Cola 20L FUT
2-BG	5-World Cola	PET	150 cl	284WOR-World Cola 150cl PET
2-BG	5-World Cola	PET	50 cl	273WOR-World Cola 50cl PET
2-BG	5-World Cola	VER	100 cl	222WOR-World Cola 100cl VER
2-BG	5-World Cola	VER	30 cl	282WOR-World Cola 30cl VER
2-BG	6-Coca	FUT	2000 cl	110COC-Coca-Cola 20L FUT
2-BG	6-Coca	PET	150 cl	218-Coca-Cola 150 cl PET
2-BG	6-Coca	PET	35 cl	211-Coca-Cola 35 cl PET
2-BG	6-Coca	PET	35 cl	211ZER-Coca-Cola zero 35cl PET
2-BG	6-Coca	PET	50 cl	215-Coca-Cola 50 cl PET
2-BG	6-Coca	VER	100 cl	217-Coca-Cola 100 cl VER
2-BG	6-Coca	VER	30 cl	216-Coca-Cola 30 cl VER
2-BG	7-Fanta	FUT	2000 cl	110FOR-Fanta Orange 20L FUT
2-BG	7-Fanta	PET	150 cl	219ANN-Fanta Ananas 150 cl PET
2-BG	7-Fanta	PET	150 cl	219-Fanta Orange 150 cl PET
2-BG	7-Fanta	PET	150 cl	219POM-Fanta Pomme 150 cl PET
2-BG	7-Fanta	PET	150 cl	219RAI-Fanta Raisin 150 cl PET
2-BG	7-Fanta	PET	35 cl	239-Fanta Orange 35 cl PET
2-BG	7-Fanta	PET	50 cl	221-Fanta Orange 50 cl PET
2-BG	7-Fanta	PET	50 cl	221POM-Fanta Pomme 50 cl PET
2-BG	7-Fanta	VER	100 cl	220ANN-Fanta Ananas 100 cl VER
2-BG	7-Fanta	VER	100 cl	220-Fanta Orange 100 cl VER
2-BG	7-Fanta	VER	100 cl	220POM-Fanta Pomme 100 cl VER
2-BG	7-Fanta	VER	30 cl	210ANN-Fanta Ananas 30 cl VER
2-BG	7-Fanta	VER	30 cl	210-Fanta Orange 30 cl VER
2-BG	7-Fanta	VER	30 cl	210POM-Fanta Pomme 30 cl VER
2-BG	8-Sprite	PET	150 cl	224-Sprite 150 cl PET
2-BG	8-Sprite	PET	50 cl	225-Sprite 50 cl PET
2-BG	8-Sprite	VER	100 cl	222-Sprite 100 cl VER
2-BG	8-Sprite	VER	30 cl	223-Sprite 30 cl VER
3-EAUX	1-Cristalline	PET	100 cl	190-Cristalline 100 cl PET
3-EAUX	1-Cristalline	PET	150 cl	245-Cristalline 150 cl PET
3-EAUX	1-Cristalline	PET	200 cl	189-Cristalline 200 cl PET
3-EAUX	1-Cristalline	VER	100 cl	270-Cristalline 100 cl VER
3-EAUX	2-Eau vive	PET	150 cl	192-Eau vive 150 cl PET
3-EAUX	2-Eau vive	PET	50 cl	193-Eau vive 50 cl PET
3-EAUX	3-Cristal	PET	150 cl	133-Cristal 150 cl PET
3-EAUX	3-Cristal	VER	100 cl	104-Cristal 100 cl VER
3-EAUX	3-Cristal	VER	30 cl	107-Cristal 30 cl VER
3-EAUX	3-Cristal	VER	50 cl	273CRI-Cristal 50 cl VER
3-EAUX	4-Autre eau	PET	50 cl	198-La Source 50 cl PET
4-JUS	2-Judor	PET	150 cl	247COK-Judor Coktail 150 cl PET
4-JUS	2-Judor	PET	150 cl	247ORA-Judor Orange 150 cl PET
4-JUS	2-Judor	PET	35 cl	240COK-Judor Coktail 35 cl PET
4-JUS	2-Judor	PET	35 cl	240ORA-Judor Orange 35 cl PET
5-ALCOMIX	1-Booster	PET	35 cl	267-Booster Apple-Mix 35CL PET
5-ALCOMIX	1-Booster	PET	35 cl	267CIT-Booster CITRUS 35CL PET
5-ALCOMIX	1-Booster	VER	30 cl	261-Booster Appel-Mix 30CL VER
5-ALCOMIX	1-Booster	VER	30 cl	266-Booster Whisky-Cola 30CL VER
5-ALCOMIX	1-Booster	VER	30 cl	269-Booster Tornado 30CL VER
5-ALCOMIX	1-Booster	VER	30 cl	269GIN-Booster Kamikaz 30CL VER
5-ALCOMIX	1-Booster	VER	50 cl	269APP-Booster Appel-Mix 50CL VER
5-ALCOMIX	1-Booster	VER	50 cl	269TOR-Booster Tornado 50CL BLA VER
6-NEGOCE	2-Negoce	BOI	100 cl	205MAN-Nectar Mangue 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	205ORA-Nectar Orange 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	205PEC-Nectar Peche 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	205TUT-Nectar tutti Frutti 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	249MAN-Jus Gud Mangue 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	249ORA-Jus Gud Orange 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	249PEC-Jus Gud Peche 1L BOI
6-NEGOCE	2-Negoce	BOI	100 cl	249TUT-Jus Gud Tutti Fruit 1L BOI
6-NEGOCE	2-Negoce	CAN	33 cl	145-Heineken 33 cl CAN
6-NEGOCE	2-Negoce	CAN	33 cl	232-Coca-Cola 33 cl CAN
6-NEGOCE	2-Negoce	CAN	33 cl	234-Sprite 33 cl CAN
6-NEGOCE	2-Negoce	CAN	33 cl	235ZER-Coca-Cola Zero 33 cl CAN
6-NEGOCE	2-Negoce	CAN	33 cl	255-Guiness Fes 33 cl CAN
6-NEGOCE	2-Negoce	CAN	50 cl	251-Heineken 50 cl CAN
6-NEGOCE	2-Negoce	CAN	50 cl	254-Skol Force 50 cl CAN
6-NEGOCE	2-Negoce	VER	33 cl	155-Heineken 33 cl VER
6-NEGOCE	2-Negoce	VER	33 cl	253-Skol Cactus 33 cl VER
6-NEGOCE	2-Negoce	VER	34 cl	279-Grantera 34cl VER
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
                # Historique (avant 2027) : bruit et saisonnalité
                # Prévision (2027+) : prolongation tendance + bruit réduit
                if date.year < 2027:
                    seasonal = 1 + 0.3 * np.sin((date.month - 1) * 2 * np.pi / 12)
                    noise = random.uniform(-0.2, 0.2)
                    quantite = max(0, int(base * (1 + i * trend) * seasonal * (1 + noise)))
                else:
                    # Prévision : tendance linéaire + légère saisonnalité, moins de bruit
                    seasonal = 1 + 0.1 * np.sin((date.month - 1) * 2 * np.pi / 12)
                    noise = random.uniform(-0.05, 0.05)
                    # i est l'index global depuis 2017, on continue la tendance
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

# Années : de 2017 à 2031 (toutes les options)
annees_options = list(range(2017, 2032))
selected_annees = st.sidebar.multiselect("Année", options=annees_options, default=annees_options)

# Note sur les prévisions
st.sidebar.markdown("**Note** : Les années 2027 à 2031 sont des **prévisions** (affichées en bleu dans le mode Par année).")

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
    styled = pivot.style.set_properties(**{'color': 'black'})  # pas de coloration spéciale

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
    styled = pivot.style.set_properties(**{'color': 'black'})

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
    # Colonnes des années 2027 à 2031 en bleu
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
    st.subheader(f"Ventes par année (les colonnes 2027+ sont des prévisions en bleu)")
    styled = pivot.style.apply(lambda col: [color_blue(v, col.name) for v in col], axis=0)

# --------------------------------------------------------------------
# 7. AFFICHAGE DU TABLEAU
# --------------------------------------------------------------------
pivot_reset = pivot.reset_index()
pivot_reset.columns = [str(col) for col in pivot_reset.columns]

if unite == "Volume (hectolitres)":
    for col in pivot_reset.columns[1:]:
        pivot_reset[col] = pivot_reset[col].round(2)

# Utiliser le Styler pour l'affichage si coloration définie
if mode_affichage == "Par année":
    # Réapplique le style sur le DataFrame reset_index (les colonnes années sont des chaînes)
    # On reconstruit le Styler sur pivot_reset avec les mêmes règles
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
    st.dataframe(styled, use_container_width=True, height=700)
else:
    st.dataframe(pivot_reset, use_container_width=True, height=700)

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
