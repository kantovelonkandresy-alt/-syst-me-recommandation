# app.py
# NOVA RECO - Application Web (Streamlit) du système de recommandation
# utilisateur-item, avec un design glassmorphism (light mode) enrichi.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="NOVA RECO",
    page_icon="✨",
    layout="wide",
)

# --- Style glassmorphism enrichi (light mode) ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Fond animé en dégradé mouvant */
    .stApp {
        background: linear-gradient(-45deg, #eef2ff, #f5f3ff, #eafaf6, #fdf2f8);
        background-size: 400% 400%;
        animation: nova-gradient 18s ease infinite;
    }
    @keyframes nova-gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Cartes "verre" */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.7);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15), inset 0 0 0 1px rgba(255,255,255,0.4);
        padding: 1rem 1.2rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 40px rgba(99, 102, 241, 0.22);
    }

    /* Hero / titre */
    .nova-hero {
        text-align: center;
        padding: 1.8rem 1rem 1.2rem 1rem;
    }
    .nova-titre {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #a855f7, #06b6d4, #6366f1);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: nova-shine 6s linear infinite;
        margin-bottom: 0;
        letter-spacing: 1px;
    }
    @keyframes nova-shine {
        to { background-position: 300% center; }
    }
    .nova-soustitre {
        color: #6b7280;
        font-size: 1.05rem;
        margin-top: 0.3rem;
        font-weight: 400;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-right: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* Cartes statistiques */
    .nova-stat-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(14px);
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.7);
        box-shadow: 0 6px 20px rgba(99,102,241,0.12);
        padding: 1.1rem 1rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .nova-stat-card:hover {
        transform: scale(1.03);
    }
    .nova-stat-nombre {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .nova-stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Boutons néon */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7, #06b6d4);
        background-size: 200% auto;
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        transition: all 0.25s ease;
    }
    div.stButton > button:hover {
        background-position: right center;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 26px rgba(168, 85, 247, 0.5);
    }

    /* Badge score */
    .nova-badge {
        display: inline-block;
        background: linear-gradient(90deg, rgba(99,102,241,0.18), rgba(6,182,212,0.18));
        border: 1px solid rgba(99,102,241,0.35);
        color: #4338ca;
        border-radius: 999px;
        padding: 0.2rem 0.8rem;
        font-size: 0.85rem;
        font-weight: 700;
        margin-left: 0.5rem;
    }

    /* Ligne résultat avec effet au survol */
    .nova-ligne {
        background: rgba(255,255,255,0.5);
        border-radius: 14px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(255,255,255,0.6);
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .nova-ligne:hover {
        transform: translateX(4px);
        background: rgba(255,255,255,0.75);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def charger_systeme():
    """
    Charge les données et construit le système de recommandation.
    @st.cache_data évite de relire le CSV à chaque interaction de l'utilisateur.
    """
    donnees = obtenir_donnees()
    genres = obtenir_genres()
    return donnees, genres


# --- En-tête ---
st.markdown(
    """
    <div class="nova-hero">
        <p class="nova-titre">✨ NOVA RECO</p>
        <p class="nova-soustitre">
            Système de recommandation intelligent basé sur un graphe utilisateur-item
            <br>Projet L2 — École Supérieure Polytechnique
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)

# --- Cartes statistiques ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class="nova-stat-card">
                <div class="nova-stat-nombre">{len(donnees)}</div>
                <div class="nova-stat-label">Utilisateurs</div>
            </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div class="nova-stat-card">
                <div class="nova-stat-nombre">{len(genres)}</div>
                <div class="nova-stat-label">Films</div>
            </div>""",
        unsafe_allow_html=True,
    )
with col3:
    nb_genres = len(set(genres.values()))
    st.markdown(
        f"""<div class="nova-stat-card">
                <div class="nova-stat-nombre">{nb_genres}</div>
                <div class="nova-stat-label">Genres</div>
            </div>""",
        unsafe_allow_html=True,
    )

st.write("")

# --- Menu de navigation ---
page = st.sidebar.radio(
    "Navigation",
    [
        "🕸️ Graphe utilisateur-item",
        "🔗 Utilisateurs similaires",
        "🎯 Recommandations",
        "📋 Liste des utilisateurs",
        "➕ Ajouter un utilisateur",
    ],
)


# --- Page : Graphe ---
if page == "🕸️ Graphe utilisateur-item":
    with st.container(border=True):
        st.header("🕸️ Visualisation du graphe")
        st.write(
            "Les noeuds **bleus** sont les utilisateurs, les noeuds **oranges** "
            "sont les films. La taille d'un noeud dépend de son nombre de connexions."
        )
        graphe = creer_graphe()
        fig = obtenir_figure_graphe(graphe)
        st.pyplot(fig)


# --- Page : Utilisateurs similaires ---
elif page == "🔗 Utilisateurs similaires":
    with st.container(border=True):
        st.header("🔗 Trouver les utilisateurs similaires")
        utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

        if st.button("Rechercher", key="btn_similaires"):
            similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
            if similaires:
                st.subheader(f"Utilisateurs similaires à {utilisateur}")
                for nom, score in similaires:
                    st.markdown(
                        f"<div class='nova-ligne'>👤 <b>{nom}</b> "
                        f"<span class='nova-badge'>similarité : {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")


# --- Page : Recommandations ---
elif page == "🎯 Recommandations":
    with st.container(border=True):
        st.header("🎯 Obtenir des recommandations")
        utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

        if st.button("Générer les recommandations", key="btn_reco"):
            recommandations = systeme.generer_recommandations(utilisateur)
            if recommandations:
                st.subheader(f"Recommandations pour {utilisateur}")
                for film, score in recommandations:
                    genre = genres.get(film, "Genre inconnu")
                    st.markdown(
                        f"<div class='nova-ligne'>🎬 <b>{film}</b> — <i>{genre}</i> "
                        f"<span class='nova-badge'>score : {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucune recommandation disponible pour {utilisateur}.")


# --- Page : Liste des utilisateurs ---
elif page == "📋 Liste des utilisateurs":
    with st.container(border=True):
        st.header("📋 Tous les utilisateurs et leurs films")
        for nom, films in donnees.items():
            with st.expander(f"👤 {nom} ({len(films)} film(s))"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.write(f"🎬 {film} — *{genre}*")


# --- Page : Ajouter un utilisateur ---
elif page == "➕ Ajouter un utilisateur":
    with st.container(border=True):
        st.header("➕ Ajouter un nouvel utilisateur")

        nom = st.text_input("Nom du nouvel utilisateur")
        films_texte = st.text_input("Films aimés (séparés par une virgule)")

        if st.button("Ajouter", key="btn_ajouter"):
            if nom in donnees:
                st.error(f"'{nom}' existe déjà. Choisissez un autre nom.")
            elif not nom.strip():
                st.error("Le nom ne peut pas être vide.")
            else:
                liste_films = [f.strip() for f in films_texte.split(",") if f.strip()]
                if not liste_films:
                    st.error("Vous devez indiquer au moins un film.")
                else:
                    ajouter_utilisateur(nom.strip(), liste_films)
                    st.success(f"Utilisateur '{nom}' ajouté avec succès.")
                    st.cache_data.clear()
                    st.rerun()
