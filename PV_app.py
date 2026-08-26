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

# Convertir en DataFrame
df_active = pd.DataFrame(ACTIVE_ARTICLES, columns=["segment_actif", "marque_actif", "article_actif"])

# --------------------------------------------------------------------
# 2. FONCTIONS UTILITAIRES
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

def nettoyer_reference(ref):
    if isinstance(ref, str):
        return re.sub(r'^\d+\s*-\s*', '', ref)
    return ref

def extraire_contenance_cl(contenances):
    m = re.search(r'(\d+)\s*cl', str(contenances))
    if m:
        return int(m.group(1))
    return None

# --------------------------------------------------------------------
# 3. FONCTION DE CHARGEMENT ET NETTOYAGE (avec cache)
# --------------------------------------------------------------------
@st.cache_data
def traiter_fichier(file_bytes, filename):
    """Lit le fichier, nettoie et filtre les données, retourne un DataFrame prêt."""
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))

    # Vérifier colonnes requises
    required_cols = ['Année', 'Mois', 'segment', 'marque_1', 'format', 'Nom agence', 'contenances', 'Référence', 'ventes hecto']
    if not all(col in df_raw.columns for col in required_cols):
        raise ValueError(f"Colonnes manquantes. Requises : {required_cols}")

    # Filtrer les lignes de détail : Référence non vide et ne contenant pas "Total"
    df = df_raw[df_raw['Référence'].notna() & ~df_raw['Référence'].astype(str).str.contains('Total', na=False)].copy()

    # Nettoyer la colonne Référence (supprimer préfixe)
    df['Référence'] = df['Référence'].apply(nettoyer_reference)

    # Filtrer pour ne garder que les articles actifs
    df = df[df['Référence'].isin(df_active['article_actif'])]

    # Convertir la colonne Année en numérique
    df['Année'] = pd.to_numeric(df['Année'].astype(str).str.replace(' ', ''), errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)

    # Convertir la colonne "ventes hecto" en numérique
    df['ventes_hecto'] = df['ventes hecto'].apply(nettoyer_nombre)

    # Créer la date
    df['mois_num'] = df['Mois'].apply(parse_mois)
    df = df[df['mois_num'].notna()]
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(int).astype(str) + '-01')

    # Extraire la contenance en cl
    df['contenance_cl'] = df['contenances'].apply(extraire_contenance_cl)

    # Renommer les colonnes
    df.rename(columns={'Nom agence': 'agence', 'marque_1': 'marque'}, inplace=True)

    return df

# --------------------------------------------------------------------
# 4. FONCTION DE CALCUL DES PRÉVISIONS (avec cache)
# --------------------------------------------------------------------
@st.cache_data
def calculer_previsions(df_hist, annees_prev):
    """Calcule les prévisions pour les années données à partir de l'historique."""
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    previsions = []

    for keys, group in df_hist.groupby(group_cols):
        serie = group.sort_values('date').set_index('date')['valeur']
        if len(serie) < 12:
            continue

        dernier_mois = serie.index.max()
        date_debut = dernier_mois - pd.DateOffset(years=3)
        serie_recente = serie[serie.index >= date_debut]
        if len(serie_recente) == 0:
            continue

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
# 5. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.title("📈 Analyse et Prévision des ventes")

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois, segment, marque_1, format, Nom agence, contenances, Référence, ventes hecto.")
    st.stop()

# Lire les bytes du fichier uploadé
file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

try:
    df = traiter_fichier(file_bytes, filename)
except Exception as e:
    st.error(f"Erreur lors du traitement du fichier : {e}")
    st.stop()

# --------------------------------------------------------------------
# 6. CHOIX DE L'UNITÉ
# --------------------------------------------------------------------
unite = st.sidebar.radio("Unité d'affichage", ["Hectolitres (ventes hecto)", "Bouteilles (ventes cols)"])

if unite == "Hectolitres (ventes hecto)":
    df['valeur'] = df['ventes_hecto']
else:
    df['valeur'] = df['ventes_hecto'] * 10000 / df['contenance_cl']
    df['valeur'] = df['valeur'].round(0)

# --------------------------------------------------------------------
# 7. GÉNÉRATION DES PRÉVISIONS (2027-2031)
# --------------------------------------------------------------------
df_hist = df[df['date'].dt.year <= 2026].copy()
annees_prev = [2027, 2028, 2029, 2030, 2031]

df_prev = calculer_previsions(df_hist, annees_prev)

# --------------------------------------------------------------------
# 8. FILTRES (prévisions uniquement)
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
# 9. TABLEAU CROISÉ DYNAMIQUE
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
# 10. AFFICHAGE DU TABLEAU
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
# 11. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"previsions_{mode_affichage.lower().replace(' ', '_')}_{unite.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
