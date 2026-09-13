# app.py
# NOVA RECO - Application Web (Streamlit) du système de recommandation
# utilisateur-item, avec un design glassmorphism (light mode).
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

# --- Style glassmorphism (light mode) ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 40%, #eafaf6 100%);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.12);
        padding: 0.5rem;
    }

    .nova-titre {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #a855f7, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .nova-soustitre {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0.2rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-right: 1px solid rgba(255, 255, 255, 0.5);
    }

    div.stButton > button {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
        transition: transform 0.15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45);
    }

    .nova-badge {
        display: inline-block;
        background: linear-gradient(90deg, rgba(99,102,241,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(99,102,241,0.3);
        color: #4338ca;
        border-radius: 999px;
        padding: 0.15rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
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


st.markdown('<p class="nova-titre">✨ NOVA RECO</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="nova-soustitre">Système de recommandation intelligent basé sur '
    "un graphe utilisateur-item — Projet L2, École Supérieure Polytechnique</p>",
    unsafe_allow_html=True,
)
st.write("")

donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)

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

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(donnees)}** utilisateurs")
st.sidebar.markdown(f"**{len(genres)}** films")


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
                        f"**{nom}** <span class='nova-badge'>similarité : {score}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")


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
                        f"🎬 **{film}** — *{genre}* "
                        f"<span class='nova-badge'>score : {score}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucune recommandation disponible pour {utilisateur}.")


elif page == "📋 Liste des utilisateurs":
    with st.container(border=True):
        st.header("📋 Tous les utilisateurs et leurs films")
        for nom, films in donnees.items():
            with st.expander(f"{nom} ({len(films)} film(s))"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.write(f"- {film} ({genre})")


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
