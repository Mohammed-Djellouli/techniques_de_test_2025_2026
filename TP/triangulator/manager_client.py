from urllib.error import HTTPError, URLError
import urllib.request
from uuid import UUID

class PointSetManagerError(Exception):
    pass

def fetch_pointset_from_manager(base_url: str, pointSetId: UUID) -> bytes:
    url_to_call = f"{base_url}/pointset/{pointSetId}"
    print(f"fetch_pointset_from_manager: devrait appeler {url_to_call}")
    raise NotImplementedError("Le client HTTP n'est pas implémenté")