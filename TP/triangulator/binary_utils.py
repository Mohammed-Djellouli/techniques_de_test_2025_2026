from typing import List, Tuple

Point = Tuple[float, float]
Triangle = Tuple[int, int, int]

class BinaryFormatError(Exception):
    pass

def binary_to_pointset(data: bytes) -> List[Point]:

    print(f"binary_to_pointset appelé avec {len(data)} bytes.")
    
    raise NotImplementedError("n'est pas implémentée")


def triangles_to_binary(vertices: List[Point], triangles: List[Triangle]) -> bytes:

    print(f"triangles_to_binary appelé pour {len(vertices)} points et {len(triangles)} triangles.")
    
    raise NotImplementedError("n'est pas implémentée")