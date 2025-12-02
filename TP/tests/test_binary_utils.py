"""
Tests Unitaires

ce fichier teste les "traducteurs" binaires pour s'assurer
qu'ils lisent et écrivent le format binaire correctement
"""

import pytest
import struct
from triangulator.binary_utils import (
    binary_to_pointset,
    triangles_to_binary,
    BinaryFormatError
)
from triangulator.core import Point, Triangle


#PointSet (Lecture / Désérialisation)


def test_binary_to_pointset_simple():
#teste la désérialisation d'un PointSet binaire valide avec 2 points
    #données binaires valides pour 2 points: (1.0, 2.0) et (-3.0, -4.0)
    # Header: 4 bytes, count=2 (format '!I' -> network byte order, unsigned int)
    header = struct.pack("!I", 2)
    # Point 1: 8 bytes, (1.0, 2.0) (format '!ff' -> 2 floats)
    point1 = struct.pack("!ff", 1.0, 2.0)
    # Point 2: 8 bytes, (-3.0, -4.0)
    point2 = struct.pack("!ff", -3.0, -4.0)
    
    valid_data = header + point1 + point2
    
    points = binary_to_pointset(valid_data)
    
    assert points == [(1.0, 2.0), (-3.0, -4.0)]

def test_binary_to_pointset_malforme_header_court():
#test la désérialisation avec un header binaire trop court
    invalid_data = b"\x00\x01"  # 2 bytes au lieu de 4
    
    with pytest.raises(BinaryFormatError):
        binary_to_pointset(invalid_data)

def test_binary_to_pointset_malforme_data_incomplet():
#test la désérialisation, le header annonce plus de points que les données n'en contiennent
    # Header: 4 bytes, count=10
    header = struct.pack("!I", 10)
    # Données: 8 bytes, 1 point
    point1 = struct.pack("!ff", 1.0, 2.0)
    
    invalid_data = header + point1 # Annonce 10 points, ne fournit qu'1
    
    with pytest.raises(BinaryFormatError):
        binary_to_pointset(invalid_data)


#triangles (Écriture / Sérialisation)


def test_triangles_to_binary_simple():
    #test la sérialisation d'un objet Triangles valide (2 points, 1 triangle)
    vertices: List[Point] = [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]
    triangles: List[Triangle] = [(0, 1, 2)]
    
    result_bytes = triangles_to_binary(vertices, triangles)

    
    # Partie 1: Vertices (3)
    part1_header = struct.pack("!I", 3)
    part1_data = struct.pack("!ffffff", 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
    
    # Partie 2: Triangles (1)
    part2_header = struct.pack("!I", 1)
    part2_data = struct.pack("!III", 0, 1, 2) # 3 unsigned ints
    
    expected_bytes = part1_header + part1_data + part2_header + part2_data
    
    assert result_bytes == expected_bytes

def test_triangles_to_binary_no_triangles():
#test la sérialisation pour un cas avec des points mais 0 triangle
    vertices: List[Point] = [(1.0, 2.0), (3.0, 4.0)] # 2 points, colinéaires
    triangles: List[Triangle] = []
    
    result_bytes = triangles_to_binary(vertices, triangles)

    
    # Partie 1: Vertices (2)
    part1_header = struct.pack("!I", 2)
    part1_data = struct.pack("!ffff", 1.0, 2.0, 3.0, 4.0)
    
    # Partie 2: Triangles (0)
    part2_header = struct.pack("!I", 0)
    part2_data = b""
    
    expected_bytes = part1_header + part1_data + part2_header + part2_data
    
    assert result_bytes == expected_bytes