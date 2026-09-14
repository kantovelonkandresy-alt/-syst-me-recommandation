# app.py
# CinéReco - Application Web (Streamlit) du système de recommandation
# utilisateur-item. Thème "Aurora" : fond sombre avec bandes de lumière
# animées (violet, cyan, ambre, lime) + glassmorphism moderne.
# Lancer avec : streamlit run app.py

import hashlib
import requests
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
#  POSTERS (réels via OMDb, avec repli sur poster généré)
# ============================================================
GRADIENTS_POSTER = [
    ("#7C3AED", "#22D3EE"),
    ("#F59E0B", "#A3E635"),
    ("#EC4899", "#7C3AED"),
    ("#22D3EE", "#A3E635"),
    ("#7C3AED", "#F59E0B"),
    ("#A3E635", "#22D3EE"),
]
ICONES_POSTER = ["🎬", "🎞️", "🍿", "🎭", "📽️", "⭐"]


def couleurs_poster(nom_film: str):
    h = int(hashlib.md5(nom_film.encode()).hexdigest(), 16)
    debut, fin = GRADIENTS_POSTER[h % len(GRADIENTS_POSTER)]
    icone = ICONES_POSTER[h % len(ICONES_POSTER)]
    return debut, fin, icone


@st.cache_data(show_spinner=False)
def obtenir_url_poster(nom_film: str):
    """Maka poster OMDb raha misy API key; raha tsy misy dia fallback gradient."""
    try:
        cle_api = st.secrets.get("OMDB_API_KEY", "")
    except Exception:
        # Tsy misy secrets.toml: ampiasaina ho azy ny poster gradient.
        cle_api = ""

    if not cle_api:
        return None

    try:
        reponse = requests.get(
            "https://www.omdbapi.com/",
            params={"t": nom_film, "apikey": cle_api},
            timeout=5,
        )
        reponse.raise_for_status()
        donnees_api = reponse.json()
        url = donnees_api.get("Poster")
        if url and url != "N/A":
            return url
    except Exception:
        # Raha tsy mandeha OMDb na tsy hita ilay film,
        # dia hiverina amin'ny poster gradient ao amin'ny poster_html().
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
#  STYLE PERSONNALISÉ (CSS) — thème Aurora
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #070912;
        --panel: rgba(18, 23, 38, 0.78);
        --panel-strong: rgba(23, 29, 48, 0.94);
        --text: #f5f7ff;
        --muted: #9aa5bd;
        --purple: #8b5cf6;
        --purple-light: #c084fc;
        --blue: #38bdf8;
        --pink: #f472b6;
        --gold: #fbbf24;
        --green: #a3e635;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 82% 5%, rgba(56,189,248,.14), transparent 28%),
            radial-gradient(circle at 10% 45%, rgba(139,92,246,.16), transparent 32%),
            radial-gradient(circle at 72% 82%, rgba(244,114,182,.10), transparent 27%),
            var(--bg);
        color: var(--text);
        overflow-x: hidden;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }

    [data-testid="stAppViewContainer"], section[data-testid="stSidebar"] {
        position: relative;
        z-index: 1;
    }

    [data-testid="stAppViewContainer"] *, [data-testid="stMarkdownContainer"] p {
        color: var(--text);
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.025em;
    }

    h2, h3 {
        color: #ffffff !important;
        text-shadow: 0 2px 22px rgba(139,92,246,.22);
    }

    /* Ambient moving light */
    .aurora-bande {
        position: fixed;
        inset: -25%;
        z-index: -1;
        pointer-events: none;
        opacity: .55;
        filter: blur(90px);
        background:
            radial-gradient(ellipse at 18% 35%, rgba(139,92,246,.46), transparent 23%),
            radial-gradient(ellipse at 78% 22%, rgba(56,189,248,.36), transparent 20%),
            radial-gradient(ellipse at 62% 78%, rgba(244,114,182,.24), transparent 22%);
        animation: ambientMove 24s ease-in-out infinite alternate;
    }

    @keyframes ambientMove {
        0% { transform: translate3d(-3%, -2%, 0) scale(1); }
        50% { transform: translate3d(3%, 2%, 0) scale(1.08); }
        100% { transform: translate3d(-1%, 4%, 0) scale(1.02); }
    }

    /* Premium hero */
    .hero {
        position: relative;
        overflow: hidden;
        margin: .3rem 0 2rem;
        padding: 2.8rem 2.6rem;
        border: 1px solid rgba(255,255,255,.14);
        border-top: 4px solid var(--purple-light);
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(139,92,246,.22), rgba(56,189,248,.08) 52%, rgba(255,255,255,.035)),
            var(--panel);
        box-shadow: 0 24px 70px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.11);
        animation: reveal .7s ease both;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: -70px;
        top: -100px;
        border-radius: 50%;
        background: rgba(56,189,248,.24);
        filter: blur(8px);
        animation: orbFloat 6s ease-in-out infinite;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background: linear-gradient(110deg, transparent 25%, rgba(255,255,255,.09) 50%, transparent 75%);
        transform: translateX(-120%);
        animation: shine 8s ease-in-out infinite;
    }

    .hero h1 {
        position: relative;
        z-index: 2;
        margin: 0;
        color: #fff;
        font-size: clamp(2rem, 4vw, 3.1rem);
        font-weight: 700;
        text-shadow: 0 0 34px rgba(192,132,252,.35);
    }

    .hero p {
        position: relative;
        z-index: 2;
        color: #b7c0d5;
        font-size: 1.05rem;
        max-width: 780px;
    }

    @keyframes orbFloat { 50% { transform: translate(-22px, 18px) scale(1.14); } }
    @keyframes shine { 0%,65% { transform: translateX(-120%); } 85%,100% { transform: translateX(120%); } }
    @keyframes reveal { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:none; } }

    /* Glass surfaces */
    .glass-card, .stat-card, .result-card {
        background: linear-gradient(145deg, rgba(255,255,255,.095), rgba(255,255,255,.035));
        border: 1px solid rgba(255,255,255,.13);
        box-shadow: 0 18px 45px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.07);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }

    .glass-card { border-radius: 22px; }

    .stat-card {
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        padding: 1.45rem 1.4rem;
        text-align: center;
        animation: reveal .7s ease both;
    }

    .stat-card::after {
        content: "";
        position: absolute;
        left: 0; right: 0; bottom: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--purple-light), transparent);
    }
    .stat-card.violet { border-top: 3px solid var(--purple); }
    .stat-card.cyan { border-top: 3px solid var(--blue); }
    .stat-card.ambre { border-top: 3px solid var(--gold); }
    .stat-card:hover { transform: translateY(-8px); box-shadow: 0 24px 50px rgba(0,0,0,.32), 0 0 28px rgba(139,92,246,.18); }
    .stat-card .value { font-size: 2.35rem; font-weight: 700; color: #fff; }
    .stat-card .label { color: #aab4ca; font-size: .74rem; text-transform: uppercase; letter-spacing: .14em; font-weight: 700; }

    /* Results */
    .result-card {
        border-left: 4px solid var(--purple);
        border-radius: 16px;
        padding: 1rem 1.4rem;
        margin-bottom: .7rem;
        animation: reveal .45s ease both;
    }
    .result-card.film { border-left-color: var(--blue); }
    .result-card:hover { transform: translateX(7px); border-color: rgba(192,132,252,.5); box-shadow: 0 16px 35px rgba(0,0,0,.28), 0 0 22px rgba(139,92,246,.18); }
    .result-card h4 { color: #fff; }
    .score-text { color: var(--muted); }
    .genre-badge { background: rgba(163,230,53,.13); color: var(--green); border-color: rgba(163,230,53,.4); }
    .avatar { background: linear-gradient(135deg, var(--purple), var(--pink)); box-shadow: 0 0 15px rgba(192,132,252,.28); }

    /* Posters */
    .poster-row { gap: 1.15rem; padding: .7rem .3rem 1.2rem; }
    .poster-card {
        flex-basis: 158px;
        height: 225px;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 18px;
        box-shadow: 0 12px 26px rgba(0,0,0,.34);
        transition: transform .32s ease, box-shadow .32s ease, border-color .32s ease;
    }
    .poster-card:hover { transform: translateY(-11px) scale(1.045); border-color: rgba(56,189,248,.7); box-shadow: 0 24px 45px rgba(0,0,0,.46), 0 0 26px rgba(56,189,248,.2); }
    .poster-card::before { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(120deg, transparent 25%, rgba(255,255,255,.18), transparent 70%); transform:translateX(-130%); transition:transform .7s ease; z-index:4; }
    .poster-card:hover::before { transform:translateX(130%); }
    .poster-img { transition: transform .55s ease, filter .55s ease; }
    .poster-card:hover .poster-img { transform:scale(1.1); filter:brightness(1.12) saturate(1.18); }
    .poster-badge { background: rgba(7,9,18,.82); color: var(--green); box-shadow: 0 0 12px rgba(163,230,53,.18); }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(10,13,25,.98), rgba(16,12,32,.96)); border-right: 1px solid rgba(192,132,252,.15); }
    section[data-testid="stSidebar"] button { border-radius: 13px !important; transition: transform .22s ease, background .22s ease, box-shadow .22s ease !important; }
    section[data-testid="stSidebar"] button:hover { transform: translateX(6px); background: rgba(139,92,246,.18) !important; box-shadow: 0 8px 20px rgba(0,0,0,.2); }
    section[data-testid="stSidebar"] button[kind="primary"] { background: linear-gradient(100deg, #7c3aed, #a855f7) !important; box-shadow: 0 8px 24px rgba(124,58,237,.35); }
    .sidebar-logo { padding-bottom: 1.4rem; border-bottom: 1px solid rgba(255,255,255,.12); }

    /* Buttons */
    button[kind="primary"] { background: linear-gradient(100deg, #7c3aed, #a855f7) !important; border: 0 !important; box-shadow: 0 8px 22px rgba(124,58,237,.32); }
    button[kind="primary"]:hover { transform: translateY(-3px); filter: brightness(1.12); box-shadow: 0 14px 30px rgba(124,58,237,.48); }
    button[kind="secondary"]:hover { border-color: rgba(192,132,252,.55) !important; }

    /* Fields */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div { border-radius: 12px !important; background: rgba(255,255,255,.065) !important; }
    input:focus, textarea:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: var(--purple-light) !important; box-shadow: 0 0 0 3px rgba(139,92,246,.18), 0 0 22px rgba(139,92,246,.14); }

    /* Plotly container */
    div[data-testid="stPlotlyChart"] { position:relative; overflow:hidden; border:1px solid rgba(255,255,255,.12); border-radius:18px; background:rgba(255,255,255,.035); box-shadow:0 18px 45px rgba(0,0,0,.23); animation:reveal .7s ease both; }
    div[data-testid="stPlotlyChart"]:hover { transform:translateY(-4px); border-color:rgba(56,189,248,.5); box-shadow:0 25px 55px rgba(0,0,0,.32), 0 0 28px rgba(56,189,248,.16); }
    div[data-testid="stPlotlyChart"]::after { content:""; position:absolute; left:7%; right:7%; bottom:0; height:2px; pointer-events:none; background:linear-gradient(90deg,transparent,var(--purple),var(--blue),var(--pink),transparent); background-size:200% 100%; animation:chartFlow 5s linear infinite; }
    @keyframes chartFlow { to { background-position:200% 50%; } }
    div[data-testid="stPlotlyChart"] .modebar { opacity:0; transition:opacity .22s ease; }
    div[data-testid="stPlotlyChart"]:hover .modebar { opacity:.9; }

    /* Empty state and scrollbar */
    .empty-state { border-color: rgba(192,132,252,.42); background: rgba(255,255,255,.035); }
    .empty-state:hover { transform:translateY(-4px); background:rgba(139,92,246,.09); border-color:rgba(192,132,252,.75); }
    .empty-state .icon { display:inline-block; animation:floatIcon 2.8s ease-in-out infinite; }
    @keyframes floatIcon { 50% { transform:translateY(-7px) rotate(3deg); } }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--purple), var(--blue)) !important; }
    .stProgress > div > div { background: linear-gradient(90deg, var(--purple), var(--blue), var(--pink)) !important; background-size:200% 100% !important; animation:chartFlow 3s linear infinite; }

    @media (max-width: 768px) {
        .hero { padding: 2rem 1.3rem; }
        .hero h1 { font-size: 2rem; }
        .poster-card:hover { transform: translateY(-7px) scale(1.02); }
        .result-card:hover { transform: translateY(-2px); }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; scroll-behavior:auto !important; }
    }


    /* ============================================================
       SLOW PAGE FADE-IN — CSS only
       ============================================================ */

    /* Ny contenu lehibe rehetra dia miseho miadana rehefa misokatra/miova pejy */
    [data-testid="stAppViewContainer"] .main > div {
        animation: pageFadeIn 900ms cubic-bezier(.22, .8, .25, 1) both;
    }

    @keyframes pageFadeIn {
        from {
            opacity: 0;
            transform: translateY(18px);
            filter: blur(3px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0);
        }
    }

    /* Fivoahana miadana ho an'ny text */
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] .stMarkdown,
    [data-testid="stAppViewContainer"] .stCaption {
        animation: textFadeIn 850ms ease-out both;
    }

    @keyframes textFadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Stagger: tsy mivoaka miaraka daholo ireo éléments */
    [data-testid="stAppViewContainer"] h1 { animation-delay: 80ms; }
    [data-testid="stAppViewContainer"] h2 { animation-delay: 130ms; }
    [data-testid="stAppViewContainer"] h3 { animation-delay: 170ms; }
    [data-testid="stAppViewContainer"] p { animation-delay: 230ms; }
    [data-testid="stAppViewContainer"] label { animation-delay: 300ms; }

    /* Inputs sy boutons mivoaka aorian'ny text */
    [data-testid="stAppViewContainer"] .stSelectbox,
    [data-testid="stAppViewContainer"] .stTextInput,
    [data-testid="stAppViewContainer"] .stButton,
    [data-testid="stAppViewContainer"] .stPlotlyChart {
        animation: contentFadeUp 800ms cubic-bezier(.22, .8, .25, 1) both;
        animation-delay: 350ms;
    }

    @keyframes contentFadeUp {
        from {
            opacity: 0;
            transform: translateY(20px) scale(.985);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Poster sy result cards: miseho tsikelikely avy ankavia */
    [data-testid="stAppViewContainer"] .poster-card,
    [data-testid="stAppViewContainer"] .result-card {
        animation: cardFadeUp 700ms cubic-bezier(.22, .8, .25, 1) both;
    }

    [data-testid="stAppViewContainer"] .poster-card:nth-child(1),
    [data-testid="stAppViewContainer"] .result-card:nth-child(1) { animation-delay: 100ms; }
    [data-testid="stAppViewContainer"] .poster-card:nth-child(2),
    [data-testid="stAppViewContainer"] .result-card:nth-child(2) { animation-delay: 180ms; }
    [data-testid="stAppViewContainer"] .poster-card:nth-child(3),
    [data-testid="stAppViewContainer"] .result-card:nth-child(3) { animation-delay: 260ms; }
    [data-testid="stAppViewContainer"] .poster-card:nth-child(4),
    [data-testid="stAppViewContainer"] .result-card:nth-child(4) { animation-delay: 340ms; }
    [data-testid="stAppViewContainer"] .poster-card:nth-child(5),
    [data-testid="stAppViewContainer"] .result-card:nth-child(5) { animation-delay: 420ms; }

    @keyframes cardFadeUp {
        from {
            opacity: 0;
            transform: translateY(24px) scale(.96);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Sidebar logo sy navigation */
    section[data-testid="stSidebar"] .sidebar-logo,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] button {
        animation: sidebarFadeIn 650ms ease-out both;
    }

    section[data-testid="stSidebar"] button:nth-of-type(1) { animation-delay: 100ms; }
    section[data-testid="stSidebar"] button:nth-of-type(2) { animation-delay: 160ms; }
    section[data-testid="stSidebar"] button:nth-of-type(3) { animation-delay: 220ms; }
    section[data-testid="stSidebar"] button:nth-of-type(4) { animation-delay: 280ms; }
    section[data-testid="stSidebar"] button:nth-of-type(5) { animation-delay: 340ms; }
    section[data-testid="stSidebar"] button:nth-of-type(6) { animation-delay: 400ms; }

    @keyframes sidebarFadeIn {
        from {
            opacity: 0;
            transform: translateX(-16px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Respecte le choix de l'utilisateur */
    @media (prefers-reduced-motion: reduce) {
        [data-testid="stAppViewContainer"] .main > div,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] .stMarkdown,
        [data-testid="stAppViewContainer"] .stCaption,
        [data-testid="stAppViewContainer"] .stSelectbox,
        [data-testid="stAppViewContainer"] .stTextInput,
        [data-testid="stAppViewContainer"] .stButton,
        [data-testid="stAppViewContainer"] .stPlotlyChart,
        [data-testid="stAppViewContainer"] .poster-card,
        [data-testid="stAppViewContainer"] .result-card,
        section[data-testid="stSidebar"] .sidebar-logo,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] button {
            animation: none !important;
        }
    }



    /* ============================================================
       PREMIUM HOVER EFFECTS — buttons and cards
       ============================================================ */

    /* Boutons rehetra */
    button[kind="primary"],
    button[kind="secondary"],
    section[data-testid="stSidebar"] button {
        position: relative;
        transition:
            transform 220ms cubic-bezier(.22, .8, .25, 1),
            box-shadow 220ms ease,
            border-color 220ms ease,
            background 220ms ease,
            filter 220ms ease !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-5px) scale(1.015) !important;
        filter: brightness(1.12) saturate(1.08);
        box-shadow:
            0 14px 30px rgba(124, 58, 237, .48),
            0 0 26px rgba(168, 85, 247, .30),
            inset 0 1px 0 rgba(255, 255, 255, .22) !important;
    }

    button[kind="primary"]:active {
        transform: translateY(-1px) scale(.99) !important;
        box-shadow: 0 5px 14px rgba(124, 58, 237, .30) !important;
    }

    button[kind="secondary"]:hover {
        transform: translateY(-4px) !important;
        background: rgba(139, 92, 246, .20) !important;
        border-color: rgba(192, 132, 252, .72) !important;
        box-shadow:
            0 10px 24px rgba(0, 0, 0, .25),
            0 0 18px rgba(139, 92, 246, .16) !important;
    }

    button[kind="secondary"]:active {
        transform: translateY(-1px) !important;
    }

    /* Stat cards */
    .stat-card {
        transition:
            transform 280ms cubic-bezier(.22, .8, .25, 1),
            box-shadow 280ms ease,
            border-color 280ms ease !important;
    }

    .stat-card:hover {
        transform: translateY(-9px) scale(1.018) !important;
        border-color: rgba(255, 255, 255, .26) !important;
        box-shadow:
            0 24px 52px rgba(0, 0, 0, .36),
            0 0 30px rgba(139, 92, 246, .22),
            inset 0 1px 0 rgba(255, 255, 255, .16) !important;
    }

    .stat-card .value {
        transition: transform 280ms ease, text-shadow 280ms ease;
    }

    .stat-card:hover .value {
        transform: scale(1.08);
        text-shadow:
            0 0 12px rgba(192, 132, 252, .65),
            0 0 28px rgba(56, 189, 248, .28);
    }

    /* Cards glass et result cards */
    .glass-card,
    .result-card,
    .empty-state {
        transition:
            transform 260ms cubic-bezier(.22, .8, .25, 1),
            box-shadow 260ms ease,
            border-color 260ms ease,
            background 260ms ease !important;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(56, 189, 248, .38);
        box-shadow:
            0 24px 54px rgba(0, 0, 0, .30),
            0 0 26px rgba(56, 189, 248, .13),
            inset 0 1px 0 rgba(255, 255, 255, .12);
    }

    .result-card:hover {
        transform: translateX(8px) translateY(-3px) !important;
        border-color: rgba(192, 132, 252, .60) !important;
        box-shadow:
            0 16px 34px rgba(0, 0, 0, .30),
            0 0 24px rgba(139, 92, 246, .20),
            inset 0 1px 0 rgba(255, 255, 255, .10) !important;
    }

    .result-card h4,
    .result-card .score-text,
    .genre-badge {
        transition: color 220ms ease, transform 220ms ease;
    }

    .result-card:hover h4 {
        color: #ffffff !important;
        transform: translateX(3px);
    }

    .result-card:hover .genre-badge {
        transform: scale(1.06);
    }

    /* Movie posters */
    .poster-card {
        transition:
            transform 300ms cubic-bezier(.22, .8, .25, 1),
            box-shadow 300ms ease,
            border-color 300ms ease !important;
    }

    .poster-card:hover {
        transform: translateY(-12px) scale(1.055) !important;
        border-color: rgba(56, 189, 248, .78) !important;
        box-shadow:
            0 26px 48px rgba(0, 0, 0, .50),
            0 0 28px rgba(56, 189, 248, .25),
            inset 0 1px 0 rgba(255, 255, 255, .20) !important;
        z-index: 8;
    }

    .poster-card:hover .poster-title {
        text-shadow: 0 2px 12px rgba(0, 0, 0, .8);
    }

    /* Chart cards */
    div[data-testid="stPlotlyChart"] {
        transition:
            transform 280ms cubic-bezier(.22, .8, .25, 1),
            box-shadow 280ms ease,
            border-color 280ms ease !important;
    }

    div[data-testid="stPlotlyChart"]:hover {
        transform: translateY(-6px) scale(1.006) !important;
        border-color: rgba(56, 189, 248, .62) !important;
        box-shadow:
            0 28px 58px rgba(0, 0, 0, .38),
            0 0 32px rgba(56, 189, 248, .20),
            inset 0 1px 0 rgba(255, 255, 255, .12) !important;
    }

    /* Sidebar navigation */
    section[data-testid="stSidebar"] button:hover {
        transform: translateX(7px) translateY(-2px) !important;
    }

    section[data-testid="stSidebar"] button[kind="primary"]:hover {
        box-shadow:
            0 12px 28px rgba(124, 58, 237, .46),
            0 0 22px rgba(168, 85, 247, .24) !important;
    }

    /* Focus clavier: garde l'interface accessible */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 2px solid #c084fc !important;
        outline-offset: 3px;
    }

    @media (prefers-reduced-motion: reduce) {
        button[kind="primary"],
        button[kind="secondary"],
        section[data-testid="stSidebar"] button,
        .stat-card,
        .glass-card,
        .result-card,
        .empty-state,
        .poster-card,
        div[data-testid="stPlotlyChart"] {
            transition: none !important;
        }
    }

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

    RANGS = ["🥇", "🥈", "🥉"]

    if st.button("✨ Générer les recommandations", type="primary"):
        recommandations = systeme.generer_recommandations(utilisateur)
        if recommandations:
            st.write(f"**Films recommandés pour {utilisateur} :**")
            posters = "".join(
                poster_html(film, genres.get(film, ""), badge=f"{score}")
                for film, score in recommandations
            )
            st.markdown(f'<div class="poster-row">{posters}</div>', unsafe_allow_html=True)

            st.write("")
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
                    posters = "".join(
                        poster_html(f, genres.get(f, "")) for f in films
                    )
                    st.markdown(f'<div class="poster-row">{posters}</div>', unsafe_allow_html=True)

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

    apercu_films = [f.strip() for f in films_texte.split(",") if f.strip()]
    if apercu_films:
        st.write("**Aperçu :**")
        posters_apercu = "".join(
            poster_html(f, genres.get(f, "Nouveau")) for f in apercu_films
        )
        st.markdown(f'<div class="poster-row">{posters_apercu}</div>', unsafe_allow_html=True)

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
