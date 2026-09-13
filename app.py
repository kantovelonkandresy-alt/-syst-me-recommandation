# app.py
# NOVA RECO - Thème Cyberpunk AI. Fond sombre, néon magenta/cyan,
# panneaux à coins coupés (angulaires), scanlines discrètes.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="NOVA RECO",
    page_icon="▲",
    layout="wide",
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #c9c9d9; }

    /* Fond sombre + scanlines discrètes + lueur magenta/cyan aux coins */
    .stApp {
        background-color: #0a0510;
        background-image:
            repeating-linear-gradient(0deg, rgba(255,255,255,0.018) 0px, rgba(255,255,255,0.018) 1px, transparent 1px, transparent 3px),
            radial-gradient(ellipse at top left, rgba(255,0,153,0.14) 0%, transparent 50%),
            radial-gradient(ellipse at bottom right, rgba(0,230,255,0.12) 0%, transparent 50%);
    }

    section[data-testid="stSidebar"] {
        background: rgba(10, 5, 16, 0.9);
        border-right: 1px solid rgba(255,0,153,0.3);
    }
    section[data-testid="stSidebar"] * { color: #a99bb5 !important; }

    /* Panneaux angulaires (coins coupés), pas de border-radius */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20, 10, 28, 0.7);
        clip-path: polygon(0 14px, 14px 0, 100% 0, 100% calc(100% - 14px), calc(100% - 14px) 100%, 0 100%);
        border: 1px solid rgba(0, 230, 255, 0.35);
        box-shadow: 0 0 24px rgba(255, 0, 153, 0.08), inset 0 0 30px rgba(0,230,255,0.03);
        padding: 0.6rem 1.3rem 1.1rem 1.3rem;
    }

    .nova-hero {
        padding: 1.8rem 0 1.4rem 0;
        border-bottom: 1px solid rgba(255,0,153,0.3);
        margin-bottom: 1.6rem;
    }
    .nova-tag {
        font-family: 'JetBrains Mono', monospace;
        color: #ff0099;
        font-size: 0.78rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .nova-titre {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 3.4rem;
        margin: 0.2rem 0 0.4rem 0;
        letter-spacing: 2px;
        color: #ffffff;
        text-shadow:
            0 0 8px rgba(0,230,255,0.6),
            2px 0 0 rgba(255,0,153,0.5),
            -2px 0 0 rgba(0,230,255,0.4);
    }
    .nova-soustitre {
        color: #9d93ab;
        font-size: 1rem;
        max-width: 660px;
        line-height: 1.55;
    }

    .nova-stats { display: flex; gap: 2.4rem; margin-top: 1.3rem; flex-wrap: wrap; }
    .nova-stat-item { font-family: 'JetBrains Mono', monospace; }
    .nova-stat-item .valeur {
        color: #00e6ff;
        font-size: 1.6rem;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(0,230,255,0.5);
    }
    .nova-stat-item .label {
        color: #7a6f88;
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.35rem !important;
        letter-spacing: 1px;
        border-left: 3px solid #ff0099;
        padding-left: 0.6rem;
    }

    p, span, label, div { color: #a99bb5; }

    div.stButton > button {
        background: transparent;
        color: #ff0099;
        border: 1px solid #ff0099;
        clip-path: polygon(0 8px, 8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
        padding: 0.55rem 1.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: rgba(255,0,153,0.15);
        box-shadow: 0 0 20px rgba(255,0,153,0.5);
        color: #ffffff;
    }

    .nova-badge {
        display: inline-block;
        background: rgba(0, 230, 255, 0.1);
        border: 1px solid rgba(0, 230, 255, 0.5);
        color: #00e6ff;
        padding: 0.1rem 0.55rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        margin-left: 0.5rem;
    }

    .nova-ligne {
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(255,0,153,0.12);
        color: #d8d0e0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.92rem;
    }
    .nova-ligne:last-child { border-bottom: none; }

    div[data-baseweb="select"], div[data-baseweb="input"], input {
        background-color: rgba(10,5,16,0.7) !important;
        border-color: rgba(255,0,153,0.35) !important;
        color: #d8d0e0 !important;
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


donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)
nb_genres = len(set(genres.values()))

st.markdown(
    f"""
    <div class="nova-hero">
        <div class="nova-tag">// Réseau de recommandation en ligne</div>
        <div class="nova-titre">NOVA RECO</div>
        <div class="nova-soustitre">
            Le graphe utilisateur-item cartographie chaque connexion de la ville :
            qui aime quoi, et qui est sur le point d'aimer quoi d'autre.
        </div>
        <div class="nova-stats">
            <div class="nova-stat-item">
                <div class="valeur">{len(donnees):02d}</div>
                <div class="label">Utilisateurs</div>
            </div>
            <div class="nova-stat-item">
                <div class="valeur">{len(genres):02d}</div>
                <div class="label">Films</div>
            </div>
            <div class="nova-stat-item">
                <div class="valeur">{nb_genres:02d}</div>
                <div class="label">Genres</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "MODULE",
    [
        "Graphe utilisateur-item",
        "Utilisateurs similaires",
        "Recommandations",
        "Liste des utilisateurs",
        "Ajouter un utilisateur",
    ],
)


if page == "Graphe utilisateur-item":
    with st.container(border=True):
        st.header("Visualisation du graphe")
        st.write(
            "Noeuds **bleus** = utilisateurs. Noeuds **oranges** = films. "
            "La taille d'un noeud est proportionnelle à son nombre de connexions."
        )
        graphe = creer_graphe()
        fig = obtenir_figure_graphe(graphe)
        st.pyplot(fig)


elif page == "Utilisateurs similaires":
    with st.container(border=True):
        st.header("Détection d'utilisateurs similaires")
        utilisateur = st.selectbox("Cible :", list(donnees.keys()))

        if st.button("Rechercher", key="btn_similaires"):
            similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
            if similaires:
                st.subheader(f"Résultats pour {utilisateur}")
                for nom, score in similaires:
                    st.markdown(
                        f"<div class='nova-ligne'>{nom} "
                        f"<span class='nova-badge'>SIM {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucune correspondance détectée pour {utilisateur}.")


elif page == "Recommandations":
    with st.container(border=True):
        st.header("Génération de recommandations")
        utilisateur = st.selectbox("Cible :", list(donnees.keys()))

        if st.button("Générer", key="btn_reco"):
            recommandations = systeme.generer_recommandations(utilisateur)
            if recommandations:
                st.subheader(f"Résultats pour {utilisateur}")
                for film, score in recommandations:
                    genre = genres.get(film, "Genre inconnu")
                    st.markdown(
                        f"<div class='nova-ligne'>{film} — {genre} "
                        f"<span class='nova-badge'>SCORE {score}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(f"Aucune recommandation disponible pour {utilisateur}.")


elif page == "Liste des utilisateurs":
    with st.container(border=True):
        st.header("Registre des utilisateurs")
        for nom, films in donnees.items():
            with st.expander(f"{nom} ({len(films)} film(s))"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.write(f"{film} — {genre}")


elif page == "Ajouter un utilisateur":
    with st.container(border=True):
        st.header("Enregistrer un nouvel utilisateur")

        nom = st.text_input("Nom")
        films_texte = st.text_input("Films aimés (séparés par une virgule)")

        if st.button("Enregistrer", key="btn_ajouter"):
            if nom in donnees:
                st.error(f"'{nom}' existe déjà.")
            elif not nom.strip():
                st.error("Le nom ne peut pas être vide.")
            else:
                liste_films = [f.strip() for f in films_texte.split(",") if f.strip()]
                if not liste_films:
                    st.error("Indiquez au moins un film.")
                else:
                    ajouter_utilisateur(nom.strip(), liste_films)
                    st.success(f"Utilisateur '{nom}' enregistré.")
                    st.cache_data.clear()
                    st.rerun()
