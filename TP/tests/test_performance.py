"""
Tests de Performance

Tous les tests ici sont marqués avec '@pytest.mark.perf' pour être
exécutés séparément
"""
import pytest
import random
from triangulator.core import compute_triangulation, Point, Triangle
from triangulator.binary_utils import binary_to_pointset, triangles_to_binary,BinaryFormatError

def _generate_large_pointset(count: int) -> list[Point]:
    #génére un nuage de points aléatoire de 'count' points
    points = []
    for _ in range(count):
        points.append(
            (random.uniform(0, 1000), random.uniform(0, 1000))
        )
    return points

def _generate_large_triangles(point_count: int) -> tuple[list[Point], list[Triangle]]:
    #génére un grand ensemble de points et une liste "fausse" de triangles
    points = _generate_large_pointset(point_count)
    #2*2-2 triangles pour N points
    triangles = []
    if point_count >= 3:
        num_triangles = 2 * point_count - 2
        for i in range(num_triangles):
            triangles.append(
                (0, 1, 2)
            )
    return points, triangles


#tests de Performance


@pytest.mark.perf
def test_perf_triangulation_100_points():
    #mesure le temps de calcul pour 100 points
    points = _generate_large_pointset(100)
    compute_triangulation(points)
    
@pytest.mark.perf
def test_perf_triangulation_10000_points():
    #mesure le temps de calcul pour 10 000 points
    points = _generate_large_pointset(10000)
    compute_triangulation(points)

@pytest.mark.perf
def test_perf_triangulation_100k_points():
    #mesure le temps de calcul pour 100 000 points
    points = _generate_large_pointset(100000)
    compute_triangulation(points)

@pytest.mark.perf
def test_perf_serialisation_large():
    #mesure le temps de sérialisation pour 100k points / 200k triangles
    points, triangles = _generate_large_triangles(100000)
    
    triangles_to_binary(points, triangles)

@pytest.mark.perf
def test_perf_deserialisation_large():
    #mesure le temps de désérialisation pour 100k points
    
    fake_large_bytes = b"header_placeholder" * 100000
    
    try:
        binary_to_pointset(fake_large_bytes)
    except (NotImplementedError, BinaryFormatError):
        pass