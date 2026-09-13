# test_recommandation.py
# Tests automatiques pour la classe SystemeRecommandation.
# Lancer avec : python -m unittest test_recommandation.py

import unittest
from recommandation import SystemeRecommandation


class TestSystemeRecommandation(unittest.TestCase):
    """
    Ensemble de tests pour vérifier que SystemeRecommandation se comporte
    correctement, y compris sur des cas limites (erreurs, données vides).
    """

    def setUp(self):
        """
        Exécuté avant CHAQUE test : prépare des données simples et
        prévisibles, indépendantes du fichier CSV réel du projet.
        """
        self.donnees_test = {
            "Alice": ["FilmA", "FilmB"],
            "Bob": ["FilmA", "FilmB", "FilmC"],
            "Claire": ["FilmC"],
        }
        self.genres_test = {
            "FilmA": "Action",
            "FilmB": "Action",
            "FilmC": "Drame",
        }
        self.systeme = SystemeRecommandation(self.donnees_test, self.genres_test)

    def test_similarite_jaccard_identique(self):
        """Deux ensembles identiques doivent avoir une similarité de 1.0."""
        resultat = self.systeme.similarite_jaccard({"A", "B"}, {"A", "B"})
        self.assertEqual(resultat, 1.0)

    def test_similarite_jaccard_aucun_commun(self):
        """Deux ensembles sans intersection doivent avoir une similarité de 0.0."""
        resultat = self.systeme.similarite_jaccard({"A"}, {"B"})
        self.assertEqual(resultat, 0.0)

    def test_similarite_jaccard_partielle(self):
        """
        {A,B} et {A,B,C} : intersection = {A,B} (2), union = {A,B,C} (3)
        donc la similarité attendue est 2/3.
        """
        resultat = self.systeme.similarite_jaccard({"A", "B"}, {"A", "B", "C"})
        self.assertAlmostEqual(resultat, 2 / 3)

    def test_trouver_utilisateurs_similaires_ordre(self):
        """Bob (2 films communs avec Alice) doit être plus similaire qu'un
        utilisateur sans film en commun."""
        resultat = self.systeme.trouver_utilisateurs_similaires("Alice")
        noms_trouves = [nom for nom, score in resultat]
        self.assertIn("Bob", noms_trouves)
        self.assertNotIn("Claire", noms_trouves)  # Alice et Claire n'ont rien en commun

    def test_utilisateur_introuvable_leve_erreur(self):
        """Un utilisateur qui n'existe pas doit lever une KeyError."""
        with self.assertRaises(KeyError):
            self.systeme.trouver_utilisateurs_similaires("Inexistant")

    def test_generer_recommandations_exclut_films_deja_vus(self):
        """Un film déjà vu par l'utilisateur ne doit jamais être recommandé."""
        recommandations = self.systeme.generer_recommandations("Alice")
        films_recommandes = [film for film, score in recommandations]
        self.assertNotIn("FilmA", films_recommandes)
        self.assertNotIn("FilmB", films_recommandes)

    def test_generer_recommandations_contenu(self):
        """Alice n'a pas vu FilmC ; Bob (similaire) l'a vu, donc FilmC doit
        être recommandé à Alice."""
        recommandations = self.systeme.generer_recommandations("Alice")
        films_recommandes = [film for film, score in recommandations]
        self.assertIn("FilmC", films_recommandes)

    def test_donnees_vides_leve_erreur(self):
        """Créer un système avec un dictionnaire vide doit lever une ValueError."""
        with self.assertRaises(ValueError):
            SystemeRecommandation({})


if __name__ == "__main__":
    unittest.main()
