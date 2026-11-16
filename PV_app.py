import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import unicodedata
import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from openpyxl.styles import Font, PatternFill, Alignment

# ==============================================================================
# CONFIGURATION ET DESIGN
# ==============================================================================
st.set_page_config(page_title="PREVISIONS STAR MADAGASCAR", layout="wide", page_icon="⭐", initial_sidebar_state="expanded")

COLORS = {
    "ROUGE": "#E30613", "ROUGE_FONCE": "#B3050F", "ROUGE_CLAIR": "#FDECEE",
    "BLANC": "#FFFFFF", "TEXTE": "#111827", "TEXTE_SECONDAIRE": "#6B7280",
    "BORDURE": "#E5E7EB", "GRIS": "#9CA3AF", "VERT": "#059669",
    "VERT_CLAIR": "#D1FAE5", "ORANGE": "#D97706"
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: #FAFAFA !important; }}
    [data-testid="stSidebar"] {{ background-color: {COLORS['BLANC']} !important; border-right: 1px solid {COLORS['BORDURE']}; }}
    [data-testid="stSidebar"] h2 {{ color: {COLORS['TEXTE']} !important; font-size: 1.1rem; font-weight: 700; }}
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stNumberInput label, [data-testid="stSidebar"] .stMultiSelect label {{ color: {COLORS['TEXTE_SECONDAIRE']} !important; font-size: 0.85rem !important; font-weight: 600 !important; }}
    .hero-header {{ background: {COLORS['ROUGE']}; color: white; padding: 20px 30px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
    .hero-header h1 {{ color: white !important; font-size: 1.6rem; font-weight: 700; margin: 0; }}
    .hero-header p {{ color: rgba(255,255,255,0.9); font-size: 0.9rem; margin: 5px 0 0 0; }}
    .badge-demo {{ background-color: white; color: {COLORS['ROUGE']}; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; box-shadow: 0 2px 4px rgba(0,0,0,0.1); white-space: nowrap; }}
    div[data-testid="stExpander"] {{ background-color: {COLORS['BLANC']} !important; border-radius: 10px !important; border: 1px solid {COLORS['BORDURE']} !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important; margin-bottom: 20px !important; }}
    div[data-testid="stExpander"] > details > summary {{ background-color: {COLORS['BLANC']} !important; border-radius: 10px !important; padding: 15px 20px !important; font-weight: 600 !important; font-size: 1rem !important; color: {COLORS['TEXTE']} !important; }}
    .kpi-card {{ background: {COLORS['BLANC']}; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid {COLORS['BORDURE']}; border-left: 4px solid {COLORS['ROUGE']}; height: 100%; }}
    .kpi-label {{ color: {COLORS['TEXTE_SECONDAIRE']}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }}
    .kpi-value {{ color: {COLORS['TEXTE']}; font-size: 2rem; font-weight: 700; line-height: 1.1; }}
    .kpi-delta {{ font-size: 0.85rem; font-weight: 600; margin-top: 5px; }}
    .progress-container {{ width: 100%; background-color: {COLORS['BORDURE']}; border-radius: 4px; height: 8px; margin-top: 10px; }}
    .progress-bar {{ height: 8px; border-radius: 4px; background-color: {COLORS['ROUGE']}; }}
    div[role="radiogroup"] {{ gap: 20px !important; border-bottom: 2px solid {COLORS['BORDURE']} !important; padding-bottom: 0px !important; margin-bottom: 30px !important; display: flex !important; flex-wrap: nowrap !important; overflow-x: auto !important; align-items: flex-end !important; white-space: nowrap !important; }}
    div[role="radiogroup"]::-webkit-scrollbar {{ display: none; }}
    div[role="radiogroup"] label {{ background: transparent !important; border: none !important; border-bottom: 4px solid transparent !important; border-radius: 0 !important; padding: 10px 4px 16px 4px !important; margin: 0 !important; cursor: pointer !important; }}
    div[role="radiogroup"] label div p {{ font-size: 1.2rem !important; font-weight: 600 !important; color: {COLORS['TEXTE_SECONDAIRE']} !important; margin: 0 !important; }}
    div[role="radiogroup"] label:has(input:checked) {{ border-bottom: 4px solid {COLORS['ROUGE']} !important; }}
    div[role="radiogroup"] label:has(input:checked) div p {{ color: {COLORS['ROUGE']} !important; font-weight: 800 !important; }}
    div[role="radiogroup"] label > div:first-child {{ display: none !important; }}
    .block-container {{ padding-top: 1rem !important; }}

    div[data-testid="stDataFrame"] {{ border-radius: 10px; border: 1px solid {COLORS['BORDURE']}; box-shadow: 0 2px 4px rgba(0,0,0,0.02); background-color: {COLORS['BLANC']}; }}
    div[data-testid="stDataFrame"] > div {{ border-radius: 10px; }}
    div[data-testid="stDataFrame"] th {{ background-color: #F9FAFB !important; color: {COLORS['TEXTE_SECONDAIRE']} !important; font-weight: 700 !important; text-transform: uppercase; font-size: 0.75rem !important; border-bottom: 2px solid {COLORS['BORDURE']} !important; }}
    div[data-testid="stDataFrame"] td {{ font-size: 0.85rem !important; color: {COLORS['TEXTE']} !important; }}

    .white-card {{ background: {COLORS['BLANC']}; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid {COLORS['BORDURE']}; height: 100%; }}
    .kpi-value-dark {{ color: {COLORS['TEXTE']}; font-size: 2rem; font-weight: 700; line-height: 1.1; }}
    .kpi-footer {{ color: {COLORS['TEXTE_SECONDAIRE']}; font-size: 0.75rem; margin-top: 8px; }}
    .kpi-delta.up {{ color: {COLORS['VERT']}; }}
    .kpi-delta.down {{ color: {COLORS['ROUGE']}; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================
def format_fr(val, decimals=0, signed=False):
    if pd.isna(val): return "0"
    sign = "+" if signed and val > 0 else ""
    if decimals == 0:
        return sign + f"{val:,.0f}".replace(",", " ")
    else:
        return sign + f"{val:,.{decimals}f}".replace(",", " ").replace(".", ",")

def ajouter_total(df, label_col, label="TOTAL", exclude_cols=None, custom_total_calc=None):
    if df is None or df.empty: return df
    exclude = exclude_cols or []
    row = {c: np.nan for c in df.columns}
    if label_col in df.columns: row[label_col] = label
    
    for c in df.columns:
        if c == label_col or c in exclude: continue
        try:
            if pd.api.types.is_numeric_dtype(df[c]):
                row[c] = df[c].fillna(0).sum()
        except Exception: pass
    
    if custom_total_calc:
        for col, func in custom_total_calc.items():
            if col in row:
                row[col] = func(row)
                
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            if pd.isna(row[c]):
                row[c] = ""
                
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)

def small_kpi(label, value, color=COLORS['ROUGE']):
    st.markdown(f"""
    <div style="display: inline-block; background-color: {COLORS['BLANC']}; padding: 12px 20px; border-radius: 10px; border: 1px solid {COLORS['BORDURE']}; border-left: 4px solid {color}; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; margin-right: 10px;">
        <div style="color: {COLORS['TEXTE_SECONDAIRE']}; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">{label}</div>
        <div style="color: {COLORS['TEXTE']}; font-size: 1.5rem; font-weight: 800;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def bold_total_row(df):
    return df.style.apply(lambda x: ['font-weight: bold; background-color: #F9FAFB;'] * len(x) if x.name == len(df)-1 else [''] * len(x), axis=1)

def color_error(val, seuil_alerte=10, seuil_bon=5):
    try:
        val = float(val)
        if val > seuil_alerte: return f'background-color: {COLORS["ROUGE_CLAIR"]}; color: {COLORS["ROUGE_FONCE"]}; font-weight: bold;'
        if val < seuil_bon: return f'background-color: #D1FAE5; color: {COLORS["VERT"]}; font-weight: bold;'
        return f'background-color: #FEF3C7; color: #92400E; font-weight: bold;'
    except: return ''

def get_region_vectorized(series):
    a = series.astype(str).str.lower().str.replace("-", "").str.replace(" ", "").str.replace("_", "")
    result = np.select(
        [a.str.contains('andranomahery|antsirabe'), a.str.contains('tanjombato|tamatave'), a.str.contains('diego|majunga|ambanja|sambava|nosybe'), a.str.contains('tulear|fianarantsoa|ihosy|manakara|morondava|dauphin')],
        ['Centre', 'Est', 'Nord', 'Sud'], default='Autre'
    )
    return pd.Series(result, index=series.index)

def extraire_marque(article):
    if pd.isna(article): return "Inconnu"
    a = str(article).strip().lower()
    if "world cola" in a: return "World Cola"
    if "eau vive" in a: return "Eau Vive"
    return str(article).split()[0]

def extraire_emballage(article):
    if pd.isna(article): return "Inconnu"
    a = str(article).upper()
    if "PET" in a: return "PET"
    if "CAN" in a: return "CAN"
    if "VER" in a: return "VER"
    if "BOB" in a: return "BOB"
    return "AUTRE"

def clean_text_for_key(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]', '', text)

def clean_text_for_budget_key(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = text.replace('33 cl', '33').replace('33cl', '33')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-z0-9]', '', text)

REF_DEFAUT = [
    {"Article": "Booster Appel-Mix 50CL VER", "Contenance (Cl)": 50, "Positionnement": "Entrée"}, {"Article": "Booster Tornado 50CL VER VER", "Contenance (Cl)": 50, "Positionnement": "Entrée"},
    {"Article": "Caprice Ananas 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"}, {"Article": "Caprice Ananas 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"},
    {"Article": "Caprice Ananas 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"}, {"Article": "Caprice Bonbon Anglais 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"},
    {"Article": "Caprice Bonbon Anglais 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"}, {"Article": "Caprice Bonbon Anglais 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"},
    {"Article": "Caprice Bonbon Anglais 35 cl PET", "Contenance (Cl)": 35, "Positionnement": "Milieu"}, {"Article": "Caprice Bonbon Anglais 50 cl PET", "Contenance (Cl)": 50, "Positionnement": "Milieu"},
    {"Article": "Caprice Grenadine 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"}, {"Article": "Caprice Grenadine 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"},
    {"Article": "Caprice Grenadine 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"}, {"Article": "Caprice Grenadine 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Milieu"},
    {"Article": "Caprice Grenadine 35 cl PET", "Contenance (Cl)": 35, "Positionnement": "Milieu"}, {"Article": "Caprice Grenadine 50 cl PET", "Contenance (Cl)": 50, "Positionnement": "Milieu"},
    {"Article": "Caprice Orange 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"}, {"Article": "Caprice Orange 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"},
    {"Article": "Caprice Orange 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"}, {"Article": "Caprice Orange 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Milieu"},
    {"Article": "Caprice Orange 35 cl PET", "Contenance (Cl)": 35, "Positionnement": "Milieu"}, {"Article": "Caprice Orange 50 cl PET", "Contenance (Cl)": 50, "Positionnement": "Milieu"},
    {"Article": "Caprice Bonbon Anglais 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Milieu"}, {"Article": "Caprice Citron 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"},
    {"Article": "Caprice Citron 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"}, {"Article": "Caprice Citron 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"},
    {"Article": "Caprice Citron 50 cl PET", "Contenance (Cl)": 50, "Positionnement": "Milieu"}, {"Article": "Tonic 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"},
    {"Article": "Tonic 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"}, {"Article": "World Cola 100cl VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"},
    {"Article": "World Cola 100cl WOCO VER", "Contenance (Cl)": 100, "Positionnement": "Milieu"}, {"Article": "World Cola 150cl PET", "Contenance (Cl)": 150, "Positionnement": "Milieu"},
    {"Article": "World Cola 30cl VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"}, {"Article": "World Cola 30cl WOCO VER", "Contenance (Cl)": 30, "Positionnement": "Milieu"},
    {"Article": "World Cola 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Milieu"}, {"Article": "World Cola 35cl PET", "Contenance (Cl)": 35, "Positionnement": "Milieu"},
    {"Article": "World Cola 50cl PET", "Contenance (Cl)": 50, "Positionnement": "Milieu"}, {"Article": "Beaufort 33 CL CAN", "Contenance (Cl)": 33, "Positionnement": "Premium"},
    {"Article": "Beaufort 33CL VER", "Contenance (Cl)": 33, "Positionnement": "Premium"}, {"Article": "FRESH 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Entrée"},
    {"Article": "THB Fresh 33 cl VER", "Contenance (Cl)": 33, "Positionnement": "Entrée"}, {"Article": "THB Fresh 65 cl VER", "Contenance (Cl)": 65, "Positionnement": "Entrée"},
    {"Article": "Gold 8 50 cl CAN", "Contenance (Cl)": 50, "Positionnement": "Premium"}, {"Article": "Gold 8 50 cl VER", "Contenance (Cl)": 50, "Positionnement": "Premium"},
    {"Article": "Gold Blanche 33cl VER", "Contenance (Cl)": 33, "Positionnement": "Premium"}, {"Article": "Gold Blanche 50 cl CAN", "Contenance (Cl)": 50, "Positionnement": "Premium"},
    {"Article": "Gold Blanche 50 cl VER", "Contenance (Cl)": 50, "Positionnement": "Premium"}, {"Article": "Gold Blonde 33 cl VER", "Contenance (Cl)": 33, "Positionnement": "Premium"},
    {"Article": "Gold Blonde 50 cl CAN", "Contenance (Cl)": 50, "Positionnement": "Premium"}, {"Article": "Gold Blonde 50 cl VER", "Contenance (Cl)": 50, "Positionnement": "Premium"},
    {"Article": "Gold Blonde 65 cl VER", "Contenance (Cl)": 65, "Positionnement": "Premium"}, {"Article": "Queen s 65 cl VER", "Contenance (Cl)": 65, "Positionnement": "Premium"},
    {"Article": "THB Pilsener 33 cl VER", "Contenance (Cl)": 33, "Positionnement": "Milieu"}, {"Article": "THB Pilsener 50 cl CAN", "Contenance (Cl)": 50, "Positionnement": "Milieu"},
    {"Article": "THB Pilsener 65 cl VER", "Contenance (Cl)": 65, "Positionnement": "Milieu"}, {"Article": "Cristal 100 cl VER", "Contenance (Cl)": 100, "Positionnement": "Entrée"},
    {"Article": "Cristal 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Entrée"}, {"Article": "Cristal 30 cl VER", "Contenance (Cl)": 30, "Positionnement": "Entrée"},
    {"Article": "Cristal 50 cl VER", "Contenance (Cl)": 50, "Positionnement": "Entrée"}, {"Article": "Cristalline 100 cl PET", "Contenance (Cl)": 100, "Positionnement": "Entrée"},
    {"Article": "Cristalline 200 cl PET", "Contenance (Cl)": 200, "Positionnement": "Entrée"}, {"Article": "Eau vive 150 cl PET", "Contenance (Cl)": 150, "Positionnement": "Entrée"},
    {"Article": "Eau vive 50 cl PET", "Contenance (Cl)": 50, "Positionnement": "Entrée"}, {"Article": "Eau vive 50 cl VER", "Contenance (Cl)": 50, "Positionnement": "Entrée"},
    {"Article": "FOSA 50 cl CAN", "Contenance (Cl)": 50, "Positionnement": "Entrée"}, {"Article": "XXL 30cl BOB VER", "Contenance (Cl)": 30, "Positionnement": "Entrée"},
    {"Article": "XXL 30cl VER", "Contenance (Cl)": 30, "Positionnement": "Entrée"}, {"Article": "XXL 33 cl CAN", "Contenance (Cl)": 33, "Positionnement": "Entrée"},
    {"Article": "XXL 35cl PET", "Contenance (Cl)": 35, "Positionnement": "Entrée"}
]

MOIS_NOMS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]

def normaliser_mois(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie): return serie.fillna(1).astype(int)
    series_clean = serie.astype(str).str.strip()
    numeric_series = pd.to_numeric(series_clean, errors='coerce')
    if numeric_series.notna().all():
        if numeric_series.between(1, 12).all(): return numeric_series.astype(int)
        dates = pd.to_datetime(numeric_series, unit='D', origin='1899-12-30', errors='coerce')
        if dates.notna().all(): return dates.dt.month
    mois_map = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
    texte_series = series_clean.apply(lambda x: unicodedata.normalize("NFD", str(x)).encode("ascii", "ignore").decode("utf-8").lower())
    return texte_series.map(mois_map).fillna(1).astype(int)

# ==============================================================================
# LOGIQUE DE CALCUL
# ==============================================================================
@st.cache_data(show_spinner=False)
def charger_ruptures(rupture_bytes):
    if rupture_bytes is None: return pd.DataFrame()
    try:
        xls = pd.ExcelFile(io.BytesIO(rupture_bytes))
        sheet_rupture = next((name for name in xls.sheet_names if name.lower() in ["rupture", "ruptures"]), None)
        if sheet_rupture is None: return pd.DataFrame()
        df = pd.read_excel(xls, sheet_name=sheet_rupture, header=None)
        df = df.iloc[1:, [0, 1, 2, 3]].copy()
        df.columns = ['Mois_Str', 'agence', 'article', 'rupture_hl']
        df['Mois_Str'] = df['Mois_Str'].astype(str).str.strip()
        dates = pd.to_datetime(df['Mois_Str'], errors='coerce', dayfirst=True)
        df['mois'] = dates.dt.month
        df['annee'] = dates.dt.year
        mask_nan = df['mois'].isna()
        if mask_nan.any():
            df.loc[mask_nan, 'mois'] = pd.to_numeric(df.loc[mask_nan, 'Mois_Str'].str.split(' ').str[0], errors='coerce')
            df.loc[mask_nan, 'annee'] = pd.to_numeric(df.loc[mask_nan, 'Mois_Str'].str.split(' ').str[1], errors='coerce')
        df = df.dropna(subset=['mois', 'annee', 'agence', 'article'])
        df['annee'] = df['annee'].astype(int)
        df['mois'] = df['mois'].astype(int)
        df['rupture_hl'] = pd.to_numeric(df['rupture_hl'], errors='coerce').fillna(0.0)
        df['agence'] = df['agence'].astype(str).str.strip()
        df['cle_article'] = df['article'].astype(str).apply(clean_text_for_key)
        df = df.groupby(['annee', 'mois', 'agence', 'cle_article'], as_index=False)['rupture_hl'].sum()
        return df[['annee', 'mois', 'agence', 'cle_article', 'rupture_hl']]
    except Exception as e:
        st.error(f"Erreur de lecture du fichier rupture : {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner="Chargement et enrichissement des données...")
def charger_et_enrichir(ventes_bytes: bytes, ref_bytes: bytes, rupture_bytes: bytes) -> pd.DataFrame:
    if ref_bytes is not None:
        xls_ref = pd.ExcelFile(io.BytesIO(ref_bytes))
        sheet_ref = next((name for name in xls_ref.sheet_names if name.lower() in ["ref actif", "classeur.2", "classeur2", "referentiel", "référentiel"]), None)
        if sheet_ref is None: sheet_ref = 1 if len(xls_ref.sheet_names) > 1 else 0
        df_ref = pd.read_excel(xls_ref, sheet_name=sheet_ref)
        df_ref = df_ref.rename(columns={"Article": "article_original", "Positionnement": "positionnement", "Occasion": "occasion", "Contenance (Cl)": "contenance_cl"}, errors="ignore")
        for col in ["positionnement", "occasion", "contenance_cl"]:
            if col not in df_ref.columns: df_ref[col] = "Non renseigné" if col != "contenance_cl" else 100.0
        df_ref = df_ref[["article_original", "positionnement", "occasion", "contenance_cl"]].copy()
    else:
        df_ref = pd.DataFrame(REF_DEFAUT).rename(columns={"Article": "article_original", "Contenance (Cl)": "contenance_cl", "Positionnement": "positionnement"})
        df_ref["occasion"] = "Non renseigné"

    df_ref["article_original"] = df_ref["article_original"].astype(str).str.strip()
    df_ref["marque"] = df_ref["article_original"].apply(extraire_marque)
    df_ref["emballage"] = df_ref["article_original"].apply(extraire_emballage)
    df_ref["cle_article"] = df_ref["article_original"].apply(clean_text_for_key)
    df_ref = df_ref.drop_duplicates(subset=["cle_article"]).reset_index(drop=True)

    df_raw = pd.read_excel(io.BytesIO(ventes_bytes), sheet_name=0, header=None)
    annee0 = pd.to_numeric(df_raw.iloc[:, 0], errors="coerce")
    if annee0.between(1990, 2100).sum() < len(df_raw) * 0.3 and df_raw.shape[1] >= 8:
        rename = {df_raw.columns[i]: col for i, col in enumerate(["annee", "mois", "segment", "produit", "agence", "nature", "volume_brut"], start=1)}
    else:
        rename = {df_raw.columns[i]: col for i, col in enumerate(["annee", "mois", "segment", "produit", "agence", "nature", "volume_brut"])}

    df = df_raw.rename(columns=rename).copy()
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    df["mois"] = normaliser_mois(df["mois"])
    df["volume_brut"] = pd.to_numeric(df["volume_brut"], errors="coerce").fillna(0.0)

    masque_total = df[['segment', 'produit', 'agence', 'nature']].astype(str).apply(lambda s: s.str.contains("total", case=False, na=False)).any(axis=1) | df['nature'].isna()
    df = df[~masque_total].copy()

    df["article_original"] = df["nature"].astype(str).str.replace(r'^[^-]+-', '', regex=True).str.strip()
    df["agence"] = df["agence"].astype(str).str.strip()
    df["annee"] = df["annee"].fillna(2026).astype(int)
    df["cle_article"] = df["article_original"].apply(clean_text_for_key)

    if ref_bytes is not None:
        df_enrichi = pd.merge(df_ref, df, on="cle_article", how="inner", sort=False)
    else:
        df_enrichi = pd.merge(df_ref, df, on="cle_article", how="outer", sort=False)

    df_enrichi["article"] = df_enrichi["article_original_x"].fillna(df_enrichi["article_original_y"]).fillna("Inconnu").astype(str)
    df_enrichi["annee"] = df_enrichi["annee"].fillna(2026).astype(int)
    df_enrichi["volume_brut"] = df_enrichi["volume_brut"].fillna(0.0)
    df_enrichi["agence"] = df_enrichi["agence"].fillna("Aucune vente")
    df_enrichi["marque"] = df_enrichi["marque"].fillna("Inconnu")
    df_enrichi["emballage"] = df_enrichi["emballage"].fillna("AUTRE")
    df_enrichi["contenance_cl"] = pd.to_numeric(df_enrichi["contenance_cl"], errors="coerce").fillna(100.0)
    df_enrichi.loc[df_enrichi["contenance_cl"] <= 0, "contenance_cl"] = 100.0

    masque_fut20 = df_enrichi["article"].str.contains(r'20L|20 L|FUT 20', case=False, na=False, regex=True)
    df_enrichi.loc[masque_fut20, "contenance_cl"] = 2000.0

    df_enrichi["hl"] = df_enrichi["volume_brut"].fillna(0.0)
    df_enrichi["region"] = get_region_vectorized(df_enrichi["agence"])
    df_enrichi["occasion"] = df_enrichi["occasion"].fillna("Non renseigné").astype(str)
    df_enrichi["positionnement"] = df_enrichi["positionnement"].fillna("Non renseigné").astype(str)

    conditions = [df_enrichi["article"].str.contains(x, case=False, na=False) for x in ["booster|alcoomix", "caprice|tonic|world cola|d jino|youzou|coca|fanta|sprite", "beaufort|fresh|thb|gold|queen|skol|castel|libertalia", "cristal|cristalline|eau vive|eau", "xxl|fosa", "judor|jus", "vin", "negoce"]]
    choices = ["5-ALCOMIX", "2-BG", "1-BIERES", "4-EAUX", "3-ENERGY", "4-JUS", "7-VIN", "6-NEGOCE"]
    df_enrichi["segment"] = np.select(conditions, choices, default="AUTRE / INCONNU")

    df_ruptures = charger_ruptures(rupture_bytes)
    if not df_ruptures.empty:
        df_enrichi = df_enrichi.merge(df_ruptures, on=['annee', 'mois', 'agence', 'cle_article'], how='left', sort=False)
        df_enrichi['rupture_hl'] = df_enrichi['rupture_hl'].fillna(0.0)
    else:
        df_enrichi['rupture_hl'] = 0.0

    df_enrichi["hl_potentiel"] = df_enrichi["hl"] + df_enrichi["rupture_hl"]

    for col in ['region', 'segment', 'positionnement', 'occasion', 'marque', 'emballage']:
        if col in df_enrichi.columns: df_enrichi[col] = df_enrichi[col].astype('category')

    return df_enrichi[["annee", "mois", "segment", "region", "produit", "agence", "hl", "hl_potentiel", "rupture_hl", "volume_brut", "article", "positionnement", "occasion", "marque", "contenance_cl", "emballage"]]

def _calculer_indices_fallback(df_realise, annee_min_is, annee_max_is):
    df_h_global = df_realise[(df_realise['annee'] >= annee_min_is) & (df_realise['annee'] <= annee_max_is)].copy()
    if df_h_global.empty: df_h_global = df_realise.copy()

    def _calc_idx(df_h, group_cols):
        if df_h.empty: return pd.DataFrame(columns=group_cols + ['mois', 'Indice'])
        v = (df_h.groupby(group_cols + ['annee', 'mois'], observed=True)['hl'].sum().unstack('mois').fillna(0.0).reindex(columns=range(1, 13), fill_value=0.0))
        cum_m = v.groupby(group_cols).sum()
        cum_a = v.sum(axis=1).groupby(group_cols).sum()
        moy_mensuelle = cum_a / 12.0
        indices = cum_m.div(moy_mensuelle, axis=0)
        indices = indices.replace([np.inf, -np.inf], np.nan)
        return indices.reset_index().melt(id_vars=group_cols, var_name='mois', value_name='Indice')

    idx1_glob = _calc_idx(df_h_global, ['agence', 'article'])
    idx2_glob = _calc_idx(df_h_global, ['article']).rename(columns={'Indice': 'Indice_art'})
    idx3_glob = _calc_idx(df_h_global, ['marque']).rename(columns={'Indice': 'Indice_marque'})
    idx4_glob = _calc_idx(df_h_global, ['segment']).rename(columns={'Indice': 'Indice_seg'})
    tot_glob = df_h_global.groupby('mois', observed=True)['hl'].sum().reindex(range(1, 13), fill_value=0.0)
    glob_glob = (tot_glob / (tot_glob.sum() / 12.0)).reset_index()
    glob_glob.columns = ['mois', 'Indice_glob']

    df_base_glob = df_h_global[['agence', 'article', 'marque', 'segment', 'mois']].drop_duplicates()
    result_glob = (df_base_glob.merge(idx1_glob, on=['agence', 'article', 'mois'], how='left', sort=False)
                              .merge(idx2_glob, on=['article', 'mois'], how='left', sort=False)
                              .merge(idx3_glob, on=['marque', 'mois'], how='left', sort=False)
                              .merge(idx4_glob, on=['segment', 'mois'], how='left', sort=False)
                              .merge(glob_glob, on='mois', how='left', sort=False))
    result_glob['Indice'] = result_glob['Indice'].fillna(result_glob['Indice_art']).fillna(result_glob['Indice_marque']).fillna(result_glob['Indice_seg']).fillna(result_glob['Indice_glob']).fillna(1.0)

    results = []
    global_rolling = []
    annees = df_realise['annee'].unique()
    for annee in annees:
        df_h = df_realise[(df_realise['annee'] >= annee - 2) & (df_realise['annee'] <= annee - 1)].copy()
        if df_h.empty: continue

        idx1 = _calc_idx(df_h, ['agence', 'article'])
        idx2 = _calc_idx(df_h, ['article']).rename(columns={'Indice': 'Indice_art'})
        idx3 = _calc_idx(df_h, ['marque']).rename(columns={'Indice': 'Indice_marque'})
        idx4 = _calc_idx(df_h, ['segment']).rename(columns={'Indice': 'Indice_seg'})
        tot = df_h.groupby('mois', observed=True)['hl'].sum().reindex(range(1, 13), fill_value=0.0)
        glob = (tot / (tot.sum() / 12.0)).reset_index()
        glob.columns = ['mois', 'Indice_glob']
        glob['annee'] = annee
        global_rolling.append(glob)

        df_base = df_h[['agence', 'article', 'marque', 'segment', 'mois']].drop_duplicates()
        result = (df_base.merge(idx1, on=['agence', 'article', 'mois'], how='left', sort=False)
                          .merge(idx2, on=['article', 'mois'], how='left', sort=False)
                          .merge(idx3, on=['marque', 'mois'], how='left', sort=False)
                          .merge(idx4, on=['segment', 'mois'], how='left', sort=False)
                          .merge(glob.drop(columns=['annee']), on='mois', how='left', sort=False))
        result['Indice'] = result['Indice'].fillna(result['Indice_art']).fillna(result['Indice_marque']).fillna(result['Indice_seg']).fillna(result['Indice_glob']).fillna(1.0)
        result['annee'] = annee
        results.append(result[['annee', 'agence', 'article', 'mois', 'Indice']])

    table_rolling = pd.concat(results, ignore_index=True) if results else pd.DataFrame()
    df_global_rolling = pd.concat(global_rolling, ignore_index=True) if global_rolling else pd.DataFrame()

    return table_rolling, df_global_rolling, result_glob[['agence', 'article', 'mois', 'Indice']]

@st.cache_data(show_spinner="Calcul des prévisions...")
def calculer_etape_5(df_perimetre, annee_min_is, annee_max_is, annee_min_cagr, annee_max_cagr, annee_cloture, mois_cutoff, annee_cible, methode_croissance, annee_rupture_tendance, budget_bytes, budget_all_agencies, cache_bust="v177"):
    budget_status = "skipped"

    annees_recentes = [annee_cloture, annee_cloture - 1]
    df_recent = df_perimetre[df_perimetre['annee'].isin(annees_recentes)]
    couples_actifs = df_recent[df_recent['hl'] > 0][['agence', 'article']].drop_duplicates()

    df_perimetre_filtre = pd.merge(df_perimetre, couples_actifs, on=['agence', 'article'], how='inner', sort=False)
    if df_perimetre_filtre.empty: return None, None, None, None, df_perimetre, budget_status, None

    df_limite = df_perimetre_filtre[(df_perimetre_filtre["annee"] < annee_cloture) | ((df_perimetre_filtre["annee"] == annee_cloture) & (df_perimetre_filtre["mois"] <= mois_cutoff))].copy()
    df_realise = df_limite[df_limite["annee"] <= annee_cloture].copy()
    if df_realise.empty: return None, None, None, None, df_perimetre_filtre, budget_status, None

    table_indices_rolling, df_global_rolling, table_indices_forecast = _calculer_indices_fallback(df_realise, annee_min_is, annee_max_is)

    df_realise_agg = df_realise.groupby(['annee', 'mois', 'agence', 'article'], observed=True)[['hl', 'hl_potentiel', 'rupture_hl']].sum().reset_index()
    min_annee = df_realise_agg['annee'].min()
    dates = pd.date_range(start=f'{min_annee}-01-01', end=f'{annee_cloture}-{mois_cutoff:02d}-01', freq='MS')
    df_dates = pd.DataFrame({'Date': dates})
    df_dates['annee'] = df_dates['Date'].dt.year
    df_dates['mois'] = df_dates['Date'].dt.month

    ag_art = df_realise_agg[['agence', 'article']].drop_duplicates()
    df_skeleton = pd.merge(ag_art, df_dates, how='cross')

    df_sarr_cont = pd.merge(df_skeleton, df_realise_agg, on=['annee', 'mois', 'agence', 'article'], how='left', sort=False)
    df_sarr_cont = df_sarr_cont.merge(table_indices_rolling, on=['annee', 'mois', 'agence', 'article'], how='left', sort=False)
    df_sarr_cont = df_sarr_cont.merge(table_indices_forecast, on=['mois', 'agence', 'article'], how='left', suffixes=('', '_glob'), sort=False)
    df_sarr_cont['Indice'] = df_sarr_cont['Indice'].fillna(df_sarr_cont['Indice_glob']).fillna(1.0)
    df_sarr_cont = df_sarr_cont.drop(columns=['Indice_glob'])

    df_sarr_cont['Indice'] = df_sarr_cont['Indice'].clip(lower=0.1)
    df_sarr_cont['SARR_HL'] = df_sarr_cont['hl'] / df_sarr_cont['Indice']

    df_sarr_cont = df_sarr_cont.sort_values(['agence', 'article', 'annee', 'mois']).reset_index(drop=True)
    g = df_sarr_cont.groupby(['agence', 'article'], observed=True)

    df_sarr_cont['SARR_M1'] = g['SARR_HL'].shift(1)
    df_sarr_cont['SARR_M2'] = g['SARR_HL'].shift(2)
    df_sarr_cont['SARR_M3'] = g['SARR_HL'].shift(3)

    df_sarr_cont['SARR_MA3'] = df_sarr_cont[['SARR_M1', 'SARR_M2', 'SARR_M3']].mean(axis=1)

    df_sarr_cont['Base_EXCEL'] = df_sarr_cont['SARR_HL'].fillna(0.0)
    mask_ma3 = df_sarr_cont['SARR_MA3'].notna()
    df_sarr_cont.loc[mask_ma3, 'Base_EXCEL'] = np.maximum(df_sarr_cont.loc[mask_ma3, 'SARR_HL'].fillna(0.0), df_sarr_cont.loc[mask_ma3, 'SARR_MA3'])

    df_sarr_cont['Ecart_1'] = df_sarr_cont['SARR_HL'].fillna(0.0) - df_sarr_cont['SARR_M1'].fillna(0.0)
    df_sarr_cont['Ecart_2'] = df_sarr_cont['SARR_M1'].fillna(0.0) - df_sarr_cont['SARR_M2'].fillna(0.0)
    df_sarr_cont['Ecart_3'] = df_sarr_cont['SARR_M2'].fillna(0.0) - df_sarr_cont['SARR_M3'].fillna(0.0)
    df_sarr_cont['Momentum'] = df_sarr_cont[['Ecart_1', 'Ecart_2', 'Ecart_3']].mean(axis=1).fillna(0.0)

    df_base_momentum = df_sarr_cont[(df_sarr_cont['annee'] == annee_cloture) & (df_sarr_cont['mois'] == mois_cutoff)][['agence', 'article', 'Base_EXCEL', 'Momentum']].copy()

    df_perim_unique = df_perimetre_filtre[['agence', 'article', 'contenance_cl']].drop_duplicates(subset=['agence', 'article'])
    df_realise['hl_positif'] = np.maximum(0.0, df_realise['hl'])
    df_ytd = (df_realise[(df_realise['annee'] == annee_cloture) & (df_realise['mois'] <= mois_cutoff)].groupby(['agence', 'article'], observed=True)['hl_positif'].sum().reset_index().rename(columns={'hl_positif': 'YTD_HL'}))
    df_premiere_annee = (df_realise[df_realise['hl'] > 0].groupby(['agence', 'article'], observed=True)['annee'].min().reset_index().rename(columns={'annee': 'Annee_Debut'}))

    df_ytd_pot = (df_realise[(df_realise['annee'] == annee_cloture) & (df_realise['mois'] <= mois_cutoff)]
                  .groupby(['agence', 'article'], observed=True)['hl_potentiel'].sum()
                  .reset_index().rename(columns={'hl_potentiel': 'YTD_HL_pot'}))

    df_base = (df_perim_unique.merge(df_ytd, on=['agence', 'article'], how='left', sort=False)
                              .merge(df_ytd_pot, on=['agence', 'article'], how='left', sort=False)
                              .merge(df_premiere_annee, on=['agence', 'article'], how='left', sort=False))
    df_base['YTD_HL'] = df_base['YTD_HL'].fillna(0.0)
    df_base['YTD_HL_pot'] = df_base['YTD_HL_pot'].fillna(0.0)
    df_base['Annee_Debut'] = df_base['Annee_Debut'].fillna(annee_cloture)

    df_base['Annee_Base'] = np.maximum(np.maximum(annee_min_cagr, annee_rupture_tendance), df_base['Annee_Debut'])

    df_base_vol = (df_realise.groupby(['agence', 'article', 'annee'], observed=True)['hl'].sum().reset_index())
    df_base = df_base.merge(df_base_vol, left_on=['agence', 'article', 'Annee_Base'], right_on=['agence', 'article', 'annee'], how='left', sort=False)
    df_base = df_base.rename(columns={'hl': 'Base_Hist'}).drop(columns=['annee'])
    df_base['Base_Hist'] = df_base['Base_Hist'].fillna(0.0)

    df_mois_debut = (df_realise[(df_realise['annee'] == annee_cloture) & (df_realise['hl'] > 0)]
                     .groupby(['agence', 'article'], observed=True)['mois'].min()
                     .reset_index().rename(columns={'mois': 'Mois_Debut'}))

    df_base = df_base.merge(df_mois_debut, on=['agence', 'article'], how='left', sort=False)
    df_base['Mois_Debut'] = df_base['Mois_Debut'].fillna(1).astype(int)

    df_indices_temp = df_base[['agence', 'article', 'Mois_Debut']].merge(table_indices_forecast, on=['agence', 'article'], how='left', sort=False)
    df_cumul = (df_indices_temp[(df_indices_temp['mois'] >= df_indices_temp['Mois_Debut']) & (df_indices_temp['mois'] <= mois_cutoff)]
                .groupby(['agence', 'article'], observed=True)['Indice'].sum()
                .reset_index().rename(columns={'Indice': 'Cumul_Coef'}))

    df_base = df_base.drop(columns=['Mois_Debut']).merge(df_cumul, on=['agence', 'article'], how='left', sort=False)
    df_base['Cumul_Coef'] = df_base['Cumul_Coef'].fillna(mois_cutoff * 1.0).replace(0, 1.0)
    df_base['Base_Mensuelle'] = df_base['YTD_HL'] / df_base['Cumul_Coef']
    df_base['Base_Mensuelle_pot'] = df_base['YTD_HL_pot'] / df_base['Cumul_Coef']
    df_base['Projection_CurrentYear'] = df_base['Base_Mensuelle'] * 12.0
    df_base['Nb_Annees'] = annee_cloture - df_base['Annee_Base']

    annee_debut_effective = max(annee_min_cagr, annee_rupture_tendance)
    df_hist_cagr = df_realise[(df_realise['annee'] >= annee_debut_effective) & (df_realise['annee'] <= annee_max_cagr)].groupby(['agence', 'article', 'annee'], observed=True)['hl_potentiel'].sum().reset_index()

    if not df_hist_cagr.empty:
        g = df_hist_cagr.groupby(['agence', 'article'], observed=True)
        df_vol_debut = (df_hist_cagr[df_hist_cagr['annee'] == g['annee'].transform('min')].groupby(['agence', 'article'], observed=True)['hl_potentiel'].sum().rename('Vol_Debut').reset_index())
        df_vol_fin = (df_hist_cagr[df_hist_cagr['annee'] == g['annee'].transform('max')].groupby(['agence', 'article'], observed=True)['hl_potentiel'].sum().rename('Vol_Fin').reset_index())
        df_annees_hist = (df_hist_cagr.groupby(['agence', 'article'], observed=True)['annee'].agg(['min', 'max']).rename(columns={'min': 'Annee_Debut_Hist', 'max': 'Annee_Fin_Hist'}).reset_index())
        df_base = (df_base.merge(df_vol_debut, on=['agence', 'article'], how='left', sort=False)
                          .merge(df_vol_fin, on=['agence', 'article'], how='left', sort=False)
                          .merge(df_annees_hist, on=['agence', 'article'], how='left', sort=False))
        df_base['Nb_Annees_Hist'] = (df_base['Annee_Fin_Hist'] - df_base['Annee_Debut_Hist']).clip(lower=0)
        df_base['CAGR_Hist'] = np.where((df_base['Vol_Debut'] > 0) & (df_base['Vol_Fin'] > 0) & (df_base['Nb_Annees_Hist'] > 0), (df_base['Vol_Fin'] / df_base['Vol_Debut']) ** (1 / df_base['Nb_Annees_Hist']) - 1, 0.0)
    else:
        df_base['CAGR_Hist'] = 0.0

    df_base['CAGR_Hist'] = df_base['CAGR_Hist'].clip(lower=-0.20, upper=0.30)

    if methode_croissance == "CAGR Classique":
        df_base['CAGR_brut'] = np.where((df_base['Base_Hist'] > 0) & (df_base['Projection_CurrentYear'] > 0) & (df_base['Nb_Annees'] > 0), (df_base['Projection_CurrentYear'] / df_base['Base_Hist']) ** (1 / df_base['Nb_Annees']) - 1, df_base['CAGR_Hist'])
        df_base['CAGR_val'] = np.where(df_base['Base_Hist'] < 100.0, df_base['CAGR_Hist'], df_base['CAGR_brut'])
    elif methode_croissance == "Tendance Linéaire":
        slopes_data = []
        for (agence, article), group in df_hist_cagr.groupby(['agence', 'article'], observed=True):
            try:
                x = group['annee'].values.astype(float)
                y = group['hl_potentiel'].values.astype(float)
                mask = ~np.isnan(x) & ~np.isnan(y)
                x = x[mask]; y = y[mask]
                if len(x) >= 2 and np.sum(y) > 0:
                    slope, _ = np.polyfit(x, y, 1)
                    mean_y = np.mean(y)
                    slope_rel = float(slope / mean_y) if mean_y > 0 else 0.0
                else: slope_rel = np.nan
            except Exception: slope_rel = np.nan
            slopes_data.append({'agence': agence, 'article': article, 'Slope_Rel': slope_rel})
        slopes = pd.DataFrame(slopes_data, columns=['agence', 'article', 'Slope_Rel'])
        if not slopes.empty:
            df_base = df_base.merge(slopes, on=['agence', 'article'], how='left', sort=False)
            df_base['CAGR_val'] = df_base['Slope_Rel'].fillna(df_base['CAGR_Hist'])
        else: df_base['CAGR_val'] = df_base['CAGR_Hist']
    elif methode_croissance == "Moyenne 3 ans":
        try:
            df_pivot = df_hist_cagr.pivot_table(index=['agence', 'article'], columns='annee', values='hl_potentiel', aggfunc='sum').fillna(0)
            growth_rates = df_pivot.pct_change(axis=1).iloc[:, -3:].mean(axis=1).reset_index(name='Avg_Growth')
            if not growth_rates.empty:
                df_base = df_base.merge(growth_rates, on=['agence', 'article'], how='left', sort=False)
                df_base['CAGR_val'] = df_base['Avg_Growth'].fillna(df_base['CAGR_Hist'])
            else: df_base['CAGR_val'] = df_base['CAGR_Hist']
        except: df_base['CAGR_val'] = df_base['CAGR_Hist']
    else:
        df_base['CAGR_val'] = df_base['CAGR_Hist']

    masque_nouveau = (df_base['Nb_Annees_Hist'] < 2) | (df_base['CAGR_val'].isna()) | (df_base['CAGR_val'] == 0)
    df_matures = df_base[~masque_nouveau]
    cagr_par_marque = df_matures.groupby('marque', observed=True)['CAGR_val'].median().to_dict() if not df_matures.empty and 'marque' in df_matures.columns else {}
    cagr_par_segment = df_matures.groupby('segment', observed=True)['CAGR_val'].median().to_dict() if not df_matures.empty and 'segment' in df_matures.columns else {}
    cagr_global = df_matures['CAGR_val'].median() if not df_matures.empty else 0.03
    if pd.isna(cagr_global): cagr_global = 0.03

    def appliquer_fallback(row):
        if 'marque' in row and row['marque'] in cagr_par_marque:
            val = cagr_par_marque[row['marque']]
            if not pd.isna(val): return val
        if 'segment' in row and row['segment'] in cagr_par_segment:
            val = cagr_par_segment[row['segment']]
            if not pd.isna(val): return val
        if not pd.isna(cagr_global): return cagr_global
        return 0.03

    df_base.loc[masque_nouveau, 'CAGR_val'] = df_base.loc[masque_nouveau].apply(appliquer_fallback, axis=1)
    df_base['CAGR_val'] = df_base['CAGR_val'].clip(lower=-0.20, upper=0.30)
    df_base = df_base.merge(df_base_momentum, on=['agence', 'article'], how='left', sort=False).fillna({'Base_EXCEL': 0.0, 'Momentum': 0.0})

    annees_cibles = list(range(annee_cloture, annee_cible + 1))
    mois_cibles = list(range(1, 13))
    n_base = len(df_base)
    idx = pd.MultiIndex.from_product([range(n_base), annees_cibles, mois_cibles], names=['_i', 'annee', 'mois'])
    df_cross = df_base.reset_index(drop=True).iloc[idx.get_level_values('_i').to_numpy()].reset_index(drop=True)
    df_cross['annee'] = idx.get_level_values('annee').to_numpy()
    df_cross['mois'] = idx.get_level_values('mois').to_numpy()

    df_cross = df_cross.merge(table_indices_forecast, on=['mois', 'agence', 'article'], how='left', sort=False)
    df_cross['Indice'] = df_cross['Indice'].fillna(1.0)

    df_realise_grouped = (df_realise.groupby(['annee', 'mois', 'agence', 'article'], observed=True)
                          .agg(hl_reel=('hl', 'sum'), hl_pot_reel=('hl_potentiel', 'sum'))
                          .reset_index())
    df_cross = df_cross.merge(df_realise_grouped, on=['annee', 'mois', 'agence', 'article'], how='left', sort=False)

    df_cross['is_realise'] = (df_cross['annee'] == annee_cloture) & (df_cross['mois'] <= mois_cutoff)
    df_cross['multiplicateur_cagr'] = (1 + df_cross['CAGR_val']) ** (df_cross['annee'] - annee_cloture)

    prev_2026 = df_cross['Base_Mensuelle'] * df_cross['Indice']
    prev_futur = df_cross['Base_Mensuelle'] * df_cross['Indice'] * df_cross['multiplicateur_cagr']
    df_cross['Prevision_HL'] = np.where(df_cross['annee'] <= annee_cible, prev_2026, prev_futur)
    df_cross['Prevision_HL'] = np.maximum(0.0, df_cross['Prevision_HL'])

    prev_sans_2026 = df_cross['Base_Mensuelle_pot'] * df_cross['Indice']
    prev_sans_futur = df_cross['Base_Mensuelle_pot'] * df_cross['Indice'] * df_cross['multiplicateur_cagr']
    df_cross['Prevision_HL_sans_rupture'] = np.where(df_cross['annee'] <= annee_cible, prev_sans_2026, prev_sans_futur)
    df_cross['Prevision_HL_sans_rupture'] = np.maximum(0.0, df_cross['Prevision_HL_sans_rupture'])

    df_cross['key_article_budget'] = df_cross['article'].apply(clean_text_for_budget_key)

    if budget_bytes is not None:
        try:
            xls = pd.ExcelFile(io.BytesIO(budget_bytes))
            df_budget = None
            for sheet in xls.sheet_names:
                temp = pd.read_excel(xls, sheet_name=sheet)
                temp.columns = [str(c).strip().lower() for c in temp.columns]
                if any('article' in c for c in temp.columns) and any('valeur' in c for c in temp.columns) and any('mois' in c for c in temp.columns):
                    df_budget = temp.copy(); break
            if df_budget is None: budget_status = "warning"
            else:
                col_art = next((c for c in df_budget.columns if 'article' in c), None)
                col_val = next((c for c in df_budget.columns if 'valeur' in c), None)
                col_mois = next((c for c in df_budget.columns if 'mois' in c), None)
                col_ag = next((c for c in df_budget.columns if 'attribut' in c or 'agence' in c), None)
                if col_art and col_val and col_mois:
                    df_budget = df_budget.dropna(subset=[col_art])
                    mask_33can = df_budget[col_art].astype(str).str.contains('33', na=False) & df_budget[col_art].astype(str).str.contains('CAN', case=False, na=False)
                    df_budget = df_budget[mask_33can].copy()
                    if df_budget.empty: budget_status = "warning"
                    else:
                        df_budget['key_article_budget'] = df_budget[col_art].apply(clean_text_for_budget_key)
                        df_budget['mois'] = pd.to_numeric(df_budget[col_mois], errors='coerce')
                        df_budget['valeur_budget'] = pd.to_numeric(df_budget[col_val], errors='coerce').fillna(0.0)
                        df_budget = df_budget.dropna(subset=['mois'])
                        df_temp_content = df_cross[['key_article_budget', 'contenance_cl']].drop_duplicates(subset=['key_article_budget'])
                        df_budget = df_budget.merge(df_temp_content, on='key_article_budget', how='left', sort=False)
                        df_budget['contenance_cl'] = df_budget['contenance_cl'].fillna(33.0)
                        df_budget['valeur_budget'] = df_budget['valeur_budget'] * (df_budget['contenance_cl'] / 10000.0)
                        mask_budget_target = (df_cross['annee'] == annee_cible) & (~df_cross['is_realise'])
                        if budget_all_agencies or not col_ag:
                            df_budget_agg = df_budget.groupby(['key_article_budget', 'mois'])['valeur_budget'].sum().reset_index()
                            df_cross = df_cross.merge(df_budget_agg, on=['key_article_budget', 'mois'], how='left', suffixes=('', '_budget'), sort=False)
                            df_cross['Forecast_Total_Article_Mois'] = (df_cross.loc[mask_budget_target].groupby(['key_article_budget', 'mois'])['Prevision_HL'].transform('sum').reindex(df_cross.index))
                            mask_apply = mask_budget_target & df_cross['valeur_budget'].notna()
                            mask_denom_pos = mask_apply & (df_cross['Forecast_Total_Article_Mois'] > 0)
                            mask_denom_zero = mask_apply & (df_cross['Forecast_Total_Article_Mois'] == 0)
                            df_cross.loc[mask_denom_pos, 'Prevision_HL'] = (df_cross.loc[mask_denom_pos, 'Prevision_HL'] * (df_cross.loc[mask_denom_pos, 'valeur_budget'] / df_cross.loc[mask_denom_pos, 'Forecast_Total_Article_Mois']))
                            df_cross.loc[mask_denom_zero, 'Prevision_HL'] = df_cross.loc[mask_denom_zero, 'valeur_budget']
                        else:
                            df_budget['agence_clean'] = df_budget[col_ag].astype(str).str.replace(r'^\d+-', '', regex=True)
                            df_budget['key_agence'] = df_budget['agence_clean'].apply(clean_text_for_key)
                            df_cross['key_agence'] = df_cross['agence'].apply(clean_text_for_key)
                            df_budget_agg = df_budget.groupby(['key_article_budget', 'key_agence', 'mois'])['valeur_budget'].sum().reset_index()
                            df_cross = df_cross.merge(df_budget_agg, on=['key_article_budget', 'key_agence', 'mois'], how='left', suffixes=('', '_budget'), sort=False)
                            mask_apply = mask_budget_target & df_cross['valeur_budget'].notna()
                            df_cross.loc[mask_apply, 'Prevision_HL'] = df_cross.loc[mask_apply, 'valeur_budget']
                        budget_status = "ok"
                else: budget_status = "warning"
        except Exception: budget_status = "error"

    for c in ['key_article_budget', 'key_agence', 'valeur_budget', 'Forecast_Total_Article_Mois', 'contenance_cl_x', 'contenance_cl_y', 'agence_clean']:
        if c in df_cross.columns: df_cross = df_cross.drop(columns=[c])

    df_cross['Prevision_HL'] = np.maximum(0.0, df_cross['Prevision_HL'])
    df_cross['Volume_HL'] = np.where(df_cross['is_realise'], df_cross['hl_reel'].fillna(0.0), df_cross['Prevision_HL'])
    df_cross['Volume_HL'] = np.maximum(0.0, df_cross['Volume_HL'])

    df_cross['Volume_HL_sans_rupture'] = np.where(df_cross['is_realise'], df_cross['hl_pot_reel'].fillna(0.0), df_cross['Prevision_HL_sans_rupture'])
    df_cross['Volume_HL_sans_rupture'] = np.maximum(0.0, df_cross['Volume_HL_sans_rupture'])

    contenance_safe = df_cross['contenance_cl'].replace(0, 100).fillna(100.0)
    df_cross['Volume_Cols'] = df_cross['Volume_HL'] * (10000.0 / contenance_safe)
    df_cross['Prevision_Cols'] = df_cross['Prevision_HL'] * (10000.0 / contenance_safe)

    df_cross['Volume_Cols_sans_rupture'] = df_cross['Volume_HL_sans_rupture'] * (10000.0 / contenance_safe)
    df_cross['Prevision_Cols_sans_rupture'] = df_cross['Prevision_HL_sans_rupture'] * (10000.0 / contenance_safe)

    df_cross['Statut'] = np.where(df_cross['is_realise'], "Réalisé", "Prévision")
    df_cross['CAGR (%)'] = df_cross['CAGR_val'] * 100

    df_cross['mois'] = pd.to_numeric(df_cross['mois'], errors='coerce').fillna(1).astype(int)
    df_cross['mois'] = df_cross['mois'].clip(1, 12)
    _mois_arr = np.array(MOIS_NOMS, dtype=object)
    df_cross['Date'] = (_mois_arr[df_cross['mois'].to_numpy() - 1] + '-' + df_cross['annee'].astype(str).str[-2:].to_numpy())

    cols_finales = ["annee", "mois", "agence", "article", "contenance_cl", "Date", "Statut", "Indice", "Base_EXCEL", "Momentum", "Base_Mensuelle", "CAGR (%)", "Volume_HL", "Volume_Cols", "Prevision_HL", "Prevision_Cols", "hl_reel",
                    "Volume_HL_sans_rupture", "Volume_Cols_sans_rupture", "Prevision_HL_sans_rupture", "Prevision_Cols_sans_rupture"]
    df_realise_out = df_realise.merge(df_perimetre_filtre[['agence', 'article']].drop_duplicates(), on=['agence', 'article'], how='inner', sort=False).copy()
    df_sarr_out = df_sarr_cont.merge(df_perim_unique[['agence', 'article', 'contenance_cl']], on=['agence', 'article'], how='left', sort=False)

    return table_indices_rolling, df_sarr_out, df_global_rolling, df_cross[cols_finales].copy(), df_realise_out, budget_status, table_indices_forecast

@st.cache_data(show_spinner=False)
def _pivot_indices_cached(df_idx: pd.DataFrame) -> pd.DataFrame:
    p = df_idx.pivot_table(index=['agence', 'article'], columns='mois', values='Indice', aggfunc='first').fillna(1.0)
    p.columns = [MOIS_NOMS[c - 1] for c in p.columns]
    return p

# ==============================================================================
# MODULES SUPPLÉMENTAIRES
# ==============================================================================
def analyser_comportement_sku(df_sarr, df_perimetre):
    if df_sarr is None or df_sarr.empty: return pd.DataFrame()
    df_clean = df_sarr.dropna(subset=['SARR_HL']).copy()
    if df_clean.empty: return pd.DataFrame()
    resultats = []
    for (agence, article), group in df_clean.groupby(['agence', 'article'], observed=True):
        group = group.sort_values(['annee', 'mois'])
        if len(group) < 6: continue
        sarr_moyen = group['SARR_HL'].mean()
        sarr_recent = group['SARR_HL'].tail(3).mean()
        momentum_actuel = group['Momentum'].iloc[-1] if not pd.isna(group['Momentum'].iloc[-1]) else 0.0
        cagr = group['CAGR (%)'].iloc[-1] if 'CAGR (%)' in group.columns and not pd.isna(group['CAGR (%)'].iloc[-1]) else 0.0
        volatilite = (group['SARR_HL'].std() / sarr_moyen) if sarr_moyen > 0 else 0.0
        indices = group[['mois', 'Indice']].drop_duplicates(subset=['mois'])
        if not indices.empty:
            peak_idx = indices['Indice'].idxmax()
            peak_mois = int(indices.loc[peak_idx, 'mois'])
            peak_nom = MOIS_NOMS[peak_mois - 1]
            peak_ratio = indices['Indice'].max() / indices['Indice'].mean() if indices['Indice'].mean() > 0 else 1.0
        else: peak_nom, peak_ratio = "N/A", 1.0
        if volatilite > 0.30: profil, emoji = "Volatile", "🔄"
        elif peak_ratio > 1.50: profil, emoji = "Saisonnier", "🏔️"
        elif cagr > 5 and momentum_actuel > 0: profil, emoji = "Star", "🌟"
        elif cagr > 5 and momentum_actuel <= 0: profil, emoji = "Décélération", "⚠️"
        elif cagr < -5 and momentum_actuel < 0: profil, emoji = "En déclin", "📉"
        elif abs(cagr) <= 5 and abs(momentum_actuel) < 0.1 * sarr_moyen: profil, emoji = "Cash Cow", "⚖️"
        else: profil, emoji = "En transition", "🔄"
        phrases = []
        if profil == "Star": phrases.append(f"**{article}** ({agence}) est en forte croissance avec un CAGR de **{format_fr(cagr, 1, signed=True)}%**.")
        elif profil == "En déclin": phrases.append(f"**{article}** ({agence}) est en déclin structurel avec un CAGR de **{format_fr(cagr, 1, signed=True)}%**.")
        elif profil == "Décélération": phrases.append(f"**{article}** ({agence}) a connu une croissance passée ({format_fr(cagr, 1, signed=True)}% CAGR) mais montre des signes de ralentissement.")
        elif profil == "Saisonnier": phrases.append(f"**{article}** ({agence}) présente une forte saisonnalité avec un pic en **{peak_nom}** (indice {format_fr(peak_ratio, 2)}x).")
        elif profil == "Volatile": phrases.append(f"**{article}** ({agence}) est très volatile (CV = {format_fr(volatilite*100)}%), la prévision est peu fiable.")
        else: phrases.append(f"**{article}** ({agence}) est stable avec un CAGR de {format_fr(cagr, 1, signed=True)}%.")
        seuil_momentum = 0.10 * sarr_moyen
        if momentum_actuel > seuil_momentum: phrases.append(f"Le SARR récent ({format_fr(sarr_recent)} HL/mois) est soutenu par un Momentum **positif** ({format_fr(momentum_actuel, signed=True)} HL), signal d'accélération.")
        elif momentum_actuel < -seuil_momentum: phrases.append(f"Le SARR récent ({format_fr(sarr_recent)} HL/mois) est plombé par un Momentum **négatif** ({format_fr(momentum_actuel, signed=True)} HL), signal d'essoufflement.")
        else: phrases.append(f"Le SARR est stable autour de **{format_fr(sarr_moyen)} HL/mois** avec un Momentum neutre.")
        if peak_ratio > 1.5 and profil != "Saisonnier": phrases.append(f"Pic saisonnier marqué en **{peak_nom}** (indice {format_fr(peak_ratio, 2)}x).")
        elif peak_ratio > 1.2: phrases.append(f"Saisonnalité modérée, pic en **{peak_nom}**.")
        elif peak_ratio <= 1.2 and profil != "Volatile": phrases.append(f"Consommation régulière toute l'année.")
        if profil == "Star": reco = "✅ Prioriser le réapprovisionnement et maximiser la distribution."
        elif profil == "En déclin": reco = "⚠️ Envisager une promotion, un arrêt de référence ou une révision tarifaire."
        elif profil == "Décélération": reco = "🔍 Investiguer les causes de la baisse de Momentum."
        elif profil == "Volatile": reco = "📊 Renforcer la prévision court terme (fenêtre 3 mois)."
        elif profil == "Saisonnier": reco = f"📅 Anticiper les stocks avant le pic de {peak_nom}."
        else: reco = "➡️ Maintenir le pilotage actuel."
        resultats.append({
            'Agence': agence, 'Article': article, 'Profil': f"{emoji} {profil}",
            'Commentaire': " ".join(phrases), 'Recommandation': reco,
            'SARR moyen (HL/mois)': round(sarr_moyen, 1), 'Momentum (HL)': round(momentum_actuel, 1),
            'CAGR (%)': round(cagr, 1), 'Volatilité': f"{format_fr(volatilite*100)}%", 'Mois Pic': peak_nom,
        })
    return pd.DataFrame(resultats)

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
with st.sidebar:
    BASE_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    LOGO_PATH = BASE_DIR / "LOGO_STAR.png"
    if LOGO_PATH.exists(): st.image(str(LOGO_PATH), use_container_width=True)
    else: st.warning("⚠️ Logo non trouvé")

    st.markdown("---")
    st.markdown("### 📁 Importation")
    mode_import = st.radio("Mode d'importation", options=["Fichier unique (Multi-onglets)", "Fichiers séparés"], index=0, help="Choisissez 'Fichier unique' si vous avez un seul Excel avec les onglets Ventes, classeur.2, budget_query, rupture.")

    if mode_import == "Fichier unique (Multi-onglets)":
        fichier_unique = st.file_uploader("Fichier Global (DATA_BASEX.xlsx)", type=["xlsx"], key="uploader_unique")
        if fichier_unique is not None:
            fichier_ventes = fichier_unique; fichier_ref = fichier_unique; fichier_budget = fichier_unique; fichier_rupture = fichier_unique
        else: fichier_ventes = fichier_ref = fichier_budget = fichier_rupture = None
    else:
        fichier_ventes = st.file_uploader("Ventes (DATA_BRUT.xlsx)", type=["xlsx"], key="uploader_ventes")
        fichier_ref = st.file_uploader("Référentiel (Classeur2.xlsx)", type=["xlsx"], key="uploader_ref")
        fichier_budget = st.file_uploader("Budget Query (Optionnel)", type=["xlsx"], key="uploader_budget")
        fichier_rupture = st.file_uploader("Ruptures (Optionnel)", type=["xlsx"], key="uploader_rupture")

    budget_all_agencies = True

    if fichier_ventes is not None:
        st.markdown("---")
        st.markdown("### ⚙️ Paramètres du modèle")
        annee_cible = st.number_input("Année Cible", min_value=2020, max_value=2035, value=2026, key="param_annee_cible")
        unite_affichage = st.radio("Unité d'affichage", options=["HL", "Cols"], index=0, horizontal=True, key="param_unite")

        st.markdown("##### 🎯 Objectif")
        taux_ambition = st.number_input("Taux d'ambition vs N-1 (%)", value=5.0, step=1.0, help="Objectif calculé = Volume Réalisé N-1 * (1 + Taux)", key="param_taux")
        use_objectif_manuel = st.checkbox("Forcer un objectif manuel", key="param_use_objectif")
        if use_objectif_manuel:
            objectif_manuel = st.number_input(f"Objectif Annuel ({unite_affichage})", min_value=0.0, step=1000.0, value=4400743.0, key="param_objectif_manuel")

        methode_croissance = "Tendance Linéaire"

        with st.expander("⚙️ Paramètres avancés"):
            p1, p2 = st.columns(2)
            with p1: annee_min_is = st.number_input("Année Min IS", min_value=2010, max_value=2030, value=2024, key="param_min_is")
            with p2: annee_max_is = st.number_input("Année Max IS", min_value=annee_min_is, max_value=2030, value=max(2025, annee_min_is), key="param_max_is")
            p3, p4 = st.columns(2)
            with p3: annee_min_cagr = st.number_input("Année Min CAGR", min_value=2010, max_value=2030, value=2022, key="param_min_cagr_v2")
            with p4: annee_max_cagr = st.number_input("Année Max CAGR", min_value=annee_min_cagr, max_value=2030, value=2025, key="param_max_cagr")
            p5, p6 = st.columns(2)
            with p5: annee_cloture = st.number_input("Année Clôture", min_value=2020, max_value=2030, value=2026, key="param_annee_cloture")
            with p6: mois_cutoff = st.selectbox("Mois Cutoff", options=list(range(1, 13)), index=8, format_func=lambda m: f"{MOIS_NOMS[m-1]}", key="param_mois_cutoff")
            annee_rupture_tendance = st.number_input("Année de rupture de tendance (Ignorer avant)", min_value=2010, max_value=2030, value=2022, help="Si le marché a changé en 2024, mettez 2024. Le modèle ignorera l'historique avant cette année pour le calcul du CAGR.", key="param_rupture_tendance_v2")
            mois_cibles_selection = st.multiselect("Mois cible (Filtre tableau)", options=MOIS_NOMS, default=[], key="param_mois_cible", help="Filtre uniquement le tableau des prévisions, pas le KPI global.")

        st.markdown("---")
        if st.button("🔄 Vider le cache & Recalculer"):
            st.cache_data.clear()
            st.rerun()

        with st.expander("👁️ Affichage des onglets avancés"):
            show_raw_data = st.checkbox("Afficher l'onglet Données Brutes", value=False, key="param_show_raw")
            show_analyse_comp = st.checkbox("Afficher l'onglet Analyse Comportementale", value=False, key="param_show_analyse")

if fichier_ventes is None:
    st.markdown(f"""<div class="hero-header"><div><h1>PREVISIONS STAR MADAGASCAR</h1></div><div class="badge-demo">⭐ Données Officielles STAR</div></div>""", unsafe_allow_html=True)
    st.info("👋 **Bienvenue !** Pour démarrer :\n\n1. Choisissez votre mode d'importation dans la barre latérale.\n2. Importez vos données.\n3. Ajustez les filtres et paramètres.")
    st.stop()

df_enrichi = charger_et_enrichir(fichier_ventes.getvalue(), fichier_ref.getvalue() if fichier_ref is not None else None, fichier_rupture.getvalue() if fichier_rupture is not None else None)
if df_enrichi.empty or "annee" not in df_enrichi.columns:
    st.error("⚠️ Le fichier de ventes n'est pas au bon format ou est vide.")
    st.stop()

st.markdown(f"""<div class="hero-header"><div><h1>PREVISIONS STAR MADAGASCAR</h1></div><div class="badge-demo">⭐ Données Officielles STAR</div></div>""", unsafe_allow_html=True)

with st.expander("🎯 Filtres de périmètre", expanded=False):
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        regions_dispo = sorted([str(r) for r in df_enrichi["region"].unique() if pd.notna(r) and str(r) not in ["Aucune vente", "Autre"]])
        sel_regions = st.multiselect("Région", options=regions_dispo, placeholder="Toutes", key="filter_region")
        df_temp = df_enrichi[df_enrichi["region"].isin(sel_regions)] if sel_regions else df_enrichi
        sel_marques = st.multiselect("Marque", options=sorted([str(m) for m in df_temp["marque"].unique() if pd.notna(m) and str(m) != "Inconnu"]), placeholder="Toutes", key="filter_marque")
        df_temp = df_temp[df_temp["marque"].isin(sel_marques)] if sel_marques else df_temp
    with f2:
        agences_dispo = sorted([str(a) for a in df_temp["agence"].unique() if pd.notna(a) and str(a) != "Aucune vente"])
        sel_agences = st.multiselect("Agence", options=agences_dispo, placeholder="Toutes", key="filter_agence")
        df_temp = df_temp[df_temp["agence"].isin(sel_agences)] if sel_agences else df_temp
        sel_contenances = st.multiselect("Contenance (cl)", options=sorted([int(c) for c in df_temp["contenance_cl"].unique() if pd.notna(c)]), placeholder="Toutes", key="filter_contenance")
        df_temp = df_temp[df_temp["contenance_cl"].isin(sel_contenances)] if sel_contenances else df_temp
    with f3:
        sel_segments = st.multiselect("Segment", options=sorted([str(s) for s in df_temp["segment"].unique() if pd.notna(s)]), placeholder="Tous", key="filter_segment")
        df_temp = df_temp[df_temp["segment"].isin(sel_segments)] if sel_segments else df_temp
        sel_emballages = st.multiselect("Emballage", options=sorted([str(e) for e in df_temp["emballage"].unique() if pd.notna(e) and str(e) != "AUTRE"]), placeholder="Tous", key="filter_emballage")
        df_temp = df_temp[df_temp["emballage"].isin(sel_emballages)] if sel_emballages else df_temp
    with f4:
        sel_articles = st.multiselect("Article", options=sorted([str(a) for a in df_temp["article"].unique() if pd.notna(a)]), placeholder="Tous", key="filter_article")
        df_temp = df_temp[df_temp["article"].isin(sel_articles)] if sel_articles else df_temp
        sel_positionnements = st.multiselect("Positionnement", options=sorted([str(p) for p in df_temp["positionnement"].unique() if pd.notna(p)]), placeholder="Tous", key="filter_positionnement")
        df_temp = df_temp[df_temp["positionnement"].isin(sel_positionnements)] if sel_positionnements else df_temp
        sel_occasions = st.multiselect("Occasion", options=sorted([str(o) for o in df_temp["occasion"].unique() if pd.notna(o) and str(o) != "Non renseigné"]), placeholder="Toutes", key="filter_occasion")
        df_temp = df_temp[df_temp["occasion"].isin(sel_occasions)] if sel_occasions else df_temp

df_perimetre = df_enrichi.copy()
if sel_regions: df_perimetre = df_perimetre[df_perimetre["region"].isin(sel_regions)]
if sel_agences: df_perimetre = df_perimetre[df_perimetre["agence"].isin(sel_agences)]
if sel_positionnements: df_perimetre = df_perimetre[df_perimetre["positionnement"].isin(sel_positionnements)]
if sel_contenances: df_perimetre = df_perimetre[df_perimetre["contenance_cl"].isin(sel_contenances)]
if sel_emballages: df_perimetre = df_perimetre[df_perimetre["emballage"].isin(sel_emballages)]
if sel_segments: df_perimetre = df_perimetre[df_perimetre["segment"].isin(sel_segments)]
if sel_articles: df_perimetre = df_perimetre[df_perimetre["article"].isin(sel_articles)]
if sel_marques: df_perimetre = df_perimetre[df_perimetre["marque"].isin(sel_marques)]
if sel_occasions: df_perimetre = df_perimetre[df_perimetre["occasion"].isin(sel_occasions)]

table_indices_rolling, df_sarr, df_global_rolling, df_previsions, df_realise, budget_status, table_indices_forecast = calculer_etape_5(
    df_perimetre, annee_min_is, annee_max_is, annee_min_cagr, annee_max_cagr, annee_cloture, mois_cutoff, annee_cible, methode_croissance, annee_rupture_tendance, fichier_budget.getvalue() if fichier_budget is not None else None, budget_all_agencies, cache_bust="v177"
)

if budget_status == "ok": st.sidebar.success("✅ Budget Query (33 CAN) appliqué à l'année cible.")
elif budget_status == "warning": st.sidebar.warning("⚠️ Aucune donnée valide (33 CAN) trouvée dans le fichier Budget.")
elif budget_status == "error": st.sidebar.error("⚠️ Erreur de lecture du Budget Query, ignoré.")

if df_global_rolling is None:
    st.warning("⚠️ Impossible de calculer les prévisions. Vérifiez vos filtres (ex: pas de vente avant le cutoff).")
    st.stop()

col_prev_aff = "Volume_Cols" if unite_affichage == "Cols" else "Volume_HL"
col_prev_pure = "Prevision_Cols" if unite_affichage == "Cols" else "Prevision_HL"

df_cible_annuel = df_previsions[df_previsions['annee'] == annee_cible]
atterrissage_cible = df_cible_annuel[col_prev_aff].fillna(0).sum()

if not mois_cibles_selection:
    df_previsions_filtre = df_previsions
    label_mois_str = "Tous les mois"
    mois_cibles_nums = list(range(1, 13))
else:
    mois_cibles_nums = [MOIS_NOMS.index(m) + 1 for m in mois_cibles_selection]
    df_previsions_filtre = df_previsions[df_previsions['mois'].isin(mois_cibles_nums)].copy()
    label_mois_str = ", ".join(mois_cibles_selection)

df_cible_filtre = df_previsions_filtre[df_previsions_filtre['annee'] == annee_cible]
atterrissage_global_kpi = df_cible_filtre[col_prev_aff].fillna(0).sum()
label_atterrissage_kpi = (f"Atterrissage global {annee_cible}" if not mois_cibles_selection else f"Atterrissage global - {label_mois_str}")

df_n1 = df_perimetre[df_perimetre['annee'] == (annee_cible - 1)].copy()
if not df_n1.empty:
    contenance_safe_n1 = df_n1['contenance_cl'].replace(0, 100).fillna(100.0)
    hist_n1_val = (df_n1['hl'] * (10000.0 / contenance_safe_n1)).fillna(0).sum() if unite_affichage == "Cols" else df_n1['hl'].fillna(0).sum()
else: hist_n1_val = 0.0

if mois_cibles_selection:
    df_n1_mois = df_n1[df_n1['mois'].isin(mois_cibles_nums)].copy()
    if not df_n1_mois.empty:
        contenance_n1_mois = df_n1_mois['contenance_cl'].replace(0, 100).fillna(100.0)
        hist_n1_kpi = ((df_n1_mois['hl'] * (10000.0 / contenance_n1_mois)).fillna(0).sum() if unite_affichage == "Cols" else df_n1_mois['hl'].fillna(0).sum())
    else: hist_n1_kpi = 0.0
else: hist_n1_kpi = hist_n1_val

if hist_n1_val > 0: objectif_calcule = hist_n1_val * (1 + taux_ambition / 100.0)
else: objectif_calcule = atterrissage_cible * (1 + taux_ambition / 100.0)

objectif_final = objectif_manuel if use_objectif_manuel else objectif_calcule
gap = atterrissage_cible - objectif_final

df_eval = df_previsions_filtre[df_previsions_filtre['Statut'] == 'Réalisé'].copy()
df_eval_agg = df_eval.groupby(['annee', 'mois'], observed=True)[[col_prev_aff, col_prev_pure]].sum().reset_index()

if not df_eval_agg.empty and df_eval_agg[col_prev_aff].sum() > 0:
    y_true = df_eval_agg[col_prev_aff].values
    y_pred = df_eval_agg[col_prev_pure].values
    mae = np.mean(np.abs(y_true - y_pred))
    wmape = (np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)) * 100
    denom_smape = np.abs(y_true) + np.abs(y_pred)
    valid_smape = denom_smape > 0
    if valid_smape.any(): smape = np.mean(2 * np.abs(y_pred[valid_smape] - y_true[valid_smape]) / denom_smape[valid_smape]) * 100
    else: smape = 0.0
else: mae, wmape, smape = 0.0, 0.0, 0.0

delta_n1_pct = ((atterrissage_global_kpi - hist_n1_kpi) / hist_n1_kpi * 100) if hist_n1_kpi > 0 else 0
delta_class = "up" if delta_n1_pct >= 0 else "down"
delta_icon = "▲" if delta_n1_pct >= 0 else "▼"
progression = (atterrissage_cible / objectif_final * 100) if objectif_final > 0 else 0
progression = min(max(progression, 0), 100)

k1, k2, k3, k4 = st.columns(4, gap="large")
with k1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-label">{label_atterrissage_kpi}</div><div class="kpi-value">{format_fr(atterrissage_global_kpi)}</div><div class="kpi-delta {delta_class}">{delta_icon} {format_fr(abs(delta_n1_pct), 1)}% vs N-1</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card" style="border-left-color: {COLORS['TEXTE']};"><div class="kpi-label">Objectif Annuel ({unite_affichage})</div><div class="kpi-value">{format_fr(objectif_final)}</div><div class="progress-container"><div class="progress-bar" style="width: {progression}%;"></div></div><div class="kpi-delta" style="color: {COLORS['TEXTE_SECONDAIRE']}; font-size: 0.75rem;">{format_fr(progression, 1)}% couvert</div></div>""", unsafe_allow_html=True)
with k3:
    gap_color = COLORS["VERT"] if gap >= 0 else COLORS["ROUGE"]
    gap_icon = "✔" if gap >= 0 else "⚠"
    gap_pct = (gap / objectif_final * 100) if objectif_final > 0 else 0
    st.markdown(f"""<div class="kpi-card" style="border-left-color: {gap_color};"><div class="kpi-label">GAP</div><div class="kpi-value" style="color: {gap_color};">{format_fr(gap, signed=True)}</div><div class="kpi-delta" style="color: {gap_color};">{gap_icon} {format_fr(gap_pct, 1, signed=True)}% VS objectif</div></div>""", unsafe_allow_html=True)
with k4:
    wmape_icon = "✔" if wmape < 5 else ("⚠" if wmape <= 10 else "✖")
    wmape_color = COLORS["VERT"] if wmape < 5 else (COLORS["ROUGE"] if wmape > 10 else COLORS["TEXTE_SECONDAIRE"])
    st.markdown(f"""<div class="kpi-card" style="border-left-color: {wmape_color};"><div class="kpi-label">Fiabilité (WMAPE)</div><div class="kpi-value" style="color: {wmape_color};">{format_fr(wmape, 1)}%</div><div class="kpi-delta" style="color: {wmape_color};">{wmape_icon} Erreur moyenne</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown(f"#### Superposition Réalisé vs Prévision ({annee_cible})")
    df_real_cible = df_perimetre[df_perimetre['annee'] == annee_cible].copy()
    if annee_cible == annee_cloture: df_real_cible = df_real_cible[df_real_cible['mois'] <= mois_cutoff]
    df_real_cible['Date_Str'] = df_real_cible['annee'].astype(str) + '-' + df_real_cible['mois'].astype(str).str.zfill(2) + '-01'
    df_real_cible['Date_Plot'] = pd.to_datetime(df_real_cible['Date_Str'])
    contenance_safe_real = df_real_cible['contenance_cl'].replace(0, 100).fillna(100.0)
    df_real_cible['Volume_Aff'] = df_real_cible['hl'] * (10000.0 / contenance_safe_real) if unite_affichage == "Cols" else df_real_cible['hl']
    df_real_plot = df_real_cible.groupby('Date_Plot', observed=True)['Volume_Aff'].sum().reset_index().rename(columns={'Volume_Aff': 'Volume'})

    df_prev_cible = df_cible_annuel.copy()
    df_prev_cible['Date_Str'] = df_prev_cible['annee'].astype(str) + '-' + df_prev_cible['mois'].astype(str).str.zfill(2) + '-01'
    df_prev_cible['Date_Plot'] = pd.to_datetime(df_prev_cible['Date_Str'])
    df_prev_plot = df_prev_cible.groupby('Date_Plot', observed=True)[col_prev_pure].sum().reset_index().rename(columns={col_prev_pure: 'Volume'})

    fig1 = go.Figure()
    if not df_prev_plot.empty:
        fig1.add_trace(go.Scatter(x=df_prev_plot['Date_Plot'], y=df_prev_plot['Volume'], mode='lines+markers', name='Prévision', line=dict(color=COLORS['ROUGE'], width=3, dash='dot', shape='spline', smoothing=1.3), marker=dict(size=7, color=COLORS['ROUGE'], line=dict(color='white', width=2)), hovertemplate="<b>Prévision</b>: %{y:,.0f}<extra></extra>"))
    if not df_real_plot.empty:
        fig1.add_trace(go.Scatter(x=df_real_plot['Date_Plot'], y=df_real_plot['Volume'], mode='lines+markers', name='Réalisé', line=dict(color=COLORS['ROUGE_FONCE'], width=4, shape='spline', smoothing=1.3), marker=dict(size=9, color=COLORS['ROUGE_FONCE'], line=dict(color='white', width=2)), hovertemplate="<b>Réalisé</b>: %{y:,.0f}<extra></extra>"))
    if annee_rupture_tendance > annee_min_cagr:
        try:
            x_val = pd.to_datetime(f"{annee_rupture_tendance}-01-01")
            fig1.add_vline(x=x_val, line_width=2, line_dash="dash", line_color=COLORS['GRIS'], annotation_text="Rupture", annotation_position="top left")
        except: pass
    fig1.update_layout(separators=" ,", plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=13, family="Inter", weight="bold")), xaxis=dict(showgrid=True, gridcolor=COLORS['BORDURE'], linecolor=COLORS['BORDURE'], tickformat="%b-%y", dtick="M1", tickfont=dict(family="Inter", size=12, weight="bold"), tickangle=-45), yaxis=dict(showgrid=True, gridcolor=COLORS['BORDURE'], zeroline=False, tickfont=dict(family="Inter", size=12, weight="bold"), tickformat=",.0f"), height=500, hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

st.markdown("<hr style='border: 1px solid #E5E7EB; margin: 30px 0;'>", unsafe_allow_html=True)

# ==============================================================================
# CONSTRUCTION DYNAMIQUE DES ONGLETS
# ==============================================================================
tab_names = ["Réalisé Cumulé", "Indices & SARR", "Prévisions", "Suivi Écart (Rupt vs Réalisé)", "Pareto (ABC)", "Fiabilité", "Ruptures"]
if show_analyse_comp: tab_names.insert(5, "Analyse Comportementale")
if show_raw_data: tab_names.insert(0, "Données Brutes")

active_tab = st.radio("Navigation", tab_names, horizontal=True, label_visibility="collapsed", key="main_navigation_radio")
N_MAX_DISPLAY = 5000
tab_placeholder = st.empty()

with tab_placeholder.container():
    if active_tab == "Données Brutes":
        st.markdown("### Données Brutes Enrichies")
        with st.expander("📊 Afficher le tableau des données brutes", expanded=True):
            cols_to_show = ["annee", "mois", "region", "agence", "article", "hl", "rupture_hl", "hl_potentiel"]
            df_to_show = df_enrichi[cols_to_show].copy()
            df_to_show.columns = ["Année", "Mois", "Région", "Agence", "Article", "Ventes Réelles (HL)", "Pertes Ruptures (HL)", "Volume Potentiel (HL)"]
            if len(df_to_show) > N_MAX_DISPLAY:
                st.caption(f"⚠️ Affichage limité à {format_fr(N_MAX_DISPLAY)} lignes sur {format_fr(len(df_to_show))}.")
                df_show_limited = df_to_show.head(N_MAX_DISPLAY)
                df_show_limited = ajouter_total(df_show_limited, label_col="Année", label="TOTAL (affiché)")
                small_kpi("TOTAL Ventes Réelles", format_fr(df_show_limited['Ventes Réelles (HL)'].iloc[-1]))
                st.dataframe(bold_total_row(df_show_limited), use_container_width=True, hide_index=True)
            else:
                df_to_show = ajouter_total(df_to_show, label_col="Année")
                small_kpi("TOTAL Ventes Réelles", format_fr(df_to_show['Ventes Réelles (HL)'].iloc[-1]))
                st.dataframe(bold_total_row(df_to_show), use_container_width=True, hide_index=True)

    elif active_tab == "Réalisé Cumulé":
        st.markdown("### Réalisé Cumulé (Jusqu'au Cutoff)")
        with st.expander("📊 Afficher le tableau du réalisé", expanded=True):
            if df_realise is not None and not df_realise.empty:
                df_real_agg = (df_realise.groupby(['annee', 'mois', 'region', 'agence', 'article'], observed=True)[['hl', 'rupture_hl', 'hl_potentiel']].sum().reset_index())
                df_real_agg.columns = ["Année", "Mois", "Région", "Agence", "Article", "Ventes Réelles", "Pertes Ruptures", "Volume Potentiel"]
                df_real_agg = ajouter_total(df_real_agg, label_col="Année")
                small_kpi("TOTAL Ventes Réelles", format_fr(df_real_agg['Ventes Réelles'].iloc[-1]))
                st.dataframe(bold_total_row(df_real_agg.head(N_MAX_DISPLAY)), use_container_width=True, hide_index=True)
            else: st.info("Aucune donnée réalisée pour le moment.")

    elif active_tab == "Indices & SARR":
        st.markdown("### Indices de Saisonnalité & SARR")
        df_sarr_calc = df_sarr.sort_values(['agence', 'article', 'annee', 'mois']).copy()
        df_sarr_calc["SARR_Aff"] = (df_sarr_calc["SARR_HL"] * (10000 / df_sarr_calc["contenance_cl"].replace(0, 100)) if unite_affichage == "Cols" else df_sarr_calc["SARR_HL"])
        df_sarr_calc["SARR_M1_Aff"] = (df_sarr_calc["SARR_M1"] * (10000 / df_sarr_calc["contenance_cl"].replace(0, 100)) if unite_affichage == "Cols" else df_sarr_calc["SARR_M1"])
        df_sarr_calc["Mois M"] = df_sarr_calc.apply(lambda r: f"{MOIS_NOMS[int(r['mois'])-1]}-{int(r['annee'])}", axis=1)
        df_sarr_calc["Mois M-1"] = df_sarr_calc.groupby(['agence', 'article'])["Mois M"].shift(1)
        df_sarr_calc["Momentum_Abs"] = df_sarr_calc["SARR_Aff"] - df_sarr_calc["SARR_M1_Aff"]
        df_sarr_calc["Momentum_Pct"] = (df_sarr_calc["Momentum_Abs"] / df_sarr_calc["SARR_M1_Aff"] * 100).replace([np.inf, -np.inf], np.nan)
        df_sarr_derniers = df_sarr_calc.groupby(['agence', 'article'], observed=True).tail(5)

        filtre_sarr = st.radio("Afficher le SARR et Graphes :", ["Tous", "Momentum Positif (+)", "Momentum Négatif (-)"], horizontal=True, label_visibility="collapsed")
        df_sarr_affiche = df_sarr_derniers.copy()
        if filtre_sarr == "Momentum Positif (+)":
            df_sarr_affiche = df_sarr_affiche[df_sarr_affiche["Momentum_Abs"] > 0]
        elif filtre_sarr == "Momentum Négatif (-)":
            df_sarr_affiche = df_sarr_affiche[df_sarr_affiche["Momentum_Abs"] < 0]

        c_idx, c_sarr = st.columns(2)
        with c_idx:
            st.markdown("**Indices de Saisonnalité (Glissant par Année)**")
            st.caption("💡 Note : L'indice global est recalculé pour chaque année en utilisant les 2 années précédentes (ex: 2023 utilise 2021-2022).")
            with st.expander("📊 Afficher les indices globaux par année", expanded=True):
                if not df_global_rolling.empty:
                    pivot_global = df_global_rolling.pivot(index='annee', columns='mois', values='Indice_glob')
                    pivot_global.columns = [MOIS_NOMS[int(c)-1] for c in pivot_global.columns]
                    pivot_global.index = [f"Année {int(y)}" for y in pivot_global.index]
                    st.dataframe(pivot_global.style.format("{:.2f}"), use_container_width=True)
                    st.markdown("---")
                st.markdown("**Détail par Article (Base Prévision)**")
                if not table_indices_forecast.empty:
                    pivot_indices = _pivot_indices_cached(table_indices_forecast)
                    st.dataframe(pivot_indices, use_container_width=True)
                else: st.info("Pas d'historique complet.")
        with c_sarr:
            st.markdown("**Table SARR (5 derniers mois) avec Momentum**")
            with st.expander("📊 Afficher le SARR & Momentum", expanded=True):
                df_sarr_aff = df_sarr_affiche[["annee", "mois", "agence", "article", "Mois M-1", "SARR_M1_Aff", "Mois M", "SARR_Aff", "Momentum_Abs", "Momentum_Pct"]].rename(columns={"annee": "Année", "mois": "Mois (Num)", "agence": "Agence", "article": "Article", "SARR_M1_Aff": "SARR M-1", "SARR_Aff": "SARR M", "Momentum_Abs": "Momentum (SARR M - SARR M-1)", "Momentum_Pct": "Momentum (%)"}).sort_values(["Agence", "Article", "Année", "Mois (Num)"])
                def calc_mom_pct(r):
                    if r.get("SARR M-1", 0) > 0:
                        return (r.get("Momentum (SARR M - SARR M-1)", 0) / r["SARR M-1"]) * 100
                    return np.nan
                df_sarr_aff = ajouter_total(df_sarr_aff, label_col="Agence", exclude_cols=["Momentum (%)"], custom_total_calc={"Momentum (%)": calc_mom_pct})
                small_kpi("TOTAL SARR M", format_fr(df_sarr_aff["SARR M"].iloc[-1]))
                st.dataframe(
                    bold_total_row(df_sarr_aff),
                    use_container_width=True, hide_index=True,
                    column_config={"Année": st.column_config.NumberColumn(format="%d"), "Mois (Num)": None, "SARR M": st.column_config.NumberColumn(format="%.0f"), "SARR M-1": st.column_config.NumberColumn(format="%.0f"), "Momentum (SARR M - SARR M-1)": st.column_config.NumberColumn(format="%.1f"), "Momentum (%)": st.column_config.NumberColumn(format="%.2f %%")}
                )
        st.markdown("---")
        st.markdown("### 📈 Visualisation Graphique")
        c_graph1, c_graph2 = st.columns(2)
        with c_graph1:
            st.markdown("**Graphique du Momentum (Barres Verticales)**")
            if not df_sarr_affiche.empty:
                df_momentum_plot = df_sarr_affiche.copy()
                df_momentum_plot["Label"] = df_momentum_plot["agence"] + " - " + df_momentum_plot["article"]
                df_momentum_plot = df_momentum_plot.sort_values(['agence', 'article', 'annee', 'mois']).groupby(['agence', 'article', 'Label']).tail(1).reset_index()
                if filtre_sarr == "Tous":
                    df_momentum_plot["Abs_Mom"] = df_momentum_plot["Momentum_Abs"].abs()
                    df_momentum_plot = df_momentum_plot.sort_values("Abs_Mom", ascending=False).head(10)
                df_momentum_plot = df_momentum_plot.sort_values("Momentum_Abs", ascending=False)
                df_momentum_plot["Label_Court"] = df_momentum_plot["Label"].apply(lambda x: x if len(x) <= 25 else x[:22] + '...')
                moy_momentum_global = df_momentum_plot["Momentum_Abs"].mean()
                fig_mom = go.Figure()
                fig_mom.add_trace(go.Bar(
                    x=df_momentum_plot["Label_Court"], y=df_momentum_plot["Momentum_Abs"],
                    marker_color=[COLORS["VERT"] if x >= 0 else COLORS["ROUGE"] for x in df_momentum_plot["Momentum_Abs"]],
                    text=df_momentum_plot["Momentum_Abs"].apply(lambda x: format_fr(x, signed=True)),
                    textposition="auto", hovertemplate="<b>%{x}</b><br>Momentum: %{y:,.1f} HL<extra></extra>"
                ))
                fig_mom.add_hline(y=0, line_dash="dash", line_color=COLORS['GRIS'])
                fig_mom.add_hline(y=moy_momentum_global, line_dash="dot", line_color=COLORS['TEXTE'], annotation_text=f"Moy. Globale ({format_fr(moy_momentum_global, 1, signed=True)})", annotation_position="top right")
                fig_mom.update_layout(plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=10, r=10, t=30, b=60), xaxis=dict(title="SKU", showgrid=False, tickangle=-45, tickfont=dict(family="Inter", size=11, color=COLORS['TEXTE'], weight="bold")), yaxis=dict(title=f"Momentum ({unite_affichage})", showgrid=True, gridcolor=COLORS['BORDURE'], tickfont=dict(family="Inter", size=11, color=COLORS['TEXTE'], weight="bold")), height=500, separators=" ,")
                st.plotly_chart(fig_mom, use_container_width=True, config={'displayModeBar': False})
            else: st.info("Aucune donnée de Momentum à afficher avec ce filtre.")
        with c_graph2:
            st.markdown("**Courbe de Saisonnalité Globale**")
            if not df_perimetre.empty:
                df_global_hl = df_perimetre.groupby('mois', observed=True)['hl'].sum().reset_index()
                total_hl = df_global_hl['hl'].sum()
                df_global_hl['Indice_Glob'] = df_global_hl['hl'] / (total_hl / 12.0) if total_hl > 0 else 1.0
                df_global_hl['Mois_Nom'] = df_global_hl['mois'].apply(lambda m: MOIS_NOMS[int(m)-1])
                fig_season = go.Figure()
                fig_season.add_trace(go.Scatter(x=df_global_hl['Mois_Nom'], y=df_global_hl['Indice_Glob'], mode='lines+markers', line=dict(color=COLORS['ROUGE'], width=4, shape='spline'), marker=dict(size=8, color=COLORS['ROUGE'], line=dict(color='white', width=2)), fill='tozeroy', fillcolor='rgba(227, 6, 19, 0.1)', hovertemplate="<b>%{x}</b><br>Indice global: %{y:.2f}<extra></extra>"))
                fig_season.add_hline(y=1.0, line_dash="dot", line_color=COLORS['TEXTE'], annotation_text="Moyenne Globale (1.0)", annotation_position="top left")
                fig_season.update_layout(plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=10, r=10, t=30, b=10), xaxis=dict(title="Mois", showgrid=True, gridcolor=COLORS['BORDURE'], tickfont=dict(family="Inter", size=11, color=COLORS['TEXTE'], weight="bold")), yaxis=dict(title="Indice global de saisonnalité", showgrid=True, gridcolor=COLORS['BORDURE'], tickfont=dict(family="Inter", size=11, color=COLORS['TEXTE'], weight="bold")), height=500, separators=" ,")
                st.plotly_chart(fig_season, use_container_width=True, config={'displayModeBar': False})
            else: st.info("Pas de données de saisonnalité disponibles.")

    elif active_tab == "Prévisions":
        st.markdown("### Prévisions Détaillées")
        st.markdown(f"Projections mensuelles pour : **<span style='color: {COLORS['ROUGE']};'>{label_mois_str}</span>**", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_search, col_export = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("Rechercher", "", placeholder="Rechercher un article ou une agence...", label_visibility="collapsed", key="search_previsions")
        with col_export:
            pass

        with st.expander("📊 Afficher le tableau des prévisions détaillées (Format Excel)", expanded=True):
            df_seg = df_perimetre[['article', 'segment']].drop_duplicates(subset=['article'])
            df_prev_cible = df_previsions_filtre[df_previsions_filtre['annee'] == annee_cible].copy()
            df_prev_seg = df_prev_cible.merge(df_seg, on='article', how='left')
            pivot_mensuel = df_prev_seg.pivot_table(index=['article', 'segment'], columns='mois', values=col_prev_aff, aggfunc='sum')
            pivot_mensuel = pivot_mensuel.reindex(columns=range(1, 13), fill_value=0)
            pivot_mensuel.columns = [MOIS_NOMS[int(c) - 1] for c in pivot_mensuel.columns]
            if not mois_cibles_selection or len(mois_cibles_selection) == 12: nom_total = "Total Année"
            else: nom_total = "Total Période"
            pivot_mensuel[nom_total] = pivot_mensuel.sum(axis=1)
            pivot_mensuel = pivot_mensuel[pivot_mensuel[nom_total] > 0]
            pivot_mensuel_reset = pivot_mensuel.reset_index().rename(columns={'article': 'Articles', 'segment': 'Segments'})
            if search_query:
                mask = pivot_mensuel_reset.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                pivot_mensuel_display = pivot_mensuel_reset[mask]
            else: pivot_mensuel_display = pivot_mensuel_reset
            pivot_mensuel_display = ajouter_total(pivot_mensuel_display, label_col="Articles")
            small_kpi(f"TOTAL {nom_total} ({unite_affichage})", format_fr(pivot_mensuel_display[nom_total].iloc[-1]))
            col_config = {"Articles": st.column_config.TextColumn("Articles", width="medium"), "Segments": st.column_config.TextColumn("Segments", width="small")}
            for mois in MOIS_NOMS:
                if mois in pivot_mensuel_display.columns: col_config[mois] = st.column_config.NumberColumn(mois, format="%.2f")
            if nom_total in pivot_mensuel_display.columns: col_config[nom_total] = st.column_config.NumberColumn(nom_total, format="%.2f")
            st.dataframe(bold_total_row(pivot_mensuel_display), use_container_width=True, hide_index=True, column_config=col_config, height=600)

        with st.expander("🔍 Voir le détail des calculs (Hybride)"):
            st.markdown("**Note :** L'année de clôture utilise la projection du Run-Rate (Base Mensuelle) pour éviter l'explosion du Momentum absolu. Les années suivantes ajoutent le CAGR calculé.")
            cols_to_show = ["annee", "mois", "Statut", "agence", "article", "Indice", "Base_EXCEL", "Momentum", "Base_Mensuelle", "CAGR (%)", col_prev_aff]
            df_detail = (df_previsions_filtre[cols_to_show].sort_values(["annee", "mois", "agence", "article"]))
            df_detail = ajouter_total(df_detail, label_col="annee", exclude_cols=["CAGR (%)", "Indice"])
            st.dataframe(bold_total_row(df_detail.head(N_MAX_DISPLAY)), use_container_width=True, hide_index=True, height=400, column_config={"Base_EXCEL": st.column_config.NumberColumn(format="%.1f"), "Momentum": st.column_config.NumberColumn(format="%.1f"), "Base_Mensuelle": st.column_config.NumberColumn(format="%.1f"), "CAGR (%)": st.column_config.NumberColumn(format="%.2f %%")})

    elif active_tab == "Suivi Écart (Rupt vs Réalisé)":
        st.markdown("### 🔀 Suivi Écart (Rupt vs Réalisé)")
        st.markdown("Tableau comparatif professionnel : Réalisé vs Prévision, avec et sans rupture.")
        st.markdown("<br>", unsafe_allow_html=True)

        has_rupture = df_perimetre['rupture_hl'].fillna(0).sum() > 0
        if not has_rupture:
            st.info("ℹ️ Aucune donnée de rupture détectée dans le périmètre sélectionné. Les prévisions 'avec' et 'sans' rupture sont identiques.")

        col_vol_sans = "Volume_Cols_sans_rupture" if unite_affichage == "Cols" else "Volume_HL_sans_rupture"
        col_prev_sans = "Prevision_Cols_sans_rupture" if unite_affichage == "Cols" else "Prevision_HL_sans_rupture"

        df_year = df_previsions_filtre[df_previsions_filtre['annee'] == annee_cible].copy()
        if df_year.empty:
            st.warning("Aucune donnée de prévision pour l'année cible.")
        else:
            total_avec = df_year[col_prev_aff].fillna(0).sum()
            total_sans = df_year[col_vol_sans].fillna(0).sum()
            diff = total_sans - total_avec
            diff_pct = (diff / total_avec * 100) if total_avec > 0 else 0

            # --- KPI CARDS AMÉLIORÉES ---
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.markdown(f"""<div class="kpi-card" style="border-left-color: {COLORS['ROUGE']};"><div class="kpi-label">Total AVEC rupture ({unite_affichage})</div><div class="kpi-value">{format_fr(total_avec)}</div><div class="kpi-delta" style="color: {COLORS['TEXTE_SECONDAIRE']};">Base : ventes réelles</div></div>""", unsafe_allow_html=True)
            with rc2:
                st.markdown(f"""<div class="kpi-card" style="border-left-color: {COLORS['VERT']};"><div class="kpi-label">Total SANS rupture ({unite_affichage})</div><div class="kpi-value">{format_fr(total_sans)}</div><div class="kpi-delta" style="color: {COLORS['TEXTE_SECONDAIRE']};">Base : volume potentiel</div></div>""", unsafe_allow_html=True)
            with rc3:
                ecart_color = COLORS['VERT'] if diff >= 0 else COLORS['ROUGE']
                st.markdown(f"""<div class="kpi-card" style="border-left-color: {ecart_color};"><div class="kpi-label">Manque à gagner (rupture)</div><div class="kpi-value" style="color: {ecart_color};">{format_fr(diff, signed=True)}</div><div class="kpi-delta" style="color: {ecart_color};">{format_fr(diff_pct, 1, signed=True)}% vs prévision avec rupture</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- FILTRES ET OPTIONS DU TABLEAU ---
            col_search_tab, col_view_mode = st.columns([2, 1])
            with col_search_tab:
                search_query = st.text_input("🔍 Rechercher un article ou une marque", "", placeholder="Ex: World Cola, FOSA...", key="search_recap")
            with col_view_mode:
                view_mode = st.radio("Vue", ["Compacte", "Complète"], horizontal=True, label_visibility="collapsed")

            mode_affichage = st.radio("Mode d'affichage", ["Récap Annuel par Article", "Détail Mensuel Côte-à-côte"], horizontal=True, label_visibility="collapsed", key="recap_mode_tab")

            df_meta = df_perimetre[['article', 'segment', 'marque']].drop_duplicates(subset=['article'])
            df_year = df_year.merge(df_meta, on='article', how='left')

            if mode_affichage == "Récap Annuel par Article":
                # Aggregations
                recap_df = df_year.groupby(['marque', 'article'], as_index=False).agg(
                    Realise=('hl_reel', 'sum'),
                    Prevision=(col_prev_pure, 'sum')
                )

                # Aggregate Rupture for the same period
                df_rupture_sum = df_perimetre[(df_perimetre['annee'] == annee_cible) & (df_perimetre['mois'].isin(mois_cibles_nums))]
                df_rupture_sum = df_rupture_sum.groupby('article', as_index=False)['rupture_hl'].sum()
                
                recap_df = recap_df.merge(df_rupture_sum, on='article', how='left').fillna({'rupture_hl': 0})

                # Calculations
                recap_df['Réalisé + Rupture'] = recap_df['Realise'] + recap_df['rupture_hl']
                recap_df['Écart PV'] = recap_df['Prevision'] - recap_df['Réalisé + Rupture']
                recap_df['% PV'] = np.where(recap_df['Prevision'] > 0, (recap_df['Réalisé + Rupture'] - recap_df['Prevision']) / recap_df['Prevision'] * 100, 0)

                # Rename for display
                recap_df = recap_df.rename(columns={
                    'marque': 'Marque',
                    'article': 'Article',
                    'Realise': 'Réalisé',
                    'Prevision': 'Prévision',
                    'rupture_hl': 'Rupture'
                })

                # Filter 0 rows
                recap_df = recap_df[(recap_df['Réalisé'] > 0) | (recap_df['Prévision'] > 0)]
                recap_df = recap_df.sort_values('Réalisé', ascending=False)

                # Apply search filter
                if search_query:
                    mask = recap_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                    recap_df = recap_df[mask]

                # Apply view mode columns
                if view_mode == "Compacte":
                    cols_to_keep = ['Marque', 'Article', 'Réalisé', 'Prévision', 'Écart PV', '% PV']
                    recap_df = recap_df[cols_to_keep]
                else:
                    cols_to_keep = ['Marque', 'Article', 'Réalisé', 'Prévision', 'Rupture', 'Réalisé + Rupture', 'Écart PV', '% PV']
                    recap_df = recap_df[cols_to_keep]

                # Add Total row
                recap_df = ajouter_total(recap_df, label_col="Marque", label="TOTAL", exclude_cols=["% PV"], custom_total_calc={
                    "% PV": lambda r: (r["Réalisé"] - r["Prévision"]) / r["Prévision"] * 100 if "Réalisé" in r and "Prévision" in r and r["Prévision"] > 0 else 0
                })

                # --- STYLE PROFESSIONNEL DU TABLEAU ---
                def style_dataframe(df):
                    def color_ecart(val):
                        if pd.isna(val): return ''
                        # Ecart PV = Prevision - Reel. Negatif = On a depasse la prev -> Vert. Positif = On a pas atteint -> Rouge.
                        if val > 0:
                            return f'background-color: {COLORS["ROUGE_CLAIR"]}; color: {COLORS["ROUGE"]}; font-weight: 700; border-left: 2px solid {COLORS["ROUGE"]};'
                        elif val < 0:
                            return f'background-color: {COLORS["VERT_CLAIR"]}; color: {COLORS["VERT"]}; font-weight: 700; border-left: 2px solid {COLORS["VERT"]};'
                        return ''

                    def color_pct(val):
                        if pd.isna(val): return ''
                        # % PV = Reel / Prevision. Positif = On a depasse -> Vert. Negatif = On a pas atteint -> Rouge.
                        if val >= 0:
                            return f'background-color: {COLORS["VERT_CLAIR"]}; color: {COLORS["VERT"]}; font-weight: 700;'
                        else:
                            return f'background-color: {COLORS["ROUGE_CLAIR"]}; color: {COLORS["ROUGE"]}; font-weight: 700;'

                    def color_rupture(val):
                        if pd.isna(val): return ''
                        if val > 0:
                            return f'color: {COLORS["ORANGE"]}; font-weight: 700;'
                        return ''

                    fmt_dict = {
                        'Réalisé': '{:,.0f}',
                        'Prévision': '{:,.0f}',
                        'Rupture': '{:,.0f}',
                        'Réalisé + Rupture': '{:,.0f}',
                        'Écart PV': '{:+,.0f}',
                        '% PV': '{:+.1f} %'
                    }

                    styled = df.style.format(fmt_dict)
                    if 'Écart PV' in df.columns:
                        styled = styled.map(color_ecart, subset=['Écart PV'])
                    if '% PV' in df.columns:
                        styled = styled.map(color_pct, subset=['% PV'])
                    if 'Rupture' in df.columns:
                        styled = styled.map(color_rupture, subset=['Rupture'])
                    
                    def highlight_total(row):
                        if row.name == len(df) - 1:
                            return [f'background-color: #F3F4F6; font-weight: 800; color: {COLORS["TEXTE"]}; border-top: 2px solid #9CA3AF;'] * len(row)
                        return [''] * len(row)
                    
                    styled = styled.apply(highlight_total, axis=1)
                    return styled

                with st.container(border=True):
                    st.markdown(f"#### 📊 Récap Annuel par Article")
                    st.caption("🟢 Vert = Objectif dépassé / 🔴 Rouge = Objectif manqué / 🟠 Orange = Rupture")
                    st.dataframe(style_dataframe(recap_df), use_container_width=True, hide_index=True, height=600)
            else:
                pivot_avec = df_year.pivot_table(index=['article', 'segment'], columns='mois', values=col_prev_aff, aggfunc='sum').fillna(0)
                pivot_avec = pivot_avec.reindex(columns=range(1, 13), fill_value=0)
                pivot_avec.columns = [MOIS_NOMS[int(c) - 1] for c in pivot_avec.columns]
                pivot_sans = df_year.pivot_table(index=['article', 'segment'], columns='mois', values=col_vol_sans, aggfunc='sum').fillna(0)
                pivot_sans = pivot_sans.reindex(columns=range(1, 13), fill_value=0)
                pivot_sans.columns = [MOIS_NOMS[int(c) - 1] for c in pivot_sans.columns]

                pivot_avec_reset = pivot_avec.reset_index().rename(columns={'article': 'Article', 'segment': 'Segment'})
                pivot_avec_reset = ajouter_total(pivot_avec_reset, label_col="Article")
                pivot_sans_reset = pivot_sans.reset_index().rename(columns={'article': 'Article', 'segment': 'Segment'})
                pivot_sans_reset = ajouter_total(pivot_sans_reset, label_col="Article")

                c_avec, c_sans = st.columns(2)
                with c_avec:
                    with st.container(border=True):
                        st.markdown(f"**🟥 AVEC rupture ({unite_affichage})**")
                        st.dataframe(bold_total_row(pivot_avec_reset), use_container_width=True, height=600, hide_index=True)
                with c_sans:
                    with st.container(border=True):
                        st.markdown(f"**🟩 SANS rupture ({unite_affichage})**")
                        st.dataframe(bold_total_row(pivot_sans_reset), use_container_width=True, height=600, hide_index=True)

    elif active_tab == "Pareto (ABC)":
        st.markdown("### Analyse Pareto & Classification ABC")
        st.markdown("La classification ABC est une méthode de gestion des stocks qui consiste à diviser les articles en trois classes en fonction de leur contribution au volume total :")
        st.markdown("- **Classe A (0-80.5%)** : Les articles vitaux (généralement 20% des articles qui font 80% des ventes).\n- **Classe B (80.5-95%)** : Les articles intermédiaires.\n- **Classe C (95-100%)** : Les articles à faible rotation (la longue traîne).")
        st.markdown("---")
        st.markdown("#### 🧩 Matrice ABC-XYZ")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            seuil_x_pct = st.number_input("Seuil X (Stable) - CV < (%)", min_value=1.0, max_value=100.0, value=25.0, step=1.0, key="param_seuil_x")
        with col_s2:
            seuil_y_pct = st.number_input("Seuil Y (Variable) - CV < (%)", min_value=seuil_x_pct, max_value=200.0, value=50.0, step=1.0, key="param_seuil_y")
        st.markdown(f"La classification **XYZ** est basée sur la volatilité des ventes (Coefficient de Variation = Écart-type / Moyenne) :\n- **X** : Faible volatilité (CV < {format_fr(seuil_x_pct, 0)}%) - Ventes régulières\n- **Y** : Volatilité moyenne ({format_fr(seuil_x_pct, 0)}% <= CV < {format_fr(seuil_y_pct, 0)}%)\n- **Z** : Forte volatilité (CV >= {format_fr(seuil_y_pct, 0)}%) - Ventes irrégulières")
        df_pareto = df_previsions_filtre.groupby('article', observed=True)[col_prev_aff].sum().sort_values(ascending=False).reset_index()
        df_pareto = df_pareto[df_pareto[col_prev_aff] > 0]
        if not df_pareto.empty:
            total_vol = df_pareto[col_prev_aff].sum()
            df_pareto['Cumul_Pct'] = (df_pareto[col_prev_aff].cumsum() / total_vol) * 100
            df_pareto['Classe'] = np.select([df_pareto['Cumul_Pct'] <= 80.5, df_pareto['Cumul_Pct'] <= 95], ['A', 'B'], default='C')
            pivot_vol = df_previsions_filtre.pivot_table(index='article', columns='mois', values=col_prev_aff, aggfunc='sum').fillna(0)
            if not pivot_vol.empty:
                df_xyz = pd.DataFrame({'Mean': pivot_vol.mean(axis=1), 'Std': pivot_vol.std(axis=1)}).reset_index()
                df_xyz['CV'] = df_xyz['Std'] / df_xyz['Mean']
                df_xyz['CV'] = df_xyz['CV'].replace([np.inf, -np.inf], np.nan).fillna(0)
                seuil_x_dec = seuil_x_pct / 100.0
                seuil_y_dec = seuil_y_pct / 100.0
                df_xyz['XYZ'] = np.select([df_xyz['CV'] < seuil_x_dec, df_xyz['CV'] < seuil_y_dec], ['X', 'Y'], default='Z')
                df_pareto_xyz = df_pareto.merge(df_xyz[['article', 'XYZ']], on='article', how='left')
                df_pareto_xyz['XYZ'] = df_pareto_xyz['XYZ'].fillna('Z')
                df_matrix = pd.crosstab(df_pareto_xyz['Classe'], df_pareto_xyz['XYZ'], margins=True, margins_name='Total')
                df_matrix = df_matrix.reindex(index=['A', 'B', 'C', 'Total'], columns=['X', 'Y', 'Z', 'Total'], fill_value=0)
                st.dataframe(df_matrix, use_container_width=True)
            else: st.info("Pas assez de données pour calculer la matrice XYZ.")
            st.markdown("---")
            df_pareto_graph = df_pareto.head(15).copy()
            df_pareto_graph['Index'] = range(len(df_pareto_graph))
            df_pareto_graph['Article_Court'] = df_pareto_graph['article'].apply(lambda x: x if len(str(x)) <= 22 else str(x)[:19] + '...')
            fig2 = go.Figure()
            couleurs = {'A': COLORS['ROUGE'], 'B': '#F59E0B', 'C': '#9CA3AF'}
            for classe in ['A', 'B', 'C']:
                df_class = df_pareto_graph[df_pareto_graph['Classe'] == classe]
                if not df_class.empty:
                    fig2.add_trace(go.Bar(x=df_class['Index'], y=df_class[col_prev_aff], name=f'Classe {classe}', marker_color=couleurs[classe], customdata=df_class['article'], hovertemplate="<b>%{customdata}</b><br>Volume: %{y:,.0f}<extra></extra>"))
            fig2.add_trace(go.Scatter(x=df_pareto_graph['Index'], y=df_pareto_graph['Cumul_Pct'], name='% Cumulé', mode='lines+markers', line=dict(color=COLORS['TEXTE'], width=2), marker=dict(size=6, color=COLORS['TEXTE']), yaxis='y2', customdata=df_pareto_graph['article'], hovertemplate="<b>%{customdata}</b><br>% Cumulé: %{y:.1f}%<extra></extra>"))
            for seuil, color in [(80.5, COLORS['ROUGE']), (95, '#F59E0B')]:
                fig2.add_shape(type="line", x0=-0.5, x1=len(df_pareto_graph)-0.5, y0=seuil, y1=seuil, line=dict(color=color, width=1.5, dash="dot"), xref='x', yref='y2')
            fig2.update_layout(separators=" ,", plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=0, r=0, t=20, b=60), yaxis=dict(title=f"Volume ({unite_affichage})", showgrid=True, gridcolor=COLORS['BORDURE'], tickfont=dict(family="Inter", size=12, weight="bold")), yaxis2=dict(title="% Cumulé", overlaying='y', side='right', range=[0, 110], tickvals=[0, 20, 40, 60, 80, 100], showgrid=False, ticksuffix="%", tickfont=dict(family="Inter", size=12, weight="bold")), xaxis=dict(tickmode='array', tickvals=df_pareto_graph['Index'], ticktext=df_pareto_graph['Article_Court'], tickangle=-45, showgrid=False, tickfont=dict(size=11, family="Inter", weight="bold")), legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5), height=450, bargap=0.3, hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            with st.expander("📋 Voir le détail par article", expanded=True):
                df_table = df_pareto_xyz[['article', 'Classe', 'XYZ', col_prev_aff, 'Cumul_Pct']].copy()
                df_table.columns = ['Article', 'Classe ABC', 'Classe XYZ', f'Volume ({unite_affichage})', '% Cumulé']
                df_table = ajouter_total(df_table, label_col="Article", exclude_cols=["% Cumulé"], custom_total_calc={"% Cumulé": lambda r: 100.0})
                small_kpi("TOTAL Volume", format_fr(df_table[f'Volume ({unite_affichage})'].iloc[-1]))
                st.dataframe(bold_total_row(df_table), use_container_width=True, hide_index=True, column_config={f'Volume ({unite_affichage})': st.column_config.NumberColumn(format="localized"), '% Cumulé': st.column_config.NumberColumn(format="%.1f %%"), 'Classe ABC': st.column_config.TextColumn(width="small"), 'Classe XYZ': st.column_config.TextColumn(width="small")}, height=400)
        else: st.info("Pas assez de données pour l'analyse.")

    elif active_tab == "Analyse Comportementale":
        st.markdown("### 🧠 Analyse Comportementale par SKU")
        st.markdown("Cette section analyse le comportement de chaque article (croissance, saisonnalité, momentum) et génère un diagnostic automatique.")
        st.markdown("<br>", unsafe_allow_html=True)
        df_analyse = analyser_comportement_sku(df_sarr, df_perimetre)
        if df_analyse.empty:
            st.info("Pas assez de données pour l'analyse comportementale (minimum 6 mois d'historique par SKU).")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtre_profil = st.multiselect("Filtrer par profil", options=sorted(df_analyse['Profil'].unique()), default=[], placeholder="Tous les profils")
            with col_f2:
                search_sku = st.text_input("Rechercher un SKU", "", placeholder="Nom de l'article ou agence...")
            df_display = df_analyse.copy()
            if filtre_profil: df_display = df_display[df_display['Profil'].isin(filtre_profil)]
            if search_sku:
                mask = df_display['Article'].str.contains(search_sku, case=False, na=False) | df_display['Agence'].str.contains(search_sku, case=False, na=False)
                df_display = df_display[mask]
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                nb_star = (df_analyse['Profil'].str.contains("Star")).sum()
                st.markdown(f"""<div class="kpi-card"><div class="kpi-label">🌟 SKU Stars</div><div class="kpi-value">{format_fr(nb_star)}</div><div class="kpi-delta up">Priorité réappro</div></div>""", unsafe_allow_html=True)
            with k2:
                nb_declin = (df_analyse['Profil'].str.contains("déclin")).sum()
                st.markdown(f"""<div class="kpi-card" style="border-left-color: {COLORS['ROUGE']};"><div class="kpi-label">📉 SKU En Déclin</div><div class="kpi-value" style="color: {COLORS['ROUGE']};">{format_fr(nb_declin)}</div><div class="kpi-delta down">À arbitrer</div></div>""", unsafe_allow_html=True)
            with k3:
                nb_saison = (df_analyse['Profil'].str.contains("Saisonnier")).sum()
                st.markdown(f"""<div class="kpi-card" style="border-left-color: #F59E0B;"><div class="kpi-label">🏔️ SKU Saisonniers</div><div class="kpi-value" style="color: #F59E0B;">{format_fr(nb_saison)}</div><div class="kpi-delta">Stock anticipé</div></div>""", unsafe_allow_html=True)
            with k4:
                nb_total = len(df_analyse)
                st.markdown(f"""<div class="kpi-card" style="border-left-color: {COLORS['TEXTE']};"><div class="kpi-label">📊 SKU Analysés</div><div class="kpi-value">{format_fr(nb_total)}</div><div class="kpi-delta" style="color: {COLORS['TEXTE_SECONDAIRE']};">Total</div></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(f"📋 Diagnostic détaillé ({format_fr(len(df_display))} SKU)", expanded=True):
                for _, row in df_display.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            st.markdown(f"**{row['Article']}**")
                            st.caption(f"_{row['Agence']}_")
                            st.markdown(f"### {row['Profil']}")
                        with c2:
                            st.markdown(row['Commentaire'])
                            st.info(f"**Recommandation :** {row['Recommandation']}")
                            mc1, mc2, mc3, mc4 = st.columns(4)
                            mc1.metric("SARR moyen", f"{format_fr(row['SARR moyen (HL/mois)'])} HL")
                            mc2.metric("Momentum", f"{format_fr(row['Momentum (HL)'], signed=True)} HL")
                            mc3.metric("CAGR", f"{format_fr(row['CAGR (%)'], 1, signed=True)}%")
                            mc4.metric("Pic", row['Mois Pic'])

    elif active_tab == "Fiabilité":
        st.markdown("### Qualité et Fiabilité du Modèle")
        st.markdown("Cette section évalue la précision de l'algorithme sur les mois déjà réalisés (période de cutoff). Elle permet de savoir si l'on peut faire confiance aux prévisions futures.")
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"""<div class="white-card" style="border-top: 4px solid {COLORS['TEXTE_SECONDAIRE']};"><div class="kpi-label">MAE (Erreur Absolue Moyenne)</div><div class="kpi-value kpi-value-dark" style="font-size: 1.8rem;">{format_fr(mae, 2)}</div><div class="kpi-footer">Marge d'erreur moyenne en {unite_affichage}</div></div>""", unsafe_allow_html=True)
        with m2: st.markdown(f"""<div class="white-card" style="border-top: 4px solid {COLORS['TEXTE_SECONDAIRE']};"><div class="kpi-label">WMAPE (Erreur % Pondérée)</div><div class="kpi-value kpi-value-dark" style="font-size: 1.8rem;">{format_fr(wmape, 2)}%</div><div class="kpi-footer">Précision sur le volume total (Standard industrie)</div></div>""", unsafe_allow_html=True)
        with m3: st.markdown(f"""<div class="white-card" style="border-top: 4px solid {COLORS['TEXTE_SECONDAIRE']};"><div class="kpi-label">SMAPE (Erreur % Symétrique)</div><div class="kpi-value kpi-value-dark" style="font-size: 1.8rem;">{format_fr(smape, 2)}%</div><div class="kpi-footer">Précision sur les articles à faibles volumes</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📊 Afficher le détail mensuel (Prévision vs Réalisé)", expanded=True):
            st.markdown("Ce tableau compare ce que le modèle prévoyait pour chaque mois écoulé par rapport à ce qui a réellement été vendu. Les cellules rouges indiquent une erreur critique (>10%).")
            if not df_eval_agg.empty:
                df_error_monthly = df_eval_agg.copy()
                df_error_monthly['Ecart'] = df_error_monthly[col_prev_aff] - df_error_monthly[col_prev_pure]
                df_error_monthly['Erreur_Absolue'] = df_error_monthly['Ecart'].abs()
                df_error_monthly['Erreur_Pct (%)'] = np.where(df_error_monthly[col_prev_aff] > 0, (df_error_monthly['Erreur_Absolue'] / df_error_monthly[col_prev_aff]) * 100, 0)
                df_error_monthly['Mois_Label'] = df_error_monthly['mois'].apply(lambda m: MOIS_NOMS[int(m)-1])
                df_error_monthly = df_error_monthly[['annee', 'Mois_Label', col_prev_aff, col_prev_pure, 'Ecart', 'Erreur_Pct (%)']]
                df_error_monthly.columns = ['Année', 'Mois', f'Réalisé ({unite_affichage})', f'Prévision ({unite_affichage})', 'Écart', 'Erreur (%)']
                def calc_err_pct(r):
                    if r.get(f'Réalisé ({unite_affichage})', 0) > 0:
                        return (abs(r.get('Écart', 0)) / r[f'Réalisé ({unite_affichage})']) * 100
                    return np.nan
                df_error_monthly = ajouter_total(df_error_monthly, label_col="Année", exclude_cols=["Erreur (%)"], custom_total_calc={"Erreur (%)": calc_err_pct})
                styled_error_df = df_error_monthly.style.map(color_error, subset=['Erreur (%)']).apply(lambda x: ['font-weight: bold; background-color: #F9FAFB;'] * len(x) if x.name == len(df_error_monthly)-1 else [''] * len(x), axis=1)
                st.dataframe(styled_error_df, use_container_width=True, hide_index=True, column_config={f'Réalisé ({unite_affichage})': st.column_config.NumberColumn(format="localized"), f'Prévision ({unite_affichage})': st.column_config.NumberColumn(format="localized"), 'Écart': st.column_config.NumberColumn(format="localized"), 'Erreur (%)': st.column_config.NumberColumn(format="%.2f %%")})
            else: st.info("Aucune donnée réalisée à évaluer pour le moment (le mois de cutoff n'est peut-être pas encore passé).")

    elif active_tab == "Ruptures":
        st.markdown("### Analyse de Rupture de Tendance")
        st.markdown("Cette section affiche les volumes perdus à cause des ruptures de stock, par SKU et par mois.")
        st.markdown("<br>", unsafe_allow_html=True)
        df_rupture_hist = df_perimetre[df_perimetre['rupture_hl'] > 0].copy()
        if not df_rupture_hist.empty:
            kr1, kr2, kr3 = st.columns(3)
            with kr1:
                vol_perdu_total = df_rupture_hist['rupture_hl'].sum()
                st.markdown(f"""<div class="white-card" style="border-top: 4px solid #F59E0B;"><div class="kpi-label">Volume Total Perdu</div><div class="kpi-value kpi-value-dark">{format_fr(vol_perdu_total)} HL</div><div class="kpi-footer">Sur le périmètre filtré</div></div>""", unsafe_allow_html=True)
            with kr2:
                nb_mois_ruptures = df_rupture_hist.groupby(['annee', 'mois']).ngroups
                st.markdown(f"""<div class="white-card" style="border-top: 4px solid #F59E0B;"><div class="kpi-label">Mois impactés</div><div class="kpi-value kpi-value-dark">{format_fr(nb_mois_ruptures)}</div><div class="kpi-footer">Nombre de mois avec au moins une rupture</div></div>""", unsafe_allow_html=True)
            with kr3:
                nb_sku_impactes = df_rupture_hist['article'].nunique()
                st.markdown(f"""<div class="white-card" style="border-top: 4px solid #F59E0B;"><div class="kpi-label">SKU Impactés</div><div class="kpi-value kpi-value-dark">{format_fr(nb_sku_impactes)}</div><div class="kpi-footer">Nombre d'articles différents</div></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Top 15 des SKU les plus impactés")
                df_rupture_sku = df_rupture_hist.groupby('article', observed=True)['rupture_hl'].sum().reset_index()
                df_rupture_sku = df_rupture_sku.sort_values(by='rupture_hl', ascending=True).tail(15)
                fig_sku = go.Figure(go.Bar(x=df_rupture_sku['rupture_hl'], y=df_rupture_sku['article'], orientation='h', marker_color='#F59E0B', text=df_rupture_sku['rupture_hl'].apply(lambda x: format_fr(x)), textposition='auto', hovertemplate="<b>%{y}</b><br>Perte: %{x:,.1f} HL<extra></extra>"))
                fig_sku.update_layout(separators=" ,", plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=10, r=10, t=30, b=10), xaxis=dict(title="Volume Perdu (HL)", showgrid=True, gridcolor=COLORS['BORDURE']), yaxis=dict(showgrid=False, tickfont=dict(size=11)), height=450)
                st.plotly_chart(fig_sku, use_container_width=True, config={'displayModeBar': False})
            with col_chart2:
                st.markdown("#### Évolution mensuelle des pertes (Top 5 SKU)")
                top_5_skus = df_rupture_sku.tail(5)['article'].tolist()
                df_top = df_rupture_hist[df_rupture_hist['article'].isin(top_5_skus)].copy()
                df_top['Date_Str'] = df_top['annee'].astype(str) + '-' + df_top['mois'].astype(str).str.zfill(2) + '-01'
                df_top['Date_Plot'] = pd.to_datetime(df_top['Date_Str'])
                df_top_agg = df_top.groupby(['Date_Plot', 'article'], observed=True)['rupture_hl'].sum().reset_index()
                fig_trend = go.Figure()
                palette = [COLORS['ROUGE'], '#F59E0B', COLORS['TEXTE'], COLORS['VERT'], COLORS['GRIS']]
                for i, sku in enumerate(top_5_skus):
                    df_sku = df_top_agg[df_top_agg['article'] == sku].sort_values('Date_Plot')
                    fig_trend.add_trace(go.Scatter(x=df_sku['Date_Plot'], y=df_sku['rupture_hl'], mode='lines+markers', name=str(sku)[:25], line=dict(color=palette[i % len(palette)], width=2.5), marker=dict(size=7), hovertemplate="<b>%{fullData.name}</b><br>%{x|%b-%y}: %{y:,.1f} HL<extra></extra>"))
                fig_trend.update_layout(separators=" ,", plot_bgcolor=COLORS['BLANC'], paper_bgcolor=COLORS['BLANC'], margin=dict(l=10, r=10, t=30, b=10), xaxis=dict(showgrid=True, gridcolor=COLORS['BORDURE'], tickformat="%b-%y", tickangle=-45), yaxis=dict(title="Volume perdu (HL)", showgrid=True, gridcolor=COLORS['BORDURE']), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5, font=dict(size=11)), height=450, hovermode="x unified")
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 Tableau détaillé des ruptures", expanded=False):
                df_rupture_detail = df_rupture_hist.groupby(['annee', 'mois', 'agence', 'article'], observed=True)['rupture_hl'].sum().reset_index()
                df_rupture_detail['Mois_Label'] = df_rupture_detail['mois'].apply(lambda m: MOIS_NOMS[int(m)-1])
                df_rupture_detail = df_rupture_detail[['annee', 'Mois_Label', 'agence', 'article', 'rupture_hl']]
                df_rupture_detail.columns = ['Année', 'Mois', 'Agence', 'Article', 'Volume Perdu (HL)']
                df_rupture_detail = df_rupture_detail.sort_values('Volume Perdu (HL)', ascending=False)
                df_rupture_detail = ajouter_total(df_rupture_detail, label_col="Année")
                small_kpi("TOTAL Volume Perdu", format_fr(df_rupture_detail['Volume Perdu (HL)'].iloc[-1]))
                st.dataframe(bold_total_row(df_rupture_detail.head(N_MAX_DISPLAY)), use_container_width=True, hide_index=True, column_config={'Volume Perdu (HL)': st.column_config.NumberColumn(format="%.2f")})
        else:
            st.info("Aucune rupture enregistrée sur le périmètre sélectionné.")
