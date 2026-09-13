# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="Système de recommandation",
    page_icon="🎬",
    layout="wide",
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


st.title("🎬 Système de recommandation utilisateur-item")
st.caption(
    "Projet L2 - Recommandation basée sur un graphe utilisateur-item "
    "(similarité de Jaccard + bonus de genre)"
)

donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)

# Menu de navigation sur le côté gauche
page = st.sidebar.radio(
    "Navigation",
    [
        "Graphe utilisateur-item",
        "Utilisateurs similaires",
        "Recommandations",
        "Liste des utilisateurs",
        "Ajouter un utilisateur",
    ],
)

st.sidebar.markdown("---")
st.sidebar.write(f"**{len(donnees)}** utilisateurs")
st.sidebar.write(f"**{len(genres)}** films")


# --- Page : Graphe ---
if page == "Graphe utilisateur-item":
    st.header("Visualisation du graphe")
    st.write(
        "Les noeuds **bleus** sont les utilisateurs, les noeuds **oranges** "
        "sont les films. La taille d'un noeud dépend de son nombre de connexions."
    )
    graphe = creer_graphe()
    fig = obtenir_figure_graphe(graphe)
    st.pyplot(fig)


# --- Page : Utilisateurs similaires ---
elif page == "Utilisateurs similaires":
    st.header("Trouver les utilisateurs similaires")
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    if st.button("Rechercher"):
        similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
        if similaires:
            st.subheader(f"Utilisateurs similaires à {utilisateur}")
            for nom, score in similaires:
                st.write(f"- **{nom}** — similarité : {score}")
        else:
            st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")


# --- Page : Recommandations ---
elif page == "Recommandations":
    st.header("Obtenir des recommandations")
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    if st.button("Générer les recommandations"):
        recommandations = systeme.generer_recommandations(utilisateur)
        if recommandations:
            st.subheader(f"Recommandations pour {utilisateur}")
            for film, score in recommandations:
                genre = genres.get(film, "Genre inconnu")
                st.write(f"- **{film}** ({genre}) — score : {score}")
        else:
            st.warning(f"Aucune recommandation disponible pour {utilisateur}.")


# --- Page : Liste des utilisateurs ---
elif page == "Liste des utilisateurs":
    st.header("Tous les utilisateurs et leurs films")
    for nom, films in donnees.items():
        with st.expander(f"{nom} ({len(films)} film(s))"):
            for film in films:
                genre = genres.get(film, "Genre inconnu")
                st.write(f"- {film} ({genre})")


# --- Page : Ajouter un utilisateur ---
elif page == "Ajouter un utilisateur":
    st.header("Ajouter un nouvel utilisateur")

    nom = st.text_input("Nom du nouvel utilisateur")
    films_texte = st.text_input("Films aimés (séparés par une virgule)")

    if st.button("Ajouter"):
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
                st.cache_data.clear()  # Force le rechargement des données
                st.rerun()