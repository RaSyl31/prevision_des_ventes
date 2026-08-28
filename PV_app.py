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
    
    .titre-rouge {
        background-color: #CC0000;
        color: white !important;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: block;
        margin: 10px 0;
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
    
    /* Tableau compact coefficient global */
    .coef-global-table {
        background-color: #E3F2FD;
        border-radius: 5px;
        padding: 8px;
        overflow-x: auto;
        margin: 5px 0;
    }
    .coef-global-table table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        white-space: nowrap;
    }
    .coef-global-table th {
        background-color: #CC0000;
        color: white;
        padding: 5px 10px;
        text-align: center;
        font-weight: bold;
    }
    .coef-global-table td {
        padding: 5px 10px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .coef-global-table .ligne-mois {
        background-color: #CC0000;
        color: white;
        font-weight: bold;
    }
    .coef-global-table .ligne-coef {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTES DE RÉFÉRENCE
# --------------------------------------------------------------------
AGENCES = [
    "00-", "01-Tanjombato", "03-Usine-Diego", "04-Tulear", "05-Fianarantsoa",
    "06-Ihosy", "07-Majunga", "08-Manakara", "09-Tamatave", "11-Andranomahery",
    "12-Antsirabe", "18-Ambanja", "19-Sambava", "21-Nosy-Be", "23-Morondava",
    "24-Fort-Dauphin"
]

SEGMENTS = ["1-BIERES", "2-BG", "3-EAUX", "5-ALCOMIX", "7-VIN"]

ARTICLES_ACTIFS = [
    "Booster Appel-Mix 50CL VER", "Booster Tornado 50CL VER VER",
    "Caprice Ananas 100 cl VER", "Caprice Ananas 150 cl PET", "Caprice Ananas 30 cl VER",
    "Caprice Bonbon Anglais 100 cl VER", "Caprice Bonbon Anglais 150 cl PET",
    "Caprice Bonbon Anglais 30 cl VER", "Caprice Bonbon Anglais 35 cl PET",
    "Caprice Bonbon Anglais 50 cl PET", "Caprice Grenadine 100 cl VER",
    "Caprice Grenadine 150 cl PET", "Caprice Grenadine 30 cl VER",
    "Caprice Grenadine 33 cl CAN", "Caprice Grenadine 35 cl PET", "Caprice Grenadine 50 cl PET",
    "Caprice Orange 100 cl VER", "Caprice Orange 150 cl PET", "Caprice Orange 30 cl VER",
    "Caprice Orange 33 cl CAN", "Caprice Orange 35 cl PET", "Caprice Orange 50 cl PET",
    "Caprice Bonbon Anglais 33 cl CAN", "Caprice Citron 100 cl VER",
    "Caprice Citron 150 cl PET", "Caprice Citron 30 cl VER", "Caprice Citron 50 cl PET",
    "Tonic 100 cl VER", "Tonic 30 cl VER",
    "World Cola 100cl VER", "World Cola 100cl WOCO VER", "World Cola 150cl PET",
    "World Cola 30cl VER", "World Cola 30cl WOCO VER", "World Cola 33 cl CAN",
    "World Cola 35cl PET", "World Cola 50cl PET",
    "Beaufort 33 CL CAN", "Beaufort 33CL VER",
    "FRESH 33 cl CAN", "THB Fresh 33 cl VER", "THB Fresh 65 cl VER",
    "Gold 8 50 cl CAN", "Gold 8 50 cl VER", "Gold Blanche 33cl VER",
    "Gold Blanche 50 cl CAN", "Gold Blanche 50 cl VER", "Gold Blonde 33 cl VER",
    "Gold Blonde 50 cl CAN", "Gold Blonde 50 cl VER", "Gold Blonde 65 cl VER",
    "Queen s 65 cl VER", "THB Pilsener 33 cl VER", "THB Pilsener 50 cl CAN",
    "THB Pilsener 65 cl VER",
    "Cristal 100 cl VER", "Cristal 150 cl PET", "Cristal 30 cl VER", "Cristal 50 cl VER",
    "Cristalline 100 cl PET", "Cristalline 200 cl PET",
    "Eau vive 150 cl PET", "Eau vive 50 cl PET", "Eau vive 50 cl VER",
    "FOSA 50 cl CAN", "XXL 30cl BOB VER", "XXL 30cl VER", "XXL 33 cl CAN", "XXL 35cl PET"
]

MARQUES = [
    "1-Booster", "1-Caprice", "1-Cristalline", "1-Queen s", "1-XXL",
    "2-Alcomix Divers", "2-Eau vive", "2-FOSA", "2-Tonic", "3-Cristal",
    "3-D jino", "3-Fresh", "4-THB", "4-Youzou", "5-Gold", "5-World Cola",
    "6-Beaufort", "7-Autres bieres", "Vin"
]

# --------------------------------------------------------------------
# 2. FONCTIONS UTILITAIRES
# --------------------------------------------------------------------
def nettoyer_nombre(val):
    if isinstance(val, str):
        val = val.replace(' ', '').replace(',', '.')
    try:
        return float(val)
    except:
        return 0.0

# --------------------------------------------------------------------
# 3. FONCTION D'INTERPRÉTATION IA
# --------------------------------------------------------------------
def interpreter_resultats(df_filtre):
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
    
    return "\n".join(interpretations)

# --------------------------------------------------------------------
# 4. CHARGEMENT DES DONNÉES BRUTES
# --------------------------------------------------------------------
@st.cache_data
def charger_donnees_brutes(file_bytes, filename):
    """Charge le fichier et retourne les données brutes filtrées."""
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))
    
    required_cols = ['Année', 'Mois année', 'Segments', 'Marque', 'Format', 'Agences', 'Contenance', 'Articles', 'Vente hl direct']
    missing_cols = [col for col in required_cols if col not in df_raw.columns]
    if missing_cols:
        st.error(f"Colonnes manquantes : {missing_cols}")
        st.stop()
    
    df = df_raw.copy()
    
    df = df[df['Articles'].notna()]
    df = df[~df['Articles'].astype(str).str.contains('Total', case=False, na=False)]
    df = df[~df['Articles'].astype(str).str.contains('vide', case=False, na=False)]
    df = df[df['Articles'].astype(str).str.strip() != '']
    df = df[df['Mois année'].notna()]
    df = df[~df['Mois année'].astype(str).str.contains('Total', case=False, na=False)]
    df = df[df['Agences'].notna()]
    df = df[~df['Agences'].astype(str).str.contains('Total', case=False, na=False)]
    
    df.rename(columns={
        'Segments': 'segment',
        'Marque': 'marque',
        'Format': 'format',
        'Agences': 'agence',
        'Contenance': 'contenances',
        'Articles': 'Référence',
        'Vente hl direct': 'ventes_hecto'
    }, inplace=True)
    
    df['Année'] = pd.to_numeric(df['Année'], errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)
    df['ventes_hecto'] = df['ventes_hecto'].apply(nettoyer_nombre)
    df['mois_num'] = df['Mois année'].astype(str).str.strip().str.split(' ').str[0]
    df['mois_num'] = pd.to_numeric(df['mois_num'], errors='coerce')
    df = df.dropna(subset=['mois_num'])
    df['mois_num'] = df['mois_num'].astype(int)
    
    return df

# --------------------------------------------------------------------
# 5. FONCTION DE CALCUL DES COEFFICIENTS PAR ARTICLE-AGENCE
# --------------------------------------------------------------------
def calculer_coefficients_par_article_agence(df_brut, annees=[2024, 2025]):
    """Calcule les coefficients par combinaison article-agence."""
    df_periode = df_brut[df_brut['Année'].isin(annees)]
    
    if df_periode.empty:
        return pd.DataFrame()
    
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    moyenne_generale = df_periode.groupby(group_cols)['ventes_hecto'].mean()
    moyenne_par_mois = df_periode.groupby(group_cols + [df_periode['mois_num']])['ventes_hecto'].mean()
    
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
# 6. FONCTION DE CALCUL DU COEFFICIENT GLOBAL
# --------------------------------------------------------------------
def calculer_coefficient_global(df_brut_filtre, annees=[2024, 2025]):
    """
    Calcule le coefficient global par mois à partir des données brutes filtrées.
    """
    df_periode = df_brut_filtre[df_brut_filtre['Année'].isin(annees)]
    
    if df_periode.empty:
        return None
    
    moyenne_generale = df_periode['ventes_hecto'].mean()
    
    if moyenne_generale <= 0:
        return None
    
    coeffs = {}
    for mois in range(1, 13):
        ventes_mois = df_periode[df_periode['mois_num'] == mois]['ventes_hecto']
        if len(ventes_mois) > 0:
            moyenne_mois = ventes_mois.mean()
        else:
            moyenne_mois = 0
        coeffs[mois] = moyenne_mois / moyenne_generale
    
    somme_coeffs = sum(coeffs.values())
    if somme_coeffs > 0:
        coeffs_normalises = {m: round((c / somme_coeffs) * 12, 2) for m, c in coeffs.items()}
    else:
        coeffs_normalises = coeffs
    
    return coeffs_normalises

# --------------------------------------------------------------------
# 7. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📊 Coefficients de Saisonnalité par Article et Agence</span>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois année, Segments, Marque, Format, Agences, Contenance, Articles, Vente hl direct")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

df_brut = charger_donnees_brutes(file_bytes, filename)

if df_brut.empty:
    st.warning("Aucune donnée valide trouvée.")
    st.stop()

# --------------------------------------------------------------------
# 8. FILTRES
# --------------------------------------------------------------------
st.sidebar.header("Filtres")

agences_options = sorted(df_brut['agence'].unique())
selected_agences = st.sidebar.multiselect("Agence", options=agences_options, default=agences_options)

segments_options = sorted(df_brut['segment'].unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)

articles_options = sorted(df_brut['Référence'].unique())
selected_articles = st.sidebar.multiselect("Article", options=articles_options, default=articles_options)

marques_options = sorted(df_brut['marque'].unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)

df_brut_filtre = df_brut[
    (df_brut['agence'].isin(selected_agences)) &
    (df_brut['segment'].isin(selected_segments)) &
    (df_brut['Référence'].isin(selected_articles)) &
    (df_brut['marque'].isin(selected_marques))
]

if df_brut_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --------------------------------------------------------------------
# 9. CALCUL DES COEFFICIENTS PAR ARTICLE-AGENCE
# --------------------------------------------------------------------
df_coefficients = calculer_coefficients_par_article_agence(df_brut_filtre, annees=[2024, 2025])

if df_coefficients.empty:
    st.warning("Aucun coefficient calculé pour les filtres sélectionnés.")
    st.stop()

st.success(f"Calcul terminé : {len(df_coefficients)} coefficients")

# --------------------------------------------------------------------
# 10. TABLEAU PIVOT DES COEFFICIENTS PAR ARTICLE-AGENCE
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">Coefficients de saisonnalité mensuels</span>', unsafe_allow_html=True)

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

pivot['Total'] = pivot.sum(axis=1)

st.dataframe(pivot, width='stretch', height=600)

# --------------------------------------------------------------------
# 11. COEFFICIENT GLOBAL PAR MOIS (tableau 2 lignes avec entêtes rouges)
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📊 Coefficient Global par Mois</span>', unsafe_allow_html=True)

coefs_globaux = calculer_coefficient_global(df_brut_filtre, annees=[2024, 2025])

if coefs_globaux:
    noms_mois_courts = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    coefs_values = [coefs_globaux.get(m, 0) for m in range(1, 13)]
    
    # Créer le tableau HTML avec entêtes en gras rouge
    html_table = '<div class="coef-global-table">'
    html_table += '<table>'
    
    # Ligne d'en-tête (mois) en rouge gras
    html_table += '<tr>'
    html_table += '<th style="background-color: #CC0000; color: white; font-weight: bold; padding: 5px 10px;">Mois</th>'
    for m in noms_mois_courts:
        html_table += f'<th style="background-color: #CC0000; color: white; font-weight: bold; padding: 5px 10px;">{m}</th>'
    html_table += '</tr>'
    
    # Ligne des coefficients
    html_table += '<tr>'
    html_table += '<td style="font-weight: bold; background-color: #E3F2FD; padding: 5px 10px;">Coefficient</td>'
    for v in coefs_values:
        html_table += f'<td style="background-color: white; padding: 5px 10px; text-align: center;">{v:.2f}</td>'
    html_table += '</tr>'
    
    html_table += '</table></div>'
    
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.warning("Impossible de calculer le coefficient global pour les filtres sélectionnés.")
    coefs_globaux = {m: 0 for m in range(1, 13)}

# --------------------------------------------------------------------
# 12. GRAPHIQUE
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📈 Variation mensuelle des coefficients</span>', unsafe_allow_html=True)

coefs_norm_list = [coefs_globaux.get(m, 0) for m in range(1, 13)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=noms_mois,
    y=coefs_norm_list,
    mode='lines+markers',
    name='Coefficient global (réel)',
    line=dict(color='blue', width=2),
    marker=dict(size=8)
))
fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Moyenne = 1.0")
fig.update_layout(
    title="Coefficients de saisonnalité globaux par mois (calcul réel à partir des ventes)",
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
# 13. INTERPRÉTATION IA
# --------------------------------------------------------------------
st.markdown("### 🤖 Interprétation et Recommandations")
st.markdown('<div class="ia-box">' + interpreter_resultats(df_coefficients).replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------
# 14. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot.reset_index().to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les coefficients (CSV)",
    data=csv,
    file_name="coefficients_saisonnalite.csv",
    mime="text/csv"
)
