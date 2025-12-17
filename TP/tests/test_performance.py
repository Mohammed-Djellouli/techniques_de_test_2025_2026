"""Tests de Performance.

Tous les tests ici sont marqués avec '@pytest.mark.perf' pour être
exécutés séparément.
"""

import random
import struct

import pytest
from triangulator.binary_utils import binary_to_pointset, triangles_to_binary
from triangulator.core import Point, Triangle, compute_triangulation


def _generate_large_pointset(count: int) -> list[Point]:
    """Génère un nuage de points aléatoire de 'count' points."""
    points = []
    for _ in range(count):
        points.append(
            (random.uniform(0, 1000), random.uniform(0, 1000))
        )
    return points


def _generate_large_triangles(point_count: int) -> tuple[list[Point], list[Triangle]]:
    """Génère un grand ensemble de points et une liste 'fausse' de triangles."""
    points = _generate_large_pointset(point_count)
    # 2*N-2 triangles pour N points
    triangles = []
    if point_count >= 3:
        num_triangles = 2 * point_count - 2
        for _ in range(num_triangles):
            triangles.append(
                (0, 1, 2)
            )
    return points, triangles


def _generate_valid_binary_pointset(count: int) -> bytes:
    """Génère des données binaires valides pour un PointSet."""
    header = struct.pack("!I", count)
    data = b""
    for _ in range(count):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        data += struct.pack("!ff", x, y)
    return header + data


# Tests de Performance
# Note: L'algorithme Ear Clipping a une complexité O(n²), 


@pytest.mark.perf
def test_perf_triangulation_50_points():
    """Mesure le temps de calcul pour 50 points."""
    points = _generate_large_pointset(50)
    compute_triangulation(points)


@pytest.mark.perf
def test_perf_triangulation_100_points():
    """Mesure le temps de calcul pour 100 points."""
    points = _generate_large_pointset(100)
    compute_triangulation(points)


@pytest.mark.perf
def test_perf_triangulation_10000_points():
    """Mesure le temps de calcul pour 10 000 points."""
    points = _generate_large_pointset(10000)
    compute_triangulation(points)


@pytest.mark.perf
def test_perf_triangulation_100k_points():
    """Mesure le temps de calcul pour 100 000 points."""
    points = _generate_large_pointset(100000)
    compute_triangulation(points)


@pytest.mark.perf
def test_perf_serialisation_large():
    """Mesure le temps de sérialisation pour 100k points / 200k triangles."""
    points, triangles = _generate_large_triangles(100000)

    triangles_to_binary(points, triangles)


@pytest.mark.perf
def test_perf_deserialisation_large():
    """Mesure le temps de désérialisation pour 100k points."""
    valid_binary_data = _generate_valid_binary_pointset(100000)

    # Teste réellement la désérialisation (pas juste catch d'erreur)
    result = binary_to_pointset(valid_binary_data)

    # Vérifie que la désérialisation a bien fonctionné
    assert len(result) == 100000
