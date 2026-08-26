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
# 1. LISTE DES ARTICLES ACTIFS
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

df_active = pd.DataFrame(ACTIVE_ARTICLES, columns=["segment_actif", "marque_actif", "article_actif"])

# --------------------------------------------------------------------
# 2. TABLE DE CORRESPONDANCE RÉFÉRENCE -> ARTICLE
# --------------------------------------------------------------------
# (Insérer ici le dictionnaire complet fourni précédemment)
REFERENCE_TO_ARTICLE = {
    "105-THB Pilsener 33 cl CAN": "THB Pilsener 33 cl CAN",
    "102-THB Pilsener 33 cl VER": "THB Pilsener 33 cl VER",
    "186-THB Pilsener 50 cl CAN": "THB Pilsener 50 cl CAN",
    "184-THB Pilsener 50 cl VER": "THB Pilsener 50 cl VER",
    "110EXP-THB Pilsener 20L FUT": "THB Pilsener 20L FUT",
    "150EXP-THB Pilsener 30L FUT": "THB Pilsener 30L FUT",
    "132BBA-Caprice Bonbon Anglais 150 cl PET": "Caprice Bonbon Anglais 150 cl PET",
    "159-Queen s 50 cl VER": "Queen s 50 cl VER",
    "103-Queen s 65 cl VER": "Queen s 65 cl VER",
    "127-THB Fresh 65 cl VER": "THB Fresh 65 cl VER",
    "101-THB Pilsener 65 cl VER": "THB Pilsener 65 cl VER",
    "110-THB Pilsener 20L FUT": "THB Pilsener 20L FUT",
    "143-Castel beer 50cl VER": "Castel beer 50cl VER",
    "129-Gold Blonde 33 cl VER": "Gold Blonde 33 cl VER",
    "158-Gold Blonde 50 cl VER": "Gold Blonde 50 cl VER",
    "252-Gold Blonde 50 cl CAN": "Gold Blonde 50 cl CAN",
    "173-Gold 8 50 cl VER": "Gold 8 50 cl VER",
    "153-Gold Blanche 33cl VER": "Gold Blanche 33cl VER",
    "151-Gold Blanche 20L FUT": "Gold Blanche 20L FUT",
    "258-Gold Amigo Tequila 50cl VER": "Gold Amigo Tequila 50cl VER",
    "176-Skol 50cl VER": "Skol 50cl VER",
    "177-Skol 65cl VER": "Skol 65cl VER",
    "182-Libertalia 50cl VER": "Libertalia 50cl VER",
    "114BBA-Caprice Bonbon Anglais 30 cl VER": "Caprice Bonbon Anglais 30 cl VER",
    "168BBA-Caprice Bonbon Anglais 35 cl PET": "Caprice Bonbon Anglais 35 cl PET",
    "139BBA-Caprice Bonbon Anglais 50 cl PET": "Caprice Bonbon Anglais 50 cl PET",
    "111BBA-Caprice Bonbon Anglais 100 cl VER": "Caprice Bonbon Anglais 100 cl VER",
    "114GRE-Caprice Grenadine 30 cl VER": "Caprice Grenadine 30 cl VER",
    "111GRE-Caprice Grenadine 100 cl VER": "Caprice Grenadine 100 cl VER",
    "122-Caprice Orange 30 cl VER": "Caprice Orange 30 cl VER",
    "136-Caprice Orange 50 cl PET": "Caprice Orange 50 cl PET",
    "131-Caprice Orange 100 cl VER": "Caprice Orange 100 cl VER",
    "135-Caprice Orange 150 cl PET": "Caprice Orange 150 cl PET",
    "113-Tonic 30 cl VER": "Tonic 30 cl VER",
    "123-Tonic 100 cl VER": "Tonic 100 cl VER",
    "211ZER-Coca-Cola zero 35cl PET": "Coca-Cola zero 35cl PET",
    "216-Coca-Cola 30 cl VER": "Coca-Cola 30 cl VER",
    "211-Coca-Cola 35 cl PET": "Coca-Cola 35 cl PET",
    "215-Coca-Cola 50 cl PET": "Coca-Cola 50 cl PET",
    "217-Coca-Cola 100 cl VER": "Coca-Cola 100 cl VER",
    "218-Coca-Cola 150 cl PET": "Coca-Cola 150 cl PET",
    "239-Fanta Orange 35 cl PET": "Fanta Orange 35 cl PET",
    "210-Fanta Orange 30 cl VER": "Fanta Orange 30 cl VER",
    "221-Fanta Orange 50 cl PET": "Fanta Orange 50 cl PET",
    "220-Fanta Orange 100 cl VER": "Fanta Orange 100 cl VER",
    "219-Fanta Orange 150 cl PET": "Fanta Orange 150 cl PET",
    "210ANN-Fanta Ananas 30 cl VER": "Fanta Ananas 30 cl VER",
    "220ANN-Fanta Ananas 100 cl VER": "Fanta Ananas 100 cl VER",
    "219ANN-Fanta Ananas 150 cl PET": "Fanta Ananas 150 cl PET",
    "210POM-Fanta Pomme 30 cl VER": "Fanta Pomme 30 cl VER",
    "221POM-Fanta Pomme 50 cl PET": "Fanta Pomme 50 cl PET",
    "220POM-Fanta Pomme 100 cl VER": "Fanta Pomme 100 cl VER",
    "219POM-Fanta Pomme 150 cl PET": "Fanta Pomme 150 cl PET",
    "223-Sprite 30 cl VER": "Sprite 30 cl VER",
    "222-Sprite 100 cl VER": "Sprite 100 cl VER",
    "224-Sprite 150 cl PET": "Sprite 150 cl PET",
    "161-XXL 30cl VER": "XXL 30cl VER",
    "170-XXL 35cl PET": "XXL 35cl PET",
    "163-XXL 50cl PET": "XXL 50cl PET",
    "190-Cristalline 100 cl PET": "Cristalline 100 cl PET",
    "245-Cristalline 150 cl PET": "Cristalline 150 cl PET",
    "189-Cristalline 200 cl PET": "Cristalline 200 cl PET",
    "193-Eau vive 50 cl PET": "Eau vive 50 cl PET",
    "192-Eau vive 150 cl PET": "Eau vive 150 cl PET",
    "107-Cristal 30 cl VER": "Cristal 30 cl VER",
    "104-Cristal 100 cl VER": "Cristal 100 cl VER",
    "133-Cristal 150 cl PET": "Cristal 150 cl PET",
    "240COK-Judor Coktail 35 cl PET": "Judor Coktail 35 cl PET",
    "247COK-Judor Coktail 150 cl PET": "Judor Coktail 150 cl PET",
    "240ORA-Judor Orange 35 cl PET": "Judor Orange 35 cl PET",
    "247ORA-Judor Orange 150 cl PET": "Judor Orange 150 cl PET",
    "279-Grantera 34cl VER": "Grantera 34cl VER",
    "145-Heineken 33 cl CAN": "Heineken 33 cl CAN",
    "251-Heineken 50 cl CAN": "Heineken 50 cl CAN",
    "155-Heineken 33 cl VER": "Heineken 33 cl VER",
    "253-Skol Cactus 33 cl VER": "Skol Cactus 33 cl VER",
    "254-Skol Force 50 cl CAN": "Skol Force 50 cl CAN",
    "255-Guiness Fes 33 cl CAN": "Guiness Fes 33 cl CAN",
    "235ZER-Coca-Cola Zero 33 cl CAN": "Coca-Cola Zero 33 cl CAN",
    "232-Coca-Cola 33 cl CAN": "Coca-Cola 33 cl CAN",
    "234-Sprite 33 cl CAN": "Sprite 33 cl CAN",
    "205MAN-Nectar Mangue 1L BOI": "Nectar Mangue 1L BOI",
    "205ORA-Nectar Orange 1L BOI": "Nectar Orange 1L BOI",
    "205PEC-Nectar Peche 1L BOI": "Nectar Peche 1L BOI",
    "205TUT-Nectar tutti Frutti 1L BOI": "Nectar tutti Frutti 1L BOI",
    "249MAN-Jus Gud Mangue 1L BOI": "Jus Gud Mangue 1L BOI",
    "249ORA-Jus Gud Orange 1L BOI": "Jus Gud Orange 1L BOI",
    "249PEC-Jus Gud Peche 1L BOI": "Jus Gud Peche 1L BOI",
    "249TUT-Jus Gud Tutti Fruit 1L BOI": "Jus Gud Tutti Fruit 1L BOI",
    "130-Gold Blonde 65 cl VER": "Gold Blonde 65 cl VER",
    "179-Skol 20L FUT": "Skol 20L FUT",
    "165-Castel beer 65cl VER": "Castel beer 65cl VER",
    "260-Gold Blanche 50 cl CAN": "Gold Blanche 50 cl CAN",
    "263-Gold Amigo Red 50cl VER": "Gold Amigo Red 50cl VER",
    "261-Booster Appel-Mix 30CL VER": "Booster Appel-Mix 30CL VER",
    "150-THB Pilsener 30L FUT": "THB Pilsener 30L FUT",
    "199-THB Fresh 50 cl VER": "THB Fresh 50 cl VER",
    "264-Beaufort 33CL VER": "Beaufort 33CL VER",
    "114LET-Caprice Letchi 30 cl VER": "Caprice Letchi 30 cl VER",
    "111LET-Caprice Letchi 100 cl VER": "Caprice Letchi 100 cl VER",
    "132LET-Caprice Letchi 150 cl PET": "Caprice Letchi 150 cl PET",
    "114COL-Caprice Cola 30 cl VER": "Caprice Cola 30 cl VER",
    "111COL-Caprice Cola 100 cl VER": "Caprice Cola 100 cl VER",
    "219RAI-Fanta Raisin 150 cl PET": "Fanta Raisin 150 cl PET",
    "267-Booster Apple-Mix 35CL PET": "Booster Apple-Mix 35CL PET",
    "266-Booster Whisky-Cola 30CL VER": "Booster Whisky-Cola 30CL VER",
    "264CAN-Beaufort 50 CL CAN": "Beaufort 50 CL CAN",
    "271-Chill 50cl VER": "Chill 50cl VER",
    "225-Sprite 50 cl PET": "Sprite 50 cl PET",
    "270-Cristalline 100 cl VER": "Cristalline 100 cl VER",
    "269-Booster Tornado 30CL VER": "Booster Tornado 30CL VER",
    "264FUT-Beaufort 20L FUT": "Beaufort 20L FUT",
    "173CAN-Gold 8 50 cl CAN": "Gold 8 50 cl CAN",
    "280-Gold Blanche 50 cl VER": "Gold Blanche 50 cl VER",
    "281-Chill 33cl VER": "Chill 33cl VER",
    "272-Doppel Munich 50CL VER": "Doppel Munich 50CL VER",
    "282COL-D Jino Cola 30cl VER": "D Jino Cola 30cl VER",
    "274COL-D Jino Cola 35cl PET": "D Jino Cola 35cl PET",
    "273COL-D Jino Cola 50cl VER": "D Jino Cola 50cl VER",
    "284COL-D Jino Cola 150cl PET": "D Jino Cola 150cl PET",
    "274LIM-D Jino Limonady 35cl PET": "D Jino Limonady 35cl PET",
    "273LIM-D Jino Limonady 50cl VER": "D Jino Limonady 50cl VER",
    "274COK-D Jino Tropical 35cl PET": "D Jino Tropical 35cl PET",
    "273COK-D Jino Tropical 50cl VER": "D Jino Tropical 50cl VER",
    "284COK-D Jino Tropical 150cl PET": "D Jino Tropical 150cl PET",
    "282IPE-D Jino Ice Tea 30cl VER": "D Jino Ice Tea 30cl VER",
    "273IPE-D Jino Ice Tea 50cl VER": "D Jino Ice Tea 50cl VER",
    "269GIN-Booster Kamikaz 30CL VER": "Booster Kamikaz 30CL VER",
    "110CBB-Caprice Bonbon Anglais 20L FUT": "Caprice Bonbon Anglais 20L FUT",
    "110COC-Coca-Cola 20L FUT": "Coca-Cola 20L FUT",
    "110FOR-Fanta Orange 20L FUT": "Fanta Orange 20L FUT",
    "184TBL-THB Blanche 50 cl VER": "THB Blanche 50 cl VER",
    "110TBL-THB Blanche 20L Export FUT": "THB Blanche 20L Export FUT",
    "184TH8-THB 8% 50 cl VER": "THB 8% 50 cl VER",
    "103VER-Queen s 65 cl VER": "Queen s 65 cl VER",
    "264VER-Beaufort 50CL VER": "Beaufort 50CL VER",
    "139GRE-Caprice Grenadine 50 cl PET": "Caprice Grenadine 50 cl PET",
    "132GRE-Caprice Grenadine 150 cl PET": "Caprice Grenadine 150 cl PET",
    "139POM-Caprice Pomme 50 cl PET": "Caprice Pomme 50 cl PET",
    "132POM-Caprice Pomme 150 cl PET": "Caprice Pomme 150 cl PET",
    "139ANN-Caprice Ananas 50 cl PET": "Caprice Ananas 50 cl PET",
    "132ANN-Caprice Ananas 150 cl PET": "Caprice Ananas 150 cl PET",
    "168TON-Tonic 35 cl PET": "Tonic 35 cl PET",
    "212TON-Tonic 125 cl PET": "Tonic 125 cl PET",
    "212COL-D Jino Cola 125cl PET": "D Jino Cola 125cl PET",
    "212COK-D Jino tropical 125cl PET": "D Jino tropical 125cl PET",
    "274IPT-D Jino Ice Tea Petillant 35cl PET": "D Jino Ice Tea Petillant 35cl PET",
    "212IPT-D Jino Ice Tea Petillant 125cl PET": "D Jino Ice Tea Petillant 125cl PET",
    "282YOU-Youzou 30 cl VER": "Youzou 30 cl VER",
    "274YOU-Youzou 35cl PET": "Youzou 35cl PET",
    "225YOU-Youzou 50cl PET": "Youzou 50cl PET",
    "273YOU-Youzou 50cl VER": "Youzou 50cl VER",
    "222YOU-Youzou 100 cl VER": "Youzou 100 cl VER",
    "284YOU-Youzou 150 cl PET": "Youzou 150 cl PET",
    "282WOR-World Cola 30cl VER": "World Cola 30cl VER",
    "273WOR-World Cola 50cl PET": "World Cola 50cl PET",
    "222WOR-World Cola 100cl VER": "World Cola 100cl VER",
    "284WOR-World Cola 150cl PET": "World Cola 150cl PET",
    "273CRI-Cristal 50 cl VER": "Cristal 50 cl VER",
    "269TOR-Booster Tornado 50CL BLA VER": "Booster Tornado 50CL BLA VER",
    "269APP-Booster Appel-Mix 50CL VER": "Booster Appel-Mix 50CL VER",
    "267CIT-Booster CITRUS 35CL PET": "Booster CITRUS 35CL PET",
    "212YOU-Youzou 125cl PET": "Youzou 125cl PET",
    "198-La Source 50 cl PET": "La Source 50 cl PET",
    "154-Gold Blonde 20L FUT": "Gold Blonde 20L FUT",
    "110COR-Caprice Orange 20L FUT": "Caprice Orange 20L FUT",
    "110WOR-World Cola 20L FUT": "World Cola 20L FUT",
    "128-THB Fresh 33 cl VER": "THB Fresh 33 cl VER",
    "150GBL-Gold Blanche 30L FUT": "Gold Blanche 30L FUT",
    "150CBB-Caprice Bonbon Anglais 30L FUT": "Caprice Bonbon Anglais 30L FUT",
    "150COR-Caprice Orange 30L FUT": "Caprice Orange 30L FUT",
    "114POM-Caprice Pomme 30 cl VER": "Caprice Pomme 30 cl VER",
    "111POM-Caprice Pomme 100 cl VER": "Caprice Pomme 100 cl VER",
    "114ANN-Caprice Ananas 30 cl VER": "Caprice Ananas 30 cl VER",
    "111ANN-Caprice Ananas 100 cl VER": "Caprice Ananas 100 cl VER",
    "150WOR-World Cola 30L FUT": "World Cola 30L FUT",
    "269VOR-Booster Tornado 50CL VER VER": "Booster Tornado 50CL VER VER",
    "269CUB-Booster CUBA LIBRE 50CL VER": "Booster CUBA LIBRE 50CL VER",
    "269EXO-Booster EXOTIQUE 50CL VER": "Booster EXOTIQUE 50CL VER",
    "110EXP-THB Pilsener 20L Export FUT": "THB Pilsener 20L Export FUT",
    "150EXP-THB Pilsener 30L Export FUT": "THB Pilsener 30L Export FUT",
    "167-Queen s 33 cl VER": "Queen s 33 cl VER",
    "282WOB-World Cola 30cl WOCO VER": "World Cola 30cl WOCO VER",
    "222WOB-World Cola 100cl WOCO VER": "World Cola 100cl WOCO VER",
    "267TOR-Booster Tornado 35CL PET": "Booster Tornado 35CL PET",
    "102RAC-Racines 33 cl VER": "Racines 33 cl VER",
    "125-Caprice Passion 100 cl VER": "Caprice Passion 100 cl VER",
    "102SPE-THB Speciale NOEL 33 cl VER": "THB Speciale NOEL 33 cl VER",
    "268AMS-Gold Amigo 33cl VER": "Gold Amigo 33cl VER",
    "211WOR-World Cola 35cl PET": "World Cola 35cl PET",
    "161XLB-XXL 30cl BOB VER": "XXL 30cl BOB VER",
    "105XXL-XXL 33 cl CAN": "XXL 33 cl CAN",
    "199FRE-BOTA Fresh 50 cl VER": "BOTA Fresh 50 cl VER",
    "400VAL-Valmont 50cl": "Valmont 50cl",
    "128CAN-FRESH 33 cl EXPORT CAN": "FRESH 33 cl EXPORT CAN",
    "105BFT-Beaufort 33 cl CAN": "Beaufort 33 cl CAN",
    "105BBA-Caprice Bonbon Anglais 33 cl CAN": "Caprice Bonbon Anglais 33 cl CAN",
    "105GRE-Caprice Grenadine 33 cl CAN": "Caprice Grenadine 33 cl CAN",
    "105ORA-Caprice Orange 33 cl CAN": "Caprice Orange 33 cl CAN",
    "105WOR-World Cola 33 cl CAN": "World Cola 33 cl CAN",
    "105FRE-FRESH 33 cl CAN": "FRESH 33 cl CAN",
    "129ROS-Gold Rosee 33cl VER": "Gold Rosee 33cl VER",
    "168GRE-Caprice Grenadine 35 cl PET": "Caprice Grenadine 35 cl PET",
    "169-Caprice Orange 35 cl PET": "Caprice Orange 35 cl PET",
    "236FOS-FOSA 50 cl CAN": "FOSA 50 cl CAN",
    "193EVV-Eau vive 50 cl VER": "Eau vive 50 cl VER",
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
# 5. FONCTION DE CHARGEMENT ET NETTOYAGE AVEC SIMILARITÉ AMÉLIORÉE
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

    df['Année'] = pd.to_numeric(df['Année'].astype(str).str.replace(' ', ''), errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)

    df['ventes_hecto'] = df['ventes hecto'].apply(nettoyer_nombre)
    df['mois_num'] = df['Mois'].apply(parse_mois)
    df = df[df['mois_num'].notna()]
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(int).astype(str) + '-01')
    df['contenance_cl'] = df['contenances'].apply(extraire_contenance_cl)
    df.rename(columns={'Nom agence': 'agence', 'marque_1': 'marque'}, inplace=True)

    # Filtrer pour ne garder que les articles actifs présents
    df = df[df['Référence'].isin(df_active['article_actif'])]

    # --------------------------------------------------------------------
    # Gestion des articles actifs manquants (similarité améliorée)
    # --------------------------------------------------------------------
    articles_presents = set(df['Référence'].unique())
    articles_actifs_set = set(df_active['article_actif'])
    articles_manquants = articles_actifs_set - articles_presents

    if articles_manquants:
        # DataFrame des articles présents avec leurs caractéristiques
        df_presents = df[['Référence', 'segment', 'marque', 'format', 'contenance_cl']].drop_duplicates()
        for article_manquant in articles_manquants:
            info_manquant = df_active[df_active['article_actif'] == article_manquant].iloc[0]
            seg_manquant = info_manquant['segment_actif']
            marque_manquant = info_manquant['marque_actif']
            format_manquant = extraire_format(article_manquant)
            contenance_manquant = extraire_contenance_cl(article_manquant)

            # Recherche de candidats par priorité décroissante
            candidats = pd.DataFrame()
            # 1. Même marque, même format
            candidats = df_presents[
                (df_presents['marque'] == marque_manquant) &
                (df_presents['format'] == format_manquant)
            ]
            # 2. Même marque, tous formats
            if candidats.empty:
                candidats = df_presents[df_presents['marque'] == marque_manquant]
            # 3. Même segment, même format
            if candidats.empty:
                candidats = df_presents[
                    (df_presents['segment'] == seg_manquant) &
                    (df_presents['format'] == format_manquant)
                ]
            # 4. Même segment, tous formats
            if candidats.empty:
                candidats = df_presents[df_presents['segment'] == seg_manquant]

            if not candidats.empty:
                # Choisir le candidat avec la contenance la plus proche
                candidats = candidats.copy()
                candidats['diff_contenance'] = (candidats['contenance_cl'] - contenance_manquant).abs()
                meilleur = candidats.sort_values('diff_contenance').iloc[0]
                article_similaire = meilleur['Référence']

                lignes_similaires = df[df['Référence'] == article_similaire].copy()
                if not lignes_similaires.empty:
                    lignes_similaires['Référence'] = article_manquant
                    lignes_similaires['segment'] = seg_manquant
                    lignes_similaires['marque'] = marque_manquant
                    lignes_similaires['format'] = format_manquant
                    lignes_similaires['contenances'] = info_manquant.get('contenances', '')
                    lignes_similaires['contenance_cl'] = contenance_manquant
                    df = pd.concat([df, lignes_similaires], ignore_index=True)

    return df

# --------------------------------------------------------------------
# 6. FONCTION DE CALCUL DES PRÉVISIONS AMÉLIORÉE
# --------------------------------------------------------------------
@st.cache_data
def calculer_previsions(df_hist, annees_prev):
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    previsions = []

    for keys, group in df_hist.groupby(group_cols):
        serie = group.sort_values('date').set_index('date')['valeur']
        if len(serie) == 0:
            continue

        dernier_mois = serie.index.max()
        date_debut = dernier_mois - pd.DateOffset(years=3)
        serie_recente = serie[serie.index >= date_debut]
        if len(serie_recente) == 0:
            # Utiliser la série complète si moins de 3 ans
            serie_recente = serie

        # Si moins de 12 points, on utilise la moyenne comme prévision constante
        if len(serie_recente) < 12:
            pente = 0
            derniere_valeur = serie_recente.mean() if len(serie_recente) > 0 else 0
        else:
            # Régression linéaire
            x = np.arange(len(serie_recente))
            y = serie_recente.values
            coeffs = np.polyfit(x, y, 1)
            pente = coeffs[0]
            derniere_valeur = serie_recente.iloc[-1]

        segment_val, marque_val, format_val, contenances_val, ref_val, agence_val = keys

        for annee in annees_prev:
            for mois in range(1, 13):
                date_prev = pd.Timestamp(year=annee, month=mois, day=1)
                nb_mois = (date_prev.year - dernier_mois.year) * 12 + (date_prev.month - dernier_mois.month)
                if nb_mois < 0:
                    continue
                prev_value = max(0, derniere_valeur + pente * nb_mois)
                previsions.append({
                    'date': date_prev,
                    'segment': segment_val,
                    'marque': marque_val,
                    'format': format_val,
                    'contenances': contenances_val,
                    'Référence': ref_val,
                    'agence': agence_val,
                    'valeur': prev_value
                })

    return pd.DataFrame(previsions)

# --------------------------------------------------------------------
# 7. CHARGEMENT DU FICHIER
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
# 8. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité d'affichage", ["Hectolitres (ventes hecto)", "Bouteilles (ventes cols)"])

if unite == "Hectolitres (ventes hecto)":
    df['valeur'] = df['ventes_hecto']
else:
    df['valeur'] = df['ventes_hecto'] * 10000 / df['contenance_cl']
    df['valeur'] = df['valeur'].round(0)

# --------------------------------------------------------------------
# 9. GÉNÉRATION DES PRÉVISIONS (2027-2031)
# --------------------------------------------------------------------
df_hist = df[df['date'].dt.year <= 2026].copy()
annees_prev = [2027, 2028, 2029, 2030, 2031]

df_prev = calculer_previsions(df_hist, annees_prev)

# --------------------------------------------------------------------
# 10. AJOUT DE ZÉROS EN DERNIER RECOURS (uniquement si toujours manquant)
# --------------------------------------------------------------------
nouvelles_lignes = []
for _, row_active in df_active.iterrows():
    seg = row_active['segment_actif']
    marque = row_active['marque_actif']
    article = row_active['article_actif']
    format_art = extraire_format(article)
    contenance = extraire_contenance_cl(article)
    for agence in AGENCES:
        masque = (
            (df_prev['segment'] == seg) &
            (df_prev['marque'] == marque) &
            (df_prev['Référence'] == article) &
            (df_prev['agence'] == agence)
        )
        if not masque.any():
            for annee in annees_prev:
                for mois in range(1, 13):
                    nouvelles_lignes.append({
                        'date': pd.Timestamp(year=annee, month=mois, day=1),
                        'segment': seg,
                        'marque': marque,
                        'format': format_art,
                        'contenances': '',  # ou on peut calculer la contenance réelle
                        'Référence': article,
                        'agence': agence,
                        'valeur': 0.0
                    })

if nouvelles_lignes:
    df_prev = pd.concat([df_prev, pd.DataFrame(nouvelles_lignes)], ignore_index=True)

# --------------------------------------------------------------------
# 11. FILTRES
# --------------------------------------------------------------------
st.sidebar.header("Filtres (sélection multiple)")

mode_affichage = st.sidebar.radio("Affichage", ["Par mois", "Par agence", "Par année"])

selected_annees = st.sidebar.multiselect(
    "Année (prévisions)",
    options=annees_prev,
    default=annees_prev
)

df_filtre = df_prev[df_prev['date'].dt.year.isin(selected_annees)]

# Segment
segments_options = sorted(df_filtre['segment'].dropna().unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)
df_filtre = df_filtre[df_filtre['segment'].isin(selected_segments)]

# Marque
marques_options = sorted(df_filtre['marque'].dropna().unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)
df_filtre = df_filtre[df_filtre['marque'].isin(selected_marques)]

# Format
formats_options = sorted(df_filtre['format'].dropna().unique())
selected_formats = st.sidebar.multiselect("Format", options=formats_options, default=formats_options)
df_filtre = df_filtre[df_filtre['format'].isin(selected_formats)]

# Contenance
contenances_options = sorted(df_filtre['contenances'].dropna().unique())
selected_contenances = st.sidebar.multiselect("Contenance", options=contenances_options, default=contenances_options)
df_filtre = df_filtre[df_filtre['contenances'].isin(selected_contenances)]

# Agence (si mode "Par mois")
if mode_affichage == "Par mois":
    agences_options = sorted(df_filtre['agence'].unique())
    selected_agences = st.sidebar.multiselect("Agence", options=agences_options, default=agences_options)
    df_filtre = df_filtre[df_filtre['agence'].isin(selected_agences)]

# --------------------------------------------------------------------
# 12. TABLEAU CROISÉ DYNAMIQUE
# --------------------------------------------------------------------
index_cols = ['segment', 'marque', 'format', 'contenances', 'Référence']

if df_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

if mode_affichage == "Par mois":
    df_filtre['mois'] = df_filtre['date'].dt.month.astype(str).str.zfill(2)
    pivot = pd.pivot_table(
        df_filtre,
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
        df_filtre,
        values='valeur',
        index=index_cols,
        columns='agence',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total général'
    )
    st.subheader("Prévisions par agence (années 2027-2031)")

else:
    df_filtre['annee'] = df_filtre['date'].dt.year
    pivot = pd.pivot_table(
        df_filtre,
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
# 13. AFFICHAGE DU TABLEAU
# --------------------------------------------------------------------
pivot_reset = pivot.reset_index()
pivot_reset.columns = [str(col) for col in pivot_reset.columns]

if unite == "Hectolitres (ventes hecto)":
    for col in pivot_reset.columns[1:]:
        pivot_reset[col] = pivot_reset[col].round(2)
else:
    for col in pivot_reset.columns[1:]:
        pivot_reset[col] = pivot_reset[col].round(0)

st.dataframe(pivot_reset, use_container_width=True, height=800)

# --------------------------------------------------------------------
# 14. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"previsions_{mode_affichage.lower().replace(' ', '_')}_{unite.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
