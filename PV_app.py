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
    # ... (toute la liste des articles actifs, identique à avant)
    ("ALCOMIX", "Booster", "Booster Appel-Mix 50CL VER"),
    ("ALCOMIX", "Booster", "Booster Tornado 50CL VER VER"),
    # ... (ajoutez tous les autres articles comme précédemment)
]

df_active = pd.DataFrame(ACTIVE_ARTICLES, columns=["segment_actif", "marque_actif", "article_actif"])

# --------------------------------------------------------------------
# 2. TABLE DE CORRESPONDANCE RÉFÉRENCE -> ARTICLE
# --------------------------------------------------------------------
REFERENCE_TO_ARTICLE = {
    # ... (dictionnaire complet fourni précédemment)
    "105-THB Pilsener 33 cl CAN": "THB Pilsener 33 cl CAN",
    # ... etc.
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
    # ... (identique à avant, sans changement)
    pass

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
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    previsions = []

    # Pré-calcul de la saisonnalité par segment
    saisonnalite_segment = {}
    for segment in df_hist['segment'].unique():
        saisonnalite_segment[segment] = obtenir_saisonnalite_segment(df_hist, segment)

    for keys, group in df_hist.groupby(group_cols):
        segment, marque, format, contenances, reference, agence = keys

        serie = group.set_index('date')['valeur'].sort_index()

        # Saisonnalité spécifique
        saisonnalite = calculer_saisonnalite(serie)
        if saisonnalite is None:
            saisonnalite = saisonnalite_segment.get(segment)
        if saisonnalite is None:
            saisonnalite = {i: 1.0 for i in range(1, 13)}

        # Agrégation annuelle
        annuel = serie.resample('YE').sum()   # Changement ici : 'YE' au lieu de 'Y'
        if len(annuel) >= 2:
            valeur_initiale = annuel.iloc[0]
            valeur_finale = annuel.iloc[-1]
            nb_annees = len(annuel) - 1
            if valeur_initiale > 0 and valeur_finale > 0:
                cagr = (valeur_finale / valeur_initiale) ** (1 / nb_annees) - 1
            else:
                cagr = 0
            somme_derniere_annee = annuel.iloc[-1]
        else:
            cagr = 0
            somme_derniere_annee = annuel.iloc[0] if len(annuel) == 1 else serie.sum()

        for i, annee in enumerate(annees_prev):
            nb_annees_projection = i + 1
            somme_annuelle_prevue = somme_derniere_annee * (1 + cagr) ** nb_annees_projection
            for mois in range(1, 13):
                date_prev = pd.Timestamp(year=annee, month=mois, day=1)
                coeff = saisonnalite.get(mois, 1.0)
                valeur_mensuelle = (somme_annuelle_prevue / 12) * coeff
                previsions.append({
                    'date': date_prev,
                    'segment': segment,
                    'marque': marque,
                    'format': format,
                    'contenances': contenances,
                    'Référence': reference,
                    'agence': agence,
                    'valeur': valeur_mensuelle
                })

    return pd.DataFrame(previsions)

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
    df['valeur'] = df['ventes_hecto']
else:
    df['valeur'] = df['ventes_hecto'] * 10000 / df['contenance_cl']
    df['valeur'] = df['valeur'].round(0)

# --------------------------------------------------------------------
# 10. GÉNÉRATION DES PRÉVISIONS (2027-2031)
# --------------------------------------------------------------------
df_hist = df[df['date'].dt.year <= 2026].copy()
annees_prev = [2027, 2028, 2029, 2030, 2031]

df_prev = calculer_previsions_saisonnalite(df_hist, annees_prev)

# --------------------------------------------------------------------
# 11. DERNIER RECOURS : MOYENNE GLOBALE SI TOUJOURS MANQUANT
# --------------------------------------------------------------------
moyenne_globale = df_hist['valeur'].mean() if not df_hist.empty else 0
articles_prev = set(df_prev['Référence'].unique())
articles_manquants = set(df_active['article_actif']) - articles_prev
if articles_manquants:
    nouvelles_lignes = []
    for article in articles_manquants:
        info = df_active[df_active['article_actif'] == article].iloc[0]
        seg = info['segment_actif']
        marque = info['marque_actif']
        format_art = extraire_format(article)
        contenance = extraire_contenance_cl(article)
        # Utiliser la saisonnalité du segment (ou uniforme)
        saisonnalite_seg = obtenir_saisonnalite_segment(df_hist, seg)
        if saisonnalite_seg is None:
            saisonnalite_seg = {i: 1.0 for i in range(1, 13)}
        for agence in AGENCES:
            for annee in annees_prev:
                somme_annuelle = moyenne_globale * 12  # approximation
                for mois in range(1, 13):
                    coeff = saisonnalite_seg.get(mois, 1.0)
                    valeur = (somme_annuelle / 12) * coeff
                    nouvelles_lignes.append({
                        'date': pd.Timestamp(year=annee, month=mois, day=1),
                        'segment': seg,
                        'marque': marque,
                        'format': format_art,
                        'contenances': '',
                        'Référence': article,
                        'agence': agence,
                        'valeur': valeur
                    })
    if nouvelles_lignes:
        df_prev = pd.concat([df_prev, pd.DataFrame(nouvelles_lignes)], ignore_index=True)

# --------------------------------------------------------------------
# 12. FILTRES
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
# 13. TABLEAU CROISÉ DYNAMIQUE
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
# 14. AFFICHAGE DU TABLEAU
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
# 15. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot_reset.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger le tableau (CSV)",
    data=csv,
    file_name=f"previsions_{mode_affichage.lower().replace(' ', '_')}_{unite.lower().replace(' ', '_')}.csv",
    mime="text/csv"
)
