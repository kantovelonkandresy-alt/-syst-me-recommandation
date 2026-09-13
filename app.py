# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Version avec interface modernisée.
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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Bannière d'en-tête */
    .hero {
        background: linear-gradient(135deg, #6C5CE7 0%, #FD79A8 100%);
        padding: 2.2rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 24px rgba(108, 92, 231, 0.25);
    }
    .hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    .hero p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    /* Cartes de statistiques */
    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #EEE;
        text-align: center;
    }
    .stat-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #6C5CE7;
    }
    .stat-card .label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cartes de résultats (utilisateurs / films) */
    .result-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #6C5CE7;
    }
    .result-card.film {
        border-left: 5px solid #FD79A8;
    }
    .result-card h4 {
        margin: 0 0 0.3rem 0;
        color: #2D2D2D;
        font-size: 1.05rem;
    }
    .genre-badge {
        display: inline-block;
        background: #FFEAF3;
        color: #FD79A8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        margin-left: 0.5rem;
    }
    .score-text {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.3rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #1E1B2E;
    }
    section[data-testid="stSidebar"] * {
        color: #F1F1F1 !important;
    }

    #MainMenu, footer {visibility: hidden;}
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
st.sidebar.markdown("### 📌 Navigation")
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
    <div style="text-align:center;">
        <div style="font-size:1.6rem; font-weight:700;">{len(donnees)}</div>
        <div style="font-size:0.75rem; opacity:0.7;">UTILISATEURS</div>
        <br>
        <div style="font-size:1.6rem; font-weight:700;">{len(genres)}</div>
        <div style="font-size:0.75rem; opacity:0.7;">FILMS</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  STATISTIQUES RAPIDES (en haut de chaque page)
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="stat-card"><div class="value">{len(donnees)}</div>'
        f'<div class="label">Utilisateurs</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="stat-card"><div class="value">{len(genres)}</div>'
        f'<div class="label">Films</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    total_connexions = sum(len(f) for f in donnees.values())
    st.markdown(
        f'<div class="stat-card"><div class="value">{total_connexions}</div>'
        f'<div class="label">Connexions</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ============================================================
#  PAGE : GRAPHE
# ============================================================
if page == "🕸️ Graphe utilisateur-item":
    st.subheader("Visualisation du graphe utilisateur-item")
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
    st.subheader("Trouver les utilisateurs similaires")
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
    st.subheader("Obtenir des recommandations personnalisées")
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
    st.subheader("Tous les utilisateurs et leurs films")
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
    st.subheader("Ajouter un nouvel utilisateur")

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
