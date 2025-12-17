# RETEX - Retour d'Expérience

## Résumé du Projet

**Résultats finaux :**
- 48 tests passent
- 92% de couverture de code
- 0 erreur ruff (linting)
- Documentation générée avec pdoc3

---

## Ce qui a été bien fait

### 1. Plan de test structuré (PLAN.md)

La rédaction d'un plan de test **avant** de coder a été très bénéfique :
- Organisation claire en 4 catégories (Unitaires, API, Performance, Qualité)
- Identification anticipée des cas limites (0 points, points colinéaires, doublons)
- Facilité à suivre la progression

### 2. Séparation des responsabilités

L'architecture en modules distincts a facilité les tests :

| Module | Responsabilité | Testabilité |
|--------|---------------|-------------|
| `core.py` | Algorithme pur | Très facile (pas de dépendances) |
| `binary_utils.py` | Sérialisation | Facile (entrée/sortie bien définies) |
| `manager_client.py` | Client HTTP | Mock du réseau |
| `app.py` | Routage Flask | Mock des autres modules |

### 3. Utilisation du mocking

Le mocking a permis de :
- Tester `manager_client.py` sans serveur réel
- Tester `app.py` en isolant chaque composant
- Simuler des erreurs (404, 503, timeout) de manière déterministe

### 4. Tests des cas d'erreur

Bonne couverture des scénarios d'échec :
- Données binaires corrompues
- Header trop court
- Réseau indisponible
- PointSet non trouvé

---

## Ce qui aurait pu être mieux fait

### 1. Algorithme initial trop simpliste

**Problème :** J'ai d'abord implémenté **Fan Triangulation**, qui ne fonctionne que pour les polygones convexes.

**Conséquence :** J'ai dû réécrire entièrement `core.py` avec l'algorithme **Ear Clipping** pour supporter les formes concaves.

**Leçon :** Mieux analyser les spécifications au départ. La question "Le polygone peut-il être concave ?" aurait dû être posée immédiatement.

### 2. Tests de performance mal dimensionnés

**Problème :** Les tests de performance utilisaient 10 000 et 100 000 points, adaptés à Fan Triangulation O(n) mais beaucoup trop lents pour Ear Clipping O(n²).

**Conséquence :** Tests qui timeout ou prennent plusieurs minutes.

**Leçon :** Les tests de performance doivent être adaptés à la complexité algorithmique.

### 3. Couverture initiale insuffisante sur manager_client.py

**Problème :** Ce module n'avait que 33% de couverture au début car il nécessite du mocking plus avancé.

**Conséquence :** Des bugs potentiels non détectés dans la gestion des erreurs réseau.

**Leçon :** Ne pas négliger les modules "plomberie" qui gèrent les I/O.

### 4. Erreurs ruff ignorées trop longtemps

**Problème :** plus de 100 erreurs ruff accumulées (docstrings, imports, types).

**Conséquence :** Correction en masse à la fin au lieu d'au fur et à mesure.

**Leçon :** Intégrer le linting dans le workflow dès le début (pre-commit hook).

### 5. Poser des questions au prof pour bien comprendre ce qu'on doit faire dès le début

---

## Ce que je ferais différemment

### 1. Commencer par les tests des cas concaves

Si je refaisais le projet, j'écrirais d'abord :

```python
def test_triangulation_forme_L():
    """Forme en L (concave) -> doit produire des triangles valides."""
    points = [(0,0), (2,0), (2,1), (1,1), (1,2), (0,2)]
    vertices, triangles = compute_triangulation(points)
    assert len(triangles) == 4  # 6 sommets - 2
```

Ce test aurait **échoué immédiatement** avec Fan Triangulation et m'aurait orienté vers Ear Clipping dès le départ.

### 2. Configurer ruff + pre-commit dès le jour 1

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
```

### 3. Utiliser des fixtures pytest plus tôt

Au lieu de répéter les données de test dans chaque fichier :

```python
# conftest.py
@pytest.fixture
def sample_square_points():
    return [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

@pytest.fixture
def sample_binary_pointset():
    return struct.pack("!I", 4) + struct.pack("!ff", 0.0, 0.0) + ...
```

### 4. Documenter le format binaire plus clairement

Créer un schéma visuel du format binaire dès le début aurait aidé :

```
PointSet:
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  count (4B) │  x1,y1 (8B) │  x2,y2 (8B) │     ...     │
│     !I      │     !ff     │     !ff     │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```
---

## Évaluation du plan initial

### Points positifs du PLAN.md

| Aspect | Évaluation |
|--------|------------|
| Structure en catégories |  Excellente |
| Identification des cas limites |  Complète |
| Nommage des tests |  Descriptif |
| Couverture des erreurs HTTP |  Exhaustive |

### Points à améliorer

| Aspect | Problème |
|--------|----------|
| Pas de tests concaves |  Oubli critique |
| Pas de complexité algorithmique |  Performance non anticipée |
| Pas de tests d'intégration E2E |  Manque optionnel |

---

##  Leçons apprises

1. **Test-First fonctionne** : Écrire les tests avant le code aide à clarifier les spécifications et évite les régressions.

2. **Le mocking est indispensable** : Sans mock, impossible de tester les interactions réseau de manière fiable.

3. **La couverture n'est pas tout** : 100% de couverture ne garantit pas l'absence de bugs (ex: algorithme incorrect mais couvert).

4. **L'architecture impacte la testabilité** : Des modules bien séparés = des tests plus simples.

5. **Les outils de qualité (ruff, coverage) doivent être intégrés tôt** : Corriger 125 erreurs à la fin est pénible.

6. **Ne pas hésiter à poser des questions au prof**
---

## Conclusion

Ce projet m'a permis de pratiquer concrètement l'approche **Test-First** et de comprendre l'importance de :
- Bien analyser les spécifications avant de coder
- Écrire des tests pour les cas nominaux ET les cas d'erreur
- Utiliser le mocking pour isoler les dépendances externes
- Maintenir la qualité du code tout au long du développement

Le principal regret est de ne pas avoir anticipé le support des polygones concaves, ce qui a nécessité une réécriture majeure. Mais cette erreur m'a appris que les **tests doivent couvrir les cas métier complexes**, pas seulement les cas techniques.
