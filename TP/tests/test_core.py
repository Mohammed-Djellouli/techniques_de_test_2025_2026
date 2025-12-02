"""
Tests Unitaires

la fonction 'compute_triangulation'
"""

import pytest
from triangulator.core import compute_triangulation, Point


#cas normaux
def test_triangulation_3_points():
    #vérifie qu'un set de 3 points non-alignés produit 1 triangle
    points: List[Point] = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 3
    assert len(triangles) == 1

def test_triangulation_4_points_carre():
    #vérifie qu'un set de 4 points en carré produit 2 triangles
    points: List[Point] = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 4
    assert len(triangles) == 2

def test_triangulation_5_points_convexe():
    #vérifie qu'un pentagone convexe produit 3 triangles
    points: List[Point] = [
        (0.0, 0.0), (1.0, 0.0), (1.5, 1.0), (0.5, 1.5), (-0.5, 1.0)
    ]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 5
    assert len(triangles) == 3


#cas limites
def test_triangulation_0_points():
#vérifie qu'un set de 0 point produit 0 triangle
    points: List[Point] = []
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 0
    assert len(triangles) == 0

def test_triangulation_1_point():
#vérifie qu'un set de 1 point produit 0 triangle
    points: List[Point] = [(1.0, 1.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 1
    assert len(triangles) == 0

def test_triangulation_2_points():
#vérifie qu'un set de 2 points produit 0 triangle
    points: List[Point] = [(1.0, 1.0), (2.0, 2.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 2
    assert len(triangles) == 0

#cas Bizarres

def test_triangulation_points_colineaires():
#vérifie que N points alignés produisent 0 triangle
    points: List[Point] = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(vertices) == 4
    assert len(triangles) == 0

def test_triangulation_points_doublons():
#vérifie que des points identiques sont gérés (produisent 0 triangle)
    points: List[Point] = [(0.0, 0.0), (0.0, 0.0), (1.0, 1.0), (1.0, 1.0)]
    
    vertices, triangles = compute_triangulation(points)
    
    assert len(triangles) == 0