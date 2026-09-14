# graphe.py
# Ce fichier construit le graphe bipartite utilisateur-item et fournit
# deux façons de l'afficher : Matplotlib (statique, pour l'export PNG)
# et Plotly (interactif, pour l'application Web).

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import plotly.graph_objects as go
from donnees import obtenir_donnees


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
    Construit et retourne une figure Matplotlib statique du graphe
    (utilisée par le programme terminal main.py et pour l'export PNG).
    """
    couleurs, tailles = [], []

    for noeud, attributs in G.nodes(data=True):
        if attributs["type"] == "utilisateur":
            couleurs.append("lightblue")
        else:
            couleurs.append("orange")
        tailles.append(300 + G.degree(noeud) * 250)

    position = nx.spring_layout(G, seed=42, k=0.6)

    fig, ax = plt.subplots(figsize=(9, 7))
    nx.draw(
        G, pos=position, with_labels=True, node_color=couleurs,
        node_size=tailles, font_size=8, font_weight="bold",
        edge_color="gray", ax=ax,
    )
    legende = [
        Patch(facecolor="lightblue", label="Utilisateur"),
        Patch(facecolor="orange", label="Film"),
    ]
    ax.legend(handles=legende, loc="upper right")
    ax.set_title("Graphe utilisateur-item\n(taille du noeud = nombre de connexions)")
    return fig


def afficher_graphe(G, sauvegarder=False, chemin_fichier="graphe.png"):
    """Affiche le graphe dans une fenêtre (utilisé par le programme terminal)."""
    fig = obtenir_figure_graphe(G)
    if sauvegarder:
        fig.savefig(chemin_fichier, dpi=150, bbox_inches="tight")
        print(f"✔ Graphe sauvegardé sous '{chemin_fichier}'")
    plt.show()


def obtenir_figure_plotly(G, utilisateur_selectionne=None):
    """
    Construit une figure Plotly interactive du graphe : zoom, déplacement,
    et infobulle (hover) au survol de chaque noeud.

    Si utilisateur_selectionne est fourni, ses arêtes et son noeud sont
    mis en évidence (surlignés) pour montrer ses connexions.
    """
    position = nx.spring_layout(G, seed=42, k=0.6)

    # --- Traces des arêtes ---
    arete_x, arete_y = [], []
    arete_x_surlignee, arete_y_surlignee = [], []

    for noeud_a, noeud_b in G.edges():
        x0, y0 = position[noeud_a]
        x1, y1 = position[noeud_b]

        est_connectee = utilisateur_selectionne in (noeud_a, noeud_b)
        if est_connectee:
            arete_x_surlignee += [x0, x1, None]
            arete_y_surlignee += [y0, y1, None]
        else:
            arete_x += [x0, x1, None]
            arete_y += [y0, y1, None]

    trace_aretes = go.Scatter(
        x=arete_x, y=arete_y, mode="lines",
        line=dict(width=1, color="rgba(150,150,150,0.4)"),
        hoverinfo="none", showlegend=False,
    )
    trace_aretes_surlignees = go.Scatter(
        x=arete_x_surlignee, y=arete_y_surlignee, mode="lines",
        line=dict(width=2.5, color="rgba(236,72,153,0.9)"),
        hoverinfo="none", showlegend=False,
    )

    # --- Traces des noeuds (séparées par type pour la légende) ---
    traces_noeuds = []
    for type_noeud, couleur, nom_legende in [
        ("utilisateur", "#A855F7", "Utilisateur"),
        ("film", "#EC4899", "Film"),
    ]:
        xs, ys, textes, tailles, contours = [], [], [], [], []
        for noeud, attributs in G.nodes(data=True):
            if attributs["type"] != type_noeud:
                continue
            x, y = position[noeud]
            xs.append(x)
            ys.append(y)
            degre = G.degree(noeud)
            textes.append(f"{noeud}<br>{degre} connexion(s)")
            tailles.append(18 + degre * 6)
            contours.append(
                "#22D3EE" if noeud == utilisateur_selectionne else "rgba(255,255,255,0.6)"
            )

        traces_noeuds.append(
            go.Scatter(
                x=xs, y=ys, mode="markers+text",
                text=[n for n, a in G.nodes(data=True) if a["type"] == type_noeud],
                textposition="top center",
                textfont=dict(size=10, color="#EDEBF5"),
                hovertext=textes, hoverinfo="text",
                marker=dict(
                    size=tailles, color=couleur,
                    line=dict(width=2, color=contours),
                ),
                name=nom_legende,
            )
        )

    fig = go.Figure(
        data=[trace_aretes, trace_aretes_surlignees] + traces_noeuds,
        layout=go.Layout(
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                font=dict(color="#EDEBF5"),
            ),
            hovermode="closest",
            margin=dict(b=10, l=10, r=10, t=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=520,
        ),
    )
    return fig


if __name__ == "__main__":
    graphe = creer_graphe()
    print("Noeuds :", graphe.nodes(data=True))
    print("Arêtes :", graphe.edges())
    afficher_graphe(graphe)
