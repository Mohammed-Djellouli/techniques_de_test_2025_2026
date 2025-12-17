"""Fichier de configuration global pour pytest.

Ce fichier définit des 'fixtures' réutilisables pour les tests.
"""

import pytest
from triangulator.app import app as flask_app


@pytest.fixture(scope="session")
def app():
    """Fixture pour fournir une instance de l'application Flask.

    Configurée pour le mode 'TESTING'.
    """
    # Configure l'application pour les tests
    # Cela désactive par exemple les messages d'erreur HTML au profit d'exceptions
    flask_app.config.update({
        "TESTING": True,
    })

    # "yield" est comme un "return" pour les fixtures
    # Il fournit l'objet 'flask_app' au test
    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Fixture pour fournir un 'client de test' Flask.

    Permet de simuler des requêtes HTTP (GET, POST...) sur l'app.
    'scope="function"' signifie qu'un nouveau client est créé pour chaque test.
    """
    # Crée un client de test à partir de l'application
    return app.test_client()