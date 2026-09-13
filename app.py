# ============================================================
# NOVA RECO
# Système de recommandation basé sur un graphe utilisateur-item
# Projet L2 - Python / NetworkX / Streamlit
# ============================================================

import streamlit as st
from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, obtenir_figure_plotly
from recommandation import SystemeRecommandation


# ============================================================
# CONFIGURATION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="NOVA RECO | AI Recommendation",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS - INTERFACE FUTURISTE
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap'
    );

    * {
        font-family: 'Inter', sans-serif;
    }

    /* --------------------------------------------------------
       BACKGROUND
    -------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(124, 58, 237, 0.20),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(236, 72, 153, 0.14),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(6, 182, 212, 0.10),
                transparent 35%
            ),
            #050509;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* --------------------------------------------------------
       ANIMATIONS
    -------------------------------------------------------- */

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            box-shadow:
                0 0 18px rgba(168, 85, 247, 0.20);
        }

        50% {
            box-shadow:
                0 0 35px rgba(236, 72, 153, 0.38);
        }
    }

    @keyframes gradientMove {
        0% {
            background-position: 0% 50%;
        }

        50% {
            background-position: 100% 50%;
        }

        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes onlinePulse {
        0% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.6);
        }

        70% {
            box-shadow: 0 0 0 8px rgba(34, 197, 94, 0);
        }

        100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
        }
    }

    /* --------------------------------------------------------
       TEXT
    -------------------------------------------------------- */

    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }

    p, label {
        color: #cbd5e1 !important;
    }

    /* --------------------------------------------------------
       HERO
    -------------------------------------------------------- */

    .hero {
        position: relative;
        overflow: hidden;

        padding: 2.5rem 2.8rem;
        margin-bottom: 1.8rem;

        border-radius: 26px;

        background:
            linear-gradient(
                120deg,
                #7c3aed,
                #a855f7,
                #ec4899,
                #06b6d4,
                #7c3aed
            );

        background-size: 350% 350%;

        animation:
            gradientMove 10s ease infinite,
            fadeUp 0.7s ease;

        box-shadow:
            0 20px 70px rgba(124, 58, 237, 0.25);

        border: 1px solid rgba(255,255,255,0.15);
    }

    .hero::before {
        content: "";
        position: absolute;

        width: 280px;
        height: 280px;

        right: -100px;
        top: -130px;

        border-radius: 50%;

        background: rgba(255,255,255,0.12);

        filter: blur(5px);
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .hero-small {
        font-size: 0.78rem;
        font-weight: 800;

        letter-spacing: 0.20em;

        text-transform: uppercase;

        color: rgba(255,255,255,0.85);
    }

    .hero-title {
        font-size: 3rem;
        line-height: 1.05;

        font-weight: 900;

        color: white !important;

        margin: 0.35rem 0;

        letter-spacing: -0.05em;

        text-shadow:
            0 5px 30px rgba(0,0,0,0.20);
    }

    .hero-subtitle {
        font-size: 1rem;

        color: rgba(255,255,255,0.92) !important;

        max-width: 850px;

        margin-top: 0.8rem;
    }

    .hero-badge {
        display: inline-block;

        margin-top: 1rem;

        padding: 0.45rem 0.85rem;

        border-radius: 999px;

        background: rgba(0,0,0,0.18);

        border: 1px solid rgba(255,255,255,0.20);

        color: white;

        font-size: 0.75rem;

        font-weight: 700;
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0c0817 0%,
                #07060d 55%,
                #040408 100%
            );

        border-right:
            1px solid rgba(168,85,247,0.18);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    .sidebar-logo {
        text-align: center;

        padding: 1.3rem 0 1.5rem;
    }

    .sidebar-logo-title {
        font-size: 1.55rem;

        font-weight: 900;

        background:
            linear-gradient(
                90deg,
                #c084fc,
                #f472b6,
                #22d3ee
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sidebar-logo-subtitle {
        color: #64748b !important;

        font-size: 0.68rem;

        letter-spacing: 0.16em;

        text-transform: uppercase;
    }

    section[data-testid="stSidebar"] button {
        border-radius: 13px !important;

        min-height: 42px;

        font-weight: 600 !important;

        transition:
            transform 0.15s ease,
            background 0.15s ease !important;
    }

    section[data-testid="stSidebar"]
    button[kind="secondary"] {
        background:
            rgba(255,255,255,0.035) !important;

        border:
            1px solid rgba(255,255,255,0.06) !important;
    }

    section[data-testid="stSidebar"]
    button[kind="secondary"]:hover {
        transform: translateX(4px);

        background:
            rgba(168,85,247,0.12) !important;

        border-color:
            rgba(168,85,247,0.35) !important;
    }

    section[data-testid="stSidebar"]
    button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #ec4899
            ) !important;

        border: none !important;

        animation:
            pulseGlow 2.8s infinite;
    }

    /* --------------------------------------------------------
       USER STATUS
    -------------------------------------------------------- */

    .online-card {
        margin-top: 1.2rem;

        padding: 0.9rem;

        border-radius: 15px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.07);
    }

    .online-dot {
        display: inline-block;

        width: 9px;
        height: 9px;

        border-radius: 50%;

        background: #22c55e;

        margin-right: 7px;

        animation:
            onlinePulse 2s infinite;
    }

    /* --------------------------------------------------------
       STAT CARDS
    -------------------------------------------------------- */

    .stat-card {
        position: relative;

        overflow: hidden;

        padding: 1.35rem;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.065),
                rgba(255,255,255,0.025)
            );

        border:
            1px solid rgba(255,255,255,0.08);

        backdrop-filter: blur(16px);

        animation:
            fadeUp 0.6s ease;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);

        border-color:
            rgba(168,85,247,0.40);

        box-shadow:
            0 15px 40px rgba(124,58,237,0.15);
    }

    .stat-icon {
        font-size: 1.5rem;

        margin-bottom: 0.7rem;
    }

    .stat-value {
        font-size: 2rem;

        line-height: 1;

        font-weight: 900;

        background:
            linear-gradient(
                90deg,
                #c084fc,
                #f472b6,
                #22d3ee
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-label {
        margin-top: 0.45rem;

        color: #94a3b8;

        font-size: 0.72rem;

        text-transform: uppercase;

        letter-spacing: 0.13em;

        font-weight: 700;
    }

    /* --------------------------------------------------------
       SECTION TITLE
    -------------------------------------------------------- */

    .section-title {
        margin-top: 2rem;
        margin-bottom: 0.9rem;

        font-size: 1.35rem;

        font-weight: 800;

        color: #f8fafc;
    }

    .section-line {
        height: 2px;

        width: 55px;

        margin-top: 0.45rem;

        border-radius: 999px;

        background:
            linear-gradient(
                90deg,
                #a855f7,
                #ec4899,
                #22d3ee
            );
    }

    /* --------------------------------------------------------
       GLASS CARD
    -------------------------------------------------------- */

    .glass {
        padding: 1.4rem;

        border-radius: 20px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.08);

        backdrop-filter: blur(15px);
    }

    /* --------------------------------------------------------
       AI CARD
    -------------------------------------------------------- */

    .ai-card {
        padding: 1.4rem;

        border-radius: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(124,58,237,0.17),
                rgba(236,72,153,0.10),
                rgba(6,182,212,0.07)
            );

        border:
            1px solid rgba(168,85,247,0.25);

        box-shadow:
            0 0 35px rgba(124,58,237,0.08);
    }

    .ai-label {
        color: #c084fc;

        font-size: 0.7rem;

        font-weight: 800;

        letter-spacing: 0.16em;

        text-transform: uppercase;
    }

    .ai-title {
        margin-top: 0.35rem;

        font-size: 1.35rem;

        font-weight: 800;

        color: #f8fafc;
    }

    .ai-text {
        margin-top: 0.5rem;

        color: #a8b2c1;

        font-size: 0.88rem;

        line-height: 1.6;
    }

    /* --------------------------------------------------------
       RESULT CARDS
    -------------------------------------------------------- */

    .result-card {
        padding: 1.05rem 1.25rem;

        margin-bottom: 0.75rem;

        border-radius: 16px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.075);

        border-left:
            4px solid #a855f7;

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease;
    }

    .result-card:hover {
        transform: translateX(5px);

        box-shadow:
            0 12px 35px rgba(124,58,237,0.13);
    }

    .result-card.film {
        border-left-color: #ec4899;
    }

    .result-title {
        color: #f8fafc;

        font-size: 1rem;

        font-weight: 700;
    }

    .result-info {
        color: #94a3b8;

        font-size: 0.78rem;

        margin-top: 0.3rem;
    }

    .score {
        color: #22d3ee;

        font-size: 1.15rem;

        font-weight: 900;
    }

    .rank {
        display: inline-flex;

        align-items: center;
        justify-content: center;

        width: 30px;
        height: 30px;

        margin-right: 8px;

        border-radius: 9px;

        background:
            rgba(168,85,247,0.13);

        color: #c084fc;

        font-size: 0.8rem;

        font-weight: 800;
    }

    .genre {
        display: inline-block;

        margin-left: 0.5rem;

        padding: 0.2rem 0.55rem;

        border-radius: 999px;

        background:
            rgba(236,72,153,0.10);

        border:
            1px solid rgba(236,72,153,0.22);

        color: #f472b6;

        font-size: 0.65rem;

        font-weight: 700;
    }

    /* --------------------------------------------------------
       EMPTY STATE
    -------------------------------------------------------- */

    .empty {
        padding: 3rem 1rem;

        text-align: center;

        border-radius: 20px;

        background:
            rgba(255,255,255,0.025);

        border:
            1px dashed rgba(168,85,247,0.30);
    }

    .empty-icon {
        font-size: 2.8rem;

        margin-bottom: 0.7rem;
    }

    .empty-title {
        color: #e2e8f0;

        font-size: 1rem;

        font-weight: 700;
    }

    .empty-text {
        color: #64748b;

        font-size: 0.82rem;

        margin-top: 0.35rem;
    }

    /* --------------------------------------------------------
       INPUTS
    -------------------------------------------------------- */

    input,
    textarea,
    [data-baseweb="select"] > div {
        background:
            rgba(255,255,255,0.045) !important;

        border:
            1px solid rgba(255,255,255,0.10) !important;

        border-radius: 12px !important;

        color: #f8fafc !important;
    }

    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #ec4899
            ) !important;

        border: none !important;

        box-shadow:
            0 10px 30px rgba(124,58,237,0.20) !important;

        font-weight: 700 !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px);

        box-shadow:
            0 15px 40px rgba(236,72,153,0.25) !important;
    }

    /* --------------------------------------------------------
       PROGRESS
    -------------------------------------------------------- */

    [data-testid="stProgress"] > div > div {
        background:
            linear-gradient(
                90deg,
                #7c3aed,
                #ec4899,
                #22d3ee
            ) !important;
    }

    /* --------------------------------------------------------
       GRAPH CONTAINER
    -------------------------------------------------------- */

    .graph-header {
        padding: 1rem 1.2rem;

        margin-bottom: 1rem;

        border-radius: 15px;

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.07);
    }

    .legend-user {
        color: #a855f7;

        font-weight: 700;
    }

    .legend-film {
        color: #ec4899;

        font-weight: 700;
    }

    /* --------------------------------------------------------
       FOOTER
    -------------------------------------------------------- */

    .footer {
        margin-top: 3rem;

        padding: 1.4rem;

        text-align: center;

        border-top:
            1px solid rgba(255,255,255,0.06);

        color: #475569;

        font-size: 0.72rem;
    }

    /* --------------------------------------------------------
       HIDE STREAMLIT ELEMENTS
    -------------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def charger_systeme():
    donnees = obtenir_donnees()
    genres = obtenir_genres()
    return donnees, genres


donnees, genres = charger_systeme()

systeme = SystemeRecommandation(
    donnees,
    genres
)


# ============================================================
# INFORMATIONS GÉNÉRALES
# ============================================================

nombre_utilisateurs = len(donnees)
nombre_films = len(genres)

total_connexions = sum(
    len(films)
    for films in donnees.values()
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-content">

            <div class="hero-small">
                ◈ AI RECOMMENDATION INTELLIGENCE
            </div>

            <div class="hero-title">
                NOVA RECO
            </div>

            <div class="hero-subtitle">
                Système intelligent de recommandation basé sur
                un graphe utilisateur-item, la similarité de
                Jaccard et l'analyse des genres.
            </div>

            <div class="hero-badge">
                🧠 PYTHON · NETWORKX · STREAMLIT
            </div>

        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "accueil"


PAGES = [
    ("accueil", "⌂  Dashboard"),
    ("graphe", "◈  Graphe intelligent"),
    ("similaires", "◎  Utilisateurs similaires"),
    ("recommandations", "✦  Recommandations IA"),
    ("liste", "◉  Utilisateurs"),
    ("ajouter", "+  Ajouter utilisateur"),
]


with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-logo-title">
                NOVA RECO
            </div>

            <div class="sidebar-logo-subtitle">
                AI recommendation system
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")

    for cle, libelle in PAGES:

        actif = (
            st.session_state.page == cle
        )

        if st.button(
            libelle,
            key=f"nav_{cle}",
            use_container_width=True,
            type="primary" if actif else "secondary",
        ):
            st.session_state.page = cle
            st.rerun()

    st.markdown("---")

    st.markdown(
        f"""
        <div class="online-card">

            <div style="font-weight:700;">
                <span class="online-dot"></span>
                SYSTEM ONLINE
            </div>

            <div style="
                margin-top:0.55rem;
                color:#64748b;
                font-size:0.72rem;
            ">
                Recommendation engine active
            </div>

        </div>

        <div style="
            margin-top:1.2rem;
            padding:1rem;
            border-radius:15px;
            background:rgba(255,255,255,0.025);
            border:1px solid rgba(255,255,255,0.06);
        ">

            <div style="
                color:#64748b;
                font-size:0.65rem;
                letter-spacing:0.12em;
            ">
                DATABASE
            </div>

            <div style="
                margin-top:0.5rem;
                font-size:1.4rem;
                font-weight:800;
            ">
                {nombre_utilisateurs}
            </div>

            <div style="
                color:#64748b;
                font-size:0.7rem;
            ">
                utilisateurs
            </div>

            <div style="
                margin-top:0.9rem;
                font-size:1.4rem;
                font-weight:800;
            ">
                {nombre_films}
            </div>

            <div style="
                color:#64748b;
                font-size:0.7rem;
            ">
                films
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


page = st.session_state.page


# ============================================================
# STATISTIQUES
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="stat-card">

            <div class="stat-icon">👥</div>

            <div class="stat-value">
                {nombre_utilisateurs}
            </div>

            <div class="stat-label">
                Utilisateurs
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with c2:
    st.markdown(
        f"""
        <div class="stat-card">

            <div class="stat-icon">🎬</div>

            <div class="stat-value">
                {nombre_films}
            </div>

            <div class="stat-label">
                Films
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with c3:
    st.markdown(
        f"""
        <div class="stat-card">

            <div class="stat-icon">🔗</div>

            <div class="stat-value">
                {total_connexions}
            </div>

            <div class="stat-label">
                Connexions
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with c4:
    st.markdown(
        """
        <div class="stat-card">

            <div class="stat-icon">🧠</div>

            <div class="stat-value">
                IA
            </div>

            <div class="stat-label">
                Moteur actif
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE ACCUEIL
# ============================================================

if page == "accueil":

    st.markdown(
        """
        <div class="section-title">
            Bienvenue dans NOVA RECO
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(
        [1.35, 1],
        gap="large",
    )

    with col_left:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-label">
                    ✦ INTELLIGENT ENGINE
                </div>

                <div class="ai-title">
                    Votre système de recommandation
                </div>

                <div class="ai-text">
                    NOVA RECO analyse les relations entre
                    les utilisateurs et les films sous forme
                    de graphe. Le moteur utilise la similarité
                    de Jaccard pour identifier les utilisateurs
                    ayant des goûts proches et proposer ensuite
                    des films susceptibles de plaire.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown(
            """
            <div class="glass">

                <div style="
                    font-size:0.72rem;
                    color:#a78bfa;
                    font-weight:800;
                    letter-spacing:0.12em;
                ">
                    COMMENT ÇA MARCHE ?
                </div>

                <div style="
                    margin-top:1rem;
                    line-height:2;
                    color:#cbd5e1;
                ">

                    <b>01</b> &nbsp; 👤 Sélectionner un utilisateur
                    <br>

                    <b>02</b> &nbsp; 🔗 Analyser le graphe
                    utilisateur-item
                    <br>

                    <b>03</b> &nbsp; 🧠 Calculer la similarité
                    de Jaccard
                    <br>

                    <b>04</b> &nbsp; 🎬 Générer les recommandations
                    <br>

                    <b>05</b> &nbsp; 📊 Afficher les scores

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:

        st.markdown(
            """
            <div class="glass">

                <div style="
                    font-size:0.72rem;
                    color:#22d3ee;
                    font-weight:800;
                    letter-spacing:0.12em;
                ">
                    SYSTEM STATUS
                </div>

                <div style="
                    margin-top:1rem;
                    font-size:1.1rem;
                    font-weight:800;
                ">
                    🟢 Recommendation Engine
                </div>

                <div style="
                    margin-top:0.7rem;
                    color:#94a3b8;
                    font-size:0.8rem;
                ">
                    Tous les modules principaux sont prêts
                    à être utilisés.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if nombre_utilisateurs > 0:

            utilisateur_exemple = list(
                donnees.keys()
            )[0]

            st.markdown(
                f"""
                <div class="glass">

                    <div style="
                        color:#64748b;
                        font-size:0.7rem;
                        text-transform:uppercase;
                        letter-spacing:0.12em;
                    ">
                        Utilisateur disponible
                    </div>

                    <div style="
                        margin-top:0.6rem;
                        font-size:1.4rem;
                        font-weight:800;
                    ">
                        👤 {utilisateur_exemple}
                    </div>

                    <div style="
                        margin-top:0.4rem;
                        color:#94a3b8;
                        font-size:0.78rem;
                    ">
                        {len(donnees[utilisateur_exemple])}
                        film(s) enregistré(s)
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE GRAPHE
# ============================================================

elif page == "graphe":

    st.markdown(
        """
        <div class="section-title">
            Graphe utilisateur-item
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="graph-header">

            <span class="legend-user">
                ● Utilisateurs
            </span>

            &nbsp;&nbsp;&nbsp;

            <span class="legend-film">
                ● Films
            </span>

            <br>

            <span style="
                color:#64748b;
                font-size:0.78rem;
            ">
                Survolez les nœuds, zoomez et déplacez le graphe
                avec la souris.
            </span>

        </div>
        """,
        unsafe_allow_html=True,
    )

    graphe = creer_graphe()

    fig = obtenir_figure_plotly(graphe)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
        },
    )


# ============================================================
# PAGE UTILISATEURS SIMILAIRES
# ============================================================

elif page == "similaires":

    st.markdown(
        """
        <div class="section-title">
            Utilisateurs similaires
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-label">
                🧠 JACCARD ANALYSIS
            </div>

            <div class="ai-title">
                Trouver les profils ayant des goûts proches
            </div>

            <div class="ai-text">
                Le système compare les films appréciés
                par chaque utilisateur et calcule un score
                de similarité.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if donnees:

        utilisateur = st.selectbox(
            "Sélectionnez un utilisateur",
            list(donnees.keys()),
            key="similar_user",
        )

        if st.button(
            "🔍 ANALYSER LA SIMILARITÉ",
            type="primary",
            use_container_width=True,
        ):

            similaires = (
                systeme.trouver_utilisateurs_similaires(
                    utilisateur
                )
            )

            if similaires:

                st.markdown(
                    f"""
                    <div style="
                        margin:1.2rem 0 1rem;
                        color:#94a3b8;
                        font-size:0.85rem;
                    ">
                        Résultats pour
                        <b style="color:#c084fc;">
                            {utilisateur}
                        </b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for i, (nom, score) in enumerate(
                    similaires
                ):

                    pourcentage = score * 100

                    st.markdown(
                        f"""
                        <div class="result-card">

                            <div class="result-title">
                                <span class="rank">
                                    {i + 1}
                                </span>

                                👤 {nom}

                                <span class="score">
                                    {pourcentage:.1f}%
                                </span>
                            </div>

                            <div class="result-info">
                                Similarité calculée avec
                                l'indice de Jaccard
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.progress(
                        min(score, 1.0)
                    )

            else:

                st.markdown(
                    """
                    <div class="empty">

                        <div class="empty-icon">
                            🔎
                        </div>

                        <div class="empty-title">
                            Aucun utilisateur similaire
                        </div>

                        <div class="empty-text">
                            Aucun profil avec une similarité
                            positive n'a été trouvé.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.warning(
            "Aucun utilisateur disponible."
        )


# ============================================================
# PAGE RECOMMANDATIONS
# ============================================================

elif page == "recommandations":

    st.markdown(
        """
        <div class="section-title">
            Recommandations IA
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-label">
                ✦ NOVA AI ENGINE
            </div>

            <div class="ai-title">
                Découvrez vos prochains films
            </div>

            <div class="ai-text">
                Les recommandations sont générées à partir
                des utilisateurs similaires et des films
                qu'ils apprécient.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if donnees:

        utilisateur = st.selectbox(
            "Sélectionnez un utilisateur",
            list(donnees.keys()),
            key="recommend_user",
        )

        if st.button(
            "✨ GÉNÉRER LES RECOMMANDATIONS",
            type="primary",
            use_container_width=True,
        ):

            recommandations = (
                systeme.generer_recommandations(
                    utilisateur
                )
            )

            if recommandations:

                score_max = max(
                    score
                    for _, score in recommandations
                )

                if score_max <= 0:
                    score_max = 1

                st.markdown(
                    f"""
                    <div style="
                        margin:1.2rem 0;
                        padding:0.8rem 1rem;
                        border-radius:13px;
                        background:rgba(34,211,238,0.05);
                        border:1px solid rgba(34,211,238,0.12);
                    ">
                        🎯 Recommandations personnalisées
                        pour
                        <b style="color:#22d3ee;">
                            {utilisateur}
                        </b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for i, (film, score) in enumerate(
                    recommandations
                ):

                    genre = genres.get(
                        film,
                        "Genre inconnu"
                    )

                    progression = (
                        score / score_max
                    )

                    st.markdown(
                        f"""
                        <div class="result-card film">

                            <div class="result-title">

                                <span class="rank">
                                    {i + 1}
                                </span>

                                🎬 {film}

                                <span class="genre">
                                    {genre}
                                </span>

                                <span class="score">
                                    {score:.2f}
                                </span>

                            </div>

                            <div class="result-info">
                                Score de pertinence
                                calculé par le moteur
                                de recommandation
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.progress(
                        min(progression, 1.0)
                    )

            else:

                st.markdown(
                    """
                    <div class="empty">

                        <div class="empty-icon">
                            🎬
                        </div>

                        <div class="empty-title">
                            Aucune recommandation
                        </div>

                        <div class="empty-text">
                            Le système ne dispose pas encore
                            d'informations suffisantes.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.warning(
            "Aucun utilisateur disponible."
        )


# ============================================================
# PAGE LISTE UTILISATEURS
# ============================================================

elif page == "liste":

    st.markdown(
        """
        <div class="section-title">
            Utilisateurs & préférences
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if donnees:

        colonnes = st.columns(2)

        for i, (nom, films) in enumerate(
            donnees.items()
        ):

            with colonnes[i % 2]:

                with st.expander(
                    f"👤 {nom}   ·   {len(films)} film(s)"
                ):

                    st.markdown(
                        f"""
                        <div style="
                            color:#64748b;
                            font-size:0.72rem;
                            margin-bottom:0.7rem;
                            text-transform:uppercase;
                            letter-spacing:0.1em;
                        ">
                            Films appréciés
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    for film in films:

                        genre = genres.get(
                            film,
                            "Genre inconnu"
                        )

                        st.markdown(
                            f"""
                            <div style="
                                padding:0.65rem 0;
                                border-bottom:
                                1px solid
                                rgba(255,255,255,0.05);
                            ">

                                🎬
                                <b>{film}</b>

                                <span class="genre">
                                    {genre}
                                </span>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    else:

        st.warning(
            "Aucun utilisateur enregistré."
        )


# ============================================================
# PAGE AJOUTER UTILISATEUR
# ============================================================

elif page == "ajouter":

    st.markdown(
        """
        <div class="section-title">
            Ajouter un utilisateur
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-label">
                + NEW PROFILE
            </div>

            <div class="ai-title">
                Créer un nouveau profil
            </div>

            <div class="ai-text">
                Ajoutez un utilisateur ainsi que les films
                qu'il apprécie. Ces données seront utilisées
                par le moteur de recommandation.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2 = st.columns(
        [1, 1.5],
        gap="large",
    )

    with col1:

        nom = st.text_input(
            "Nom de l'utilisateur",
            placeholder="Ex : Kanto",
        )

    with col2:

        films_texte = st.text_input(
            "Films aimés",
            placeholder="Ex : Avengers, Titanic, Avatar",
        )

    st.write("")

    if st.button(
        "➕ CRÉER LE PROFIL",
        type="primary",
        use_container_width=True,
    ):

        nom_propre = nom.strip()

        liste_films = [
            film.strip()
            for film in films_texte.split(",")
            if film.strip()
        ]

        if not nom_propre:

            st.error(
                "❌ Le nom de l'utilisateur est obligatoire."
            )

        elif nom_propre in donnees:

            st.error(
                f"❌ L'utilisateur '{nom_propre}' existe déjà."
            )

        elif not liste_films:

            st.error(
                "❌ Ajoutez au moins un film."
            )

        else:

            ajouter_utilisateur(
                nom_propre,
                liste_films,
            )

            st.success(
                f"✅ L'utilisateur '{nom_propre}' a été ajouté avec succès."
            )

            st.cache_data.clear()

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <div style="
            font-size:0.85rem;
            color:#64748b;
            font-weight:700;
        ">
            NOVA RECO
        </div>

        <div style="margin-top:0.35rem;">
            AI Recommendation Intelligence
            · Projet L2
            · Python / NetworkX / Streamlit
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)
