# graphe.py
# Ce fichier construit et affiche le graphe bipartite utilisateur-item

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
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
    Construit et retourne une figure Matplotlib du graphe (sans l'afficher).
    Utilisée à la fois par le programme terminal (main.py) et par
    l'application Web (app.py).
    """
    couleurs = []
    tailles = []

    for noeud, attributs in G.nodes(data=True):
        if attributs["type"] == "utilisateur":
            couleurs.append("lightblue")
        else:
            couleurs.append("orange")

        degre = G.degree(noeud)
        tailles.append(300 + degre * 250)

    position = nx.spring_layout(G, seed=42, k=0.6)

    fig, ax = plt.subplots(figsize=(9, 7))
    nx.draw(
        G,
        pos=position,
        with_labels=True,
        node_color=couleurs,
        node_size=tailles,
        font_size=8,
        font_weight="bold",
        edge_color="gray",
        ax=ax,
    )

    legende = [
        Patch(facecolor="lightblue", label="Utilisateur"),
        Patch(facecolor="orange", label="Film"),
    ]
    ax.legend(handles=legende, loc="upper right")
    ax.set_title("Graphe utilisateur-item\n(taille du noeud = nombre de connexions)")

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
