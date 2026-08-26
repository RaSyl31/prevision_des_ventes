import streamlit as st

# Liste des agences (à adapter selon vos noms exacts)
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

# Utilisation dans l'interface
selected_agence = st.selectbox("Choisissez une agence", AGENCES)
