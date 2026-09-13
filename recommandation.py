# recommandation.py
# Ce fichier contient la classe SystemeRecommandation, qui encapsule
# toute la logique de similarité et de génération de recommandations,
# combinant la similarité de Jaccard et une bonification par genre.

from typing import Dict, List, Tuple, Optional


class SystemeRecommandation:
    """
    Système de recommandation hybride basé sur :
    - la similarité de Jaccard entre utilisateurs (films en commun)
    - une bonification par genre (un film du même genre qu'un film déjà
      aimé reçoit un léger bonus de score)
    """

    # Poids du bonus de genre par rapport au score de similarité Jaccard.
    # 0.15 signifie que le bonus de genre pèse 15% du score de base.
    POIDS_BONUS_GENRE = 0.15

    def __init__(
        self,
        donnees: Dict[str, List[str]],
        genres: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialise le système avec les données utilisateur -> films,
        et un dictionnaire optionnel film -> genre pour la bonification.

        Lève une erreur si les données sont vides ou mal formées.
        """
        if not donnees:
            raise ValueError("Les données ne peuvent pas être vides.")

        self.donnees = donnees
        self.genres = genres or {}

    def similarite_jaccard(self, ensemble_a: set, ensemble_b: set) -> float:
        """
        Calcule la similarité de Jaccard entre deux ensembles :
        J(A,B) = |A ∩ B| / |A ∪ B|

        Retourne un score entre 0.0 (aucun point commun) et 1.0
        (ensembles identiques).
        """
        union = ensemble_a | ensemble_b

        if len(union) == 0:
            return 0.0

        intersection = ensemble_a & ensemble_b
        return len(intersection) / len(union)

    def trouver_utilisateurs_similaires(
        self, utilisateur_cible: str
    ) -> List[Tuple[str, float]]:
        """
        Retourne la liste des autres utilisateurs avec leur score de
        similarité de Jaccard par rapport à utilisateur_cible, triée du
        plus similaire au moins similaire.

        Lève une erreur si utilisateur_cible n'existe pas dans les données.
        """
        if utilisateur_cible not in self.donnees:
            raise KeyError(f"Utilisateur '{utilisateur_cible}' introuvable.")

        films_cible = set(self.donnees[utilisateur_cible])
        similarites = []

        for utilisateur, films in self.donnees.items():
            if utilisateur == utilisateur_cible:
                continue

            films_autre = set(films)
            score = self.similarite_jaccard(films_cible, films_autre)

            if score > 0:
                similarites.append((utilisateur, round(score, 3)))

        similarites.sort(key=lambda x: x[1], reverse=True)
        return similarites

    def _bonus_genre(self, film: str, genres_cible: set) -> float:
        """
        Calcule un bonus si le genre de `film` fait partie des genres déjà
        aimés par l'utilisateur (genres_cible). Retourne 0.0 si le film
        n'a pas de genre connu, ou si son genre n'est pas dans genres_cible.
        """
        genre_du_film = self.genres.get(film)

        if genre_du_film is None:
            return 0.0

        if genre_du_film in genres_cible:
            return self.POIDS_BONUS_GENRE

        return 0.0

    def generer_recommandations(
        self, utilisateur_cible: str
    ) -> List[Tuple[str, float]]:
        """
        Génère une liste de films à recommander à utilisateur_cible :
        des films aimés par des utilisateurs similaires (score de base =
        similarité de Jaccard cumulée), mais que utilisateur_cible n'a
        pas encore vus. Un bonus est ajouté si le film partage un genre
        avec un film déjà aimé par utilisateur_cible.

        Retourne une liste de tuples (film, score), triée par score
        décroissant.
        """
        if utilisateur_cible not in self.donnees:
            raise KeyError(f"Utilisateur '{utilisateur_cible}' introuvable.")

        films_cible = set(self.donnees[utilisateur_cible])
        similaires = self.trouver_utilisateurs_similaires(utilisateur_cible)

        # Genres déjà aimés par l'utilisateur cible (pour le bonus)
        genres_cible = {
            self.genres[film] for film in films_cible if film in self.genres
        }

        scores_films: Dict[str, float] = {}

        for utilisateur, score_similarite in similaires:
            for film in self.donnees[utilisateur]:
                if film in films_cible:
                    continue

                score = score_similarite + self._bonus_genre(film, genres_cible)
                scores_films[film] = scores_films.get(film, 0) + score

        recommandations = sorted(
            scores_films.items(), key=lambda x: x[1], reverse=True
        )
        return [(film, round(score, 3)) for film, score in recommandations]


if __name__ == "__main__":
    from donnees import obtenir_donnees, obtenir_genres

    systeme = SystemeRecommandation(obtenir_donnees(), obtenir_genres())
    utilisateur_test = "Kanto"

    print(
        f"Utilisateurs similaires à {utilisateur_test} :",
        systeme.trouver_utilisateurs_similaires(utilisateur_test),
    )
    print(
        f"Recommandations pour {utilisateur_test} :",
        systeme.generer_recommandations(utilisateur_test),
    )