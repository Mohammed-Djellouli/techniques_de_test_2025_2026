"""Tests d'API et Intégration.

Ce fichier teste le service Flask (app.py)
en simulant (mockant) sa seule dépendance externe : le PointSetManager.
"""

import struct
from urllib.error import HTTPError, URLError
from uuid import UUID

from triangulator.binary_utils import BinaryFormatError

# UUID de test valide
VALID_UUID = UUID("123e4567-e89b-12d3-a456-426614174000")

# Faux "PointSet" binaire pour 4 points (carré)
FAKE_POINTSET_BYTES = (
    struct.pack("!I", 4)  # count=4
    + struct.pack("!ff", 0.0, 0.0)
    + struct.pack("!ff", 1.0, 0.0)
    + struct.pack("!ff", 1.0, 1.0)
    + struct.pack("!ff", 0.0, 1.0)
)

# Faux "Triangles" binaire pour le résultat
FAKE_TRIANGLES_BYTES = (
    struct.pack("!I", 4)  # count=4 (vertices)
    + struct.pack("!ffffff", 0.0, 0.0, 1.0, 0.0, 1.0, 1.0)  # 3 points
    + struct.pack("!ff", 0.0, 1.0)  # 4e point
    + struct.pack("!I", 2)  # count=2 (triangles)
    + struct.pack("!III", 0, 1, 2)
    + struct.pack("!III", 0, 2, 3)
)


# "Happy Path"


def test_api_triangulate_success(client, mocker):
    """Teste le scénario A->B->C->D, tout fonctionne."""
    # Scénario A: le Client appelle
    # mock l'appel au PointSetManager pour qu'il réussisse
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        return_value=FAKE_POINTSET_BYTES
    )
    # Mock la désérialisation
    mocker.patch(
        "triangulator.app.binary_utils.binary_to_pointset",
        return_value=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    )
    # mock le calcul (le "cerveau")
    mocker.patch(
        "triangulator.app.core.compute_triangulation",
        return_value=(
            [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],  # vertices
            [(0, 1, 2), (0, 2, 3)]  # triangles
        )
    )
    # Mock la sérialisation
    mocker.patch(
        "triangulator.app.binary_utils.triangles_to_binary",
        return_value=FAKE_TRIANGLES_BYTES
    )

    response = client.get(f"/triangulation/{VALID_UUID}")

    # Vérifier la réponse
    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"
    assert response.data == FAKE_TRIANGLES_BYTES


# Scénarios d'erreurs


def test_api_pointset_id_not_found(client, mocker):
    """Teste le Cas 404 (ID inconnu)."""
    #mock l'appel pour qu'il lève une erreur HTTP 404
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        side_effect=HTTPError("http://fake-url", 404, "Not Found", {}, None)
    )

    #appel
    response = client.get(f"/triangulation/{VALID_UUID}")

    #vérification
    assert response.status_code == 404
    assert response.mimetype == "application/json"
    assert response.json["code"] == "POINTSET_NOT_FOUND"


def test_api_pointsetmanager_indisponible_503(client, mocker):
    """Teste le cas 503 (panne BDD distante)."""
    #mock l'appel pour qu'il lève une erreur HTTP 503
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        side_effect=HTTPError("http://fake-url", 503, "Unavailable", {}, None)
    )

    response = client.get(f"/triangulation/{VALID_UUID}")

    #Vérification
    assert response.status_code == 503
    assert response.json["code"] == "MANAGER_ERROR"


def test_api_pointsetmanager_panne_reseau(client, mocker):
    """Teste le Cas 503 (panne réseau ou URLError)."""
    #Mock l'appel pour qu'il lève une URLError
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        side_effect=URLError("Connection refused")
    )

    response = client.get(f"/triangulation/{VALID_UUID}")

    #vérification
    assert response.status_code == 503
    assert response.json["code"] == "MANAGER_UNAVAILABLE"


def test_api_pointsetmanager_donnees_corrompues(client, mocker):
    """Teste le Cas 500 (données binaires corrompues)."""
    #mock l'appel (réussit)
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        return_value=b"\xDE\xAD\xBE\xEF"  # données corrompues
    )
    # Mock la désérialisation pour qu'elle lève l'erreur attendue
    mocker.patch(
        "triangulator.app.binary_utils.binary_to_pointset",
        side_effect=BinaryFormatError("Données corrompues")
    )

    # L'app doit attraper l'erreur de 'binary_to_pointset'
    response = client.get(f"/triangulation/{VALID_UUID}")

    # Vérification
    assert response.status_code == 500
    assert response.json["code"] == "INVALID_BINARY_DATA"


def test_api_triangulation_interne_echoue(client, mocker):
    """Teste le Cas 500 (l'algorithme interne plante)."""
    # Mock les premières étapes pour qu'elles réussissent
    mocker.patch(
        "triangulator.app.manager_client.fetch_pointset_from_manager",
        return_value=FAKE_POINTSET_BYTES
    )
    mocker.patch(
        "triangulator.app.binary_utils.binary_to_pointset",
        return_value=[(1.0, 1.0)]
    )
    # mock le "cerveau" pour qu'il lève une exception
    mocker.patch(
        "triangulator.app.core.compute_triangulation",
        side_effect=Exception("Erreur de calcul interne")
    )

    response = client.get(f"/triangulation/{VALID_UUID}")

    # Vérification
    assert response.status_code == 500
    assert response.json["code"] == "INTERNAL_ERROR"


def test_api_invalid_uuid_format(client):
    """Teste le Cas 400 (ID mal formé).

    Flask gère cela par défaut en renvoyant 404 si le type ne correspond pas.
    """
    # appel avec un ID non-UUID
    response = client.get("/triangulation/ID-PAS-UN-UUID")

    # Vérification (Flask renvoie 404, pas 400, pour un type d'URL)
    assert response.status_code == 404