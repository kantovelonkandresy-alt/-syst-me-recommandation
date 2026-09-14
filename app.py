# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Thème "Aurora" — vibrant, trendy, avec fond animé façon aurore boréale.
# Lancer avec : streamlit run app.py

import hashlib
import requests
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
#  POSTERS (réels via OMDb, avec repli sur poster généré)
# ============================================================
GRADIENTS_POSTER = [
    ("#7F5AF0", "#2CB1BC"),
    ("#F72585", "#7209B7"),
    ("#00F5D4", "#00BBF9"),
    ("#B9FF66", "#3A86FF"),
    ("#FB5607", "#FFBE0B"),
    ("#9B5DE5", "#F15BB5"),
]
ICONES_POSTER = ["🎬", "🎞️", "🍿", "🎭", "📽️", "⭐"]


def couleurs_poster(nom_film: str):
    h = int(hashlib.md5(nom_film.encode()).hexdigest(), 16)
    debut, fin = GRADIENTS_POSTER[h % len(GRADIENTS_POSTER)]
    icone = ICONES_POSTER[h % len(ICONES_POSTER)]
    return debut, fin, icone


@st.cache_data(show_spinner=False)
def obtenir_url_poster(nom_film: str):
    cle_api = st.secrets.get("OMDB_API_KEY", "")
    if not cle_api:
        return None
    try:
        reponse = requests.get(
            "https://www.omdbapi.com/",
            params={"t": nom_film, "apikey": cle_api},
            timeout=5,
        )
        donnees_api = reponse.json()
        url = donnees_api.get("Poster")
        if url and url != "N/A":
            return url
    except Exception:
        pass
    return None


def poster_html(nom_film: str, genre: str = "", badge: str = "") -> str:
    badge_html = f'<div class="poster-badge">{badge}</div>' if badge else ""
    url_reelle = obtenir_url_poster(nom_film)

    if url_reelle:
        return (
            f'<div class="poster-card">'
            f'{badge_html}'
            f'<img src="{url_reelle}" class="poster-img" alt="{nom_film}">'
            f'<div class="poster-overlay">'
            f'<div class="poster-title">{nom_film}</div>'
            f'<div class="poster-genre">{genre}</div>'
            f'</div>'
            f'</div>'
        )

    debut, fin, icone = couleurs_poster(nom_film)
    return (
        f'<div class="poster-card" style="background: linear-gradient(160deg, {debut}, {fin});">'
        f'{badge_html}'
        f'<div class="poster-icon">{icone}</div>'
        f'<div class="poster-title">{nom_film}</div>'
        f'<div class="poster-genre">{genre}</div>'
        f'</div>'
    )


# ============================================================
#  STYLE PERSONNALISÉ (CSS) — thème "Aurora"
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes floatIcon {
        0%, 100% { transform: translateY(0) rotate(-3deg); }
        50% { transform: translateY(-8px) rotate(3deg); }
    }
    @keyframes auroraDrift {
        0%   { transform: translate(0, 0) scale(1); }
        33%  { transform: translate(4%, -6%) scale(1.08); }
        66%  { transform: translate(-4%, 4%) scale(0.96); }
        100% { transform: translate(0, 0) scale(1); }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 18px rgba(127, 90, 240, 0.4); }
        50% { box-shadow: 0 0 30px rgba(0, 245, 212, 0.5); }
    }

    /* Fond animé "aurore" */
    .stApp {
        background: #0B0B14;
        position: relative;
        overflow-x: hidden;
    }
    .stApp::before, .stApp::after {
        content: "";
        position: fixed;
        width: 60vw;
        height: 60vw;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.35;
        z-index: 0;
        pointer-events: none;
    }
    .stApp::before {
        background: radial-gradient(circle, #7F5AF0, transparent 70%);
        top: -20%;
        left: -10%;
        animation: auroraDrift 18s ease-in-out infinite;
    }
    .stApp::after {
        background: radial-gradient(circle, #00F5D4, transparent 70%);
        bottom: -25%;
        right: -10%;
        animation: auroraDrift 22s ease-in-out infinite reverse;
    }
    [data-testid="stAppViewContainer"] * , [data-testid="stMarkdownContainer"] p {
        color: #EDEBFA;
        position: relative;
        z-index: 1;
    }

    /* Bannière d'en-tête */
    .hero {
        position: relative;
        z-index: 1;
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.12);
        padding: 2.6rem 2.4rem;
        border-radius: 24px;
        margin-bottom: 1.8rem;
        animation: fadeIn 0.6s ease-out;
    }
    .hero-icon {
        display: inline-block;
        animation: floatIcon 2.4s ease-in-out infinite;
    }
    .hero h1 {
        font-family: 'Sora', sans-serif;
        background: linear-gradient(90deg, #7F5AF0, #F72585, #00F5D4, #7F5AF0);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: auroraDrift 8s linear infinite;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero p {
        color: #B4AFCB;
        font-size: 1.02rem;
        margin-top: 0.5rem;
    }
    .hero-stats {
        display: flex;
        gap: 0.8rem;
        margin-top: 1.3rem;
        flex-wrap: wrap;
    }
    .hero-pill {
        background: rgba(127, 90, 240, 0.15);
        border: 1px solid rgba(127, 90, 240, 0.4);
        border-radius: 999px;
        padding: 0.5rem 1.15rem;
        font-size: 0.85rem;
        font-weight: 700;
        color: #C9BFFF;
    }

    /* Posters */
    .poster-row {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding: 0.4rem 0.2rem 1rem;
        position: relative;
        z-index: 1;
    }
    .poster-row::-webkit-scrollbar { height: 6px; }
    .poster-row::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #7F5AF0, #00F5D4);
        border-radius: 4px;
    }
    .poster-card {
        position: relative;
        flex: 0 0 150px;
        height: 210px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 0.9rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .poster-card:hover {
        transform: translateY(-6px) scale(1.04) rotate(-1deg);
        box-shadow: 0 14px 34px rgba(127, 90, 240, 0.35);
    }
    .poster-img {
        position: absolute;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .poster-overlay {
        position: relative;
        z-index: 2;
        background: linear-gradient(180deg, transparent 0%, rgba(11,11,20,0.9) 100%);
        margin: -0.9rem;
        padding: 2.2rem 0.9rem 0.7rem;
    }
    .poster-icon {
        position: absolute;
        top: 0.7rem;
        left: 0.8rem;
        font-size: 1.6rem;
        opacity: 0.9;
        z-index: 2;
    }
    .poster-badge {
        position: absolute;
        top: 0.6rem;
        right: 0.6rem;
        background: rgba(11,11,20,0.6);
        border: 1px solid rgba(0, 245, 212, 0.5);
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
        color: #00F5D4;
        z-index: 2;
    }
    .poster-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: white;
        line-height: 1.25;
        position: relative;
        z-index: 2;
    }
    .poster-genre {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.75);
        margin-top: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        position: relative;
        z-index: 2;
    }

    /* Cartes de résultats */
    .result-card {
        position: relative;
        z-index: 1;
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-left: 4px solid #7F5AF0;
        border-radius: 16px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.6rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card:hover {
        transform: translateX(5px);
        border-left-color: #00F5D4;
        box-shadow: 0 10px 26px rgba(127, 90, 240, 0.25);
    }
    .result-card h4 {
        margin: 0 0 0.35rem 0;
        color: #F5F3FF;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .score-text {
        font-size: 0.8rem;
        color: #9C93B8;
        margin-top: 0.3rem;
    }
    .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: linear-gradient(135deg, #F72585, #7F5AF0);
        color: white;
        font-weight: 800;
        font-size: 0.8rem;
        margin-right: 0.6rem;
        vertical-align: middle;
    }
    .rang-badge {
        font-size: 1.1rem;
        margin-right: 0.4rem;
        vertical-align: middle;
    }

    /* Stat cards */
    .stat-card {
        position: relative;
        z-index: 1;
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 1.1rem 1.3rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 30px rgba(0, 245, 212, 0.2);
    }
    .stat-card .value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7F5AF0, #F72585, #00F5D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .label {
        font-size: 0.75rem;
        color: #9C93B8;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        font-weight: 600;
    }

    .empty-state {
        position: relative;
        z-index: 1;
        text-align: center;
        padding: 2.4rem 1rem;
        color: #9C93B8;
        background: rgba(255,255,255,0.03);
        border-radius: 18px;
        border: 1.5px dashed rgba(127, 90, 240, 0.4);
    }
    .empty-state .icon {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: rgba(11, 11, 20, 0.9);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(127, 90, 240, 0.2);
    }
    section[data-testid="stSidebar"] * {
        color: #EDEBFA !important;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 14px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(127, 90, 240, 0.18) !important;
        border-color: rgba(0, 245, 212, 0.4) !important;
        transform: translateX(4px);
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #7F5AF0, #F72585) !important;
        border: none !important;
        animation: glowPulse 2.6s ease-in-out infinite;
    }

    /* Boutons principaux */
    button[kind="primary"] {
        background: linear-gradient(135deg, #7F5AF0, #F72585) !important;
        border: none !important;
        border-radius: 999px !important;
        box-shadow: 0 6px 20px rgba(127, 90, 240, 0.4) !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02);
    }
    button[kind="primary"]:active {
        transform: scale(0.96) !important;
    }

    /* Barres de progression */
    .stProgress > div > div {
        background: linear-gradient(90deg, #7F5AF0, #F72585, #00F5D4) !important;
    }
    .stProgress > div {
        background: rgba(255,255,255,0.08) !important;
    }

    /* Champs de saisie */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #EDEBFA !important;
        border-radius: 12px !important;
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
total_connexions = sum(len(f) for f in donnees.values())
st.markdown(
    f"""
    <div class="hero">
        <h1><span class="hero-icon">🎬</span> CinéReco</h1>
        <p>Système de recommandation basé sur un graphe utilisateur-item —
        similarité de Jaccard + bonus de genre</p>
        <div class="hero-stats">
            <div class="hero-pill">👥 {len(donnees)} utilisateurs</div>
            <div class="hero-pill">🎞️ {len(genres)} films</div>
            <div class="hero-pill">🔗 {total_connexions} connexions</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  BARRE LATÉRALE
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

# ============================================================
#  PAGE : GRAPHE
# ============================================================
if page == "graphe":
    st.subheader("Visualisation interactive du graphe utilisateur-item")
    st.write(
        "🟣 Les noeuds **violets** représentent les utilisateurs · "
        "🩵 Les noeuds **cyan** représentent les films. "
        "Survolez un noeud pour voir ses détails — zoomez et déplacez le graphe."
    )
    st.markdown(
        '<div style="background:rgba(255,255,255,0.045); backdrop-filter: blur(16px); '
        'border-radius:18px; padding:1rem; border:1px solid rgba(255,255,255,0.1); position:relative; z-index:1;">',
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
                    <div class="result-card" style="animation-delay:{i * 0.08}s;">
                        <h4><span class="rang-badge">{rang}</span><span class="avatar">{initiales}</span>{nom}</h4>
                        <div class="score-text">Similarité : {score * 100:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(score, 1.0))

            st.write("")
            st.write(f"**Films aimés par {utilisateur} :**")
            posters = "".join(
                poster_html(f, genres.get(f, "")) for f in donnees[utilisateur]
            )
            st.markdown(f'<div class="poster-row">{posters}</div>', unsafe_allow_html=True)
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

    if st.button("✨ Générer les recommandations", type="primary"):
        recommandations = systeme.generer_recommandations(utilisateur)
        if recommandations:
            st.write(f"**Films recommandés pour {utilisateur} :**")
            score_max = max(s for _, s in recommandations) or 1
            posters = "".join(
                poster_html(film, genres.get(film, ""), badge=f"{score:.2f}")
                for film, score in recommandations
            )
            st.markdown(f'<div class="poster-row">{posters}</div>', unsafe_allow_html=True)

            st.write("")
            for film, score in recommandations:
                st.progress(min(score / score_max, 1.0), text=film)
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
    for nom, films in donnees.items():
        st.markdown(f"#### 👤 {nom}  ·  {len(films)} film(s)")
        posters = "".join(poster_html(f, genres.get(f, "")) for f in films)
        st.markdown(f'<div class="poster-row">{posters}</div>', unsafe_allow_html=True)

# ============================================================
#  PAGE : AJOUTER UN UTILISATEUR
# ============================================================
elif page == "ajouter":
    st.subheader("Ajouter un nouvel utilisateur")

    st.markdown(
        '<div style="background:rgba(255,255,255,0.045); backdrop-filter: blur(16px); '
        'border-radius:18px; padding:1.5rem; border:1px solid rgba(255,255,255,0.1); position:relative; z-index:1;">',
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
    <div style="position:relative; z-index:1; text-align:center; margin-top:2.5rem; padding:1rem; color:#6B6480; font-size:0.8rem;">
        🎬 CinéReco — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
