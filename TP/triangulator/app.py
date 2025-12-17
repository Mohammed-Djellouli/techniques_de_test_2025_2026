"""Module Applicatif - Serveur Flask (Triangulator).

Ce module est le point d'entrée principal du service.
Il définit l'endpoint HTTP /triangulation/{pointSetId} et
orchestre les appels aux autres modules (client, core, binary_utils).
"""

import os
from urllib.error import HTTPError, URLError
from uuid import UUID

from flask import Flask, Response, jsonify

from . import binary_utils, core, manager_client

# Création de l'application Flask
app = Flask(__name__)

# Récupère l'URL du PointSetManager depuis une variable d'environnement
# C'est une bonne pratique pour la configuration.
POINT_SET_MANAGER_URL = os.environ.get(
    "POINT_SET_MANAGER_URL", "http://localhost:8080"
)

@app.route("/triangulation/<uuid:pointSetId>", methods=["GET"])
def get_triangulation(pointSetId: UUID):
    """Endpoint principal pour demander une triangulation.

    Prend un UUID, contacte le PointSetManager, calcule la triangulation
    et renvoie le résultat binaire.
    """
    # Convertir l'UUID en string pour l'URL et les logs
    point_set_id_str = str(pointSetId)
    # print(f"Endpoint get_triangulation appelé avec l'ID: {point_set_id_str}")
    
    try:
        # Étape 1: Appeler le PointSetManager pour récupérer les données binaires
        pointset_bytes = manager_client.fetch_pointset_from_manager(
            POINT_SET_MANAGER_URL, pointSetId
        )

        # Étape 2: Désérialiser les données binaires en liste de points
        points = binary_utils.binary_to_pointset(pointset_bytes)

        # Étape 3: Calculer la triangulation
        vertices, triangles = core.compute_triangulation(points)

        # Étape 4: Sérialiser le résultat en format binaire 'Triangles'
        response_bytes = binary_utils.triangles_to_binary(vertices, triangles)

        # Étape 5: Renvoyer la réponse avec le bon type MIME
        return Response(response_bytes, status=200, mimetype="application/octet-stream")

    except HTTPError as e:
        # Gestion des erreurs renvoyées par le PointSetManager (404, 500, 503...)
        if e.code == 404:
            return jsonify({
                "code": "POINTSET_NOT_FOUND",
                "message": f"PointSet {point_set_id_str} non trouvé."
            }), 404
        elif e.code == 503:
            return jsonify({
                "code": "MANAGER_ERROR",
                "message": "Le PointSetManager est indisponible."
            }), 503
        else:
            # Autres erreurs HTTP (500 du manager, etc.) traitées comme erreur manager
            return jsonify({
                "code": "MANAGER_ERROR",
                "message": f"Erreur du PointSetManager: {e.reason}"
            }), 503

    except URLError as e:
        # Gestion des pannes de connexion (Manager éteint, DNS, timeout, etc.)
        return jsonify({
            "code": "MANAGER_UNAVAILABLE",
            "message": f"Impossible de contacter le PointSetManager: {e.reason}"
        }), 503

    except binary_utils.BinaryFormatError as e:
        # Gestion des données corrompues reçues du Manager (Cas 500)
        return jsonify({
            "code": "INVALID_BINARY_DATA",
            "message": f"Données binaires reçues invalides: {e}"
        }), 500

    except Exception as e:
        # Gestion générique des erreurs internes (ex: bug dans l'algo core.py)
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": f"Erreur interne inattendue: {e}"
        }), 500

# Point d'entrée pour lancer le serveur en mode debug
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)