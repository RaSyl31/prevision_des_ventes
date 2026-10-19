from __future__ import annotations

import io
import hashlib
import os
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# ==============================================================================
# 1. CONFIGURATION & CONSTANTES
# ==============================================================================

st.set_page_config(
    page_title="Suivi & Prévision SAAR (S&OP)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

RACINE = Path(__file__).resolve().parent
DOSSIERS = [RACINE, RACINE.parent, Path.cwd()]
FICHIERS_CANDIDATS = ["DATA_BRUT.xlsx"]

COLONNES = [
    "annee", "mois", "periode", "agence", "region", "segment", "produit", "parfum", "format",
    "type_format", "article", "nature", "origine", "colis", "hl", "positionnement", "occasion", 
    "conditionnement", "contenance_ci", "contenance_hl"
]

MOIS = ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"]
MOIS_COMPLETS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_NOMS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

COULEUR_REALISE = "#9E6315EF"
COULEUR_PREVISION = "#9BD69E"
HAUSSE_SAISONNIERE_PREVISION = {6: 1.20, 12: 1.20}

FILTRES = [
    ("article", "🛒 Article"),
    ("positionnement", "📍 Positionnement"),
    ("occasion", "🎯 Occasion"),
    ("conditionnement", "📦 Format"),
    ("contenance_ci", "📏 Contenance (CI)"),
    ("contenance_hl", "🧪 Contenance (hl)"),
    ("agence", "🏢 Agence"),
    ("region", "🗺️ Région"),
]

AGENCES_REFERENCE = [
    "01-Tanjombato", "03-Usine-Diego", "04-Tulear", "05-Fianarantsoa", "06-Ihosy",
    "07-Majunga", "08-Manakara", "09-Tamatave", "11-Andranomahery", "12-Antsirabe",
    "18-Ambanja", "19-Sambava", "21-Nosy-be", "23-Morondova", "24-Fort-Dauphin",
]

REGION_PAR_AGENCE = {
    "01-Tanjombato": "Centre", "03-Usine-Diego": "Nord", "04-Tulear": "Sud",
    "05-Fianarantsoa": "Sud", "06-Ihosy": "Sud", "07-Majunga": "Nord",
    "08-Manakara": "Sud", "09-Tamatave": "Est", "11-Andranomahery": "Centre",
    "12-Antsirabe": "Centre", "18-Ambanja": "Nord", "19-Sambava": "Nord",
    "21-Nosy-be": "Nord", "23-Morondova": "Nord", "24-Fort-Dauphin": "Sud",
}

TYPES = {
    "SS": "SS (Single serve)", "CU": "CU (Convivial Units)",
    "IC": "IC (Individual/Immediat Consumption)", "FC": "FC (Family/Future Consumption)"
}

# ==============================================================================
# 2. RÉFÉRENTIEL EXACT (Basé sur l'image fournie)
# ==============================================================================

def _generer_catalogue_exact():
    # Liste des articles avec leur Positionnement et Occasion EXACTS
    data_raw = [
        # Booster
        ("Booster Appel-Mix 50CL VER", "PREMIUM", "CU (Convivial Units)"),
        ("Booster Tornado 50CL VER VER", "PREMIUM", "CU (Convivial Units)"),
        # Caprice Ananas
        ("Caprice Ananas 100 cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("Caprice Ananas 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Caprice Ananas 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Caprice Bonbon Anglais
        ("Caprice Bonbon Anglais 100 cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("Caprice Bonbon Anglais 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Caprice Bonbon Anglais 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Bonbon Anglais 33 cl CAN", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Bonbon Anglais 35 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Bonbon Anglais 50 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Caprice Grenadine
        ("Caprice Grenadine 100 cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("Caprice Grenadine 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Caprice Grenadine 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Grenadine 33 cl CAN", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Grenadine 35 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Grenadine 50 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Caprice Orange
        ("Caprice Orange 100 cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("Caprice Orange 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Caprice Orange 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Orange 33 cl CAN", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Orange 35 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Orange 50 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Caprice Citron
        ("Caprice Citron 100 cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("Caprice Citron 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Caprice Citron 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Caprice Citron 50 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Tonic
        ("Tonic 100 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Tonic 30 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # World Cola
        ("World Cola 100cl VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("World Cola 100cl WOCO VER", "MILIEU", "FC (Family/Future Consumption)"),
        ("World Cola 150cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("World Cola 30cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("World Cola 30cl WOCO VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("World Cola 33 cl CAN", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("World Cola 35cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("World Cola 50cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # Beaufort
        ("Beaufort 33 CL CAN", "MILIEU", "SS (Single serve)"),
        ("Beaufort 33CL VER", "PREMIUM", "SS (Single serve)"),
        # FRESH
        ("FRESH 33 cl CAN", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("THB Fresh 33 cl VER", "ENTREE", "SS (Single serve)"),
        ("THB Fresh 65 cl VER", "ENTREE", "CU (Convivial Units)"),
        # Gold
        ("Gold 8 50 cl CAN", "PREMIUM", "SS (Single serve)"),
        ("Gold 8 50 cl VER", "PREMIUM", "SS (Single serve)"),
        ("Gold Blanche 33cl VER", "PREMIUM", "SS (Single serve)"),
        ("Gold Blanche 50 cl CAN", "PREMIUM", "SS (Single serve)"),
        ("Gold Blanche 50 cl VER", "PREMIUM", "SS (Single serve)"),
        ("Gold Blonde 33 cl VER", "PREMIUM", "SS (Single serve)"),
        ("Gold Blonde 50 cl CAN", "PREMIUM", "SS (Single serve)"),
        ("Gold Blonde 50 cl VER", "PREMIUM", "SS (Single serve)"),
        ("Gold Blonde 65 cl VER", "PREMIUM", "CU (Convivial Units)"),
        # Queen
        ("Queen s 65 cl VER", "PREMIUM", "CU (Convivial Units)"),
        # THB
        ("THB Pilsener 33 cl VER", "MILIEU", "SS (Single serve)"),
        ("THB Pilsener 50 cl CAN", "MILIEU", "CU (Convivial Units)"),
        ("THB Pilsener 65 cl VER", "MILIEU", "CU (Convivial Units)"),
        # Cristal
        ("Cristal 100 cl VER", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("Cristal 150 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        ("Cristal 30 cl VER", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("Cristal 50 cl VER", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        # Cristalline
        ("Cristalline 100 cl PET", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("Cristalline 200 cl PET", "PREMIUM", "FC (Family/Future Consumption)"),
        # Eau vive
        ("Eau vive 150 cl PET", "MILIEU", "FC (Family/Future Consumption)"),
        ("Eau vive 50 cl PET", "MILIEU", "IC (Individual/Immediat Consumption)"),
        ("Eau vive 50 cl VER", "MILIEU", "IC (Individual/Immediat Consumption)"),
        # FOSA
        ("FOSA 50 cl CAN", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        # XXL
        ("XXL 30cl BOB VER", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("XXL 30cl VER", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("XXL 33 cl CAN", "PREMIUM", "IC (Individual/Immediat Consumption)"),
        ("XXL 35cl PET", "PREMIUM", "IC (Individual/Immediat Consumption)")
    ]
    
    data = []
    for art, pos, occ in data_raw:
        art_lower = art.lower()
        
        # Déduction Segment
        if "cristal" in art_lower or "eau" in art_lower: segment = "EAUX"
        elif any(x in art_lower for x in ["gold", "thb", "beaufort", "queen", "booster"]): segment = "BIERES"
        else: segment = "BOISSONS"
        
        # Format
        fmt = art.split()[-1].upper() if art.split()[-1].upper() in ["VER", "PET", "CAN"] else "VER"
        if "WOCO" in art_lower: fmt = "VER"
        if "BOB" in art_lower: fmt = "VER"
        
        # Contenance
        match = re.search(r'(\d+)\s*cl', art_lower)
        c_cl = int(match.group(1)) if match else 50
        c_hl = c_cl * 0.0001
        
        data.append({
            "article": art, "segment": segment, "produit": art.split()[0], "parfum": art,
            "positionnement": pos, "occasion": occ, "conditionnement": fmt,
            "format": f"{c_cl} cl {fmt}", "contenance_ci": c_cl, "contenance_hl": c_hl,
            "type_format": occ, "type_format_lib": occ
        })
    return pd.DataFrame(data)

CATALOGUE = _generer_catalogue_exact()
CATALOGUE_PAR_ARTICLE = {meta["article"].lower().strip(): meta for meta in CATALOGUE.to_dict(orient="records")}
ARTICLES_REFERENTIEL = CATALOGUE["article"].tolist()

# ==============================================================================
# 3. UTILITAIRES & FILTRES
# ==============================================================================

def _sans_accents(texte: str) -> str:
    return unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")

def normaliser_nom(nom: str) -> str:
    return re.sub(r'[^a-z0-9_]+', '_', _sans_accents(str(nom).strip().lower())).strip('_')

def normaliser_agence(valeur: object) -> str:
    nom = str(valeur).strip()
    cle = normaliser_nom(nom)
    for a in AGENCES_REFERENCE:
        if normaliser_nom(a) == cle or normaliser_nom(a.split("-", 1)[1]) == cle:
            return a
    if re.fullmatch(r"\d+(_0)?", cle): 
        return next((a for a in AGENCES_REFERENCE if a.startswith(f"{int(cle.split('_', 1)[0]):02d}-")), nom)
    return nom

def region_depuis_agence(valeur: object) -> str: 
    return REGION_PAR_AGENCE.get(normaliser_agence(valeur), "Non renseigné")

def assurer_dimensions_filtres(df: pd.DataFrame, catalogue: dict, types: dict) -> pd.DataFrame:
    for col in ["positionnement", "occasion", "conditionnement", "contenance_ci", "contenance_hl", "region", "type_format"]:
        if col not in df.columns: df[col] = "Non renseigné"
        if catalogue:
            champ = "type_format_lib" if col == "type_format" else col
            articles = df["article"].astype(str).str.lower().str.strip()
            correspondances = {a: m.get(champ, "Non renseigné") for a, m in catalogue.items()}
            masque_vide = df[col].astype(str).str.strip().isin(["", "Non renseigné", "nan", "None"])
            df.loc[masque_vide, col] = articles[masque_vide].map(correspondances).fillna("Non renseigné")
        df[col] = df[col].astype(str).str.strip()
    return df

def options_filtre_cascade(df: pd.DataFrame, col: str, filtres: list, selections: dict) -> list:
    if col not in df.columns: return []
    df_filtre = df.copy()
    for c, _ in filtres:
        if c != col and selections.get(c) and c in df_filtre.columns:
            df_filtre = df_filtre[df_filtre[c].isin(selections[c])]
    options = df_filtre[col].dropna().unique().tolist()
    if col in ["article", "positionnement", "occasion", "conditionnement", "contenance_ci", "contenance_hl"]:
        options = list(set(options) | set(CATALOGUE[col].dropna().unique().tolist()))
    return options

# ==============================================================================
# 4. LECTURE DES DONNÉES
# ==============================================================================

_MOIS_MAP = {
    "janvier": 1, "janv": 1, "jan": 1, "january": 1, "fevrier": 2, "fevr": 2, "fev": 2, "feb": 2,
    "february": 2, "mars": 3, "mar": 3, "march": 3, "avril": 4, "avr": 4, "apr": 4, "april": 4,
    "mai": 5, "may": 5, "juin": 6, "jun": 6, "june": 6, "juillet": 7, "juil": 7, "jul": 7, "july": 7,
    "aout": 8, "aug": 8, "august": 8, "septembre": 9, "sept": 9, "sep": 9, "september": 9,
    "octobre": 10, "oct": 10, "october": 10, "novembre": 11, "nov": 11, "november": 11,
    "decembre": 12, "dec": 12, "december": 12,
}

def normaliser_mois(valeur) -> float:
    if pd.isna(valeur): return np.nan
    if isinstance(valeur, (int, float)): return float(valeur)
    texte = str(valeur).strip().lower()
    try: return float(texte.replace(",", "."))
    except ValueError: pass
    cle = re.sub(r"[^a-z]", "", _sans_accents(texte))
    return float(_MOIS_MAP.get(cle, np.nan))

def _detecter_format_pivote(df: pd.DataFrame) -> bool:
    if df.shape[1] < 7: return False
    annee0 = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    mois1 = df.iloc[:, 1].map(normaliser_mois)
    return annee0.between(1990, 2100).sum() > len(df) * 0.3 and mois1.notna().sum() > len(df) * 0.3

def normaliser_lignes_data_brut(df_raw: pd.DataFrame, articles_referentiel: list[str]) -> pd.DataFrame:
    if _detecter_format_pivote(df_raw):
        rename = {df_raw.columns[i]: col for i, col in enumerate(["annee", "mois", "segment", "produit", "agence", "nature", "hl"])}
        df = df_raw.rename(columns=rename).copy()
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
        df["mois"] = df["mois"].map(normaliser_mois)
        df = df.dropna(subset=["annee", "mois"]).copy()
        df["mois"] = df["mois"].astype(int)
        df["hl"] = pd.to_numeric(df["hl"], errors="coerce").fillna(0.0)
        for c in ("segment", "produit", "agence", "nature"): df[c] = df[c].astype(str).str.strip()
        df = df[~(df["segment"].str.contains("total", case=False) | df["produit"].str.contains("total", case=False) | df["agence"].str.contains("total", case=False))].copy()
        df["periode"] = df["annee"].astype(str) + "-" + df["mois"].astype(str).str.zfill(2)
        df["colis"] = 0.0
        df["origine"] = "Donnée source"
        df["article"] = df["produit"] + " " + df["segment"]
        return df.reset_index(drop=True)
    return df_raw

def lire_et_normaliser(contenu: bytes | None, nom: str, chemin: str | None, annee_cloture: int, mois_cloture: int) -> pd.DataFrame:
    nom_fichier = Path(nom if contenu is not None else chemin or "").name.lower()
    est_data_brut = nom_fichier == "data_brut.xlsx"
    
    if contenu is not None:
        flux = io.BytesIO(contenu)
        if nom.lower().endswith(".csv"): df_raw = pd.read_csv(flux, sep=None, encoding="utf-8-sig", engine="python")
        else:
            feuilles = pd.ExcelFile(flux).sheet_names
            feuille = next((f for f in feuilles if normaliser_nom(f) == "export"), feuilles[0]) if est_data_brut else 0
            df_raw = pd.read_excel(flux, sheet_name=feuille, header=None) if est_data_brut else pd.read_excel(flux, sheet_name=feuille)
    else:
        chemin_str = str(chemin)
        if chemin_str.lower().endswith(".csv"): df_raw = pd.read_csv(chemin_str, sep=None, encoding="utf-8-sig", engine="python")
        else:
            feuilles = pd.ExcelFile(chemin_str).sheet_names
            feuille = next((f for f in feuilles if normaliser_nom(f) == "export"), feuilles[0]) if est_data_brut else 0
            df_raw = pd.read_excel(chemin_str, sheet_name=feuille, header=None) if est_data_brut else pd.read_excel(chemin_str, sheet_name=feuille)

    df = normaliser_lignes_data_brut(df_raw, ARTICLES_REFERENTIEL) if est_data_brut else df_raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    col_map = {"annee": "annee", "mois": "mois", "agence": "agence", "agences": "agence", "segment": "segment", "produit": "produit", "marque": "produit", "article": "article", "articles": "article", "nature": "nature", "hl": "hl", "volume": "hl", "colis": "colis"}
    df = df.rename(columns={c: col_map[normaliser_nom(c)] for c in df.columns if normaliser_nom(c) in col_map})
    
    defaut = {"annee": 2026, "mois": 1, "periode": "2026-01", "agence": "Non renseigné", "region": "Non renseigné", "segment": "Non renseigné", "produit": "Non renseigné", "parfum": "Non renseigné", "format": "Non renseigné", "type_format": "Non renseigné", "article": "Non renseigné", "nature": "Prévision", "colis": 0.0, "hl": 0.0, "origine": "Donnée source", "positionnement": "Non renseigné", "occasion": "Non renseigné", "conditionnement": "Non renseigné", "contenance_ci": 0.0, "contenance_hl": 0.0}
    for k, v in defaut.items():
        if k not in df.columns: df[k] = v

    df = df[COLONNES].copy()
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").fillna(2026).astype(int)
    df["mois"] = df["mois"].map(normaliser_mois).fillna(1).astype(int)
    df["periode"] = df["annee"].astype(str) + "-" + df["mois"].astype(str).str.zfill(2)
    df["agence"] = df["agence"].map(normaliser_agence)
    df["region"] = df["agence"].map(region_depuis_agence)
    for c in ["colis", "hl"]: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    
    df = assurer_dimensions_filtres(df, CATALOGUE_PAR_ARTICLE, TYPES)
    df = df[~df["article"].str.lower().isin(["", "non renseigné", "total", "nan"])].copy()
    cond_realise = (df["annee"] < annee_cloture) | ((df["annee"] == annee_cloture) & (df["mois"] <= mois_cloture))
    df["nature"] = np.where(cond_realise, "Réalisé", "Prévision")
    return df

# ==============================================================================
# 5. SAISONNALITÉ & SAAR
# ==============================================================================

def annees_completes_saisonnalite(donnees: pd.DataFrame, annee_debut: int, annee_fin: int, annee_cloture: int, mois_cloture: int) -> list[int]:
    realise = donnees.loc[donnees["nature"].eq("Réalisé") & donnees["mois"].between(1, 12)]
    if realise.empty: return []
    mois_par_annee = (realise.loc[realise["annee"].between(annee_debut, annee_fin)].drop_duplicates(["annee", "mois"]).groupby("annee")["mois"].nunique())
    res = []
    for annee in sorted(mois_par_annee.index):
        annee = int(annee)
        if annee == annee_cloture and mois_cloture < 12: continue
        if int(mois_par_annee.loc[annee]) == 12: res.append(annee)
    return res

def calculer_indices_saisonnalite(donnees: pd.DataFrame, valeur: str, annee_debut: int, annee_fin: int, annee_cloture: int, mois_cloture: int) -> pd.DataFrame:
    annees = annees_completes_saisonnalite(donnees, annee_debut, annee_fin, annee_cloture, mois_cloture)
    if not annees: return pd.DataFrame({"Mois": MOIS_NOMS, "Volume moyen": 0.0, "Nombre de périodes": 0, "Indice saisonnier": float("nan")})
    selection = donnees.loc[donnees["nature"].eq("Réalisé") & donnees["annee"].isin(annees) & donnees["mois"].between(1, 12)]
    volumes = selection.groupby(["annee", "mois"])[valeur].sum().unstack("mois").reindex(index=annees, columns=range(1, 13)).fillna(0.0)
    moyennes_annuelles = volumes.sum(axis=1) / 12.0
    ratios = volumes.div(moyennes_annuelles.replace(0, np.nan), axis=0)
    indices = ratios.mean(axis=0).fillna(0.0)
    if float(indices.sum()) > 0: indices = indices * 12.0 / float(indices.sum())
    return pd.DataFrame({"Mois": MOIS_NOMS, "Volume moyen": volumes.mean(axis=0).to_numpy(), "Nombre de périodes": len(annees), "Indice saisonnier": indices.to_numpy()})

@st.cache_data(show_spinner="Calcul des prévisions SAAR...")
def appliquer_projection_saar(df: pd.DataFrame, annee_cloture: int, mois_cloture: int, annee_cible: int, taux_croissance: float) -> pd.DataFrame:
    if annee_cible < annee_cloture: return df
    cles = ["agence", "article"]
    dimensions = ["agence", "region", "segment", "produit", "parfum", "format", "type_format", "article", "origine", "positionnement", "occasion", "conditionnement", "contenance_ci", "contenance_hl"]
    realise_ytd = df.loc[(df["nature"] == "Réalisé") & (df["annee"] == annee_cloture) & (df["mois"] <= mois_cloture)]
    
    if annee_cible > annee_cloture:
        base_df = df.loc[(df["annee"] == annee_cloture) & (df["nature"].isin(["Réalisé", "Prévision"]))]
        if base_df.empty: return df
        cumul_base = base_df.groupby(cles)[["hl", "colis"]].sum()
        derniere_ligne = base_df.sort_values(["annee", "mois"]).drop_duplicates(cles, keep="last").set_index(cles)
    else:
        if realise_ytd.empty: return df
        cumul_base = realise_ytd.groupby(cles)[["hl", "colis"]].sum()
        derniere_ligne = realise_ytd.sort_values(["annee", "mois"]).drop_duplicates(cles, keep="last").set_index(cles)

    df_ref = df.loc[df["annee"].isin([2024, 2025]) & (df["nature"] == "Réalisé")]
    profils_ref = {}
    if not df_ref.empty:
        volumes_mensuels = df_ref.groupby([*cles, "mois"])["hl"].sum().unstack("mois").fillna(0.0).reindex(columns=range(1, 13), fill_value=0.0).clip(lower=0.0)
        totaux = volumes_mensuels.sum(axis=1)
        profils_ref = {c: p.to_numpy(dtype=float) for c, p in volumes_mensuels.div(totaux.where(totaux > 0), axis=0).mul(12.0).iterrows() if totaux.loc[c] > 0}

    volumes_annee_precedente = df.loc[df["annee"] == annee_cible - 1].groupby([*cles, "mois"])[["hl", "colis"]].sum()
    taux_annuel = 1.0 + max(taux_croissance, 1.0) / 100.0
    facteur_croissance = taux_annuel ** (annee_cible - annee_cloture)
    
    projections = []
    for cle, volumes in cumul_base.iterrows():
        cle = cle if isinstance(cle, tuple) else (cle,)
        profil = profils_ref.get(cle, np.ones(12, dtype=float))
        if profil[:mois_cloture].sum() <= 0: profil = np.ones(12, dtype=float)
        
        poids_ecoule = profil[:mois_cloture].sum()
        base_hl = max(0.0, float(volumes["hl"]) / poids_ecoule * 12.0)
        base_colis = max(0.0, float(volumes["colis"]) / poids_ecoule * 12.0)
        
        if annee_cible > annee_cloture:
            base_hl *= taux_annuel ** (annee_cible - annee_cloture - 1)
            base_colis *= taux_annuel ** (annee_cible - annee_cloture - 1)
            
        ligne_ref = derniere_ligne.loc[cle]

        for mois in range(1, 13):
            if annee_cible == annee_cloture and mois <= mois_cloture: continue
            facteur_mois = HAUSSE_SAISONNIERE_PREVISION.get(mois, 1.0)
            ligne = {col: cle[cles.index(col)] if col in cles else ligne_ref[col] for col in dimensions}
            
            if (*cle, mois) in volumes_annee_precedente.index and volumes_annee_precedente.loc[(*cle, mois)]["hl"] > 0:
                plancher = volumes_annee_precedente.loc[(*cle, mois)]
                vol_hl_min, vol_colis_min = max(0.0, float(plancher["hl"])), max(0.0, float(plancher["colis"]))
                vol_hl_min *= taux_annuel
                vol_colis_min *= taux_annuel
            else:
                vol_hl_min = base_hl * profil[mois - 1] / 12.0
                vol_colis_min = base_colis * profil[mois - 1] / 12.0

            ligne.update({"annee": annee_cible, "mois": mois, "periode": f"{annee_cible}-{mois:02d}", "nature": "Prévision",
                          "hl": max(vol_hl_min, base_hl * profil[mois - 1] / 12.0) * facteur_mois,
                          "colis": max(vol_colis_min, base_colis * profil[mois - 1] / 12.0) * facteur_mois})
            projections.append(ligne)

    if not projections: return df
    masque_existant = (df["annee"] == annee_cible) & (df["nature"] == "Prévision")
    if annee_cible == annee_cloture: masque_existant &= df["mois"].gt(mois_cloture)
    return pd.concat([df.loc[~masque_existant], pd.DataFrame(projections).reindex(columns=df.columns)], ignore_index=True)

@st.cache_data(show_spinner="Reconstitution des prévisions historiques...")
def reconstituer_previsions_historiques(df: pd.DataFrame, annee_cloture: int, taux_croissance: float) -> pd.DataFrame:
    annees_presentes = set(df["annee"].unique())
    annees_completes = {int(a) for a, p in df.groupby("annee")["mois"].agg(["min", "max"]).iterrows() if p["min"] == 1 and p["max"] == 12}
    previsions, previsions_par_annee, facteur_min = [], {}, 1.0 + max(taux_croissance, 1.0) / 100.0

    for annee_cible in sorted(annees_presentes):
        annee_precedente = int(annee_cible) - 1
        if annee_cible >= annee_cloture or annee_precedente not in annees_completes: continue
        historique = df.loc[df["annee"] < annee_cible].copy(); historique["nature"] = "Réalisé"
        prevision = appliquer_projection_saar(historique, annee_precedente, 12, int(annee_cible), taux_croissance)
        prevision = prevision.loc[prevision["annee"].eq(annee_cible) & prevision["nature"].eq("Prévision")].copy()
        
        references = previsions_par_annee[annee_precedente].groupby(["agence", "article"])[["hl", "colis"]].sum() if annee_precedente in previsions_par_annee else df.loc[df["annee"].eq(annee_precedente)].groupby(["agence", "article"])[["hl", "colis"]].sum()
        for cle, indices in prevision.groupby(["agence", "article"]).groups.items():
            if cle not in references.index: continue
            for col in ("hl", "colis"):
                v_prev = prevision.loc[indices, col].sum()
                v_min = max(0.0, float(references.loc[cle, col])) * facteur_min
                if 0 < v_prev < v_min: prevision.loc[indices, col] *= v_min / v_prev
                    
        prevision["nature"] = "Prévision reconstituée"
        previsions_par_annee[int(annee_cible)] = prevision; previsions.append(prevision)
    return pd.concat(previsions, ignore_index=True) if previsions else df.iloc[0:0]

# ==============================================================================
# 6. AFFICHAGE & UI
# ==============================================================================

st.markdown("""
<style>
:root { --red: #d7193f; --green: #0e8a4a; }
.stApp { background: radial-gradient(1000px 400px at 100% -10%, #fff1f4, transparent), radial-gradient(1000px 400px at 0% 110%, #eaf7f0, transparent), #fff; }
.block-container { max-width: 1440px; padding: 2rem 4vw; }
.titre { font-size: 2.5rem; font-weight: 800; color: #121017; }
.titre::after { content: ""; display: block; width: 72px; height: 4px; margin-top: .8rem; background: linear-gradient(90deg, var(--red) 50%, var(--green) 50%); border-radius: 99px; }
div[data-testid="stMetric"] { background: #fff; border: 1px solid #e2e0e6; border-radius: 16px; padding: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,.03); border-top: 4px solid var(--red); }
div[data-testid="stColumn"]:nth-child(even) div[data-testid="stMetric"] { border-top-color: var(--green); }
div[data-testid="stMetric"] label { font-weight: 700; color: #5c5665; text-transform: uppercase; font-size: 0.78rem; }
div[data-testid="stMetricValue"] { font-weight: 800; color: #121017; }
</style>
""", unsafe_allow_html=True)

def nombre(x: float, dec: int) -> str: return f"{x:,.{dec}f}".replace(",", " ")
def etiquette(periode: str) -> str:
    p = str(periode).split("-")
    return f"{MOIS[int(p[1]) - 1]}-{p[0][-2:]}" if len(p) == 2 and p[1].isdigit() else str(periode)

def afficher_vue(df: pd.DataFrame, mode: str, dec: int = 0, couleur=None, hauteur=350):
    if mode == "Tableau":
        st.dataframe(df.round(dec), width="stretch")
        return
    df_graphique = df.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all").dropna(axis=0, how="all")
    if df_graphique.empty: return st.info("Aucune valeur numérique.")
    
    nom_axe = df_graphique.index.name or "Période"
    df_melt = df_graphique.reset_index().melt(id_vars=nom_axe, var_name="Série", value_name="Valeur")
    df_melt[nom_axe] = df_melt[nom_axe].astype(str)
    
    if mode == "Courbes":
        chart = alt.Chart(df_melt).mark_line(interpolate="monotone", point=alt.OverlayMarkDef(filled=True, size=35)).encode(
            x=alt.X(f"{nom_axe}:N", sort=df_graphique.index.astype(str).tolist(), title=nom_axe),
            y=alt.Y("Valeur:Q", title="Volume"),
            color=alt.Color("Série:N", scale=alt.Scale(scheme="tableau10"), legend=alt.Legend(title=None)),
            tooltip=[nom_axe, "Série", alt.Tooltip("Valeur:Q", format=",.2f")]
        )
        st.altair_chart(chart.properties(height=hauteur), width="stretch")
    elif mode == "Histogramme":
        chart = alt.Chart(df_melt).mark_bar().encode(
            x=alt.X(f"{nom_axe}:N", sort=df_graphique.index.astype(str).tolist(), title=nom_axe),
            y=alt.Y("Valeur:Q", title="Volume"),
            color=alt.Color("Série:N", scale=alt.Scale(scheme="tableau10"), legend=alt.Legend(title=None)),
            tooltip=[nom_axe, "Série", alt.Tooltip("Valeur:Q", format=",.2f")]
        )
        st.altair_chart(chart.properties(height=hauteur), width="stretch")

def trier(valeurs, col):
    v = [x for x in valeurs if pd.notna(x)]
    if col in {"contenance_ci", "contenance_hl"}: return sorted(v, key=lambda x: float(x) if str(x).replace('.','',1).isdigit() else 999)
    if col == "conditionnement": return sorted(v, key=lambda x: ({"CAN": 0, "PET": 1, "VER": 2}.get(str(x), 99), str(x)))
    return sorted(v)

# ==============================================================================
# 7. INITIALISATION
# ==============================================================================

FICHIERS_EXISTANTS = [d / f for d in DOSSIERS for f in FICHIERS_CANDIDATS if (d / f).exists()]

st.markdown('<div class="titre">Moteur S&OP : Prévision SAAR & Rolling Forecast</div>', unsafe_allow_html=True)

st.sidebar.header("📁 Source & Import")
if st.sidebar.button("Réinitialiser les imports"):
    st.session_state.clear(); st.rerun()

importe = st.sidebar.file_uploader("Importer un fichier (.csv / .xlsx)", type=["csv", "xlsx"])
chemin = FICHIERS_EXISTANTS[0] if FICHIERS_EXISTANTS else None

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Cutoff S&OP")
col_c1, col_c2 = st.sidebar.columns(2)
annee_cloture = col_c1.number_input("Année Clôture", min_value=2000, max_value=2036, value=2026)
mois_cloture = col_c2.selectbox("Mois Pivot", options=list(range(1, 13)), index=8, format_func=lambda m: f"{m} - {MOIS[m-1]}")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Cible & Affichage")
annee_cible = st.sidebar.number_input("Année Cible", min_value=2000, max_value=2040, value=int(annee_cloture) + 1)
mois_cible_str = st.sidebar.selectbox("Mois Cible", options=["Tous les mois"] + MOIS_COMPLETS, index=0)

val_choix = st.sidebar.radio("Métrique", options=["hl", "colis"], format_func=lambda x: "Hectolitres (hl)" if x == "hl" else "Colis (cs)", horizontal=True)
dec = st.sidebar.number_input("Décimales", min_value=0, max_value=4, value=0)
mode_affichage = st.sidebar.selectbox("Mode d'affichage", options=["Tableau", "Courbes", "Histogramme"], index=1)

# --- Chargement des données ---
df_brut = None
if importe is not None:
    contenu_import = importe.getvalue()
    empreinte = hashlib.sha256(contenu_import).hexdigest()
    if st.session_state.get("empreinte_import") != empreinte:
        st.session_state["df_courant"] = lire_et_normaliser(contenu_import, importe.name, None, int(annee_cloture), int(mois_cloture))
        st.session_state["empreinte_import"] = empreinte
    df_brut = st.session_state.get("df_courant")
elif "df_courant" in st.session_state: 
    df_brut = st.session_state["df_courant"]
elif chemin:
    df_brut = lire_et_normaliser(None, "", str(chemin), int(annee_cloture), int(mois_cloture))
    st.session_state["df_courant"] = df_brut

if df_brut is None or df_brut.empty:
    st.warning("⚠️ Aucune donnée. Importez un fichier via la barre latérale.")
    st.stop()

# --- Application des filtres ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtres")
if st.sidebar.button("🔄 Réinitialiser les filtres"):
    for col, _ in FILTRES:
        if f"f_{col}" in st.session_state: del st.session_state[f"f_{col}"]
    st.rerun()

selections_filtres = {col: st.session_state.get(f"f_{col}", []) for col, _ in FILTRES}
for col, label in FILTRES:
    if col not in df_brut.columns: continue
    options = options_filtre_cascade(df_brut, col, FILTRES, selections_filtres)
    options = [o for o in options if pd.notna(o) and str(o).strip().lower() not in ("", "nan", "none")]
    if col == "agence": options = [a for a in AGENCES_REFERENCE if a in set(options)]
    else: options = trier(options, col)
    if not options: continue
    cle = f"f_{col}"
    if cle in st.session_state: st.session_state[cle] = [v for v in st.session_state[cle] if v in options]
    selections_filtres[col] = st.sidebar.multiselect(label, options, key=cle, placeholder="Tous")

d = df_brut.copy()
for col, _ in FILTRES:
    if selections_filtres[col]: d = d[d[col].isin(selections_filtres[col])]
recherche = st.sidebar.text_input("🔎 Recherche article", "")
if recherche: d = d[d["article"].str.contains(recherche, case=False, na=False)]

# --- SAAR & Cumuls ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Moteur SAAR")
activer_saar = st.sidebar.checkbox("Activer la projection SAAR", value=True)
afficher_prev_hist = st.sidebar.checkbox("Afficher les prévisions historiques", value=True)
taux_saar = st.sidebar.number_input("Hausse annuelle minimale (%)", min_value=1.0, value=1.0, step=0.5)

df_previsions_hist = df_brut.iloc[0:0].copy()
df_previsions_toutes = df_brut.iloc[0:0].copy()

if activer_saar:
    df_previsions_toutes = reconstituer_previsions_historiques(df_brut, int(annee_cloture) + 1, float(taux_saar))
    if afficher_prev_hist: df_previsions_hist = df_previsions_toutes.loc[df_previsions_toutes["annee"].lt(annee_cloture)].copy()
    
    if annee_cible >= annee_cloture:
        df_brut = appliquer_projection_saar(df_brut, int(annee_cloture), int(mois_cloture), int(annee_cloture), float(taux_saar))
        for a_proj in range(int(annee_cloture) + 1, int(annee_cible) + 1):
            df_brut = appliquer_projection_saar(df_brut, int(annee_cloture), int(mois_cloture), a_proj, float(taux_saar))

d_tendance = pd.concat([d, df_previsions_hist], ignore_index=True).replace("Prévision reconstituée", "Prévision")

# --- KPI Cumuls ---
ANNEE_DEBUT_CUMUL = 2024
m_real = (d["nature"].eq("Réalisé") & d["annee"].ge(ANNEE_DEBUT_CUMUL) & (d["annee"].lt(annee_cloture) | (d["annee"].eq(annee_cloture) & d["mois"].le(mois_cloture))))
m_prev = (d["nature"].eq("Prévision") & d["annee"].eq(annee_cloture) & d["mois"].gt(mois_cloture))
vol_real = float(d.loc[m_real, val_choix].sum()); vol_prev = float(d.loc[m_prev, val_choix].sum())

k1, k2, k3 = st.columns(3)
k1.metric("Cumul réalisé à date", f"{nombre(vol_real, dec)} {val_choix}")
k2.metric(f"Cumul prévision ({MOIS[mois_cloture]} → déc)", f"{nombre(vol_prev, dec)} {val_choix}")
k3.metric("Cumul total (Réalisé + Prév)", f"{nombre(vol_real + vol_prev, dec)} {val_choix}")

# --- Onglets ---
st.markdown("---")
tab_comp, tab_detail, tab_is = st.tabs(["📊 Prévision vs Réalisé", "🔍 Détail des cumuls", "📈 Indice saisonnier"])

# ==============================================================================
# ONGLET 1 : PRÉVISION VS RÉALISÉ (Vue Globale par Année en Courbes)
# ==============================================================================
with tab_comp:
    st.subheader(f"Historique des volumes : Réalisé vs Prévision (Cible : {annee_cible})")
    
    df_comp = d_tendance.groupby(["annee", "nature"])[val_choix].sum().unstack("nature").fillna(0.0)
    if "Réalisé" not in df_comp.columns: df_comp["Réalisé"] = 0.0
    if "Prévision" not in df_comp.columns: df_comp["Prévision"] = 0.0
    
    df_comp = df_comp[df_comp.index <= annee_cible]
    df_comp.index.name = "Année"
    df_comp = df_comp.reset_index()
    df_comp["Année"] = df_comp["Année"].astype(str)
    
    st.caption(
        "Ce graphique compare le volume global de chaque année. "
        "Le 'Réalisé' montre les années clôturées. Pour l'année en cours, la courbe 'Prévision' montre l'atterrissage. "
        "Les années futures (ex: 2027) affichent la projection SAAR."
    )
    
    if mode_affichage == "Tableau":
        st.dataframe(df_comp.set_index("Année").round(dec), width="stretch")
    else:
        df_melt = df_comp.melt(id_vars="Année", var_name="Type", value_name="Volume")
        
        chart = alt.Chart(df_melt).mark_line(
            interpolate="monotone", 
            point=alt.OverlayMarkDef(filled=True, size=80)
        ).encode(
            x=alt.X("Année:N", sort=df_comp["Année"].tolist(), title="Année"),
            y=alt.Y("Volume:Q", title=f"Volume total ({val_choix})"),
            color=alt.Color("Type:N", scale=alt.Scale(
                domain=["Réalisé", "Prévision"], 
                range=[COULEUR_REALISE, COULEUR_PREVISION]
            ), legend=alt.Legend(title="Type de donnée")),
            strokeDash=alt.StrokeDash("Type:N", scale=alt.Scale(domain=["Réalisé", "Prévision"], range=[[1, 0], [5, 5]]), legend=None),
            tooltip=["Année", "Type", alt.Tooltip("Volume:Q", format=",.0f")]
        )
        
        st.altair_chart(chart.properties(height=450, width="container"), use_container_width=True)

# ==============================================================================
# ONGLET 2 : DÉTAIL DES CUMULS
# ==============================================================================
with tab_detail:
    st.subheader("Détail par article et agence")
    dims = ["article", "agence", "segment", "produit"]
    base = d.loc[m_real | m_prev].copy()
    if not base.empty:
        base["col_cumul"] = np.where(base["nature"].eq("Réalisé"), base["annee"].map(lambda a: f"Réalisé {a}"), "Prévision")
        pivot = base.pivot_table(index=dims, columns="col_cumul", values=val_choix, aggfunc="sum").fillna(0.0).reset_index()
        if mode_affichage == "Tableau":
            st.dataframe(pivot.round(dec), width="stretch", height=500)
        else:
            pivot_agence = base.pivot_table(index="agence", columns="col_cumul", values=val_choix, aggfunc="sum").fillna(0.0)
            afficher_vue(pivot_agence, mode_affichage, dec, hauteur=450)
    else:
        st.info("Aucune donnée pour les filtres actifs.")

# ==============================================================================
# ONGLET 3 : INDICE SAISONNIER
# ==============================================================================
with tab_is:
    st.subheader("Indice de saisonnalité par mois")
    annees_reelles = sorted(int(a) for a in df_brut.loc[df_brut["nature"].eq("Réalisé"), "annee"].unique())
    annees_debut_possibles = annees_reelles[:-1]
    
    indices_saisonnalite = pd.DataFrame()
    if annees_debut_possibles:
        c1, c2 = st.columns(2)
        annee_debut = c1.selectbox("Année début", options=annees_debut_possibles, index=0, key="sais_deb")
        annees_fin = [a for a in annees_reelles if a > annee_debut]
        if st.session_state.get("sais_fin") not in annees_fin: st.session_state["sais_fin"] = annees_fin[-1]
        annee_fin = c2.selectbox("Année fin", options=annees_fin, key="sais_fin")
        
        d_is = d.loc[~d["article"].astype(str).str.lower().str.contains("total", na=False)]
        indices_saisonnalite = calculer_indices_saisonnalite(d_is, val_choix, int(annee_debut), int(annee_fin), int(annee_cloture), int(mois_cloture))
        
        if not indices_saisonnalite.empty and indices_saisonnalite["Indice saisonnier"].notna().any():
            df_graph_is = indices_saisonnalite.set_index("Mois")[["Indice saisonnier"]]
            afficher_vue(df_graph_is, mode_affichage, dec=2, hauteur=350)
            st.markdown("#### Tableau détaillé")
            st.dataframe(indices_saisonnalite.round(2), width="stretch", hide_index=True)
        else:
            st.info("Données insuffisantes pour calculer l'IS.")
    else:
        st.info("Il faut au moins deux années de réalisés pour l'IS.")

# --- Export ---
st.markdown("---")
tampon = io.BytesIO()
with pd.ExcelWriter(tampon, engine="openpyxl") as xl:
    if not d.empty: d.to_excel(xl, index=False, sheet_name="Données Filtrées")
    if not df_previsions_toutes.empty: df_previsions_toutes.to_excel(xl, index=False, sheet_name="Prévisions Historiques")
    df_annee_cible = d_tendance[d_tendance["annee"] == annee_cible].copy()
    if not df_annee_cible.empty: df_annee_cible.to_excel(xl, index=False, sheet_name=f"Prévisions {annee_cible}")

st.download_button("📥 Télécharger l'export complet (.xlsx)", data=tampon.getvalue(), file_name=f"Export_SOP_{annee_cible}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
