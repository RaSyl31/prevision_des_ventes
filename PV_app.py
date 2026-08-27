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
    "03-Usine-Diego",
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
    "21-Nosy-Be",
    "21-NosyBe",
    "23-Morondava",
    "24-Fort-Dauphin",
    "24-Fort Dauphin"
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
# 4. CHARGEMENT ET TRAITEMENT OPTIMISÉ
# --------------------------------------------------------------------
@st.cache_data
def charger_et_calculer(file_bytes, filename):
    """Charge le fichier et calcule les coefficients."""
    if filename.endswith('.csv'):
        df_raw = pd.read_csv(BytesIO(file_bytes), sep='\t')
    else:
        df_raw = pd.read_excel(BytesIO(file_bytes))
    
    # Vérifier les colonnes requises
    required_cols = ['Année', 'Mois année', 'Segments', 'Marque', 'Format', 'Agences', 'Contenance', 'Articles', 'Vente hl direct']
    if not all(col in df_raw.columns for col in required_cols):
        st.error(f"Colonnes manquantes. Requises : {required_cols}")
        st.stop()
    
    # Filtrer les lignes : Articles non vide, ne contenant pas "Total" ou "vide"
    # Utiliser des conditions séparées avec parenthèses
    df = df_raw.copy()
    
    # Supprimer les lignes où Articles est NaN
    df = df[df['Articles'].notna()]
    
    # Convertir en string pour les filtres
    df['Articles_str'] = df['Articles'].astype(str)
    
    # Filtrer : pas de "Total", pas de "vide", pas vide
    df = df[
        (~df['Articles_str'].str.contains('Total', case=False, na=False)) &
        (~df['Articles_str'].str.contains('vide', case=False, na=False)) &
        (df['Articles_str'].str.strip() != '')
    ]
    
    # Filtrer Mois année : non null et pas "Total"
    df = df[df['Mois année'].notna()]
    df['Mois_annee_str'] = df['Mois année'].astype(str)
    df = df[~df['Mois_annee_str'].str.contains('Total', case=False, na=False)]
    
    # Filtrer Agences : non null et pas "Total"
    df = df[df['Agences'].notna()]
    df['Agences_str'] = df['Agences'].astype(str)
    df = df[~df['Agences_str'].str.contains('Total', case=False, na=False)]
    
    # Supprimer les colonnes temporaires
    df = df.drop(columns=['Articles_str', 'Mois_annee_str', 'Agences_str'])
    
    # Renommer les colonnes
    df.rename(columns={
        'Segments': 'segment',
        'Marque': 'marque',
        'Format': 'format',
        'Agences': 'agence',
        'Contenance': 'contenances',
        'Articles': 'Référence',
        'Vente hl direct': 'ventes_hecto'
    }, inplace=True)
    
    # Convertir Année
    df['Année'] = pd.to_numeric(df['Année'], errors='coerce')
    df = df.dropna(subset=['Année'])
    df['Année'] = df['Année'].astype(int)
    
    # Convertir ventes
    df['ventes_hecto'] = df['ventes_hecto'].apply(nettoyer_nombre)
    
    # Extraire le mois depuis "Mois année" (ex: "01 2024" -> mois = 1)
    df['mois_num'] = df['Mois année'].astype(str).str.extract(r'^(\d{2})').astype(int)
    df = df.dropna(subset=['mois_num'])
    
    # Créer la date
    df['date'] = pd.to_datetime(df['Année'].astype(str) + '-' + df['mois_num'].astype(str) + '-01')
    
    # Filtrer pour ne garder que les agences valides
    df = df[df['agence'].isin(AGENCES)]
    
    # Filtrer période 2024-2025
    df_periode = df[(df['date'].dt.year >= 2024) & (df['date'].dt.year <= 2025)]
    
    if df_periode.empty:
        return pd.DataFrame()
    
    group_cols = ['segment', 'marque', 'format', 'contenances', 'Référence', 'agence']
    moyenne_generale = df_periode.groupby(group_cols)['ventes_hecto'].mean()
    moyenne_par_mois = df_periode.groupby(group_cols + [df_periode['date'].dt.month])['ventes_hecto'].mean()
    
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
# 5. CHARGEMENT DU FICHIER
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📊 Coefficients de Saisonnalité par Article et Agence</span>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choisissez le fichier historique (Excel ou CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("Veuillez téléverser un fichier Excel (.xlsx) ou CSV contenant les colonnes : Année, Mois année, Segments, Marque, Format, Agences, Contenance, Articles, Vente hl direct")
    st.stop()

file_bytes = uploaded_file.getvalue()
filename = uploaded_file.name

df_coefficients = charger_et_calculer(file_bytes, filename)

if df_coefficients.empty:
    st.warning("Aucune donnée sur la période 2024-2025 pour calculer les coefficients.")
    st.stop()

# --------------------------------------------------------------------
# 6. FILTRES
# --------------------------------------------------------------------
st.sidebar.header("Filtres")

# Article (premier filtre)
articles_options = sorted(df_coefficients['Référence'].unique())
selected_articles = st.sidebar.multiselect("Article", options=articles_options, default=articles_options)

# Marque (filtrée selon les articles sélectionnés)
if selected_articles:
    marques_options = sorted(df_coefficients[df_coefficients['Référence'].isin(selected_articles)]['marque'].unique())
else:
    marques_options = sorted(df_coefficients['marque'].unique())
selected_marques = st.sidebar.multiselect("Marque", options=marques_options, default=marques_options)

# Segment (filtré selon articles et marques sélectionnés)
if selected_articles and selected_marques:
    segments_options = sorted(df_coefficients[
        (df_coefficients['Référence'].isin(selected_articles)) & 
        (df_coefficients['marque'].isin(selected_marques))
    ]['segment'].unique())
else:
    segments_options = sorted(df_coefficients['segment'].unique())
selected_segments = st.sidebar.multiselect("Segment", options=segments_options, default=segments_options)

# Appliquer les filtres
df_filtre = df_coefficients[
    (df_coefficients['Référence'].isin(selected_articles)) &
    (df_coefficients['marque'].isin(selected_marques)) &
    (df_coefficients['segment'].isin(selected_segments))
]

if df_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --------------------------------------------------------------------
# 7. TABLEAU PIVOT
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
# 8. GRAPHIQUE - Coefficients globaux par article (toutes agences confondues)
# --------------------------------------------------------------------
st.markdown('<span class="titre-rouge">📈 Variation mensuelle des coefficients</span>', unsafe_allow_html=True)

coeffs_globaux_par_mois = df_filtre.groupby('mois')['coefficient'].mean()

somme_coeffs_graph = coeffs_globaux_par_mois.sum()
if somme_coeffs_graph > 0:
    coeffs_globaux_normalises = (coeffs_globaux_par_mois / somme_coeffs_graph) * 12
else:
    coeffs_globaux_normalises = coeffs_globaux_par_mois

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=noms_mois,
    y=coeffs_globaux_normalises.reindex(mois_cols),
    mode='lines+markers',
    name='Coefficient global',
    line=dict(color='blue', width=2),
    marker=dict(size=8)
))

fig.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Moyenne = 1.0")

fig.update_layout(
    title="Coefficients de saisonnalité globaux par mois (toutes agences confondues)",
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
# 9. INTERPRÉTATION IA
# --------------------------------------------------------------------
st.markdown("### 🤖 Interprétation et Recommandations")
st.markdown('<div class="ia-box">' + interpreter_resultats(df_coefficients, df_filtre).replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------
# 10. TÉLÉCHARGEMENT
# --------------------------------------------------------------------
csv = pivot.reset_index().to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les coefficients (CSV)",
    data=csv,
    file_name="coefficients_saisonnalite_2024_2025.csv",
    mime="text/csv"
)
