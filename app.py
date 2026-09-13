# app.py
# NOVA RECO - Application Web (Streamlit) du système de recommandation
# utilisateur-item. Design : ciel d'aube + constellation (thème graphe/réseau).
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="NOVA RECO",
    page_icon="✦",
    layout="wide",
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Fond : ciel d'aube discret + semis d'étoiles (thème graphe/réseau) */
    .stApp {
        background:
            radial-gradient(2px 2px at 10% 20%, rgba(67,56,202,0.35) 40%, transparent 41%),
            radial-gradient(2px 2px at 25% 65%, rgba(67,56,202,0.25) 40%, transparent 41%),
            radial-gradient(1.5px 1.5px at 40% 15%, rgba(245,166,35,0.4) 40%, transparent 41%),
            radial-gradient(2px 2px at 60% 75%, rgba(67,56,202,0.3) 40%, transparent 41%),
            radial-gradient(1.5px 1.5px at 80% 30%, rgba(245,166,35,0.35) 40%, transparent 41%),
            radial-gradient(2px 2px at 90% 60%, rgba(67,56,202,0.25) 40%, transparent 41%),
            linear-gradient(160deg, #f4f2ff 0%, #f7f4fb 45%, #fbf7ef 100%);
        background-attachment: fixed;
    }

    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(67,56,202,0.12);
    }

    /* Panneau "verre" sobre : un seul accent, en haut */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.58);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(67,56,202,0.14);
        border-top: 3px solid #4338ca;
        box-shadow: 0 6px 24px rgba(30, 27, 58, 0.08);
        padding: 0.4rem 1rem;
    }

    /* Hero, aligné à gauche */
    .nova-hero {
        padding: 2.2rem 0 1.4rem 0;
        border-bottom: 1px solid rgba(67,56,202,0.14);
        margin-bottom: 1.6rem;
    }
    .nova-eyebrow {
        color: #f5a623;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.3px;
    }
    .nova-titre {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #1e1b3a;
        margin: 0.2rem 0 0.3rem 0;
        line-height: 1.05;
    }
    .nova-titre span {
        color: #4338ca;
    }
    .nova-soustitre {
        color: #55516f;
        font-size: 1.05rem;
        max-width: 640px;
        line-height: 1.5;
    }
    .nova-stats {
        margin-top: 1.1rem;
        color: #1e1b3a;
        font-size: 0.95rem;
    }
    .nova-stats b {
        font-family: 'Space Grotesk', sans-serif;
        color: #4338ca;
        font-size: 1.1rem;
    }
    .nova-stats .separateur {
        display: inline-block;
        width: 1px;
        height: 0.9em;
        background: rgba(30,27,58,0.2);
        margin: 0 0.9rem;
        vertical-align: middle;
    }

    /* Titres de section */
    h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #1e1b3a !important;
    }

    /* Boutons : un seul ton, sobre */
    div.stButton > button {
        background: #4338ca;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 1.3rem;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(67, 56, 202, 0.3);
        transition: background 0.2s ease, transform 0.2s ease;
    }
    div.stButton > button:hover {
        background: #362f9e;
        transform: translateY(-1px);
    }

    /* Badge score : un seul accent (or, pour "étoile/score") */
    .nova-badge {
        display: inline-block;
        background: rgba(245, 166, 35, 0.16);
        border: 1px solid rgba(245, 166, 35, 0.45);
        color: #96660f;
        border-radius: 8px;
        padding: 0.15rem 0.6rem;
        font-size: 0.82rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }

    .nova-ligne {
        padding: 0.65rem 0;
        border-bottom: 1px solid rgba(30,27,58,0.08);
        color: #1e1b3a;
    }
    .nova-ligne:last-child { border-bottom: none; }
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


donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)
nb_genres = len(set(genres.values()))

# --- Hero ---
st.markdown(
    f"""
    <div class="nova-hero">
        <div class="nova-eyebrow">Projet L2 — École Supérieure Polytechnique</div>
        <div class="nova-titre">NOVA <span>RECO</span></div>
        <div class="nova-soustitre">
            Un système de recommandation qui explore un graphe utilisateur-item :
            chaque utilisateur et chaque film est un noeud, et la proximité entre eux
            révèle ce que vous allez aimer ensuite.
        </div>
        <div class="nova-stats">
            <b>{len(donnees)}</b> utilisateurs
            <span class="separateur"></span>
            <b>{len(genres)}</b> films
            <span class="separateur"></span>
            <b>{nb_genres}</b> genres
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Menu de navigation ---
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


# --- Page : Graphe ---
if page == "Graphe utilisateur-item":
    with st.container(border=True):
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
    with st.container(border=True):
        st.header("Trouver les utilisateurs similaires")
        utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

        if st.button("Rechercher", key="btn_similaires"):
            similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
            if similaires:
                st.subheader(f"Utilisateurs similaires à {utilisateur}")
                for nom, score in similaires:
                    st.markdown(
                        f"<div class='nova-ligne'>{nom} "
                        f"<span class='nova-badge'>similarité {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")


# --- Page : Recommandations ---
elif page == "Recommandations":
    with st.container(border=True):
        st.header("Obtenir des recommandations")
        utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

        if st.button("Générer les recommandations", key="btn_reco"):
            recommandations = systeme.generer_recommandations(utilisateur)
            if recommandations:
                st.subheader(f"Recommandations pour {utilisateur}")
                for film, score in recommandations:
                    genre = genres.get(film, "Genre inconnu")
                    st.markdown(
                        f"<div class='nova-ligne'>{film} — <i>{genre}</i> "
                        f"<span class='nova-badge'>score {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucune recommandation disponible pour {utilisateur}.")


# --- Page : Liste des utilisateurs ---
elif page == "Liste des utilisateurs":
    with st.container(border=True):
        st.header("Tous les utilisateurs et leurs films")
        for nom, films in donnees.items():
            with st.expander(f"{nom} ({len(films)} film(s))"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.write(f"{film} — *{genre}*")


# --- Page : Ajouter un utilisateur ---
elif page == "Ajouter un utilisateur":
    with st.container(border=True):
        st.header("Ajouter un nouvel utilisateur")

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
