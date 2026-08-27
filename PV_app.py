import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
from io import BytesIO

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
    h1 { font-size: 2.5rem !important; margin-top: 0px !important; margin-bottom: 0px !important; padding-top: 0px !important; color: #000000; }
    .stDataFrame { width: 100%; border: 1px solid #CCCCCC; }
    div[data-testid="stDataFrame"] { height: 800px !important; }
    .stButton > button, .stDownloadButton > button { background-color: #4CAF50; color: white; border: none; }
    .stButton > button:hover, .stDownloadButton > button:hover { background-color: #45a049; }
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
# 2. TABLE DE CORRESPONDANCE RÉFÉRENCE -> ARTICLE (complète)
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
# 4. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.title("📊 Coefficients de Saisonnalité par Article et Agence")

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois, segment, marque_1, format, Nom agence, contenances, Référence, ventes hecto.")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

try:
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))
except Exception as e:
    st.error(f"Erreur lors du traitement du fichier : {e}")
    st.stop()

# Vérifier les colonnes
required_cols = ['Année', 'Mois', 'segment', 'marque_1', 'format', 'Nom agence', 'contenances', 'Référence', 'ventes hecto']
if not all(col in df_raw.columns for col in required_cols):
    st.error(f"Colonnes manquantes. Requises : {required_cols}")
    st.stop()

# Nettoyage
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
df['mois_num'] = df['Mois'].apply(parse_mois)
df = df[df['mois_num'].notna()]
df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(int).astype(str) + '-01')
df['contenance_cl'] = df['contenances'].apply(extraire_contenance_cl)
df.rename(columns={'Nom agence': 'agence', 'marque_1': 'marque'}, inplace=True)

# Filtrer pour ne garder que les articles actifs
df = df[df['Référence'].isin(df_active['article_actif'])]

# --------------------------------------------------------------------
# 5. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité", ["Hectolitres", "Bouteilles"])

if unite == "Hectolitres":
    df['valeur'] = df['ventes hecto']
else:
    df['valeur'] = df['ventes hecto'] * 10000 / df['contenance_cl']

# --------------------------------------------------------------------
# 6. CALCUL DES COEFFICIENTS SAISONNIERS (MOYENNE.SI.ENS sur 2024-2025)
# --------------------------------------------------------------------
def calculer_coefficients_saisonniers(df, date_debut='2024-01-01', date_fin='2025-12-31'):
    """
    Calcule les coefficients de saisonnalité comme la formule Excel :
    MOYENNE.SI.ENS sur la période 01/01/2024 au 01/12/2025,
    puis coefficient = moyenne du mois / moyenne globale sur la période.
    """
    # Filtrer sur la période 2024-2025
    df_periode = df[(df['date'] >= date_debut) & (df['date'] <= date_fin)].copy()
    
    if df_periode.empty:
        return pd.DataFrame()
    
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    coefficients = []
    
    # Moyenne globale sur la période pour chaque combinaison
    moyennes_globales = df_periode.groupby(group_cols)['valeur'].mean().to_dict()
    
    # Moyenne par mois pour chaque combinaison
    moyennes_par_mois = df_periode.groupby(group_cols + [df_periode['date'].dt.month])['valeur'].mean()
    
    for keys, moyenne_mensuelle in moyennes_par_mois.items():
        *group_keys, mois = keys
        moyenne_globale = moyennes_globales.get(tuple(group_keys), 0)
        
        if moyenne_globale > 0:
            coefficient = moyenne_mensuelle / moyenne_globale
        else:
            coefficient = 0
        
        coefficients.append({
            'segment': group_keys[0],
            'marque': group_keys[1],
            'format': group_keys[2],
            'contenances': group_keys[3],
            'Référence': group_keys[4],
            'agence': group_keys[5],
            'mois': mois,
            'coefficient': round(coefficient, 4)
        })
    
    return pd.DataFrame(coefficients)

df_coefficients = calculer_coefficients_saisonniers(df)

if df_coefficients.empty:
    st.warning("Aucune donnée sur la période 2024-2025 pour calculer les coefficients.")
    st.stop()

# --------------------------------------------------------------------
# 7. TABLEAU PIVOT
# --------------------------------------------------------------------
st.subheader("Coefficients de saisonnalité mensuels (période 2024-2025)")

pivot = df_coefficients.pivot_table(
    index=['segment', 'marque', 'format', 'contenances', 'Référence', 'agence'],
    columns='mois',
    values='coefficient',
    aggfunc='first'
)

mois_cols = list(range(1, 13))
pivot = pivot.reindex(columns=mois_cols)

noms_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
pivot.columns = noms_mois

st.dataframe(pivot, use_container_width=True, height=800)

# --------------------------------------------------------------------
# 8. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot.reset_index().to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les coefficients (CSV)",
    data=csv,
    file_name="coefficients_saisonnalite_2024_2025.csv",
    mime="text/csv"
)
