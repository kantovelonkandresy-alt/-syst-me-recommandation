# main.py
# Point d'entrée du programme : menu interactif pour l'utilisateur

from donnees import obtenir_donnees, obtenir_genres, ajouter_utilisateur
from graphe import creer_graphe, afficher_graphe
from recommandation import SystemeRecommandation


def afficher_menu():
    print("\n=== Système de recommandation utilisateur-item ===")
    print("1. Afficher le graphe utilisateur-item")
    print("2. Voir les utilisateurs similaires à un utilisateur")
    print("3. Obtenir des recommandations de films pour un utilisateur")
    print("4. Lister tous les utilisateurs")
    print("5. Exporter le graphe en image (PNG)")
    print("6. Ajouter un nouvel utilisateur")
    print("7. Quitter")


def lister_utilisateurs(donnees):
    print("\nUtilisateurs disponibles :")
    for utilisateur in donnees:
        print(f" - {utilisateur}")


def demander_utilisateur(donnees):
    """Demande un nom d'utilisateur et vérifie qu'il existe dans les données."""
    nom = input("Entrez le nom de l'utilisateur : ").strip()
    if nom not in donnees:
        print(f"⚠ Utilisateur '{nom}' introuvable.")
        return None
    return nom


def main():
    donnees = obtenir_donnees()
    genres = obtenir_genres()
    systeme = SystemeRecommandation(donnees, genres)

    while True:
        afficher_menu()
        choix = input("Votre choix (1-7) : ").strip()

        if choix == "1":
            graphe = creer_graphe()
            afficher_graphe(graphe)

        elif choix == "2":
            lister_utilisateurs(donnees)
            utilisateur = demander_utilisateur(donnees)
            if utilisateur:
                try:
                    similaires = systeme.trouver_utilisateurs_similaires(utilisateur)
                    if similaires:
                        print(f"\nUtilisateurs similaires à {utilisateur} :")
                        for nom, score in similaires:
                            print(f" - {nom} (similarité : {score})")
                    else:
                        print(f"\nAucun utilisateur similaire trouvé pour {utilisateur}.")
                except KeyError as erreur:
                    print(f"⚠ {erreur}")

        elif choix == "3":
            lister_utilisateurs(donnees)
            utilisateur = demander_utilisateur(donnees)
            if utilisateur:
                try:
                    recommandations = systeme.generer_recommandations(utilisateur)
                    if recommandations:
                        print(f"\nRecommandations pour {utilisateur} :")
                        for film, score in recommandations:
                            print(f" - {film} (score : {score})")
                    else:
                        print(f"\nAucune recommandation disponible pour {utilisateur}.")
                except KeyError as erreur:
                    print(f"⚠ {erreur}")

        elif choix == "4":
            lister_utilisateurs(donnees)

        elif choix == "5":
            graphe = creer_graphe()
            afficher_graphe(graphe, sauvegarder=True, chemin_fichier="graphe.png")

        elif choix == "6":
            nom = input("Nom du nouvel utilisateur : ").strip()
            if nom in donnees:
                print(f"⚠ '{nom}' existe déjà. Choisissez un autre nom.")
            elif not nom:
                print("⚠ Le nom ne peut pas être vide.")
            else:
                films_texte = input(
                    "Films aimés (séparés par une virgule) : "
                ).strip()
                liste_films = [f.strip() for f in films_texte.split(",") if f.strip()]

                if not liste_films:
                    print("⚠ Vous devez indiquer au moins un film.")
                else:
                    ajouter_utilisateur(nom, liste_films)
                    print(f"✔ Utilisateur '{nom}' ajouté avec succès.")
                    # Recharger les données et le système pour inclure le nouvel utilisateur
                    donnees = obtenir_donnees()
                    systeme = SystemeRecommandation(donnees, genres)

        elif choix == "7":
            print("Au revoir !")
            break

        else:
            print("⚠ Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    main()