"""Tests Unitaires pour le module manager_client.

Ce fichier teste la fonction fetch_pointset_from_manager en mockant
directement urllib.request.urlopen pour couvrir tous les cas.
"""

import struct
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError
from uuid import UUID

import pytest
from triangulator.manager_client import fetch_pointset_from_manager

# UUID de test
TEST_UUID = UUID("123e4567-e89b-12d3-a456-426614174000")
BASE_URL = "http://localhost:8080"

# Données binaires de test (2 points)
TEST_POINTSET_BYTES = (
    struct.pack("!I", 2)
    + struct.pack("!ff", 1.0, 2.0)
    + struct.pack("!ff", 3.0, 4.0)
)


def test_fetch_pointset_success():
    """Teste la récupération réussie d'un PointSet (200 OK)."""
    # Créer un mock de la réponse HTTP
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = TEST_POINTSET_BYTES
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        result = fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        # Vérifier que urlopen a été appelé avec la bonne URL
        expected_url = f"{BASE_URL}/pointset/{TEST_UUID}"
        mock_urlopen.assert_called_once_with(expected_url, timeout=5)

        # Vérifier le résultat
        assert result == TEST_POINTSET_BYTES


def test_fetch_pointset_http_404():
    """Teste la gestion d'une erreur 404 (PointSet non trouvé)."""
    http_error = HTTPError(
        f"{BASE_URL}/pointset/{TEST_UUID}",
        404,
        "Not Found",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(HTTPError) as exc_info:
            fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        assert exc_info.value.code == 404


def test_fetch_pointset_http_503():
    """Teste la gestion d'une erreur 503 (Service indisponible)."""
    http_error = HTTPError(
        f"{BASE_URL}/pointset/{TEST_UUID}",
        503,
        "Service Unavailable",
        {},
        None
    )

    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(HTTPError) as exc_info:
            fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        assert exc_info.value.code == 503


def test_fetch_pointset_url_error():
    """Teste la gestion d'une erreur réseau (URLError)."""
    url_error = URLError("Connection refused")

    with patch("urllib.request.urlopen", side_effect=url_error):
        with pytest.raises(URLError) as exc_info:
            fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        assert "Connection refused" in str(exc_info.value.reason)


def test_fetch_pointset_timeout():
    """Teste la gestion d'un timeout."""
    url_error = URLError("timed out")

    with patch("urllib.request.urlopen", side_effect=url_error):
        with pytest.raises(URLError) as exc_info:
            fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        assert "timed out" in str(exc_info.value.reason)


def test_fetch_pointset_unexpected_status():
    """Teste la gestion d'un code de statut inattendu (ex: 204 No Content)."""
    # Créer un mock avec un statut 204
    mock_response = MagicMock()
    mock_response.status = 204
    mock_response.headers = {}
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        with pytest.raises(HTTPError) as exc_info:
            fetch_pointset_from_manager(BASE_URL, TEST_UUID)

        assert exc_info.value.code == 204
        assert "Réponse inattendue" in exc_info.value.reason
