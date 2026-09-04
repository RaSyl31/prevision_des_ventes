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
st.set_page_config(page_title="Coefficients de Saisonnalité & Prévisions", layout="wide")

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
    
    .gros-titre-blanc {
        background-color: white;
        color: #CC0000 !important;
        padding: 15px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 28px;
        display: block;
        margin: 15px 0;
        border-left: 8px solid #CC0000;
        text-align: center;
    }
    
    .stButton > button, .stDownloadButton > button { background-color: #4CAF50; color: white; border: none; }
    .stButton > button:hover, .stDownloadButton > button:hover { background-color: #45a049; }
    
    .ia-box {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .table-rouge {
        background-color: white;
        border-radius: 5px;
        overflow-x: auto;
        overflow-y: auto;
        margin: 5px 0;
        border: 1px solid #ddd;
        max-height: 600px;
    }
    .table-rouge table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        white-space: nowrap;
    }
    .table-rouge th {
        background-color: #CC0000;
        color: white;
        padding: 6px 10px;
        text-align: center;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .table-rouge td {
        padding: 5px 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .table-rouge tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .table-rouge tr:hover {
        background-color: #f0f0f0;
    }
    
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
    "Booster Appel-Mix 50CL VER",
    "Booster Tornado 50CL VER VER",
    "Caprice Ananas 100 cl VER",
    "Caprice Ananas 150 cl PET",
    "Caprice Ananas 30 cl VER",
    "Caprice Bonbon Anglais 100 cl VER",
    "Caprice Bonbon Anglais 150 cl PET",
    "Caprice Bonbon Anglais 20L FUT",
    "Caprice Bonbon Anglais 30 cl VER",
    "Caprice Bonbon Anglais 30L FUT",
    "Caprice Bonbon Anglais 33 cl CAN",
    "Caprice Bonbon Anglais 35 cl PET",
    "Caprice Bonbon Anglais 50 cl PET",
    "Caprice Grenadine 100 cl VER",
    "Caprice Grenadine 150 cl PET",
    "Caprice Grenadine 30 cl VER",
    "Caprice Grenadine 33 cl CAN",
    "Caprice Grenadine 35 cl PET",
    "Caprice Grenadine 50 cl PET",
    "Caprice Orange 100 cl VER",
    "Caprice Orange 150 cl PET",
    "Caprice Orange 20L FUT",
    "Caprice Orange 30 cl VER",
    "Caprice Orange 33 cl CAN",
    "Caprice Orange 35 cl PET",
    "Caprice Orange 50 cl PET",
    "Tonic 100 cl VER",
    "Tonic 30 cl VER",
    "World Cola 100cl VER",
    "World Cola 100cl WOCO VER",
    "World Cola 150cl PET",
    "World Cola 20L FUT",
    "World Cola 30cl VER",
    "World Cola 30cl WOCO VER",
    "World Cola 33 cl CAN",
    "World Cola 35cl PET",
    "World Cola 50cl PET",
    "Beaufort 33 CL CAN",
    "Beaufort 33CL VER",
    "Beaufort 50 CL CAN",
    "FRESH 33 cl CAN",
    "FRESH 33 cl EXPORT CAN",
    "THB Fresh 33 cl VER",
    "THB Fresh 65 cl VER",
    "Gold 8 50 cl CAN",
    "Gold 8 50 cl VER",
    "Gold Amigo 33cl VER",
    "Gold Blanche 20L FUT",
    "Gold Blanche 33cl VER",
    "Gold Blanche 50 cl CAN",
    "Gold Blanche 50 cl VER",
    "Gold Blonde 33 cl VER",
    "Gold Blonde 50 cl CAN",
    "Gold Blonde 50 cl VER",
    "Gold Blonde 65 cl VER",
    "Gold Rosee 33cl VER",
    "Queen s 65 cl VER",
    "THB Blanche 20L Export FUT",
    "THB BLanche 20L FUT",
    "THB Pilsener 20L Export FUT",
    "THB Pilsener 20L FUT",
    "THB Pilsener 30L Export FUT",
    "THB Pilsener 30L FUT",
    "THB Pilsener 33 cl CAN",
    "THB Pilsener 33 cl VER",
    "THB Pilsener 50 cl CAN",
    "THB Pilsener 65 cl VER",
    "THB Speciale NOEL 33 cl VER",
    "Cristal 100 cl VER",
    "Cristal 150 cl PET",
    "Cristal 30 cl VER",
    "Cristal 50 cl VER",
    "Cristalline 100 cl PET",
    "Cristalline 200 cl PET",
    "Eau vive 150 cl PET",
    "Eau vive 50 cl PET",
    "Eau vive 50 cl VER",
    "FOSA 50 cl CAN",
    "XXL 30cl BOB VER",
    "XXL 30cl VER",
    "XXL 33 cl CAN",
    "XXL 35cl PET"
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
# 3. INTERPRÉTATION DU GRAPHIQUE
# --------------------------------------------------------------------
def interpreter_graphe(coefs_globaux):
    if not coefs_globaux:
        return "Aucune donnée à interpréter."
    noms_mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    valeurs = [coefs_globaux.get(m, 0) for m in range(1, 13)]
    mois_fort = int(np.argmax(valeurs)) + 1
    mois_faible = int(np.argmin(valeurs)) + 1
    amplitude = max(valeurs) - min(valeurs)

    texte = []
    texte.append(f"**📈 Pic :** {noms_mois[mois_fort-1]} (coefficient {max(valeurs):.2f})")
    texte.append(f"**📉 Creux :** {noms_mois[mois_faible-1]} (coefficient {min(valeurs):.2f})")
    texte.append(f"**📊 Amplitude :** {amplitude:.2f}")
    if amplitude > 1.0:
        texte.append("→ Forte variation saisonnière.")
    elif amplitude > 0.5:
        texte.append("→ Variation modérée.")
    else:
        texte.append("→ Variation faible.")
    texte.append("\n**💡 Recommandations :**")
    texte.append(f"• Prévoir des stocks suffisants avant **{noms_mois[mois_fort-1]}**.")
    texte.append(f"• Envisager des actions promotionnelles en **{noms_mois[mois_faible-1]}**.")
    return "\n".join(texte)

# --------------------------------------------------------------------
# 4. CHARGEMENT DES DONNÉES BRUTES
# --------------------------------------------------------------------
@st.cache_data
def charger_donnees_brutes(file_bytes, filename):
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
# 5. CALCUL DES COEFFICIENTS PAR ARTICLE-AGENCE
# --------------------------------------------------------------------
def calculer_coefficients_par_article_agence(df_brut, annees=[2024, 2025]):
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
# 6. CALCUL DU COEFFICIENT GLOBAL
# --------------------------------------------------------------------
def calculer_coefficient_global(df_brut_filtre, annees=[2024, 2025]):
    df_periode = df_brut_filtre[df_brut_filtre['Année'].isin(annees)]
    if df_periode.empty:
        return None
    moyenne_generale = df_periode['ventes_hecto'].mean()
    if moyenne_generale <= 0:
        return None
    coeffs_bruts = {}
    for mois in range(1, 13):
        ventes_mois = df_periode[df_periode['mois_num'] == mois]['ventes_hecto']
        moyenne_mois = ventes_mois.mean() if len(ventes_mois) > 0 else 0
        coeffs_bruts[mois] = moyenne_mois / moyenne_generale
    somme_coeffs = sum(coeffs_bruts.values())
    if somme_coeffs > 0:
        coeffs_norm = {m: (c / somme_coeffs) * 12 for m, c in coeffs_bruts.items()}
        coeffs_finaux = {}
        somme_arrondie = 0
        for mois in range(1, 12):
            coeff = round(coeffs_norm[mois], 2)
            coeffs_finaux[mois] = coeff
            somme_arrondie += coeff
        coeffs_finaux[12] = round(12 - somme_arrondie, 2)
        somme_finale = sum(coeffs_finaux.values())
        if abs(somme_finale - 12) > 0.01:
            coeffs_finaux[12] = round(coeffs_finaux[12] + (12 - somme_finale), 2)
        return coeffs_finaux
    else:
        return {m: 0 for m in range(1, 13)}

# --------------------------------------------------------------------
# 7. GÉNÉRATION DU TABLEAU HTML
# --------------------------------------------------------------------
def generer_tableau_html(pivot_df):
    html = '<div class="table-rouge"><table>'
    html += '<tr>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Segment</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Marque</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Format</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Contenance</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Article</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:left;">Agence</th>'
    for col in pivot_df.columns:
        html += f'<th style="background-color:#CC0000; color:white; font-weight:bold; padding:6px 10px; text-align:center;">{col}</th>'
    html += '</tr>'
    for idx, row in pivot_df.iterrows():
        html += '<tr>'
        if isinstance(idx, tuple):
            vals = list(idx) + [''] * (6 - len(idx))
            segment_val, marque_val, format_val, contenance_val, article_val, agence_val = vals
        else:
            segment_val, marque_val, format_val, contenance_val, article_val, agence_val = idx, '', '', '', '', ''
        html += f'<td style="text-align:left; padding:5px 8px;">{segment_val}</td>'
        html += f'<td style="text-align:left; padding:5px 8px;">{marque_val}</td>'
        html += f'<td style="text-align:left; padding:5px 8px;">{format_val}</td>'
        html += f'<td style="text-align:left; padding:5px 8px;">{contenance_val}</td>'
        html += f'<td style="text-align:left; padding:5px 8px;">{article_val}</td>'
        html += f'<td style="text-align:left; padding:5px 8px;">{agence_val}</td>'
        for col in pivot_df.columns:
            val = row[col]
            html += f'<td style="padding:5px 8px; text-align:center;">{val:.2f}</td>' if pd.notna(val) else '<td style="padding:5px 8px; text-align:center;">-</td>'
        html += '</tr>'
    html += '</table></div>'
    return html

# --------------------------------------------------------------------
# 8. APPLICATION PRINCIPALE
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

# Filtres interactifs
st.sidebar.header("Filtres")
agences_options = sorted(df_brut['agence'].unique())
selected_agences = st.sidebar.multiselect("Agence", options=agences_options, default=agences_options)

df_temp = df_brut[df_brut['agence'].isin(selected_agences)] if selected_agences else df_brut
segments_options = sorted(df_temp['segment'].unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)

df_temp = df_temp[df_temp['segment'].isin(selected_segments)] if selected_segments else df_temp
marques_options = sorted(df_temp['marque'].unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)

df_temp = df_temp[df_temp['marque'].isin(selected_marques)] if selected_marques else df_temp
articles_options = sorted(df_temp['Référence'].unique())
selected_articles = st.sidebar.multiselect("Article", options=articles_options, default=articles_options)

df_brut_filtre = df_brut[
    (df_brut['agence'].isin(selected_agences)) &
    (df_brut['segment'].isin(selected_segments)) &
    (df_brut['marque'].isin(selected_marques)) &
    (df_brut['Référence'].isin(selected_articles))
]
if df_brut_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# Coefficients
df_coefficients = calculer_coefficients_par_article_agence(df_brut_filtre)
if df_coefficients.empty:
    st.warning("Aucun coefficient calculé pour les filtres sélectionnés.")
    st.stop()

st.success(f"Calcul terminé : {len(df_coefficients)} coefficients")

# Gros titre
st.markdown('<span class="gros-titre-blanc">📊 Saisonnalité par Article</span>', unsafe_allow_html=True)

# Tableau des coefficients
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
st.markdown(generer_tableau_html(pivot), unsafe_allow_html=True)

# Coefficient global
st.markdown('<span class="titre-rouge">📊 Coefficient Global par Mois</span>', unsafe_allow_html=True)
coefs_globaux = calculer_coefficient_global(df_brut_filtre)
if coefs_globaux:
    noms_mois_courts = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    coefs_values = [coefs_globaux.get(m, 0) for m in range(1, 13)]
    total_global = sum(coefs_values)
    html = '<div class="coef-global-table"><table>'
    html += '<tr><th style="background-color:#CC0000; color:white; font-weight:bold; padding:5px 10px;">Mois</th>'
    for m in noms_mois_courts:
        html += f'<th style="background-color:#CC0000; color:white; font-weight:bold; padding:5px 10px;">{m}</th>'
    html += '<th style="background-color:#CC0000; color:white; font-weight:bold; padding:5px 10px;">Total</th></tr>'
    html += '<tr><td style="font-weight:bold; background-color:#E3F2FD; padding:5px 10px;">Coefficient</td>'
    for v in coefs_values:
        html += f'<td style="background-color:white; padding:5px 10px; text-align:center;">{v:.2f}</td>'
    html += f'<td style="background-color:#E3F2FD; font-weight:bold; padding:5px 10px; text-align:center;">{total_global:.2f}</td></tr>'
    html += '</table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.warning("Impossible de calculer le coefficient global.")
    coefs_globaux = {m: 0 for m in range(1, 13)}

# Graphique
st.markdown('<span class="titre-rouge">📈 Variation mensuelle des coefficients</span>', unsafe_allow_html=True)
coefs_norm_list = [coefs_globaux.get(m, 0) for m in range(1, 13)]
fig = go.Figure()
fig.add_trace(go.Scatter(x=noms_mois, y=coefs_norm_list, mode='lines+markers',
                         name='Coefficient global (réel)', line=dict(color='blue', width=2), marker=dict(size=8)))
fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Moyenne = 1.0")
fig.update_layout(title="Coefficients de saisonnalité globaux par mois (calcul réel à partir des ventes)",
                  xaxis_title="Mois", yaxis_title="Coefficient", height=500,
                  plot_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='lightgray'),
                  yaxis=dict(showgrid=True, gridcolor='lightgray'))
st.plotly_chart(fig, width='stretch')

# Interprétation
st.markdown("### 🤖 Interprétation et Recommandations")
st.markdown(interpreter_graphe(coefs_globaux))

# --------------------------------------------------------------------
# 9. PRÉVISIONS ANNÉE SUIVANTE (tableau unique)
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">🔮 Prévisions Année Suivante</span>', unsafe_allow_html=True)

total_prevu = st.number_input("Total prévu (hectolitres)", min_value=0.0, value=1000000.0, step=1000.0)

def previsions_detaillees(df_brut, coefs_globaux, total_prevu):
    annee_recente = df_brut['Année'].max()
    annees_ref = [annee_recente - 1, annee_recente]
    df_ref = df_brut[df_brut['Année'].isin(annees_ref)]
    total_ref = df_ref['ventes_hecto'].sum()

    poids_croise = df_ref.groupby(['segment', 'marque', 'format', 'contenances', 'Référence', 'agence'])['ventes_hecto'].sum() / total_ref
    previsions_croisees = {}
    for (segment, marque, format, contenance, article, agence), poids in poids_croise.items():
        previsions_croisees[(segment, marque, format, contenance, article, agence)] = {
            mois: (total_prevu / 12) * coefs_globaux.get(mois, 1.0) * poids
            for mois in range(1, 13)
        }
    return previsions_croisees

previsions = previsions_detaillees(df_brut_filtre, coefs_globaux, total_prevu)

previsions_df = pd.DataFrame(previsions).T
previsions_df.index = pd.MultiIndex.from_tuples(previsions_df.index, names=['Segment', 'Marque', 'Format', 'Contenance', 'Article', 'Agence'])
previsions_df.columns = noms_mois
previsions_df['Total'] = previsions_df.sum(axis=1)
previsions_df = previsions_df.round(0)

st.markdown(generer_tableau_html(previsions_df), unsafe_allow_html=True)

st.download_button("Télécharger les prévisions (CSV)",
                   data=previsions_df.to_csv().encode('utf-8'),
                   file_name="previsions_annee_suivante.csv", mime="text/csv")
