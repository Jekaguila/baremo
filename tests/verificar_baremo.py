"""Verificaciones rápidas del banco y del baremo.  Ejecutar:  python tests/verificar_baremo.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import baremo as bm
from banco import AREAS, ORDEN_AREAS, PREGUNTAS, preguntas_de_area

# 1) estructura del banco: 4 áreas x 20 preguntas, 4 subcompetencias x 5, 4 opciones distintas
assert len(PREGUNTAS) == 80
for a in ORDEN_AREAS:
    assert len(preguntas_de_area(a)) == 20
    for sub in AREAS[a]["subs"]:
        assert sum(p["sub"] == sub for p in preguntas_de_area(a)) == 5
assert all(len(set(p["opciones"])) == 4 for p in PREGUNTAS)
assert len({p["id"] for p in PREGUNTAS}) == 80

# 2) niveles en los límites del baremo del documento (0-59 / 60-74 / 75-89 / 90-100)
cortes = [60, 75, 90]
for valor, esperado in [(0, "Insuficiente"), (59, "Insuficiente"), (60, "Básico"), (74, "Básico"),
                        (75, "Satisfactorio"), (89, "Satisfactorio"), (90, "Avanzado"), (100, "Avanzado")]:
    assert bm.nivel(valor, cortes) == esperado, (valor, esperado)

# 3) ejemplo ponderado del documento: 85/70/92/80 con pesos 30/25/30/15 = 82,60 -> Satisfactorio
g = bm.nota_global({"A1": 85, "A2": 70, "A3": 92, "A4": 80}, {"A1": 30, "A2": 25, "A3": 30, "A4": 15})
assert abs(g - 82.6) < 1e-9 and bm.nivel(g, cortes) == "Satisfactorio"

# 4) puntuación: todo correcto = 100 %; todo en blanco = 0 %
for a in ORDEN_AREAS:
    perfecto = {p["id"]: p["correcta"] for p in preguntas_de_area(a)}
    assert bm.resultado_area(a, perfecto)["pct"] == 100.0
    assert bm.resultado_area(a, {})["pct"] == 0.0

print("Todas las verificaciones pasaron.")
