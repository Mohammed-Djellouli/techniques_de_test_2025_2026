"""Module Utilitaires Binaires - (Dé)Sérialisation.

Ce module gère la conversion entre les objets Python (listes de points)
et la représentation binaire compacte définie dans les spécifications.
"""

import struct

# Type hints
Point = tuple[float, float]
Triangle = tuple[int, int, int]

class BinaryFormatError(Exception):
    """Exception personnalisée pour les erreurs de parsing binaire."""

    pass

def binary_to_pointset(data: bytes) -> list[Point]:
    """Désérialise un PointSet binaire en une liste de points.

    Format d'entrée:
    - 4 bytes (unsigned long): Nombre de points (N)
    - N * 8 bytes:
        - 4 bytes (float): Coordonnée X
        - 4 bytes (float): Coordonnée Y

    Args:
        data: Les données binaires brutes reçues du PointSetManager.

    Returns:
        Une liste de tuples (x, y).

    Raises:
        BinaryFormatError: Si les données sont mal formées ou incomplètes.

    """
    # 1. Vérifier la taille minimale pour le header (4 bytes)
    if len(data) < 4:
        raise BinaryFormatError(
            "Données trop courtes pour contenir le nombre de points."
        )

    # 2. Lire le nombre de points (N)
    # '!I' = Network (Big-Endian), unsigned int
    try:
        count = struct.unpack("!I", data[:4])[0]
    except struct.error as e:
        raise BinaryFormatError(
            f"Erreur lors de la lecture du header: {e}"
        ) from e

    # 3. Vérifier la taille totale attendue
    # Chaque point fait 8 bytes (4 bytes float X + 4 bytes float Y)
    expected_size = 4 + (count * 8)
    if len(data) < expected_size:
        raise BinaryFormatError(
            f"Données incomplètes. Attendu: {expected_size} bytes, "
            f"Reçu: {len(data)} bytes."
        )

    # 4. Lire les points
    points: list[Point] = []
    offset = 4
    for _ in range(count):
        # '!ff' = 2 floats (X, Y)
        try:
            x, y = struct.unpack("!ff", data[offset : offset + 8])
            points.append((x, y))
            offset += 8
        except struct.error as e:
            raise BinaryFormatError(
                f"Erreur lors de la lecture d'un point: {e}"
            ) from e

    return points


def triangles_to_binary(vertices: list[Point], triangles: list[Triangle]) -> bytes:
    """Sérialise une liste de vertices et de triangles en 'Triangles' binaire.

    Format de sortie:
    Partie 1: Vertices (identique au format PointSet)
    - 4 bytes (unsigned long): Nombre de vertices (N)
    - N * 8 bytes: (float X, float Y)
    Partie 2: Triangles (indices)
    - 4 bytes (unsigned long): Nombre de triangles (T)
    - T * 12 bytes: (unsigned long I1, unsigned long I2, unsigned long I3)

    Args:
        vertices: La liste des points (vertices).
        triangles: La liste des triangles (tuples d'indices).

    Returns:
        Les données binaires brutes à envoyer au client.

    """
    chunks = []

    # --- Partie 1 : Vertices ---
    # Nombre de points
    chunks.append(struct.pack("!I", len(vertices)))
    
    # Points
    for x, y in vertices:
        chunks.append(struct.pack("!ff", x, y))

    # --- Partie 2 : Triangles ---
    # Nombre de triangles
    chunks.append(struct.pack("!I", len(triangles)))
    
    # Triangles (3 indices par triangle)
    for i1, i2, i3 in triangles:
        # '!III' = 3 unsigned ints
        chunks.append(struct.pack("!III", i1, i2, i3))

    return b"".join(chunks)