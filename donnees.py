# donnees.py
# Ce fichier charge les données depuis des fichiers CSV :
# - utilisateurs_films.csv : quel utilisateur aime quel film
# - genres_films.csv : le genre de chaque film

import csv
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_UTILISATEURS_FILMS = os.path.join(DOSSIER_COURANT, "utilisateurs_films.csv")
FICHIER_GENRES = os.path.join(DOSSIER_COURANT, "genres_films.csv")


def ajouter_utilisateur(nom_utilisateur, liste_films):
    """
    Ajoute un nouvel utilisateur et ses films aimés dans le fichier CSV
    utilisateurs_films.csv (une ligne par film aimé).
    """
    with open(FICHIER_UTILISATEURS_FILMS, "a", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        for film in liste_films:
            ecrivain.writerow([nom_utilisateur, film.strip()])


def obtenir_donnees():
    """
    Lit utilisateurs_films.csv et retourne un dictionnaire :
    { "Kanto": ["Avengers", "Titanic", ...], ... }

    Lève une erreur claire si le fichier est introuvable.
    """
    donnees = {}

    try:
        with open(FICHIER_UTILISATEURS_FILMS, newline="", encoding="utf-8") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                utilisateur = ligne["utilisateur"].strip()
                film = ligne["film"].strip()
                donnees.setdefault(utilisateur, []).append(film)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fichier introuvable : {FICHIER_UTILISATEURS_FILMS}. "
            "Vérifiez qu'il se trouve bien dans le même dossier que donnees.py."
        )

    return donnees


def obtenir_genres():
    """
    Lit genres_films.csv et retourne un dictionnaire :
    { "Avengers": "Action", "Titanic": "Drame", ... }

    Lève une erreur claire si le fichier est introuvable.
    """
    genres = {}

    try:
        with open(FICHIER_GENRES, newline="", encoding="utf-8") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                film = ligne["film"].strip()
                genre = ligne["genre"].strip()
                genres[film] = genre
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fichier introuvable : {FICHIER_GENRES}. "
            "Vérifiez qu'il se trouve bien dans le même dossier que donnees.py."
        )

    return genres