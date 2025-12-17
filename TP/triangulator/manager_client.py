"""Module Client - Client HTTP pour le PointSetManager.

Ce module gère la communication (requêtes HTTP) avec le service
externe PointSetManager.
"""

import urllib.request
from urllib.error import HTTPError, URLError  # noqa: F401
from uuid import UUID


class PointSetManagerError(Exception):
    """Exception de base pour les problèmes du client."""

    pass

def fetch_pointset_from_manager(base_url: str, pointSetId: UUID) -> bytes:
    """Appelle l'endpoint GET /pointset/{pointSetId} du PointSetManager.

    Args:
        base_url: L'URL de base du service PointSetManager (ex: "http://localhost:8080").
        pointSetId: L'UUID du PointSet à récupérer.

    Returns:
        Les données binaires brutes (le PointSet) en cas de succès (200 OK).

    Raises:
        HTTPError: Si le manager renvoie une erreur 4xx ou 5xx.
        URLError: S'il y a un problème de connexion (panne réseau, timeout).

    """
    url_to_call = f"{base_url}/pointset/{pointSetId}"
    
    try:
        # Timeout de 5 secondes pour ne pas bloquer indéfiniment
        with urllib.request.urlopen(url_to_call, timeout=5) as response:
            if response.status == 200:
                return response.read()
            else:
                # Bien que urlopen lève généralement HTTPError pour les non-200,
                # on gère explicitement les codes de succès inattendus (ex: 204).
                raise HTTPError(
                    url_to_call, 
                    response.status, 
                    "Réponse inattendue (pas 200 OK)", 
                    response.headers, 
                    None
                )
                
    except HTTPError as e:
        # On relance l'erreur pour qu'elle soit gérée par le contrôleur (app.py)
        # C'est important pour renvoyer le bon code (404, 503) au client final.
        print(f"Erreur HTTP {e.code} en appelant {url_to_call}")
        raise e
        
    except URLError as e:
        # Erreur de connexion bas niveau (DNS, Refused, Timeout)
        print(f"Erreur de connexion vers {url_to_call}: {e.reason}")
        raise e