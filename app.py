# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Version 3 - Thème sombre "cinéma" avec effets néon.
# Lancer avec : streamlit run app.py

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_plotly
from recommandation import SystemeRecommandation

st.set_page_config(
    page_title="CinéReco - Système de recommandation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
#  STYLE PERSONNALISÉ (CSS) — thème sombre néon
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.35); }
        50% { box-shadow: 0 0 34px rgba(236, 72, 153, 0.45); }
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Fond général sombre */
    .stApp {
        background: radial-gradient(circle at 20% 0%, #1A1030 0%, #0B0714 45%, #05040A 100%);
    }
    [data-testid="stAppViewContainer"] * , [data-testid="stMarkdownContainer"] p {
        color: #EDEBF5;
    }

    /* Bannière d'en-tête néon */
    .hero {
        background: linear-gradient(120deg, #A855F7, #EC4899, #22D3EE, #A855F7);
        background-size: 300% 300%;
        animation: gradientMove 8s ease infinite, fadeIn 0.6s ease-out;
        padding: 2.8rem 2.4rem;
        border-radius: 22px;
        margin-bottom: 1.8rem;
        box-shadow: 0 0 50px rgba(168, 85, 247, 0.35);
    }
    .hero h1 {
        color: white;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 24px rgba(255,255,255,0.5);
    }
    .hero p {
        color: rgba(255,255,255,0.95);
        font-size: 1.05rem;
        margin-top: 0.6rem;
        font-weight: 500;
    }

    /* Cartes en verre (glassmorphism) */
    .glass-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
    }

    /* Cartes de statistiques */
    .stat-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        animation: fadeIn 0.7s ease-out;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(168, 85, 247, 0.5);
        box-shadow: 0 0 24px rgba(168, 85, 247, 0.25);
    }
    .stat-card .value {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #C084FC, #F472B6, #22D3EE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .label {
        font-size: 0.8rem;
        color: #9B93B5;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* Cartes de résultats (utilisateurs / films) */
    .result-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.09);
        border-left: 4px solid #A855F7;
        border-radius: 14px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.65rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card:hover {
        transform: translateX(5px);
        border-left-color: #EC4899;
        box-shadow: 0 0 22px rgba(168, 85, 247, 0.2);
    }
    .result-card.film {
        border-left-color: #EC4899;
    }
    .result-card.film:hover {
        border-left-color: #22D3EE;
        box-shadow: 0 0 22px rgba(34, 211, 238, 0.2);
    }
    .result-card h4 {
        margin: 0 0 0.35rem 0;
        color: #F5F3FF;
        font-size: 1.08rem;
        font-weight: 600;
    }
    .genre-badge {
        display: inline-block;
        background: rgba(236, 72, 153, 0.15);
        color: #F472B6;
        border: 1px solid rgba(236, 72, 153, 0.3);
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.18rem 0.65rem;
        border-radius: 999px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    .score-text {
        font-size: 0.8rem;
        color: #9B93B5;
        margin-top: 0.35rem;
    }

    .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #A855F7, #EC4899);
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.6rem;
        vertical-align: middle;
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.5);
    }

    .rang-badge {
        font-size: 1.15rem;
        margin-right: 0.4rem;
        vertical-align: middle;
    }

    .empty-state {
        text-align: center;
        padding: 2.6rem 1rem;
        color: #9B93B5;
        background: rgba(255,255,255,0.03);
        border-radius: 18px;
        border: 1.5px dashed rgba(168, 85, 247, 0.3);
    }
    .empty-state .icon {
        font-size: 2.3rem;
        margin-bottom: 0.6rem;
        display: block;
        filter: drop-shadow(0 0 10px rgba(168, 85, 247, 0.6));
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0A1E 0%, #05040A 100%);
        border-right: 1px solid rgba(168, 85, 247, 0.15);
    }
    section[data-testid="stSidebar"] * {
        color: #EDEBF5 !important;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 12px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(168, 85, 247, 0.15) !important;
        border-color: rgba(168, 85, 247, 0.4) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #A855F7, #EC4899) !important;
        border: none !important;
        animation: glow 2.5s ease-in-out infinite;
    }

    /* Boutons principaux (zone centrale) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #A855F7, #EC4899) !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.4) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(236, 72, 153, 0.55) !important;
    }

    /* Barres de progression néon */
    .stProgress > div > div {
        background: linear-gradient(90deg, #A855F7, #EC4899, #22D3EE) !important;
    }
    .stProgress > div {
        background: rgba(255,255,255,0.08) !important;
    }

    /* Champs de saisie */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #EDEBF5 !important;
        border-radius: 10px !important;
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
        <h1>🎬 Système de recommandation basé sur un graphe utilisateur-item</h1>
        <p>Système de recommandation basé sur un graphe utilisateur-item —
        similarité de Jaccard + bonus de genre</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  BARRE LATÉRALE — navigation par boutons
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "graphe"

PAGES = [
    ("graphe", "🕸️  Graphe utilisateur-item"),
    ("similaires", "🤝  Utilisateurs similaires"),
    ("recommandations", "✨  Recommandations"),
    ("liste", "👥  Liste des utilisateurs"),
    ("ajouter", "➕  Ajouter un utilisateur"),
]

st.sidebar.markdown("### 📌 Navigation")
for cle, libelle in PAGES:
    est_active = st.session_state.page == cle
    if st.sidebar.button(
        libelle,
        key=f"nav_{cle}",
        use_container_width=True,
        type="primary" if est_active else "secondary",
    ):
        st.session_state.page = cle
        st.rerun()

page = st.session_state.page

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="text-align:center;">
        <div style="font-size:1.7rem; font-weight:800;
                    background: linear-gradient(135deg, #C084FC, #F472B6);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {len(donnees)}
        </div>
        <div style="font-size:0.75rem; opacity:0.6;">UTILISATEURS</div>
        <br>
        <div style="font-size:1.7rem; font-weight:800;
                    background: linear-gradient(135deg, #C084FC, #F472B6);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {len(genres)}
        </div>
        <div style="font-size:0.75rem; opacity:0.6;">FILMS</div>
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
if page == "graphe":
    st.subheader("Visualisation interactive du graphe utilisateur-item")
    st.write(
        "🟣 Les noeuds **violets** représentent les utilisateurs · "
        "🩷 Les noeuds **roses** représentent les films. "
        "Survolez un noeud avec la souris pour voir ses détails — "
        "vous pouvez aussi zoomer et déplacer le graphe."
    )
    st.markdown(
        '<div style="background:#F7F5FC; border-radius:18px; padding:1rem; '
        'border:1px solid rgba(255,255,255,0.09);">',
        unsafe_allow_html=True,
    )
    graphe = creer_graphe()
    fig = obtenir_figure_plotly(graphe)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#  PAGE : UTILISATEURS SIMILAIRES
# ============================================================
elif page == "similaires":
    st.subheader("Trouver les utilisateurs similaires")
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    RANGS = ["🥇", "🥈", "🥉"]

    if st.button("🔍 Rechercher", type="primary"):
        similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
        if similaires:
            st.write(f"**Résultats pour {utilisateur} :**")
            for i, (nom, score) in enumerate(similaires):
                rang = RANGS[i] if i < 3 else ""
                initiales = nom[:2].upper()
                st.markdown(
                    f"""
                    <div class="result-card">
                        <h4><span class="rang-badge">{rang}</span><span class="avatar">{initiales}</span>{nom}</h4>
                        <div class="score-text">Similarité : {score * 100:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(score, 1.0))
        else:
            st.warning(f"Aucun utilisateur similaire trouvé pour {utilisateur}.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <span class="icon">🤝</span>
                Choisissez un utilisateur puis cliquez sur « Rechercher »
                pour découvrir qui lui ressemble le plus.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
#  PAGE : RECOMMANDATIONS
# ============================================================
elif page == "recommandations":
    st.subheader("Obtenir des recommandations personnalisées")
    utilisateur = st.selectbox("Choisissez un utilisateur :", list(donnees.keys()))

    RANGS = ["🥇", "🥈", "🥉"]

    if st.button("✨ Générer les recommandations", type="primary"):
        recommandations = systeme.generer_recommandations(utilisateur)
        if recommandations:
            st.write(f"**Films recommandés pour {utilisateur} :**")
            score_max = max(s for _, s in recommandations) or 1
            for i, (film, score) in enumerate(recommandations):
                rang = RANGS[i] if i < 3 else ""
                genre = genres.get(film, "Genre inconnu")
                st.markdown(
                    f"""
                    <div class="result-card film">
                        <h4><span class="rang-badge">{rang}</span>🎬 {film}
                        <span class="genre-badge">{genre}</span></h4>
                        <div class="score-text">Score de pertinence : {score}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(score / score_max, 1.0))
        else:
            st.warning(f"Aucune recommandation disponible pour {utilisateur}.")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <span class="icon">✨</span>
                Choisissez un utilisateur puis cliquez sur « Générer les
                recommandations » pour découvrir des films à son goût.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
#  PAGE : LISTE DES UTILISATEURS
# ============================================================
elif page == "liste":
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
elif page == "ajouter":
    st.subheader("Ajouter un nouvel utilisateur")

    st.markdown('<div class="glass-card" style="padding:1.5rem;">', unsafe_allow_html=True)
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
            liste_films = [f.strip() for f in films_texte.split(",") if f.strip()]
            if not liste_films:
                st.error("❌ Vous devez indiquer au moins un film.")
            else:
                ajouter_utilisateur(nom.strip(), liste_films)
                st.success(f"✅ Utilisateur '{nom}' ajouté avec succès.")
                st.cache_data.clear()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; margin-top:2.5rem; padding:1rem; color:#6B6480; font-size:0.8rem;">
        🎬 CinéReco — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
