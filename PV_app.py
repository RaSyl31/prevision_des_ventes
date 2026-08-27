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
    
    /* Titres sur fond rouge */
    .titre-rouge {
        background-color: #CC0000;
        color: white !important;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: block;
        margin: 10px 0;
    }
    
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
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
    
    .ia-box h4 {
        color: #E65100;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTE DES AGENCES FINALES
# --------------------------------------------------------------------
AGENCES = [
    "01-Tanjombato",
    "03-Diego",
    "04-Tulear",
    "05-Fianarantsoa",
    "06-Ihosy",
    "07-Majunga",
    "08-Manakara",
    "09-Tamatave",
    "11-Andranomahery",
    "12-Antsirabe",
    "17-Antsohihy",
    "18-Ambanja",
    "19-Sambava",
    "21-NosyBe",
    "23-Morondava",
    "24-Fort Dauphin"
]

MAPPING_AGENCES = {
    "13-Diego": "03-Diego",
    "13-Usine-Diego": "03-Diego",
    "03-Usine-Diego": "03-Diego",
    "03-Diego": "03-Diego"
}

# --------------------------------------------------------------------
# 2. TABLE DE CORRESPONDANCE RÉFÉRENCE -> ARTICLE
# --------------------------------------------------------------------
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
# 3. FONCTIONS UTILITAIRES
# --------------------------------------------------------------------
MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

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
# 5. CHARGEMENT ET TRAITEMENT OPTIMISÉ
# --------------------------------------------------------------------
@st.cache_data
def charger_et_calculer(file_bytes, filename):
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))
    
    df = df_raw[
        df_raw['Référence'].notna() &
        ~df_raw['Référence'].astype(str).str.contains('Total', na=False) &
        df_raw['Mois'].notna() &
        ~df_raw['Mois'].astype(str).str.contains('Total', na=False)
    ].copy()
    
    df['Référence'] = df['Référence'].map(REFERENCE_TO_ARTICLE).fillna(df['Référence'])
    df['Année'] = pd.to_numeric(df['Année'].astype(str).str.replace(' ', ''), errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)
    df['ventes hecto'] = df['ventes hecto'].apply(nettoyer_nombre)
    df['mois_num'] = df['Mois'].map(MOIS_FR)
    df = df.dropna(subset=['mois_num'])
    df['mois_num'] = df['mois_num'].astype(int)
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(str) + '-01')
    df.rename(columns={'Nom agence': 'agence', 'marque_1': 'marque'}, inplace=True)
    df['agence'] = df['agence'].replace(MAPPING_AGENCES)
    df = df[df['agence'].isin(AGENCES)]
    
    df_periode = df[(df['date'].dt.year >= 2024) & (df['date'].dt.year <= 2025)]
    
    if df_periode.empty:
        return pd.DataFrame()
    
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    moyenne_generale = df_periode.groupby(group_cols)['ventes hecto'].mean()
    moyenne_par_mois = df_periode.groupby(group_cols + [df_periode['date'].dt.month])['ventes hecto'].mean()
    
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
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois, segment, marque_1, format, Nom agence, contenances, Référence, ventes hecto.")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

df_coefficients = charger_et_calculer(file_bytes, filename)

if df_coefficients.empty:
    st.warning("Aucune donnée sur la période 2024-2025 pour calculer les coefficients.")
    st.stop()

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

moyennes_par_mois = df_filtre.groupby('mois')['coefficient'].mean().reindex(mois_cols)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=noms_mois,
    y=moyennes_par_mois,
    mode='lines+markers',
    name='Coefficient moyen',
    line=dict(color='blue', width=2),
    marker=dict(size=8)
))

fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Moyenne = 1.0")

fig.update_layout(
    title="Coefficients de saisonnalité moyens par mois",
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
    file_name="coefficients_saisonnalite_2024_2025.csv",
    mime="text/csv"
)
