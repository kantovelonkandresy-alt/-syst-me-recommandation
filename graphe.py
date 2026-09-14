# graphe.py
# Ce fichier construit et affiche le graphe bipartite utilisateur-item

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.patches import Patch
from donnees import obtenir_donnees

COULEUR_UTILISATEUR = "#7F5AF0"
COULEUR_FILM = "#00F5D4"
COULEUR_ARETE = "#3D3A52"


def creer_graphe():
    """
    Crée un graphe bipartite :
    - Un ensemble de noeuds "utilisateurs"
    - Un ensemble de noeuds "films"
    - Une arête (edge) entre un utilisateur et un film s'il l'aime
    """
    G = nx.Graph()

    donnees = obtenir_donnees()

    for utilisateur, films in donnees.items():
        G.add_node(utilisateur, type="utilisateur")

        for film in films:
            G.add_node(film, type="film")
            G.add_edge(utilisateur, film)

    return G


def obtenir_figure_graphe(G):
    """
    Construit et retourne une figure Matplotlib du graphe (sans l'afficher).
    Utilisée à la fois par le programme terminal (main.py) et par
    l'application Web (app.py).
    """
    couleurs = []
    tailles = []

    for noeud, attributs in G.nodes(data=True):
        if attributs["type"] == "utilisateur":
            couleurs.append(COULEUR_UTILISATEUR)
        else:
            couleurs.append(COULEUR_FILM)

        degre = G.degree(noeud)
        tailles.append(500 + degre * 320)

    position = nx.kamada_kawai_layout(G)

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    nx.draw_networkx_edges(
        G, pos=position, edge_color=COULEUR_ARETE, width=1.6, ax=ax
    )
    nx.draw_networkx_nodes(
        G,
        pos=position,
        node_color=couleurs,
        node_size=tailles,
        edgecolors="white",
        linewidths=2.2,
        ax=ax,
    )
    nx.draw_networkx_labels(
        G,
        pos=position,
        font_size=9,
        font_weight="bold",
        font_family="sans-serif",
        font_color="#2D2D2D",
        ax=ax,
    )

    legende = [
        Patch(facecolor=COULEUR_UTILISATEUR, label="Utilisateur"),
        Patch(facecolor=COULEUR_FILM, label="Film"),
    ]
    ax.legend(
        handles=legende,
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="#EEEEEE",
        fontsize=10,
    )

    ax.set_axis_off()
    fig.tight_layout()

    return fig


def obtenir_figure_plotly(G):
    """
    Construit une version interactive (Plotly) du graphe utilisateur-item :
    survoler un noeud affiche son nom et son nombre de connexions,
    et le graphe peut être zoomé / déplacé à la souris.
    """
    position = nx.kamada_kawai_layout(G)

    # --- Traits (arêtes) ---
    arete_x, arete_y = [], []
    for u, v in G.edges():
        x0, y0 = position[u]
        x1, y1 = position[v]
        arete_x += [x0, x1, None]
        arete_y += [y0, y1, None]

    trace_aretes = go.Scatter(
        x=arete_x,
        y=arete_y,
        line=dict(width=1.3, color=COULEUR_ARETE),
        hoverinfo="none",
        mode="lines",
        showlegend=False,
    )

    # --- Noeuds utilisateurs et films séparés (pour la légende) ---
    def construire_trace(type_noeud, couleur, nom_legende, prefixe_info):
        xs, ys, tailles, textes_survol, noms = [], [], [], [], []
        for noeud, attributs in G.nodes(data=True):
            if attributs["type"] != type_noeud:
                continue
            x, y = position[noeud]
            degre = G.degree(noeud)
            xs.append(x)
            ys.append(y)
            tailles.append(22 + degre * 9)
            textes_survol.append(f"{prefixe_info} <b>{noeud}</b><br>{degre} connexion(s)")
            noms.append(noeud)

        return go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=noms,
            textposition="top center",
            textfont=dict(size=11, family="Sora, sans-serif", color="#EDEBFA"),
            hovertext=textes_survol,
            hoverinfo="text",
            name=nom_legende,
            marker=dict(
                color=couleur,
                size=tailles,
                line=dict(width=2, color="white"),
            ),
        )

    trace_utilisateurs = construire_trace(
        "utilisateur", COULEUR_UTILISATEUR, "Utilisateur", "👤"
    )
    trace_films = construire_trace("film", COULEUR_FILM, "Film", "🎬")

    fig = go.Figure(data=[trace_aretes, trace_utilisateurs, trace_films])
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Sora, sans-serif", size=12, color="#EDEBFA"),
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="#15121F",
        paper_bgcolor="#15121F",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        hoverlabel=dict(
            bgcolor="#0B0B14",
            bordercolor="#7F5AF0",
            font_size=13,
            font_family="Sora, sans-serif",
            font_color="#EDEBFA",
        ),
    )

    return fig


def afficher_graphe(G, sauvegarder=False, chemin_fichier="graphe.png"):
    """
    Affiche le graphe dans une fenêtre (utilisé par le programme terminal).
    """
    fig = obtenir_figure_graphe(G)

    if sauvegarder:
        fig.savefig(chemin_fichier, dpi=150, bbox_inches="tight")
        print(f"✔ Graphe sauvegardé sous '{chemin_fichier}'")

    plt.show()


if __name__ == "__main__":
    graphe = creer_graphe()
    print("Noeuds :", graphe.nodes(data=True))
    print("Arêtes :", graphe.edges())
    afficher_graphe(graphe)
