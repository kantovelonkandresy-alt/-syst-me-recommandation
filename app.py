# app.py
# NOVA RECO - Dashboard IA futuriste pour le système de recommandation
# utilisateur-item. Thème : panneau de contrôle HUD, fond sombre, accent cyan.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="NOVA RECO",
    page_icon="◆",
    layout="wide",
)

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #cbd5e1; }

    /* Fond : bleu-nuit profond + grille discrète (thème panneau de contrôle) */
    .stApp {
        background-color: #060a14;
        background-image:
            linear-gradient(rgba(34,211,238,0.055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34,211,238,0.055) 1px, transparent 1px),
            radial-gradient(ellipse at top left, rgba(34,211,238,0.10) 0%, transparent 55%),
            radial-gradient(ellipse at bottom right, rgba(6,182,212,0.08) 0%, transparent 55%);
        background-size: 42px 42px, 42px 42px, 100% 100%, 100% 100%;
    }

    section[data-testid="stSidebar"] {
        background: rgba(8, 13, 24, 0.85);
        border-right: 1px solid rgba(34,211,238,0.25);
    }
    section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

    /* Panneau HUD : coins marqués, bordure fine cyan */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;
        background: rgba(11, 18, 32, 0.75);
        border-radius: 4px;
        border: 1px solid rgba(34, 211, 238, 0.25);
        box-shadow: 0 0 0 1px rgba(34,211,238,0.04), 0 8px 30px rgba(0,0,0,0.4);
        padding: 0.5rem 1.2rem 1rem 1.2rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before,
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        content: "";
        position: absolute;
        width: 14px;
        height: 14px;
        border-color: #22d3ee;
        border-style: solid;
        opacity: 0.9;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        top: -1px; left: -1px;
        border-width: 2px 0 0 2px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        bottom: -1px; right: -1px;
        border-width: 0 2px 2px 0;
    }

    /* En-tête */
    .nova-hero {
        padding: 1.8rem 0 1.4rem 0;
        border-bottom: 1px solid rgba(34,211,238,0.2);
        margin-bottom: 1.6rem;
    }
    .nova-tag {
        font-family: 'JetBrains Mono', monospace;
        color: #22d3ee;
        font-size: 0.8rem;
        letter-spacing: 2px;
    }
    .nova-tag::before { content: "// "; opacity: 0.6; }
    .nova-titre {
        font-family: 'Orbitron', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        color: #e6faff;
        margin: 0.3rem 0 0.4rem 0;
        text-shadow: 0 0 18px rgba(34,211,238,0.35);
        letter-spacing: 1px;
    }
    .nova-soustitre {
        color: #7d8ba1;
        font-size: 1rem;
        max-width: 660px;
        line-height: 1.55;
    }

    /* Ligne de statistiques style "readout" */
    .nova-stats {
        display: flex;
        gap: 2.2rem;
        margin-top: 1.3rem;
        flex-wrap: wrap;
    }
    .nova-stat-item {
        font-family: 'JetBrains Mono', monospace;
    }
    .nova-stat-item .valeur {
        color: #22d3ee;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .nova-stat-item .label {
        color: #5b6b82;
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    h2, h3 {
        font-family: 'JetBrains Mono', monospace !important;
        color: #e6faff !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        letter-spacing: 0.5px;
    }
    h2::before, h3::before { content: "> "; color: #22d3ee; }

    p, span, label, div { color: #94a3b8; }

    /* Boutons : contour cyan, remplissage au survol */
    div.stButton > button {
        background: rgba(34,211,238,0.08);
        color: #22d3ee;
        border: 1px solid rgba(34,211,238,0.5);
        border-radius: 4px;
        padding: 0.5rem 1.3rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: rgba(34,211,238,0.18);
        box-shadow: 0 0 16px rgba(34,211,238,0.35);
        color: #e6faff;
    }

    /* Badge score : ambre, pour contraster avec le cyan (signal secondaire) */
    .nova-badge {
        display: inline-block;
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.4);
        color: #fbbf24;
        border-radius: 4px;
        padding: 0.1rem 0.55rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        margin-left: 0.5rem;
    }

    .nova-ligne {
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(34,211,238,0.1);
        color: #cbd5e1;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.92rem;
    }
    .nova-ligne:last-child { border-bottom: none; }

    /* Champs de saisie et select : style console */
    div[data-baseweb="select"], div[data-baseweb="input"], input {
        background-color: rgba(6,10,20,0.6) !important;
        border-color: rgba(34,211,238,0.3) !important;
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

# --- En-tête / HUD ---
st.markdown(
    f"""
    <div class="nova-hero">
        <div class="nova-tag">SYSTEME_RECOMMANDATION.ACTIF</div>
        <div class="nova-titre">NOVA RECO</div>
        <div class="nova-soustitre">
            Panneau de contrôle du moteur de recommandation basé sur un graphe
            utilisateur-item — chaque connexion détectée révèle une nouvelle
            correspondance.
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

# --- Menu de navigation ---
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


# --- Page : Graphe ---
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


# --- Page : Utilisateurs similaires ---
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


# --- Page : Recommandations ---
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


# --- Page : Liste des utilisateurs ---
elif page == "Liste des utilisateurs":
    with st.container(border=True):
        st.header("Registre des utilisateurs")
        for nom, films in donnees.items():
            with st.expander(f"{nom} ({len(films)} film(s))"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.write(f"{film} — {genre}")


# --- Page : Ajouter un utilisateur ---
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
