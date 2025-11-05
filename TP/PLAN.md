Les tests sont organisés en 4 catégories principales :

Tests Unitaires (logique métier et conversion binaire)

Tests d'API / Intégration (serveur Flask et gestion des pannes)

Tests de Performance (rapidité d'exécution)

Qualité & Documentation (propreté du code)

Outils utilisés : pytest, pytest-mock, coverage, ruff, pdoc3, make.

2. Catégorie 1 : Tests Unitaires

But : Vérifier les fonctions pures (logique Python), sans Flask ni réseau.

2.1. Tests de l'Algo de Triangulation

Composant vérifié : La fonction compute_triangulation dans triangulator/core.py.
Objectif : S'assurer que les calculs mathématiques sont justes.

Cas Normaux :

test_triangulation_3_points : 3 points -> 1 triangle.

test_triangulation_4_points_carre : 4 points en carré -> 2 triangles.

test_triangulation_5_points_convexe : 5 points en pentagone -> 3 triangles.

Cas Limites :

test_triangulation_0_points : 0 point -> 0 triangle.

test_triangulation_1_point : 1 point -> 0 triangle.

test_triangulation_2_points : 2 points -> 0 triangle.

Cas Bizarres:

test_triangulation_points_colineaires : N points alignés -> 0 triangle.

test_triangulation_points_doublons : Points identiques (ex: (0,0), (0,0), (1,1)) -> 0 triangle.

2.2. Tests de (Dé)Sérialisation Binaire

Composants vérifiés : Les fonctions binary_to_pointset et triangles_to_binary dans triangulator/binary_utils.py.
Objectif : S'assurer à 100% que le binaire est lu et écrit conformément aux spécifications.

PointSet (Lecture / Désérialisation) :

test_binary_to_pointset_simple : Fournir des bytes valides (2 points) -> Vérifier que la liste [(x1,y1), (x2,y2)] est obtenue.

test_binary_to_pointset_malforme_header_court : Fournir des bytes trop courts (ex: 2 au lieu de 4) -> Doit lever une exception.

test_binary_to_pointset_malforme_data_incomplet : Le header annonce "10 points" mais les données s'arrêtent après 5 -> Doit lever une exception.

test_binary_to_pointset_robustesse_floats : Vérifier la gestion des floats positifs, négatifs, et nuls.

Triangles (Écriture / Sérialisation) :

test_triangles_to_binary_simple : Fournir (3 points, 1 triangle) -> Vérifier que le bytes de sortie est parfaitement conforme (partie points + 4 bytes count=1 + 12 bytes d'indices).

test_triangles_to_binary_no_triangles : Fournir (3 points, 0 triangle) -> La partie triangles doit être juste 4 bytes count=0.

test_cycle_serialisation_deserialisation : (Test bonus) Vérifier que la re-lecture des données écrites redonne l'objet initial.

Triangles (Validation - Cas spécial) :

test_binary_to_triangles_index_out_of_bounds : (Test bonus) Si la lecture de Triangles est implémentée, tester un indice qui pointe vers un point qui n'existe pas (ex: 3 points, indice 10) -> Doit lever une exception.

3. Catégorie 2 : Tests d'API & Intégration

But : Vérifier le serveur Flask (app.py), son respect de triangulator.yaml et sa robustesse face aux pannes du PointSetManager.
Comment : Utilisation du client de test Flask (app.test_client()) pour appeler le service, et "mock" (simulation) des réponses du PointSetManager (le service distant).

3.1. Scénario "Happy Path" : Tout fonctionne

Test : test_api_triangulate_success

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-VALIDE sur le service.

B) Le service appelle le PointSetManager. Le PointSetManager est mocké pour répondre 200 OK avec un PointSet binaire valide (ex: 4 points).

C) Le service fait le calcul, sérialise les Triangles.

D) Le service répond au Client (le test) avec 200 OK et le Content-Type (application/octet-stream).

Vérification : La réponse est désérialisée et les triangles vérifiés.

3.2. Scénarios d'Erreurs et "Non-Happy Path"

Test : test_api_pointset_id_not_found (Cas 404)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-INCONNU.

B) Le service appelle le PointSetManager. Le PointSetManager est mocké pour renvoyer une erreur 404 Not Found.

C) Le service doit intercepter cette erreur 404.

D) Le service répond au Client (le test) avec un statut 404 Not Found et un JSON d'erreur (cf. triangulator.yaml).

Test : test_api_pointsetmanager_indisponible_503 (Cas Panne BDD distante)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-VALIDE.

B) Le service appelle le PointSetManager. Le PointSetManager est mocké pour renvoyer une erreur 503 Service Unavailable.

C) Le service intercepte cette erreur 503.

D) Le service répond au Client (le test) avec un statut 503 (cf. triangulator.yaml).

Test : test_api_pointsetmanager_panne_reseau (Cas Panne Réseau)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-VALIDE.

B) Le service essaie d'appeler le PointSetManager. urllib.request.urlopen est mocké pour lever une URLError (panne réseau, timeout...).

C) Le service intercepte cette URLError.

D) Le service répond au Client (le test) avec un statut 503.

Test : test_api_pointsetmanager_donnees_corrompues (Cas 500 - Données corrompues)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-VALIDE.

B) Le service appelle le PointSetManager. Le PointSetManager est mocké pour répondre 200 OK, mais avec des bytes corrompus (qui feront planter binary_to_pointset).

C) Le service essaie de désérialiser, ce qui lève une exception. app.py doit attraper cette exception.

D) Le service répond au Client (le test) avec un statut 500 Internal Server Error.

Test : test_api_triangulation_interne_echoue (Cas 500 - L'algo plante)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-VALIDE.

B) Le service appelle le PointSetManager (mock 200 OK avec données valides).

C) Le service appelle compute_triangulation. La fonction est "patchée" pour lever une exception.

D) app.py doit attraper cette exception interne.

E) Le service répond au Client (le test) avec un statut 500 Internal Server Error.

Test : test_api_invalid_uuid_format (Cas 400 - ID mal formé)

Scénario :

A) Le Client (le test) appelle GET /triangulation/ID-PAS-UN-UUID.

B) Le service (Flask) doit rejeter la requête immédiatement, sans même appeler le PointSetManager.

C) Le service répond au Client (le test) avec un statut 400 Bad Request.

4. Catégorie 3 : Tests de Performance

But : Vérifier que le code n'est pas trop lent avec beaucoup de données.
Comment : Tests marqués avec @pytest.mark.perf, lancés via make perf_test.

test_perf_triangulation_100_points: Mesurer temps de calcul pour 100 points.

test_perf_triangulation_10000_points: Mesurer temps de calcul pour 10 000 points.

test_perf_triangulation_100k_points: Mesurer temps de calcul pour 100 000 points.

test_perf_serialisation_large: Mesurer temps d'écriture binaire pour 100k points / 200k triangles.

test_perf_deserialisation_large: Mesurer temps de lecture binaire pour 100k points.

5. Catégorie 4 : Qualité de Code et Documentation

But : Assurer que le code est propre, lisible, maintenable et entièrement testé.
Comment : Utiliser les cibles make demandées.

Linting (Qualité):

Cible : make lint (avec ruff).

Objectif : Zéro erreur ruff à la fin.

Documentation (Qualité):

Cible : make doc (avec pdoc3).

Objectif : Documenter toutes les fonctions, classes et modules publics ("docstrings") pour générer une documentation HTML complète.

Couverture (Complétude des tests):

Cible : make coverage (avec coverage).

Objectif : Atteindre 100% de couverture. Si des lignes (ex: une branche except spécifique) ne sont pas couvertes, des tests (probablement de Catégorie 2) seront ajoutés pour les couvrir.