# app.py
# CinéReco - Application Web (Streamlit) du système de recommandation
# utilisateur-item. Thème "Aurora" : fond sombre avec bandes de lumière
# animées (violet, cyan, ambre, lime) + glassmorphism moderne.
# Lancer avec : streamlit run app.py

import streamlit as st
import plotly.graph_objects as go
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
#  STYLE PERSONNALISÉ (CSS) — thème Aurora
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    @keyframes auroraFlow {
        0%   { transform: translate(-10%, -5%) rotate(0deg) scale(1); }
        33%  { transform: translate(8%, 6%) rotate(8deg) scale(1.15); }
        66%  { transform: translate(-6%, 8%) rotate(-6deg) scale(1.05); }
        100% { transform: translate(-10%, -5%) rotate(0deg) scale(1); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Fond nuit + bandes d'aurore animées */
    .stApp {
        background: #05070d;
        position: relative;
        overflow-x: hidden;
    }
    .aurora-bande {
        position: fixed;
        width: 140vw;
        height: 140vh;
        top: -20vh;
        left: -20vw;
        z-index: 0;
        pointer-events: none;
        filter: blur(80px);
        opacity: 0.55;
        background:
            radial-gradient(ellipse 30% 18% at 25% 30%, #7C3AED 0%, transparent 70%),
            radial-gradient(ellipse 25% 15% at 70% 25%, #22D3EE 0%, transparent 70%),
            radial-gradient(ellipse 28% 16% at 55% 60%, #F59E0B 0%, transparent 70%),
            radial-gradient(ellipse 24% 14% at 30% 70%, #A3E635 0%, transparent 70%);
        animation: auroraFlow 26s ease-in-out infinite;
    }
    [data-testid="stAppViewContainer"], section[data-testid="stSidebar"] {
        position: relative;
        z-index: 1;
    }
    [data-testid="stAppViewContainer"] *, [data-testid="stMarkdownContainer"] p {
        color: #E7E9F0;
    }

    /* En-tête */
    .hero {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-top: 3px solid #7C3AED;
        padding: 2.6rem 2.4rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        animation: fadeIn 0.6s ease-out;
    }
    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        color: #FAFAFF; font-size: 2.5rem; font-weight: 700; margin: 0;
    }
    .hero p { color: #A6ABBD; font-size: 1.02rem; margin-top: 0.6rem; }

    /* Cartes en verre */
    .glass-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
    }

    /* Cartes de statistiques — chacune son accent Aurora */
    .stat-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        text-align: center;
        animation: fadeIn 0.7s ease-out;
    }
    .stat-card.violet { border-top: 3px solid #7C3AED; }
    .stat-card.cyan   { border-top: 3px solid #22D3EE; }
    .stat-card.ambre  { border-top: 3px solid #F59E0B; }
    .stat-card .value { font-size: 2.1rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: #FAFAFF; }
    .stat-card .label { font-size: 0.78rem; color: #8890A3; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }

    /* Cartes de résultats */
    .result-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-left: 3px solid #7C3AED;
        border-radius: 14px;
        padding: 1rem 1.4rem;
        margin-bottom: 0.65rem;
        animation: fadeIn 0.4s ease-out;
    }
    .result-card.film { border-left-color: #22D3EE; }
    .result-card h4 { margin: 0 0 0.35rem 0; color: #FAFAFF; font-size: 1.05rem; font-weight: 600; }
    .genre-badge {
        display: inline-block;
        background: rgba(163, 230, 53, 0.12);
        color: #A3E635;
        border: 1px solid rgba(163, 230, 53, 0.35);
        font-size: 0.72rem; font-weight: 600;
        padding: 0.18rem 0.65rem; border-radius: 999px;
        margin-left: 0.5rem; vertical-align: middle;
    }
    .score-text { font-size: 0.8rem; color: #8890A3; margin-top: 0.35rem; }

    .avatar {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 50%;
        background: #7C3AED; color: white; font-weight: 700; font-size: 0.8rem;
        margin-right: 0.6rem; vertical-align: middle;
    }
    .rang-badge { font-size: 1.1rem; margin-right: 0.4rem; vertical-align: middle; }

    .empty-state {
        text-align: center; padding: 2.6rem 1rem; color: #8890A3;
        background: rgba(255,255,255,0.03); border-radius: 18px;
        border: 1.5px dashed rgba(124, 58, 237, 0.35);
    }
    .empty-state .icon { font-size: 2.2rem; margin-bottom: 0.6rem; display: block; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(8, 10, 18, 0.9);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * { color: #E7E9F0 !important; }
    .sidebar-logo {
        display: flex; align-items: center; gap: 0.6rem;
        padding: 0.4rem 0 1.2rem 0; margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar-logo .emoji { font-size: 1.7rem; }
    .sidebar-logo .texte {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700; font-size: 1.1rem; color: #FAFAFF;
    }
    section[data-testid="stSidebar"] button {
        border-radius: 10px !important; text-align: left !important;
        justify-content: flex-start !important; font-weight: 500 !important;
        margin-bottom: 0.3rem !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(124, 58, 237, 0.18) !important;
        border-color: rgba(124, 58, 237, 0.5) !important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        background: #7C3AED !important; border: none !important;
    }

    button[kind="primary"] {
        background: #7C3AED !important; border: none !important;
        font-weight: 600 !important;
        transition: transform 0.15s ease, background 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background: #6D28D9 !important;
        transform: translateY(-1px);
    }

    .stProgress > div > div { background: linear-gradient(90deg, #7C3AED, #22D3EE) !important; }
    .stProgress > div { background: rgba(255,255,255,0.08) !important; }

    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        color: #E7E9F0 !important; border-radius: 10px !important;
    }
    .stSelectbox div[data-baseweb="select"] * { color: #E7E9F0 !important; }
    ul[role="listbox"] { background: #0d0f1a !important; }
    ul[role="listbox"] li { background: #0d0f1a !important; color: #E7E9F0 !important; }
    ul[role="listbox"] li:hover { background: rgba(124, 58, 237, 0.25) !important; }

    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #05070d; }
    ::-webkit-scrollbar-thumb { background: #7C3AED; border-radius: 10px; }

    #MainMenu, footer {visibility: hidden;}
    </style>

    <div class="aurora-bande"></div>
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
    ("statistiques", "📊  Statistiques"),
    ("liste", "👥  Liste des utilisateurs"),
    ("ajouter", "➕  Ajouter un utilisateur"),
]

st.sidebar.markdown(
    """
    <div class="sidebar-logo">
        <span class="emoji">🎬</span>
        <span class="texte">CinéReco</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("### 📌 Navigation")
for cle, libelle in PAGES:
    est_active = st.session_state.page == cle
    if st.sidebar.button(
        libelle, key=f"nav_{cle}", use_container_width=True,
        type="primary" if est_active else "secondary",
    ):
        st.session_state.page = cle
        st.rerun()

page = st.session_state.page

# ============================================================
#  STATISTIQUES RAPIDES (bandeau)
# ============================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div class="stat-card violet"><div class="value">{len(donnees)}</div>'
        f'<div class="label">Utilisateurs</div></div>', unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="stat-card cyan"><div class="value">{len(genres)}</div>'
        f'<div class="label">Films</div></div>', unsafe_allow_html=True,
    )
with col3:
    total_connexions = sum(len(f) for f in donnees.values())
    st.markdown(
        f'<div class="stat-card ambre"><div class="value">{total_connexions}</div>'
        f'<div class="label">Connexions</div></div>', unsafe_allow_html=True,
    )

st.write("")

# ============================================================
#  PAGE : GRAPHE
# ============================================================
if page == "graphe":
    st.subheader("Visualisation interactive du graphe utilisateur-item")
    utilisateur_focus = st.selectbox(
        "Mettre en évidence un utilisateur (optionnel) :",
        ["Aucun"] + list(donnees.keys()),
    )
    st.write(
        "🟣 Les noeuds **violets** représentent les utilisateurs · "
        "🔵 Les noeuds **cyan** représentent les films. "
        "Survolez un noeud avec la souris pour voir ses détails — "
        "vous pouvez aussi zoomer et déplacer le graphe."
    )
    st.markdown('<div class="glass-card" style="padding:1rem;">', unsafe_allow_html=True)
    graphe = creer_graphe()
    cible = None if utilisateur_focus == "Aucun" else utilisateur_focus
    fig = obtenir_figure_plotly(graphe, utilisateur_selectionne=cible)
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
#  PAGE : STATISTIQUES
# ============================================================
elif page == "statistiques":
    st.subheader("Statistiques du système")

    compte_genres = {}
    for g in genres.values():
        compte_genres[g] = compte_genres.get(g, 0) + 1

    compte_films = {}
    for films in donnees.values():
        for film in films:
            compte_films[film] = compte_films.get(film, 0) + 1
    films_tries = sorted(compte_films.items(), key=lambda x: x[1], reverse=True)

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.markdown('<div class="glass-card" style="padding:1.2rem;">', unsafe_allow_html=True)
        st.markdown("**Répartition des genres**")
        fig_genres = go.Figure(
            data=[go.Pie(
                labels=list(compte_genres.keys()),
                values=list(compte_genres.values()),
                hole=0.55,
                marker=dict(colors=["#7C3AED", "#22D3EE", "#F59E0B", "#A3E635", "#EC4899", "#818CF8"]),
                textfont=dict(color="white"),
            )]
        )
        fig_genres.update_layout(
            showlegend=True,
            legend=dict(font=dict(color="#E7E9F0")),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            height=340,
        )
        st.plotly_chart(fig_genres, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_droite:
        st.markdown('<div class="glass-card" style="padding:1.2rem;">', unsafe_allow_html=True)
        st.markdown("**Films les plus populaires**")
        fig_films = go.Figure(
            data=[go.Bar(
                x=[c for _, c in films_tries],
                y=[f for f, _ in films_tries],
                orientation="h",
                marker=dict(color="#22D3EE"),
            )]
        )
        fig_films.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E7E9F0"),
            xaxis=dict(showgrid=False),
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=340,
        )
        st.plotly_chart(fig_films, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#  PAGE : LISTE DES UTILISATEURS
# ============================================================
elif page == "liste":
    st.subheader("Tous les utilisateurs et leurs films")
    recherche = st.text_input("🔎 Rechercher un utilisateur", placeholder="Ex : Kanto")

    utilisateurs_filtres = {
        nom: films for nom, films in donnees.items()
        if recherche.strip().lower() in nom.lower()
    }

    if not utilisateurs_filtres:
        st.markdown(
            """
            <div class="empty-state">
                <span class="icon">🔎</span>
                Aucun utilisateur ne correspond à cette recherche.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        cols = st.columns(2)
        for i, (nom, films) in enumerate(utilisateurs_filtres.items()):
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
                st.cache_data.clear()
                st.toast(f"Utilisateur '{nom}' ajouté avec succès !", icon="✅")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center; margin-top:2.5rem; padding:1rem; color:#5B6172; font-size:0.8rem;">
        🎬 CinéReco — Projet L2 · Python / NetworkX / Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
