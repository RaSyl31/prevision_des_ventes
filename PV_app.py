import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Configuration de la page
st.set_page_config(page_title="Prévision des ventes", layout="wide")

# --------------------------------------------------------------------
# CSS personnalisé : fond noir et accents rouges
# --------------------------------------------------------------------
st.markdown("""
<style>
    /* Fond principal noir */
    .stApp {
        background-color: #000000;
    }

    /* Titres en rouge */
    h1, h2, h3, h4, h5, h6 {
        color: #E63946;
    }

    /* Texte général en blanc */
    .stMarkdown, .stText, .stCaption {
        color: #FFFFFF;
    }

    /* Widgets (selectbox, slider) fond sombre et bordure rouge */
    .stSelectbox div[data-baseweb="select"] > div,
    .stSlider div[data-baseweb="slider"] {
        background-color: #1A1A1A;
        border: 1px solid #E63946;
    }

    /* Boutons rouges */
    .stButton > button {
        background-color: #E63946;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #C1121F;
    }

    /* Liens en rouge */
    a {
        color: #E63946;
    }

    /* Sidebar également en noir */
    .css-1d391kg {
        background-color: #000000;
    }

    /* Tableaux et dataframes */
    .stDataFrame {
        border: 1px solid #E63946;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------
# 1. LISTES DES AGENCES, SEGMENTS, MARQUES, ARTICLES
# --------------------------------------------------------------------
AGENCES = [
    "00-Siège",
    "01-Tanjombato",
    "03-Usine-Diego",
    "04-Tulear",
    "05-Fianarantsoa",
    "06-Ihosy",
    "07-Majunga",
    "08-Manakara",
    "09-Tamatave",
    "11-Andranomahery",
    "12-Antsirabe",
    "18-Ambanja",
    "19-Sambava",
    "21-Nosy-Be",
    "23-Morondava",
    "24-Fort-Dauphin"
]

# Table article : (segment, marque, article)
ARTICLES = [
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

# Conversion en DataFrame pour faciliter le filtrage
df_articles = pd.DataFrame(ARTICLES, columns=["segment", "marque", "article"])

# --------------------------------------------------------------------
# 2. GÉNÉRATION DE DONNÉES FICTIVES (à remplacer par vos vraies données)
# --------------------------------------------------------------------
@st.cache_data
def generate_dummy_data():
    """Génère 3 ans de données mensuelles pour toutes les combinaisons agence/article."""
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2023, 12, 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # début de mois

    data = []
    for agence in AGENCES:
        for _, row in df_articles.iterrows():
            segment, marque, article = row['segment'], row['marque'], row['article']
            # Tendance de base + saisonnalité + bruit
            base = random.uniform(50, 500)
            trend = random.uniform(0, 5)  # croissance mensuelle
            for i, date in enumerate(dates):
                # Saisonnalité : pic en été (décembre) et creux en hiver (juin)
                month = date.month
                seasonal = 1 + 0.3 * np.sin((month - 1) * 2 * np.pi / 12)
                # Bruit aléatoire
                noise = random.uniform(-0.2, 0.2)
                quantite = max(0, int(base * (1 + i * trend / 100) * seasonal * (1 + noise)))
                data.append({
                    "date": date,
                    "agence": agence,
                    "segment": segment,
                    "marque": marque,
                    "article": article,
                    "quantite": quantite
                })
    return pd.DataFrame(data)

# --------------------------------------------------------------------
# 3. CHARGEMENT DES DONNÉES
# --------------------------------------------------------------------
st.title("📈 Outil de prévision des ventes (5 ans)")

data_option = st.radio(
    "Source des données :",
    ["Utiliser des données fictives (démo)", "Importer un fichier CSV"]
)

if data_option == "Utiliser des données fictives (démo)":
    df = generate_dummy_data()
    st.success("Données fictives générées.")
else:
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Assurez-vous que la colonne date est bien au format datetime
        df['date'] = pd.to_datetime(df['date'])
        st.success("Fichier chargé avec succès.")
    else:
        st.info("Veuillez téléverser un fichier CSV avec les colonnes : date, agence, segment, marque, article, quantite.")
        st.stop()

# --------------------------------------------------------------------
# 4. SÉLECTION PAR L'UTILISATEUR
# --------------------------------------------------------------------
st.sidebar.header("Paramètres de sélection")

# Agence
selected_agence = st.sidebar.selectbox("Agence", AGENCES)

# Segment (filtré selon les données disponibles)
segments_disponibles = df['segment'].unique()
selected_segment = st.sidebar.selectbox("Segment", segments_disponibles)

# Marque (filtrée selon le segment)
marques_disponibles = df[df['segment'] == selected_segment]['marque'].unique()
selected_marque = st.sidebar.selectbox("Marque", marques_disponibles)

# Article (filtré selon la marque)
articles_disponibles = df[(df['segment'] == selected_segment) & (df['marque'] == selected_marque)]['article'].unique()
selected_article = st.sidebar.selectbox("Article", articles_disponibles)

# --------------------------------------------------------------------
# 5. FILTRAGE DES DONNÉES
# --------------------------------------------------------------------
df_filtered = df[
    (df['agence'] == selected_agence) &
    (df['segment'] == selected_segment) &
    (df['marque'] == selected_marque) &
    (df['article'] == selected_article)
].sort_values('date')

if df_filtered.empty:
    st.warning("Aucune donnée pour cette combinaison. Veuillez choisir une autre sélection.")
    st.stop()

# --------------------------------------------------------------------
# 6. PRÉPARATION POUR PROPHET
# --------------------------------------------------------------------
df_prophet = df_filtered.rename(columns={'date': 'ds', 'quantite': 'y'})[['ds', 'y']]
df_prophet = df_prophet.groupby('ds', as_index=False).sum()  # agréger par mois si nécessaire

# --------------------------------------------------------------------
# 7. PARAMÈTRES DE PRÉVISION
# --------------------------------------------------------------------
periods = st.sidebar.slider("Nombre de mois à prévoir", 12, 120, 60)
seasonality_mode = st.sidebar.selectbox("Saisonnalité", ["additive", "multiplicative"])

# --------------------------------------------------------------------
# 8. MODÈLE PROPHET
# --------------------------------------------------------------------
try:
    model = Prophet(
        seasonality_mode=seasonality_mode,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
except Exception as e:
    st.error(f"Erreur lors de la modélisation : {e}")
    st.stop()

# --------------------------------------------------------------------
# 9. AFFICHAGE DES RÉSULTATS
# --------------------------------------------------------------------
st.subheader(f"Prévisions pour {selected_article} - {selected_agence}")

# Graphique interactif
fig = go.Figure()

# Historique
fig.add_trace(go.Scatter(
    x=df_prophet['ds'],
    y=df_prophet['y'],
    mode='lines+markers',
    name='Historique',
    line=dict(color='#E63946')  # rouge pour l'historique
))

# Prévision
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat'],
    mode='lines',
    name='Prévision',
    line=dict(color='#FFFFFF')  # blanc pour la prévision
))

# Intervalle de confiance
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat_upper'],
    mode='lines',
    line=dict(width=0),
    showlegend=False
))
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat_lower'],
    mode='lines',
    line=dict(width=0),
    fill='tonexty',
    fillcolor='rgba(230, 57, 70, 0.2)',  # rouge semi-transparent
    name='Intervalle de confiance'
))

fig.update_layout(
    title=f"Prévision sur {periods} mois",
    xaxis_title="Date",
    yaxis_title="Quantité",
    hovermode="x unified",
    paper_bgcolor='black',   # fond noir du graphique
    plot_bgcolor='black',
    font=dict(color='white')
)

st.plotly_chart(fig, use_container_width=True)

# Tableau des prévisions futures
st.subheader("Détail des prévisions mensuelles")
future_forecast = forecast[forecast['ds'] > df_prophet['ds'].max()][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
future_forecast = future_forecast.rename(columns={
    'ds': 'Date',
    'yhat': 'Prévision',
    'yhat_lower': 'Borne basse',
    'yhat_upper': 'Borne haute'
})
future_forecast['Date'] = future_forecast['Date'].dt.strftime('%Y-%m')
st.dataframe(future_forecast, use_container_width=True)

# Téléchargement CSV
csv = future_forecast.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les prévisions (CSV)",
    data=csv,
    file_name=f"previsions_{selected_agence}_{selected_article}.csv",
    mime="text/csv"
)
