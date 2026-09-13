# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Version 2 - Interface soignée : navigation par boutons, animations, dégradés.
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
#  STYLE PERSONNALISÉ (CSS)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #FAFAFF 0%, #F5F3FC 100%);
    }

    .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6C5CE7, #A363E8);
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.6rem;
        vertical-align: middle;
    }
    .avatar.film {
        background: linear-gradient(135deg, #FD79A8, #E84393);
    }

    .rang-badge {
        display: inline-block;
        font-size: 1.1rem;
        margin-right: 0.4rem;
        vertical-align: middle;
    }

    .empty-state {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #999;
        background: white;
        border-radius: 16px;
        border: 1.5px dashed #E0DCF0;
    }
    .empty-state .icon {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Bannière d'en-tête */
    .hero {
        background: linear-gradient(135deg, #6C5CE7 0%, #A363E8 50%, #FD79A8 100%);
        padding: 2.4rem 2.2rem;
        border-radius: 20px;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.3);
        animation: fadeIn 0.5s ease-out;
    }
    .hero h1 {
        color: white;
        font-size: 2.3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 1.02rem;
        margin-top: 0.5rem;
    }

    /* Cartes de statistiques */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 3px 12px rgba(0,0,0,0.06);
        border: 1px solid #F0F0F5;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.6s ease-out;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(108, 92, 231, 0.15);
    }
    .stat-card .value {
        font-size: 1.9rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C5CE7, #FD79A8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .label {
        font-size: 0.82rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }

    /* Cartes de résultats (utilisateurs / films) */
    .result-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #6C5CE7;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 14px rgba(108, 92, 231, 0.12);
    }
    .result-card.film {
        border-left: 5px solid #FD79A8;
    }
    .result-card h4 {
        margin: 0 0 0.3rem 0;
        color: #2D2D2D;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .genre-badge {
        display: inline-block;
        background: #FFEAF3;
        color: #E84393;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.18rem 0.65rem;
        border-radius: 999px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    .score-text {
        font-size: 0.8rem;
        color: #999;
        margin-top: 0.3rem;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1B2E 0%, #2A2440 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #F1F1F1 !important;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 10px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.25rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #6C5CE7, #FD79A8) !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.4) !important;
    }

    /* Boutons principaux (zone centrale) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #6C5CE7, #FD79A8) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(108, 92, 231, 0.35) !important;
        transition: transform 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(108, 92, 231, 0.45) !important;
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
        <div style="font-size:1.6rem; font-weight:700;">{len(donnees)}</div>
        <div style="font-size:0.75rem; opacity:0.65;">UTILISATEURS</div>
        <br>
        <div style="font-size:1.6rem; font-weight:700;">{len(genres)}</div>
        <div style="font-size:0.75rem; opacity:0.65;">FILMS</div>
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
    with st.container(border=True):
        graphe = creer_graphe()
        fig = obtenir_figure_plotly(graphe)
        st.plotly_chart(fig, use_container_width=True)

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
                        <h4>{rang}<span class="avatar">{initiales}</span>{nom}</h4>
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
                        <h4>{rang}🎬 {film} <span class="genre-badge">{genre}</span></h4>
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

st.markdown(
    """
    <div style="text-align:center; margin-top:2.5rem; padding:1rem; color:#AAA; font-size:0.8rem;">
        🎬 CinéReco — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
