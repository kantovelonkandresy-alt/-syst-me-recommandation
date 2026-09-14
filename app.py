# app.py
# Application Web (Streamlit) du système de recommandation utilisateur-item.
# Thème "Cinéma Doré" (navy + or) — posters générés + disposition en rangées.
# Lancer avec : streamlit run app.py

import hashlib
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
#  PALETTE DE GRADIENTS POUR LES POSTERS GÉNÉRÉS
#  (aucune image réelle n'est utilisée : chaque film reçoit un
#  "poster" stylisé généré à partir de son nom, pour éviter tout
#  problème de droits d'auteur sur les affiches officielles)
# ============================================================
GRADIENTS_POSTER = [
    ("#1B2A4A", "#3A5A8C"),
    ("#2E1F47", "#6C3FA6"),
    ("#0F3D3E", "#1F8A70"),
    ("#4A3B1F", "#D4AF37"),
    ("#1F2937", "#4B5563"),
    ("#142B3D", "#2C7DA0"),
]
ICONES_POSTER = ["🎬", "🎞️", "🍿", "🎭", "📽️", "⭐"]


def couleurs_poster(nom_film: str):
    """Choisit un dégradé et une icône de façon stable pour un film donné."""
    h = int(hashlib.md5(nom_film.encode()).hexdigest(), 16)
    debut, fin = GRADIENTS_POSTER[h % len(GRADIENTS_POSTER)]
    icone = ICONES_POSTER[h % len(ICONES_POSTER)]
    return debut, fin, icone


def poster_html(nom_film: str, genre: str = "", badge: str = "") -> str:
    """Construit le HTML d'un poster stylisé (généré, pas une vraie affiche)."""
    debut, fin, icone = couleurs_poster(nom_film)
    badge_html = f'<div class="poster-badge">{badge}</div>' if badge else ""
    return f"""
    <div class="poster-card" style="background: linear-gradient(160deg, {debut}, {fin});">
        {badge_html}
        <div class="poster-icon">{icone}</div>
        <div class="poster-title">{nom_film}</div>
        <div class="poster-genre">{genre}</div>
    </div>
    """


# ============================================================
#  STYLE PERSONNALISÉ (CSS) — thème "Cinéma Doré"
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes floatIcon {
        0%, 100% { transform: translateY(0) rotate(-2deg); }
        50% { transform: translateY(-8px) rotate(2deg); }
    }
    @keyframes glowGold {
        0%, 100% { box-shadow: 0 0 16px rgba(212, 175, 55, 0.35); }
        50% { box-shadow: 0 0 26px rgba(212, 175, 55, 0.55); }
    }

    /* Fond général */
    .stApp {
        background: radial-gradient(circle at 15% 0%, #10182B 0%, #0A0E17 45%, #050608 100%);
    }
    [data-testid="stAppViewContainer"] * , [data-testid="stMarkdownContainer"] p {
        color: #EDE6D6;
    }

    /* Bannière d'en-tête */
    .hero {
        background: linear-gradient(120deg, #1B2A4A 0%, #12151F 60%, #0A0E17 100%);
        padding: 2.4rem 2.4rem 1.8rem;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        border: 1px solid rgba(212, 175, 55, 0.25);
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        animation: fadeIn 0.6s ease-out;
    }
    .hero-icon {
        display: inline-block;
        animation: floatIcon 2.4s ease-in-out infinite;
    }
    .hero h1 {
        font-family: 'Playfair Display', serif;
        background: linear-gradient(90deg, #D4AF37, #F2C14E, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.7rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.01em;
    }
    .hero p {
        color: #B8B0A0;
        font-size: 1.02rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    .hero-stats {
        display: flex;
        gap: 0.8rem;
        margin-top: 1.3rem;
        flex-wrap: wrap;
    }
    .hero-pill {
        background: rgba(212, 175, 55, 0.08);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 999px;
        padding: 0.5rem 1.1rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: #F2C14E;
    }

    /* Posters générés */
    .poster-row {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding: 0.4rem 0.2rem 1rem;
    }
    .poster-row::-webkit-scrollbar {
        height: 6px;
    }
    .poster-row::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.4);
        border-radius: 4px;
    }
    .poster-card {
        position: relative;
        flex: 0 0 150px;
        height: 210px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 0.9rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .poster-card:hover {
        transform: translateY(-6px) scale(1.03);
        box-shadow: 0 12px 30px rgba(212, 175, 55, 0.25);
    }
    .poster-icon {
        position: absolute;
        top: 0.7rem;
        left: 0.8rem;
        font-size: 1.6rem;
        opacity: 0.85;
    }
    .poster-badge {
        position: absolute;
        top: 0.6rem;
        right: 0.6rem;
        background: rgba(0,0,0,0.55);
        border: 1px solid rgba(212, 175, 55, 0.5);
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
        color: #F2C14E;
    }
    .poster-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        line-height: 1.25;
    }
    .poster-genre {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.75);
        margin-top: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Cartes de résultats (utilisateurs similaires) */
    .result-card {
        background: #12151F;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 4px solid #D4AF37;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.15);
    }
    .result-card h4 {
        margin: 0 0 0.35rem 0;
        color: #F5F0E6;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .score-text {
        font-size: 0.8rem;
        color: #9A9484;
        margin-top: 0.3rem;
    }
    .avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #D4AF37, #8C6D1F);
        color: #0A0E17;
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

    /* Cartes de statistiques (page graphe) */
    .stat-card {
        background: #12151F;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(212, 175, 55, 0.15);
    }
    .stat-card .value {
        font-family: 'Playfair Display', serif;
        font-size: 1.9rem;
        font-weight: 800;
        color: #D4AF37;
    }
    .stat-card .label {
        font-size: 0.75rem;
        color: #9A9484;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .empty-state {
        text-align: center;
        padding: 2.4rem 1rem;
        color: #9A9484;
        background: #12151F;
        border-radius: 14px;
        border: 1.5px dashed rgba(212, 175, 55, 0.3);
    }
    .empty-state .icon {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: #070A11;
        border-right: 1px solid rgba(212, 175, 55, 0.15);
    }
    section[data-testid="stSidebar"] * {
        color: #EDE6D6 !important;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 10px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(212, 175, 55, 0.1) !important;
        border-color: rgba(212, 175, 55, 0.35) !important;
        transform: translateX(4px);
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #8C6D1F, #D4AF37) !important;
        color: #0A0E17 !important;
        border: none !important;
        animation: glowGold 2.6s ease-in-out infinite;
    }

    /* Boutons principaux */
    button[kind="primary"] {
        background: linear-gradient(135deg, #8C6D1F, #D4AF37) !important;
        color: #0A0E17 !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.35) !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
    }
    button[kind="primary"]:active {
        transform: scale(0.96) !important;
    }

    /* Barres de progression dorées */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8C6D1F, #D4AF37, #F2C14E) !important;
    }
    .stProgress > div {
        background: rgba(255,255,255,0.08) !important;
    }

    /* Champs de saisie */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: #12151F !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #EDE6D6 !important;
        border-radius: 8px !important;
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
#  BANNIÈRE D'EN-TÊTE (statistiques intégrées)
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

# ============================================================
#  PAGE : GRAPHE
# ============================================================
if page == "graphe":
    st.subheader("Visualisation interactive du graphe utilisateur-item")
    st.write(
        "🟡 Les noeuds **dorés** représentent les utilisateurs · "
        "🔵 Les noeuds **bleus** représentent les films. "
        "Survolez un noeud pour voir ses détails — zoomez et déplacez le graphe."
    )
    st.markdown(
        '<div style="background:#12151F; border-radius:14px; padding:1rem; '
        'border:1px solid rgba(255,255,255,0.07);">',
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

            # Aperçu des films de l'utilisateur sélectionné, en rangée de posters
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
                poster_html(
                    film,
                    genres.get(film, ""),
                    badge=f"{score:.2f}",
                )
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
#  PAGE : LISTE DES UTILISATEURS (grille de posters par utilisateur)
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
        '<div style="background:#12151F; border-radius:14px; padding:1.5rem; '
        'border:1px solid rgba(255,255,255,0.07);">',
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
    <div style="text-align:center; margin-top:2.5rem; padding:1rem; color:#6B6455; font-size:0.8rem;">
        🎬 CinéReco — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
