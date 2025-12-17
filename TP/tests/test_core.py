"""Tests Unitaires pour la fonction 'compute_triangulation'."""

from triangulator.core import (
    Point,
    _cross_product_2d,
    _is_collinear,
    _is_convex_vertex,
    _is_point_in_triangle,
    _polygon_area_signed,
    compute_triangulation,
)


# Tests de compute_triangulation - Cas normaux (convexes)


def test_triangulation_3_points():
    """Vérifie qu'un set de 3 points non-alignés produit 1 triangle."""
    points: list[Point] = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 3
    assert len(triangles) == 1


def test_triangulation_4_points_carre():
    """Vérifie qu'un set de 4 points en carré produit 2 triangles."""
    points: list[Point] = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 4
    assert len(triangles) == 2


def test_triangulation_5_points_convexe():
    """Vérifie qu'un pentagone convexe produit 3 triangles."""
    points: list[Point] = [
        (0.0, 0.0), (1.0, 0.0), (1.5, 1.0), (0.5, 1.5), (-0.5, 1.0)
    ]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 5
    assert len(triangles) == 3



# Tests de compute_triangulation - Cas CONCAVES (nouveaux tests!)



def test_triangulation_forme_L():
    """Vérifie la triangulation d'une forme en L (concave)."""
    # Forme en L
    #   4---3
    #   |   |
    #   | 5-2
    #   |   |
    #   0---1
    points: list[Point] = [
        (0.0, 0.0),   # 0 - bas gauche
        (2.0, 0.0),   # 1 - bas droite
        (2.0, 1.0),   # 2 - milieu droite
        (1.0, 1.0),   # 3 - coin intérieur (concave)
        (1.0, 2.0),   # 4 - haut milieu
        (0.0, 2.0),   # 5 - haut gauche
    ]

    vertices, triangles = compute_triangulation(points)

    # Un hexagone (6 sommets) doit produire 4 triangles (n-2)
    assert len(vertices) == 6
    assert len(triangles) == 4


def test_triangulation_fleche():
    """Vérifie la triangulation d'une forme de flèche (concave)."""
    # Flèche pointant vers la droite
    #      2
    #     /|
    #    / |
    #   1  3
    #    \ |
    #     \|
    #      4
    #      |
    #      0
    points: list[Point] = [
        (1.0, 0.0),   # 0 - base
        (0.0, 1.0),   # 1 - gauche
        (1.0, 2.0),   # 2 - pointe haute
        (0.5, 1.0),   # 3 - centre (concave)
        (1.0, 0.5),   # 4 - droite bas
    ]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 5
    assert len(triangles) == 3  # 5 - 2 = 3 triangles


def test_triangulation_etoile_simple():
    """Vérifie la triangulation d'une étoile à 4 branches (très concave)."""
    # Étoile avec centre creux
    points: list[Point] = [
        (0.0, 1.0),    # 0 - pointe gauche
        (0.4, 0.4),    # 1 - creux
        (1.0, 0.0),    # 2 - pointe bas
        (0.6, 0.4),    # 3 - creux
        (1.0, 1.0),    # 4 - pointe droite
        (0.6, 0.6),    # 5 - creux
        (0.5, 1.0),    # 6 - pointe haut
        (0.4, 0.6),    # 7 - creux
    ]

    vertices, triangles = compute_triangulation(points)

    # 8 sommets -> 6 triangles
    assert len(vertices) == 8
    assert len(triangles) == 6


def test_triangulation_u_shape():
    """Vérifie la triangulation d'une forme """
    #
    #   0-------1
    #   |       |
    #   |   3---2
    #   |   |
    #   5---4
    points: list[Point] = [
        (0.0, 2.0),   # 0 - haut gauche
        (2.0, 2.0),   # 1 - haut droite
        (2.0, 1.0),   # 2 - milieu droite
        (1.0, 1.0),   # 3 - coin intérieur haut
        (1.0, 0.0),   # 4 - coin intérieur bas
        (0.0, 0.0),   # 5 - bas gauche
    ]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 6
    assert len(triangles) == 4  # 6 - 2 = 4



# Tests de compute_triangulation - Cas limites


def test_triangulation_0_points():
    """Vérifie qu'un set de 0 point produit 0 triangle."""
    points: list[Point] = []

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 0
    assert len(triangles) == 0


def test_triangulation_1_point():
    """Vérifie qu'un set de 1 point produit 0 triangle."""
    points: list[Point] = [(1.0, 1.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 1
    assert len(triangles) == 0


def test_triangulation_2_points():
    """Vérifie qu'un set de 2 points produit 0 triangle."""
    points: list[Point] = [(1.0, 1.0), (2.0, 2.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 2
    assert len(triangles) == 0


# Tests de compute_triangulation - Cas dégénérés


def test_triangulation_points_colineaires():
    """Vérifie que N points alignés produisent 0 triangle."""
    points: list[Point] = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 4
    assert len(triangles) == 0


def test_triangulation_points_doublons():
    """Vérifie que des points identiques sont gérés (produisent 0 triangle)."""
    points: list[Point] = [(0.0, 0.0), (0.0, 0.0), (1.0, 1.0), (1.0, 1.0)]

    vertices, triangles = compute_triangulation(points)

    assert len(triangles) == 0


def test_triangulation_hexagone_regulier():
    """Vérifie la triangulation d'un hexagone régulier."""
    import math

    # Hexagone régulier centré à l'origine
    points: list[Point] = []
    for i in range(6):
        angle = i * math.pi / 3
        points.append((math.cos(angle), math.sin(angle)))

    vertices, triangles = compute_triangulation(points)

    assert len(vertices) == 6
    assert len(triangles) == 4  # 6 - 2 = 4
