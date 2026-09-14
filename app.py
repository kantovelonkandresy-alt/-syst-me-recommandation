# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Thème "Netflix" (noir & rouge).
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
#  STYLE PERSONNALISÉ (CSS) — thème Netflix (noir & rouge)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseRed {
        0%, 100% { box-shadow: 0 0 16px rgba(229, 9, 20, 0.4); }
        50% { box-shadow: 0 0 28px rgba(229, 9, 20, 0.65); }
    }

    /* Fond général - noir profond façon Netflix */
    .stApp {
        background: linear-gradient(180deg, #141414 0%, #0A0A0A 100%);
    }
    [data-testid="stAppViewContainer"] * , [data-testid="stMarkdownContainer"] p {
        color: #E5E5E5;
    }

    /* Bannière d'en-tête */
    .hero {
        background: linear-gradient(120deg, #8B0000 0%, #E50914 55%, #B81D24 100%);
        padding: 2.6rem 2.4rem;
        border-radius: 10px;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 40px rgba(229, 9, 20, 0.35);
        animation: fadeIn 0.6s ease-out;
        border-left: 6px solid #E50914;
    }
    .hero h1 {
        font-family: 'Bebas Neue', sans-serif;
        color: white;
        font-size: 3rem;
        letter-spacing: 0.03em;
        margin: 0;
        text-shadow: 0 0 20px rgba(0,0,0,0.4);
    }
    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 1.02rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Cartes de statistiques */
    .stat-card {
        background: #181818;
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        border: 1px solid #2A2A2A;
        border-top: 3px solid #E50914;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.7s ease-out;
    }
    .stat-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 10px 24px rgba(229, 9, 20, 0.25);
    }
    .stat-card .value {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.3rem;
        color: #E50914;
        letter-spacing: 0.02em;
    }
    .stat-card .label {
        font-size: 0.78rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* Cartes de résultats (utilisateurs / films) — effet "carte film" */
    .result-card {
        background: #181818;
        border-radius: 8px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.65rem;
        border: 1px solid #2A2A2A;
        border-left: 4px solid #E50914;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card:hover {
        transform: scale(1.015);
        background: #222222;
        box-shadow: 0 8px 24px rgba(229, 9, 20, 0.25);
    }
    .result-card h4 {
        margin: 0 0 0.35rem 0;
        color: #F5F5F5;
        font-size: 1.08rem;
        font-weight: 600;
    }
    .genre-badge {
        display: inline-block;
        background: rgba(229, 9, 20, 0.15);
        color: #FF3B47;
        border: 1px solid rgba(229, 9, 20, 0.35);
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.18rem 0.65rem;
        border-radius: 4px;
        margin-left: 0.5rem;
        vertical-align: middle;
        text-transform: uppercase;
    }
    .score-text {
        font-size: 0.8rem;
        color: #999;
        margin-top: 0.35rem;
    }

    .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 4px;
        background: linear-gradient(135deg, #E50914, #8B0000);
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.6rem;
        vertical-align: middle;
    }

    .rang-badge {
        font-size: 1.15rem;
        margin-right: 0.4rem;
        vertical-align: middle;
    }

    .empty-state {
        text-align: center;
        padding: 2.6rem 1rem;
        color: #999;
        background: #181818;
        border-radius: 8px;
        border: 1.5px dashed #E50914;
    }
    .empty-state .icon {
        font-size: 2.3rem;
        margin-bottom: 0.6rem;
        display: block;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: #0A0A0A;
        border-right: 1px solid #2A2A2A;
    }
    section[data-testid="stSidebar"] * {
        color: #E5E5E5 !important;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 6px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: #181818 !important;
        border: 1px solid #2A2A2A !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: #222222 !important;
        border-color: #E50914 !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: #E50914 !important;
        border: none !important;
        animation: pulseRed 2.5s ease-in-out infinite;
    }

    /* Boutons principaux (zone centrale) */
    button[kind="primary"] {
        background: #E50914 !important;
        border: none !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 14px rgba(229, 9, 20, 0.4) !important;
        transition: transform 0.15s ease, background 0.15s ease !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    button[kind="primary"]:hover {
        background: #F6121D !important;
        transform: scale(1.03);
    }

    /* Barres de progression rouges */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8B0000, #E50914) !important;
    }
    .stProgress > div {
        background: #2A2A2A !important;
    }

    /* Champs de saisie */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: #181818 !important;
        border: 1px solid #333 !important;
        color: #E5E5E5 !important;
        border-radius: 4px !important;
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
        <h1>🎬 CINÉRECO</h1>
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
        <div style="font-family:'Bebas Neue',sans-serif; font-size:1.9rem; color:#E50914;">
            {len(donnees)}
        </div>
        <div style="font-size:0.75rem; opacity:0.6;">UTILISATEURS</div>
        <br>
        <div style="font-family:'Bebas Neue',sans-serif; font-size:1.9rem; color:#E50914;">
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
        "🔴 Les noeuds **rouges** représentent les utilisateurs · "
        "⚫ Les noeuds **gris foncé** représentent les films. "
        "Survolez un noeud avec la souris pour voir ses détails — "
        "vous pouvez aussi zoomer et déplacer le graphe."
    )
    st.markdown(
        '<div style="background:#181818; border-radius:10px; padding:1rem; '
        'border:1px solid #2A2A2A;">',
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
                    <div class="result-card">
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

    st.markdown(
        '<div style="background:#181818; border-radius:10px; padding:1.5rem; '
        'border:1px solid #2A2A2A;">',
        unsafe_allow_html=True,
    )
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
    <div style="text-align:center; margin-top:2.5rem; padding:1rem; color:#666; font-size:0.8rem;">
        🎬 CINÉRECO — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
