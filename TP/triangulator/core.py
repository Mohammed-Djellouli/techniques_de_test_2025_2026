"""Module Cœur (Core) - Logique de Triangulation.

Ce module contient l'algorithme de triangulation principal utilisant
la méthode Ear Clipping, qui fonctionne pour les polygones convexes et concaves.
"""

# Type hints pour la clarté
Point = tuple[float, float]
Triangle = tuple[int, int, int]

# Tolérance pour les comparaisons flottantes
EPSILON = 1e-9


def _cross_product_2d(o: Point, a: Point, b: Point) -> float:
    """Compute the 2D cross product (OA x OB).

    Returns:
        > 0 if the turn O->A->B is counter-clockwise (left)
        < 0 if the turn O->A->B is clockwise (right)
        = 0 if the points are collinear

    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _is_collinear(p1: Point, p2: Point, p3: Point) -> bool:
    """Vérifie si 3 points sont alignés en calculant l'aire du triangle formé.

    Si l'aire est proche de 0 (avec une tolérance epsilon), ils sont alignés.
    """
    return abs(_cross_product_2d(p1, p2, p3)) < EPSILON


def _polygon_area_signed(vertices: list[Point]) -> float:
    """Compute the signed area of a polygon using the shoelace formula.

    Returns:
        > 0 if the vertices are in counter-clockwise order
        < 0 if the vertices are in clockwise order

    """
    n = len(vertices)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return area / 2.0


def _is_point_in_triangle(p: Point, t1: Point, t2: Point, t3: Point) -> bool:
    """Vérifie si le point P est strictement à l'intérieur du triangle T1-T2-T3.

    Utilise les coordonnées barycentriques / produits vectoriels.
    """
    d1 = _cross_product_2d(p, t1, t2)
    d2 = _cross_product_2d(p, t2, t3)
    d3 = _cross_product_2d(p, t3, t1)

    has_neg = (d1 < -EPSILON) or (d2 < -EPSILON) or (d3 < -EPSILON)
    has_pos = (d1 > EPSILON) or (d2 > EPSILON) or (d3 > EPSILON)

    # Si tous du même signe (ou zéro), le point est dans le triangle
    return not (has_neg and has_pos)


def _is_convex_vertex(prev_pt: Point, curr_pt: Point, next_pt: Point,
                      clockwise: bool) -> bool:
    """Vérifie si le sommet courant forme un angle convexe.

    Args:
        prev_pt: Point précédent
        curr_pt: Point courant
        next_pt: Point suivant
        clockwise: True si le polygone est en ordre horaire

    """
    cross = _cross_product_2d(prev_pt, curr_pt, next_pt)
    if clockwise:
        return cross < -EPSILON  # Convexe si virage à droite
    return cross > EPSILON  # Convexe si virage à gauche


def _is_ear(polygon_indices: list[int], vertices: list[Point],
            idx: int, clockwise: bool) -> bool:
    """Vérifie si le sommet à l'index idx est une "oreille" du polygone.

    Une oreille est un triangle formé par 3 sommets consécutifs qui:
    1. Forme un angle convexe
    2. Ne contient aucun autre sommet du polygone

    """
    n = len(polygon_indices)
    if n < 3:
        return False

    # Indices dans la liste polygon_indices
    prev_idx = (idx - 1) % n
    next_idx = (idx + 1) % n

    # Points réels
    prev_pt = vertices[polygon_indices[prev_idx]]
    curr_pt = vertices[polygon_indices[idx]]
    next_pt = vertices[polygon_indices[next_idx]]

    # 1. Vérifier que c'est un sommet convexe
    if not _is_convex_vertex(prev_pt, curr_pt, next_pt, clockwise):
        return False

    # 2. Vérifier qu'aucun autre sommet n'est dans le triangle
    for i, vi in enumerate(polygon_indices):
        if i in (prev_idx, idx, next_idx):
            continue
        test_pt = vertices[vi]
        if _is_point_in_triangle(test_pt, prev_pt, curr_pt, next_pt):
            return False

    return True


def _ear_clipping(vertices: list[Point]) -> list[Triangle]:
    """Triangule un polygone simple avec l'algorithme Ear Clipping.

    Fonctionne pour les polygones convexes ET concaves.

    Args:
        vertices: Liste des sommets du polygone dans l'ordre.

    Returns:
        Liste des triangles (tuples d'indices).

    """
    n = len(vertices)
    if n < 3:
        return []

    # Créer une liste d'indices de travail
    polygon_indices = list(range(n))
    triangles: list[Triangle] = []

    # Déterminer l'orientation du polygone (horaire ou anti-horaire)
    clockwise = _polygon_area_signed(vertices) < 0

    # Boucle principale - on retire les oreilles une par une
    max_iterations = n * n  # Sécurité contre boucle infinie
    iteration = 0

    while len(polygon_indices) > 3 and iteration < max_iterations:
        iteration += 1
        ear_found = False

        for i in range(len(polygon_indices)):
            if _is_ear(polygon_indices, vertices, i, clockwise):
                # Trouver les indices des 3 sommets
                n_current = len(polygon_indices)
                prev_idx = (i - 1) % n_current
                next_idx = (i + 1) % n_current

                # Ajouter le triangle (avec les indices originaux)
                v_prev = polygon_indices[prev_idx]
                v_curr = polygon_indices[i]
                v_next = polygon_indices[next_idx]
                triangles.append((v_prev, v_curr, v_next))

                # Retirer le sommet courant du polygone
                polygon_indices.pop(i)
                ear_found = True
                break

        if not ear_found:
            # Aucune oreille trouvée - polygone dégénéré ou erreur
            break

    # Ajouter le dernier triangle (les 3 sommets restants)
    if len(polygon_indices) == 3:
        triangles.append((
            polygon_indices[0],
            polygon_indices[1],
            polygon_indices[2]
        ))

    return triangles


def compute_triangulation(
    points: list[Point]
) -> tuple[list[Point], list[Triangle]]:
    """Compute triangulation for a set of points using Ear Clipping.

    Utilise l'algorithme Ear Clipping qui fonctionne pour les polygones
    convexes ET concaves. Les points sont traités comme les sommets
    d'un polygone simple (non auto-intersectant).

    Gère les cas dégénérés (points alignés, doublons, moins de 3 points).

    Args:
        points: Une liste de tuples (x, y) représentant les sommets du polygone.

    Returns:
        Un tuple contenant:
        - La liste des vertices (les points utilisés, sans doublons).
        - La liste des triangles (tuples d'indices référençant les vertices).

    """
    # 1. Nettoyage : Supprimer les doublons tout en gardant l'ordre
    unique_points = list(dict.fromkeys(points))

    n = len(unique_points)

    # 2. Cas limites (moins de 3 points = pas de triangle)
    if n < 3:
        return unique_points, []

    # 3. Vérification globale : Si tous les points sont colinéaires
    all_collinear = True
    for i in range(2, n):
        if not _is_collinear(unique_points[0], unique_points[1], unique_points[i]):
            all_collinear = False
            break

    if all_collinear:
        return unique_points, []

    # 4. Appliquer l'algorithme Ear Clipping
    triangles = _ear_clipping(unique_points)

    return unique_points, triangles