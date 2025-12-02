SHELL := /bin/bash

.PHONY: help
help:
	@echo "Commandes disponibles:"
	@echo "  make install     Installe les dépendances (normales et dev)"
	@echo "  make test        Lance TOUS les tests (unit + perf)"
	@echo "  make unit_test   Lance les tests unitaires (SAUF performance)"
	@echo "  make perf_test   Lance UNIQUEMENT les tests de performance"
	@echo "  make coverage    Calcule la couverture de code des tests unitaires"
	@echo "  make lint        Vérifie la qualité du code avec ruff"
	@echo "  make doc         Génère la documentation HTML avec pdoc3"

.PHONY: install
install:
	pip install -r requirements.txt
	pip install -r dev_requirements.txt

#lance tous les tests
.PHONY: test
test:
	pytest tests/

#lance les tests sauf ceux marqués @pytest.mark.perf
.PHONY: unit_test
unit_test:
	pytest tests/ -m "not perf"

#lance les tests marqués @pytest.mark.perf
.PHONY: perf_test
perf_test:
	pytest tests/ -m perf

#calcule la couverture de code (uniquement sur les tests unitaire)
.PHONY: coverage
coverage:
	coverage run -m pytest tests/ -m "not perf"
	coverage report -m

#vérifie la qualité du code
.PHONY: lint
lint:
	ruff check triangulator/ tests/

#génére la doc html
.PHONY: doc
doc:
	pdoc3 --html triangulator/ -o docs/

#nettoyer les fichiers générés
.PHONY: clean
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf docs/
	find . -type d -name "__pycache__" -exec rm -rf {} +