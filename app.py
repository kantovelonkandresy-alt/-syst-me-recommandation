# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Version "premium" avec interface soignée, animations et thème personnalisé.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_graphe
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="CinéReco - Système de recommandation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
#  STYLE PERSONNALISÉ (CSS)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, span, div {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #FAFAFF 0%, #F3F1FB 100%);
    }

    .hero {
        background: linear-gradient(135deg, #6C5CE7 0%, #A55EEA 50%, #FD79A8 100%);
        padding: 2.6rem 2.4rem;
        border-radius: 22px;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 32px rgba(108, 92, 231, 0.28);
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .hero h1 {
        color: white;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 1.02rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 4px 16px rgba(108, 92, 231, 0.08);
        border: 1px solid #EFEBFA;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 24px rgba(108, 92, 231, 0.16);
    }
    .stat-card .value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6C5CE7, #FD79A8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .label {
        font-size: 0.78rem;
        color: #9992B0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 1.4rem;
        font-weight: 700;
        color: #2D2A45;
        margin: 1.6rem 0 0.6rem 0;
    }
    .section-title .bar {
        width: 5px;
        height: 22px;
        border-radius: 4px;
        background: linear-gradient(180deg, #6C5CE7, #FD79A8);
    }

    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
        border: 1px solid #F0EEF9;
        border-left: 5px solid #6C5CE7;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .result-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 20px rgba(108, 92, 231, 0.12);
    }
    .result-card.film {
        border-left: 5px solid #FD79A8;
    }
    .result-card h4 {
        margin: 0 0 0.35rem 0;
        color: #2D2A45;
        font-size: 1.08rem;
        font-weight: 700;
    }
    .genre-badge {
        display: inline-block;
        background: linear-gradient(135deg, #FFE3EF, #FFD4EA);
        color: #E84393;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    .score-text {
        font-size: 0.82rem;
        color: #9992B0;
        margin-top: 0.3rem;
        font-weight: 500;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6C5CE7, #FD79A8) !important;
        border-radius: 999px;
    }
    .stProgress > div > div {
        background-color: #EFEBFA !important;
        border-radius: 999px;
    }

    .stButton > button {
        border-radius: 999px !important;
        font-weight: 700 !important;
        padding: 0.55rem 1.6rem !important;
        border: none !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6C5CE7, #FD79A8) !important;
        box-shadow: 0 6px 16px rgba(108, 92, 231, 0.35) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(108, 92, 231, 0.3) !important;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #211D3B 0%, #17142B 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #F1F0FA !important;
    }
    div[data-testid="stRadio"] label {
        padding: 0.55rem 0.8rem;
        border-radius: 10px;
        margin-bottom: 0.25rem;
        transition: background 0.15s ease;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,0.08);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border: 1px solid #EFEBFA !important;
        box-shadow: 0 4px 20px rgba(108, 92, 231, 0.06) !important;
    }

    #MainMenu, footer {visibility: hidden;}

    .app-footer {
        text-align: center;
        color: #B3ACC9;
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid #EFEBFA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def charger_systeme():
    donnees = obtenir_donnees()
    genres = obtenir_genres()
    return donnees, genres


donnees, genres = charger_systeme()
systeme = SystemeRecommandation(donnees, genres)

# ============================================================
#  BANNIÈRE D'EN-TÊTE
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>🎬 CinéReco</h1>
        <p>Système de recommandation basé sur un graphe utilisateur-item —
        similarité de Jaccard + bonus de genre</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  BARRE LATÉRALE
# ============================================================
st.sidebar.markdown(
    """
    <div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
        <div style="font-size:2.2rem;">🎬</div>
        <div style="font-size:1.15rem; font-weight:800; letter-spacing:-0.01em;">CinéReco</div>
        <div style="font-size:0.72rem; opacity:0.6;">Projet L2</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("##### 📌 NAVIGATION")
page = st.sidebar.radio(
    "",
    [
        "🕸️ Graphe utilisateur-item",
        "🤝 Utilisateurs similaires",
        "✨ Recommandations",
        "👥 Liste des utilisateurs",
        "➕ Ajouter un utilisateur",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="display:flex; justify-content:space-around; text-align:center;">
        <div>
            <div style="font-size:1.5rem; font-weight:800;">{len(donnees)}</div>
            <div style="font-size:0.68rem; opacity:0.65;">UTILISATEURS</div>
        </div>
        <div>
            <div style="font-size:1.5rem; font-weight:800;">{len(genres)}</div>
            <div style="font-size:0.68rem; opacity:0.65;">FILMS</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  STATISTIQUES RAPIDES
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="stat-card"><div class="value">{len(donnees)}</div>'
        f'<div class="label">👤 Utilisateurs</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="stat-card"><div class="value">{len(genres)}</div>'
        f'<div class="label">🎬 Films</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    total_connexions = sum(len(f) for f in donnees.values())
    st.markdown(
        f'<div class="stat-card"><div class="value">{total_connexions}</div>'
        f'<div class="label">🔗 Connexions</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ============================================================
#  PAGE : GRAPHE
# ============================================================
if page == "🕸️ Graphe utilisateur-item":
    st.markdown(
        '<div class="section-title"><div class="bar"></div>'
        'Visualisation du graphe utilisateur-item</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "🔵 Les noeuds **bleus** représentent les utilisateurs · "
        "🟠 Les noeuds **oranges** représentent les films. "
        "Plus un noeud est gros, plus il a de connexions."
    )
    with st.container(border=True):
        graphe = creer_graphe()
        fig = obtenir_figure_graphe(graphe)
        st.pyplot(fig, use_container_width=True)

# ============================================================
#  PAGE : UTILISATEURS SIMILAIRES
# ============================================================
elif page == "🤝 Utilisateurs similaires":
    st.markdown(
        '<div class="section-title"><div class="bar"></div>'
        'Trouver les utilisateurs similaires</div>',
        unsafe_allow_html=True,
    )
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    if st.button("🔍 Rechercher", type="primary"):
        similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
        if similaires:
            st.write(f"**Résultats pour {utilisateur} :**")
            for nom, score in similaires:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <h4>👤 {nom}</h4>
                        <div class="score-text">Similarité : {score * 100:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(score, 1.0))
        else:
            st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")

# ============================================================
#  PAGE : RECOMMANDATIONS
# ============================================================
elif page == "✨ Recommandations":
    st.markdown(
        '<div class="section-title"><div class="bar"></div>'
        'Obtenir des recommandations personnalisées</div>',
        unsafe_allow_html=True,
    )
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    if st.button("✨ Générer les recommandations", type="primary"):
        recommandations = systeme.generer_recommandations(utilisateur)
        if recommandations:
            st.write(f"**Films recommandés pour {utilisateur} :**")
            score_max = max(s for _, s in recommandations) or 1
            for film, score in recommandations:
                genre = genres.get(film, "Genre inconnu")
                st.markdown(
                    f"""
                    <div class="result-card film">
                        <h4>🎬 {film} <span class="genre-badge">{genre}</span></h4>
                        <div class="score-text">Score de pertinence : {score}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(score / score_max, 1.0))
        else:
            st.warning(f"Aucune recommandation disponible pour {utilisateur}.")

# ============================================================
#  PAGE : LISTE DES UTILISATEURS
# ============================================================
elif page == "👥 Liste des utilisateurs":
    st.markdown(
        '<div class="section-title"><div class="bar"></div>'
        'Tous les utilisateurs et leurs films</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, (nom, films) in enumerate(donnees.items()):
        with cols[i % 2]:
            with st.expander(f"👤 {nom}  ·  {len(films)} film(s)"):
                for film in films:
                    genre = genres.get(film, "Genre inconnu")
                    st.markdown(f"🎬 **{film}** — *{genre}*")

# ============================================================
#  PAGE : AJOUTER UN UTILISATEUR
# ============================================================
elif page == "➕ Ajouter un utilisateur":
    st.markdown(
        '<div class="section-title"><div class="bar"></div>'
        'Ajouter un nouvel utilisateur</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        nom = st.text_input("Nom du nouvel utilisateur")
        films_texte = st.text_input(
            "Films aimés (séparés par une virgule)",
            placeholder="Ex : Avengers, Titanic, Avatar",
        )

        if st.button("➕ Ajouter", type="primary"):
            if nom in donnees:
                st.error(f"❌ '{nom}' existe déjà. Choisissez un autre nom.")
            elif not nom.strip():
                st.error("❌ Le nom ne peut pas être vide.")
            else:
                liste_films = [
                    f.strip() for f in films_texte.split(",") if f.strip()
                ]
                if not liste_films:
                    st.error("❌ Vous devez indiquer au moins un film.")
                else:
                    ajouter_utilisateur(nom.strip(), liste_films)
                    st.success(f"✅ Utilisateur '{nom}' ajouté avec succès.")
                    st.cache_data.clear()
                    st.rerun()

# ============================================================
#  PIED DE PAGE
# ============================================================
st.markdown(
    '<div class="app-footer">🎬 CinéReco — Projet L2 · Système de recommandation '
    'basé sur un graphe utilisateur-item</div>',
    unsafe_allow_html=True,
)
