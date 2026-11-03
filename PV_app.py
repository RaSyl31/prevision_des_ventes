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

# ==============================================================================
# CONFIGURATION ET DESIGN
# ==============================================================================
st.set_page_config(page_title="PREVISIONS STAR MADAGASCAR", layout="wide", page_icon="⭐")

LOGO_PATH = Path(__file__).parent / "LOGO_STAR.png"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8F9FA !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 4px solid #E30613; }
    [data-testid="stHorizontalBlock"] { gap: 1rem; border: none !important; }
    [data-testid="column"] { border: none !important; box-shadow: none !important; }
    h1 { color: #E30613 !important; font-weight: 900 !important; margin-bottom: 0 !important; }
    h2, h3 { color: #009640 !important; font-weight: 700 !important; }
    .kpi-card {
        background-color: #FFFFFF; border-radius: 8px; padding: 20px;
        border: 1px solid #E5E7EB; border-left: 6px solid #E30613; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        display: flex; flex-direction: column; justify-content: space-between; height: 130px;
    }
    .kpi-header { display: flex; justify-content: space-between; align-items: center; color: #4B5563; font-size: 1rem; font-weight: 600; }
    .kpi-icon { font-size: 1.5rem; }
    .kpi-value { font-size: 2.4rem; font-weight: 800; color: #111827; margin-top: 5px; }
    .kpi-footer { font-size: 0.9rem; color: #6B7280; font-weight: 500;}
    .stTabs [data-baseweb="tab-list"] { gap: 15px; flex-wrap: wrap; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 45px; background-color: #F9FAFB; color: #4B5563;
        border-radius: 8px; padding: 10px 20px; font-weight: 600; border: 1px solid #E5E7EB;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E30613 !important; color: #FFFFFF !important;
        border: 1px solid #E30613 !important;
    }
    div[data-testid="stDataFrame"] { 
        background-color: #FFFFFF; padding: 15px; border-radius: 8px; 
        border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
    }
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF; padding: 15px; border-radius: 8px;
        border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# En-tête
col_logo, col_titre = st.columns([1.5, 5], gap="small", vertical_alignment="center")
with col_logo:
    if LOGO_PATH.exists(): st.image(str(LOGO_PATH), use_container_width=True)
with col_titre:
    st.markdown("""
        <div style='text-align: left;'>
            <h1 style='font-size: 2.6rem;'>PREVISIONS STAR MADAGASCAR</h1>
            <p style='color: #4B5563; font-size: 1.1rem; font-weight: 500; margin-top: 5px;'>
                Moteur de prévision S&OP complet (Étapes 1 à 5)
            </p>
        </div>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# RÉFÉRENTIEL ET MAPPING
# ==============================================================================
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

MAPPING_REGIONS = {
    "11-Andranomahery": "Centre", "12-Antsirabe": "Centre", "01-Tanjombato": "Est", "09-Tamatave": "Est",
    "03-Usine-Diego": "Nord", "07-Majunga": "Nord", "18-Ambanja": "Nord", "19-Sambava": "Nord", "21-Nosy-Be": "Nord",
    "04-Tulear": "Sud", "05-Fianarantsoa": "Sud", "06-Ihosy": "Sud", "08-Manakara": "Sud", "23-Morondava": "Sud", "24-Fort-Dauphin": "Sud"
}

MOIS_NOMS = ["Janv", "Févr", "Mars", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]

def normaliser_mois(serie: pd.Series) -> pd.Series:
    series_clean = serie.astype(str).str.strip()
    try:
        numeric_series = pd.to_numeric(series_clean, errors='coerce')
        if numeric_series.notna().all():
            dates = pd.to_datetime(numeric_series, unit='D', origin='1899-12-30', errors='coerce')
            if dates.notna().all():
                return dates.dt.month
    except: pass
    mois_map = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
    texte_series = series_clean.apply(lambda x: unicodedata.normalize("NFD", str(x)).encode("ascii", "ignore").decode("utf-8").lower())
    return texte_series.map(mois_map).fillna(1).astype(int)

def detecter_format_pivote(df: pd.DataFrame) -> bool:
    if df.shape[1] < 7: return False
    annee0 = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    if annee0.between(1990, 2100).sum() < len(df) * 0.3 and df.shape[1] >= 8:
        annee1 = pd.to_numeric(df.iloc[:, 1], errors="coerce")
        return annee1.between(1990, 2100).sum() > len(df) * 0.3
    return annee0.between(1990, 2100).sum() > len(df) * 0.3

@st.cache_data(show_spinner="Chargement et enrichissement des données...")
def charger_et_enrichir(ventes_bytes: bytes, ref_bytes: bytes = None) -> pd.DataFrame:
    if ref_bytes is not None:
        df_ref = pd.read_excel(io.BytesIO(ref_bytes), sheet_name="Ref actif")
        df_ref = df_ref.rename(columns={"Article": "article_original", "Positionnement": "positionnement", "Occasion": "occasion", "Contenance (Cl)": "contenance_cl"})
        df_ref = df_ref[["article_original", "positionnement", "occasion", "contenance_cl"]].copy()
    else:
        df_ref = pd.DataFrame(REF_DEFAUT).rename(columns={"Article": "article_original", "Contenance (Cl)": "contenance_cl", "Positionnement": "positionnement"})
        df_ref["occasion"] = "Non renseigné"
    
    df_ref["article_original"] = df_ref["article_original"].astype(str).str.strip()
    df_ref["cle_article"] = df_ref["article_original"].str.lower().str.replace(r'[^a-z0-9]', '', regex=True)
    df_ref = df_ref.drop_duplicates(subset=["cle_article"]).reset_index(drop=True)

    df_raw = pd.read_excel(io.BytesIO(ventes_bytes), sheet_name=0, header=None)
    if not detecter_format_pivote(df_raw): return pd.DataFrame()

    annee0 = pd.to_numeric(df_raw.iloc[:, 0], errors="coerce")
    if annee0.between(1990, 2100).sum() < len(df_raw) * 0.3 and df_raw.shape[1] >= 8:
        rename = {df_raw.columns[i]: col for i, col in enumerate(["annee", "mois", "segment", "produit", "agence", "nature", "volume_brut"], start=1)}
    else:
        rename = {df_raw.columns[i]: col for i, col in enumerate(["annee", "mois", "segment", "produit", "agence", "nature", "volume_brut"])}
        
    df = df_raw.rename(columns=rename).copy()
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    df["mois"] = normaliser_mois(df["mois"])
    df["volume_brut"] = pd.to_numeric(df["volume_brut"], errors="coerce").fillna(0.0)
    
    masque_total = df["segment"].astype(str).str.contains("total", case=False, na=False) | df["produit"].astype(str).str.contains("total", case=False, na=False) | df["agence"].astype(str).str.contains("total", case=False, na=False) | df["nature"].astype(str).str.contains("total", case=False, na=False) | df["nature"].isna()
    df = df[~masque_total].copy()
    
    df["article_original"] = df["nature"].astype(str).str.replace(r'^[^-]+-', '', regex=True).str.strip()
    df["agence"] = df["agence"].astype(str).str.strip()
    df["annee"] = df["annee"].fillna(2026).astype(int)
    df["cle_article"] = df["article_original"].str.lower().str.replace(r'[^a-z0-9]', '', regex=True)

    df_enrichi = pd.merge(df_ref, df, on="cle_article", how="outer")
    df_enrichi["article"] = df_enrichi["article_original_x"].fillna(df_enrichi["article_original_y"])
    df_enrichi["annee"] = df_enrichi["annee"].fillna(2026).astype(int)
    df_enrichi["volume_brut"] = df_enrichi["volume_brut"].fillna(0.0)
    df_enrichi["agence"] = df_enrichi["agence"].fillna("Aucune vente")
    
    df_enrichi["contenance_cl"] = pd.to_numeric(df_enrichi["contenance_cl"], errors="coerce").fillna(100.0)
    df_enrichi.loc[df_enrichi["contenance_cl"] <= 0, "contenance_cl"] = 100.0
    df_enrichi["hl"] = df_enrichi["volume_brut"]
    df_enrichi["region"] = df_enrichi["agence"].map(MAPPING_REGIONS).fillna("Autre")
    
    conditions = [df_enrichi["article"].str.contains(x, case=False, na=False) for x in ["booster|alcoomix", "caprice|tonic|world cola|d jino|youzou|coca|fanta|sprite", "beaufort|fresh|thb|gold|queen|skol|castel|libertalia", "cristal|cristalline|eau vive|eau", "xxl|fosa", "judor|jus", "vin", "negoce"]]
    choices = ["5-ALCOMIX", "2-BG", "1-BIERES", "4-EAUX", "3-ENERGY", "4-JUS", "7-VIN", "6-NEGOCE"]
    df_enrichi["segment"] = np.select(conditions, choices, default="AUTRE / INCONNU")
    
    return df_enrichi[["annee", "mois", "segment", "region", "produit", "agence", "hl", "volume_brut", "article", "positionnement", "occasion", "contenance_cl"]]

# ==============================================================================
# CALCULS (ÉTAPES 3 À 5)
# ==============================================================================
@st.cache_data(show_spinner="Calcul ultra-rapide des prévisions...")
def calculer_etape_5(df_perimetre: pd.DataFrame, annee_min_histo: int, annee_max_histo: int, annee_cloture: int, mois_cutoff: int, annee_cible: int):
    
    # On ne garde que les articles qui ont au moins une vente historique
    articles_avec_vente = df_perimetre.groupby('article')['hl'].sum()
    articles_avec_vente = articles_avec_vente[articles_avec_vente > 0].index
    df_perimetre_filtre = df_perimetre[df_perimetre['article'].isin(articles_avec_vente)].copy()
    
    if df_perimetre_filtre.empty:
        return None, None, None, None, df_perimetre

    df_limite = df_perimetre_filtre[(df_perimetre_filtre["annee"] < annee_cloture) | ((df_perimetre_filtre["annee"] == annee_cloture) & (df_perimetre_filtre["mois"] <= mois_cutoff))].copy()
    df_realise = df_limite[df_limite["annee"] <= annee_cloture].copy()
    if df_realise.empty: return None, None, None, None, df_perimetre_filtre

    df_hist = df_realise[(df_realise["annee"] >= annee_min_histo) & (df_realise["annee"] <= annee_max_histo)].copy()
    if df_hist.empty: return None, None, None, None, df_realise

    mois_par_annee = df_hist.groupby(['agence', 'article', 'annee'])['mois'].nunique().reset_index()
    df_hist_complet = df_hist.merge(mois_par_annee[mois_par_annee['mois'] == 12][['agence', 'article', 'annee']], on=['agence', 'article', 'annee'], how='inner')
    if df_hist_complet.empty: return None, None, None, None, df_realise

    vols = df_hist_complet.groupby(['agence', 'article', 'annee', 'mois'])['hl'].sum().unstack('mois').fillna(0.0).reindex(columns=range(1, 13), fill_value=0.0) 
    vols_mois_cumules = vols.groupby(['agence', 'article']).sum()
    vols_annuels_cumules = vols.sum(axis=1).groupby(['agence', 'article']).sum()
    indices = vols_mois_cumules.div(vols_annuels_cumules / 12.0, axis=0).replace([np.inf, -np.inf], np.nan).fillna(1.0)

    table_indices = indices.reset_index().melt(id_vars=['agence', 'article'], var_name='mois', value_name='Indice')
    table_indices['mois'] = table_indices['mois'].astype(int) 

    df_sarr = df_realise.merge(table_indices, on=['agence', 'article', 'mois'], how='left')
    df_sarr['Indice'] = df_sarr['Indice'].fillna(1.0)
    df_sarr['SARR_HL'] = df_sarr['hl'] / df_sarr['Indice'].replace(0, 1.0)

    df_sarr_sorted = df_sarr.sort_values(['agence', 'article', 'annee', 'mois']).copy()
    df_sarr_sorted['rang'] = df_sarr_sorted.groupby(['agence', 'article']).cumcount(ascending=False)
    df_derniers = df_sarr_sorted[df_sarr_sorted['rang'] < 4].copy()
    
    resultats_momentum = []
    for (ag, art), group in df_derniers.groupby(['agence', 'article']):
        def get_val(rang, col): return group[group['rang'] == rang][col].values[0] if len(group[group['rang'] == rang]) > 0 else 0
        sarr_m, sarr_m1, sarr_m2, sarr_m3 = get_val(0, 'SARR_HL'), get_val(1, 'SARR_HL'), get_val(2, 'SARR_HL'), get_val(3, 'SARR_HL')
        momentum = np.mean([sarr_m - sarr_m1, sarr_m1 - sarr_m2, sarr_m2 - sarr_m3])
        base = max(sarr_m, np.mean([sarr_m1, sarr_m2, sarr_m3]))
        info_art = group.iloc[0]
        resultats_momentum.append({"agence": ag, "article": art, "Base_HL": base, "Momentum_HL": momentum})
        
    df_momentum = pd.DataFrame(resultats_momentum)

    cagr_data = []
    if annee_cible > annee_cloture:
        for (ag, art), group in df_hist_complet.groupby(['agence', 'article']):
            a_deb, a_fin = group['annee'].min(), group['annee'].max()
            v_deb = group[group['annee'] == a_deb]['hl'].sum()
            v_fin = group[group['annee'] == a_fin]['hl'].sum()
            nb_ans = a_fin - a_deb
            cagr_val = ((v_fin / v_deb) ** (1 / nb_ans)) - 1 if nb_ans > 0 and v_deb > 0 and v_fin > 0 else 0.0
            cagr_data.append({"agence": ag, "article": art, "CAGR_val": cagr_val})
    df_cagr = pd.DataFrame(cagr_data) if cagr_data else pd.DataFrame(columns=['agence', 'article', 'CAGR_val'])

    df_perim_unique = df_perimetre_filtre[['agence', 'article', 'contenance_cl']].drop_duplicates(subset=['agence', 'article'])
    df_base = pd.merge(df_perim_unique, df_momentum, on=['agence', 'article'], how='left')
    df_base = pd.merge(df_base, df_cagr, on=['agence', 'article'], how='left')
    
    df_base['Base_HL'] = df_base['Base_HL'].fillna(0.0)
    df_base['Momentum_HL'] = df_base['Momentum_HL'].fillna(0.0)
    df_base['CAGR_val'] = df_base['CAGR_val'].fillna(0.0)
    
    annees_cibles = list(range(annee_cloture, annee_cible + 1))
    mois_cibles = list(range(1, 13))
    
    df_cross = df_base.assign(key=1).merge(pd.DataFrame({'annee': annees_cibles, 'key': 1}), on='key').drop('key', axis=1)
    df_cross = df_cross.assign(key=1).merge(pd.DataFrame({'mois': mois_cibles, 'key': 1}), on='key').drop('key', axis=1)
    
    df_cross = pd.merge(df_cross, table_indices, on=['agence', 'article', 'mois'], how='left')
    df_cross['Indice'] = df_cross['Indice'].fillna(1.0)
    
    df_realise_grouped = df_realise.groupby(['annee', 'mois', 'agence', 'article'])['hl'].sum().reset_index().rename(columns={'hl': 'hl_reel'})
    df_cross = pd.merge(df_cross, df_realise_grouped, on=['annee', 'mois', 'agence', 'article'], how='left')
    
    df_cross['is_realise'] = (df_cross['annee'] == annee_cloture) & (df_cross['mois'] <= mois_cutoff)
    df_cross['Statut'] = np.where(df_cross['is_realise'], "Réalisé", "Prévision")
    
    df_cross['multiplicateur_cagr'] = (1 + df_cross['CAGR_val']) ** (df_cross['annee'] - annee_cloture)
    df_cross['Prevision_HL'] = np.maximum(0.0, ((df_cross['Indice'].round(2) * df_cross['Base_HL'].round(2)) + df_cross['Momentum_HL'].round(2)) * df_cross['multiplicateur_cagr'])
    
    df_cross['Volume_HL'] = np.where(df_cross['is_realise'], df_cross['hl_reel'].fillna(0.0), df_cross['Prevision_HL'])
    df_cross['Volume_Cols'] = df_cross['Volume_HL'] * (10000 / df_cross['contenance_cl'])
    
    df_cross['CAGR (%)'] = df_cross['CAGR_val'] * 100
    df_cross['Date'] = df_cross['mois'].apply(lambda m: MOIS_NOMS[m-1]) + '-' + df_cross['annee'].astype(str).str[-2:]
    
    cols_finales = ["annee", "mois", "agence", "article", "Date", "Statut", "Indice", "Base_HL", "Momentum_HL", "CAGR (%)", "Volume_HL", "Volume_Cols"]
    
    return table_indices, df_sarr, df_momentum, df_cross[cols_finales].copy(), df_realise

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
with st.expander("📁 1. Importer vos fichiers (Données Brutes)", expanded=False):
    c1, c2 = st.columns(2)
    with c1: fichier_ventes = st.file_uploader("Fichier des ventes (DATA_BRUT.xlsx)", type=["xlsx"])
    with c2: fichier_ref = st.file_uploader("Fichier Référentiel (Optionnel)", type=["xlsx"])

if fichier_ventes is not None:
    df_enrichi = charger_et_enrichir(fichier_ventes.getvalue(), fichier_ref.getvalue() if fichier_ref is not None else None)

    with st.sidebar:
        st.markdown("<h2 style='font-size: 1.2rem;'>⚙️ Paramètres</h2>", unsafe_allow_html=True)
        st.markdown("##### 2. Périmètre (Filtres)")
        
        regions_dispo = sorted([r for r in df_enrichi["region"].unique() if pd.notna(r) and r != "Aucune vente"])
        sel_regions = st.multiselect("Région", options=regions_dispo, placeholder="Toutes")
        df_temp = df_enrichi[df_enrichi["region"].isin(sel_regions)] if sel_regions else df_enrichi

        positionnements_dispo = sorted([p for p in df_temp["positionnement"].unique() if pd.notna(p)])
        sel_positionnements = st.multiselect("Positionnement", options=positionnements_dispo, placeholder="Tous")
        df_temp = df_temp[df_temp["positionnement"].isin(sel_positionnements)] if sel_positionnements else df_temp

        contenances_dispo = sorted([int(c) for c in df_temp["contenance_cl"].unique() if pd.notna(c)])
        sel_contenances = st.multiselect("Contenance (cl)", options=contenances_dispo, placeholder="Toutes")
        df_temp = df_temp[df_temp["contenance_cl"].isin(sel_contenances)] if sel_contenances else df_temp

        segments_dispo = sorted([s for s in df_temp["segment"].unique() if pd.notna(s)])
        sel_segments = st.multiselect("Segment", options=segments_dispo, placeholder="Tous")
        df_temp = df_temp[df_temp["segment"].isin(sel_segments)] if sel_segments else df_temp

        articles_dispo = sorted(df_temp["article"].unique())
        sel_articles = st.multiselect("Article", options=articles_dispo, placeholder="Tous")
        df_temp = df_temp[df_temp["article"].isin(sel_articles)] if sel_articles else df_temp

        agences_dispo = sorted([a for a in df_temp["agence"].unique() if a != "Aucune vente"])
        sel_agences = st.multiselect("Agence", options=agences_dispo, placeholder="Toutes")

        st.markdown("##### 📅 Cutoff")
        annee_min_histo = st.number_input("Année Min Historique", min_value=2015, max_value=2030, value=2023)
        
        # CORRECTION ICI : value=max(2024, annee_min_histo) pour éviter l'erreur
        annee_max_histo = st.number_input("Année Max Historique", min_value=annee_min_histo, max_value=2030, value=max(2024, annee_min_histo))
        
        annee_cloture = st.number_input("Année de Clôture", min_value=2020, max_value=2030, value=2025)
        annee_cible = st.number_input("Année Cible", min_value=annee_cloture, max_value=2035, value=annee_cloture)
        mois_cutoff = st.selectbox("Mois de Cutoff", options=list(range(1, 13)), index=8, format_func=lambda m: f"{m} - {MOIS_NOMS[m-1]}")

        st.markdown("##### ⚙️ Affichage")
        unite_affichage = st.radio("Unité", options=["HL", "Cols"], index=1)

    df_perimetre = df_enrichi.copy()
    if sel_regions: df_perimetre = df_perimetre[df_perimetre["region"].isin(sel_regions)]
    if sel_positionnements: df_perimetre = df_perimetre[df_perimetre["positionnement"].isin(sel_positionnements)]
    if sel_contenances: df_perimetre = df_perimetre[df_perimetre["contenance_cl"].isin(sel_contenances)]
    if sel_segments: df_perimetre = df_perimetre[df_perimetre["segment"].isin(sel_segments)]
    if sel_articles: df_perimetre = df_perimetre[df_perimetre["article"].isin(sel_articles)]
    if sel_agences: df_perimetre = df_perimetre[df_perimetre["agence"].isin(sel_agences)]

    table_indices, df_sarr, df_momentum, df_previsions, df_realise = calculer_etape_5(
        df_perimetre, annee_min_histo, annee_max_histo, annee_cloture, mois_cutoff, annee_cible
    )

    if table_indices is None:
        st.warning("⚠️ Aucune année complète (12 mois) trouvée dans l'intervalle historique.")
        st.info("💡 Vérifiez que vous avez bien sélectionné 2 années consécutives complètes (ex: 2024 et 2025) et que votre fichier contient bien 12 mois par an.")
        st.stop()

    col_prev_aff = "Volume_Cols" if unite_affichage == "Cols" else "Volume_HL"

    df_cible = df_previsions[df_previsions['annee'] == annee_cible]
    atterrissage_cible = df_cible[col_prev_aff].sum()

    if annee_cible == annee_cloture:
        st.markdown(f"""<div class="kpi-card" style="width: 100%; border-left: 6px solid #009640;">
            <div class="kpi-header"><span>Atterrissage {annee_cible} (Réalisé + Prévisions)</span> <span class="kpi-icon">🎯</span></div>
            <div class="kpi-value">{atterrissage_cible:,.0f}</div>
            <div class="kpi-footer">{unite_affichage} (Projection finale)</div>
        </div>""", unsafe_allow_html=True)
    else:
        cagr_applique = df_previsions['CAGR (%)'].mean() if not df_previsions.empty else 0.0
        kpi1, kpi2 = st.columns(2)
        with kpi1:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-header"><span>Atterrissage {annee_cible}</span> <span class="kpi-icon">🎯</span></div><div class="kpi-value">{atterrissage_cible:,.0f}</div><div class="kpi-footer">{unite_affichage} (Réalisé + Prévisions)</div></div>""", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-header"><span>CAGR Appliqué</span> <span class="kpi-icon">📈</span></div><div class="kpi-value">{cagr_applique:,.2f}%</div><div class="kpi-footer">Croissance annuelle moyenne</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Données Brutes", "2. Périmètre", "3. Réalisé Cumulé", "4. Indices & SARR", "5. Prévisions (Dynamique)"
    ])

    with tab1:
        st.markdown("### Étape 1 : Données Brutes Enrichies (Ventes + Référentiel)")
        st.dataframe(df_enrichi, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Étape 2 : Périmètre Filtré")
        st.dataframe(df_perimetre, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### Étape 3 : Réalisé Cumulé (Jusqu'au Cutoff)")
        if df_realise is not None and not df_realise.empty:
            st.dataframe(df_realise.groupby(['annee', 'mois', 'region', 'agence', 'article'])[['hl']].sum().reset_index(), use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée réalisée pour le moment.")

    with tab4:
        st.markdown("### Étape 4 : Indices de Saisonnalité & SARR")
        c_idx, c_sarr = st.columns(2)
        with c_idx:
            st.markdown("**Indices de Saisonnalité**")
            pivot_indices = table_indices.pivot_table(index=['agence', 'article'], columns='mois', values='Indice', aggfunc='first').fillna(1.0)
            pivot_indices.columns = [MOIS_NOMS[c-1] for c in pivot_indices.columns]
            st.dataframe(pivot_indices, use_container_width=True)
        with c_sarr:
            st.markdown("**Table SARR**")
            df_sarr["SARR_Aff"] = df_sarr["SARR_HL"] * (10000 / df_sarr["contenance_cl"].replace(0, 100)) if unite_affichage == "Cols" else df_sarr["SARR_HL"]
            st.dataframe(df_sarr[["annee", "mois", "agence", "article", "SARR_Aff"]].sort_values(["annee", "mois"]), use_container_width=True, hide_index=True)

    with tab5:
        st.markdown("### Étape 5 : Dynamique (Momentum & Prévisions Finales)")
        
        mode_affichage = st.radio("Choisir le mode d'affichage :", ["📊 Tableau", "📈 Graphiques Data Analyst"], horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if mode_affichage == "📊 Tableau":
            with st.expander("5.1 Table du Momentum et de la Base"):
                st.dataframe(
                    df_momentum,
                    column_config={
                        "Base_HL": st.column_config.NumberColumn("Base (HL)", format="%.2f"),
                        "Momentum_HL": st.column_config.NumberColumn("Momentum (HL)", format="%.2f"),
                    },
                    use_container_width=True, hide_index=True
                )
                
            st.markdown("#### 5.2 Résultat Final")
            
            pivot_mensuel = df_previsions.pivot_table(
                index=['annee', 'agence', 'article'], columns='mois', values=col_prev_aff, aggfunc='sum'
            ).fillna(0)
            pivot_mensuel.columns = [MOIS_NOMS[c-1] for c in pivot_mensuel.columns]
            pivot_mensuel['Total Année'] = pivot_mensuel.sum(axis=1)
            
            pivot_mensuel = pivot_mensuel[pivot_mensuel.sum(axis=1) > 0]
            
            st.dataframe(pivot_mensuel, use_container_width=True)
            
            with st.expander("Voir le détail des calculs (Coef, Base, Momentum)"):
                cols_to_show = ["annee", "mois", "Statut", "agence", "article", "Indice", "Base_HL", "Momentum_HL", col_prev_aff]
                
                if annee_cible > annee_cloture:
                    cols_to_show.insert(-1, "CAGR (%)")
                    
                st.dataframe(
                    df_previsions[cols_to_show].sort_values(["annee", "mois", "agence", "article"]),
                    column_config={
                        "Indice": st.column_config.NumberColumn("Coef", format="%.2f"),
                        "Base_HL": st.column_config.NumberColumn("Base (HL)", format="%.2f"),
                        "Momentum_HL": st.column_config.NumberColumn("Momentum (HL)", format="%.2f"),
                        "CAGR (%)": st.column_config.NumberColumn("CAGR (%)", format="%.2f"),
                        col_prev_aff: st.column_config.NumberColumn(f"Volume ({unite_affichage})", format="%.2f"),
                    },
                    use_container_width=True, hide_index=True, height=400
                )

        else:
            st.markdown("#### 📊 Analyse Visuelle des Prévisions")
            
            st.markdown("##### 🔬 Validation du Modèle (Backtest)")
            st.info("Le Backtest permet de voir ce que le modèle aurait prédit pour l'année cible s'il n'avait eu que les données des années précédentes. Il compare cette prédiction à la réalité.")
            
            afficher_backtest = st.checkbox(f"Afficher les prévisions pour {annee_cible} calculées uniquement avec l'historique jusqu'à {annee_cible - 1}")

            if afficher_backtest:
                if annee_cible <= annee_min_histo:
                    st.warning("⚠️ Pas assez d'historique pour faire un backtest sur cette année.")
                else:
                    res_backtest = calculer_etape_5(
                        df_perimetre, annee_min_histo, annee_cible - 1, annee_cible - 1, 12, annee_cible
                    )
                    
                    if res_backtest[3] is not None:
                        df_prev_backtest = res_backtest[3]
                        df_prev_backtest = df_prev_backtest[df_prev_backtest['annee'] == annee_cible]

                        df_real_raw = df_perimetre[df_perimetre['annee'] == annee_cible].copy()
                        if not df_real_raw.empty:
                            if unite_affichage == "Cols":
                                df_real_raw['Vol_Aff'] = df_real_raw['hl'] * (10000 / df_real_raw['contenance_cl'].replace(0, 100))
                            else:
                                df_real_raw['Vol_Aff'] = df_real_raw['hl']
                            df_real_cible = df_real_raw.groupby('mois')['Vol_Aff'].sum().reset_index()
                            df_real_cible = df_real_cible.rename(columns={'Vol_Aff': col_prev_aff})
                        else:
                            df_real_cible = pd.DataFrame(columns=['mois', col_prev_aff])

                        df_real_cible['Date_Str'] = str(annee_cible) + '-' + df_real_cible['mois'].astype(str).str.zfill(2) + '-01'
                        df_real_cible['Date'] = pd.to_datetime(df_real_cible['Date_Str'])

                        df_pred_cible = df_prev_backtest.groupby('mois')[col_prev_aff].sum().reset_index()
                        df_pred_cible['Date_Str'] = str(annee_cible) + '-' + df_pred_cible['mois'].astype(str).str.zfill(2) + '-01'
                        df_pred_cible['Date'] = pd.to_datetime(df_pred_cible['Date_Str'])

                        df_real_cible = df_real_cible[df_real_cible[col_prev_aff] > 0]
                        df_pred_cible = df_pred_cible[df_pred_cible[col_prev_aff] > 0]

                        fig_bt = go.Figure()
                        
                        if not df_real_cible.empty:
                            fig_bt.add_trace(go.Scatter(
                                x=df_real_cible['Date'], y=df_real_cible[col_prev_aff], 
                                mode='lines+markers', name='Réalisé (Réel)', 
                                line=dict(color='#009640', width=3, shape='spline'),
                                fill='tozeroy', fillcolor='rgba(0, 150, 64, 0.1)'
                            ))
                        if not df_pred_cible.empty:
                            fig_bt.add_trace(go.Scatter(
                                x=df_pred_cible['Date'], y=df_pred_cible[col_prev_aff], 
                                mode='lines+markers', name='Prévision (Backtest)', 
                                line=dict(color='#E30613', width=3, dash='dot', shape='spline'),
                                fill='tozeroy', fillcolor='rgba(227, 6, 19, 0.05)'
                            ))

                        fig_bt.update_layout(
                            title=dict(text=f"Backtest {annee_cible} : Réalisé vs Modèle (entraîné jusqu'en {annee_cible-1})", font=dict(size=18, color="#111827")),
                            xaxis_title="Mois",
                            yaxis_title=f"Volume ({unite_affichage})",
                            hovermode="x unified",
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            margin=dict(l=40, r=40, t=60, b=40),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        fig_bt.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB', dtick="M1", tickformat="%b-%y")
                        fig_bt.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB')
                        
                        st.plotly_chart(fig_bt, use_container_width=True)

            st.markdown("---")
            
            st.markdown("##### 📈 Évolution Globale des Volumes (Réalisé vs Prévisions)")
            
            df_graph = df_previsions.copy()
            df_graph['Date_Str'] = df_graph['annee'].astype(str) + '-' + df_graph['mois'].astype(str).str.zfill(2) + '-01'
            df_graph['Date'] = pd.to_datetime(df_graph['Date_Str'])
            
            df_grouped = df_graph.groupby(['Date', 'Statut'])[col_prev_aff].sum().reset_index()

            df_real = df_grouped[df_grouped['Statut'] == 'Réalisé']
            df_prev = df_grouped[df_grouped['Statut'] == 'Prévision']

            df_real = df_real[df_real[col_prev_aff] > 0]
            df_prev = df_prev[df_prev[col_prev_aff] > 0]

            fig1 = go.Figure()
            
            if not df_real.empty:
                fig1.add_trace(go.Scatter(
                    x=df_real['Date'], y=df_real[col_prev_aff], 
                    mode='lines+markers', name='Réalisé', 
                    line=dict(color='#009640', width=3, shape='spline'),
                    fill='tozeroy', fillcolor='rgba(0, 150, 64, 0.1)'
                ))
            if not df_prev.empty:
                fig1.add_trace(go.Scatter(
                    x=df_prev['Date'], y=df_prev[col_prev_aff], 
                    mode='lines+markers', name='Prévision', 
                    line=dict(color='#E30613', width=3, dash='dash', shape='spline'),
                    fill='tozeroy', fillcolor='rgba(227, 6, 19, 0.05)'
                ))

            fig1.update_layout(
                title=dict(text=f"Évolution Globale (Cible: {annee_cible})", font=dict(size=18, color="#111827")),
                xaxis_title="Mois",
                yaxis_title=f"Volume ({unite_affichage})",
                hovermode="x unified",
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=40, r=40, t=60, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB', dtick="M1", tickformat="%b-%y")
            fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB')
            
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 🔍 Analyse de la Saisonnalité et des Produits")

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                df_saison = table_indices.groupby('mois')['Indice'].mean().reset_index()
                df_saison['Mois_Nom'] = df_saison['mois'].apply(lambda m: MOIS_NOMS[m-1])
                
                colors = ['#009640' if val < 1 else '#E30613' for val in df_saison['Indice']]
                
                fig2 = go.Figure(data=[go.Bar(
                    x=df_saison['Mois_Nom'], 
                    y=df_saison['Indice'], 
                    marker_color=colors,
                    text=df_saison['Indice'].round(2),
                    textposition='auto'
                )])
                
                fig2.add_hline(y=1.0, line_dash="dash", line_color="#4B5563", annotation_text="Moyenne (1.0)", annotation_position="bottom right")

                fig2.update_layout(
                    title=dict(text="Profil de Saisonnalité (Indice Moyen)", font=dict(size=16, color="#111827")),
                    xaxis_title="Mois",
                    yaxis_title="Indice (Base 1.0)",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB')
                st.plotly_chart(fig2, use_container_width=True)

            with col_g2:
                df_top = df_previsions.groupby('article')[col_prev_aff].sum().sort_values(ascending=True).tail(10).reset_index()
                
                fig3 = go.Figure(data=[go.Bar(
                    x=df_top[col_prev_aff], 
                    y=df_top['article'], 
                    orientation='h', 
                    marker=dict(color=df_top[col_prev_aff], colorscale=['#FFC0C0', '#E30613'])
                )])
                
                fig3.update_layout(
                    title=dict(text="Top 10 Articles (Volume Total Projeté)", font=dict(size=16, color="#111827")),
                    xaxis_title=f"Volume ({unite_affichage})",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                fig3.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F3F4F6', linecolor='#E5E7EB')
                st.plotly_chart(fig3, use_container_width=True)
