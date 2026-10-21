"""Lógica del baremo: puntuación, niveles de desempeño, ponderación global y retroalimentación.

El baremo sigue el modelo del documento BAREMOS.docx:
    0–59 Insuficiente · 60–74 Básico · 75–89 Satisfactorio · 90–100 Avanzado
y la nota global es un promedio ponderado:  N = Σ (peso_i × puntaje_i).
"""
import numpy as np
import pandas as pd

from banco import AREAS, ORDEN_AREAS, PREGUNTAS_POR_ID, preguntas_de_area

NIVELES = ["Insuficiente", "Básico", "Satisfactorio", "Avanzado"]

COLORES = {
    "Insuficiente": "#B5473A",
    "Básico": "#D9A441",
    "Satisfactorio": "#4C9A8B",
    "Avanzado": "#2B5FA5",
    "Pendiente": "#9AA5B1",
}

# Descriptores tomados del documento BAREMOS.docx
DESCRIPTORES = {
    "Insuficiente": "Presenta dificultades importantes en el cumplimiento de los criterios.",
    "Básico": "Cumple parcialmente los requisitos y necesita mejoras.",
    "Satisfactorio": "Demuestra un desempeño adecuado en la mayoría de los criterios.",
    "Avanzado": "Demuestra un desempeño sólido, fundamentado y consistente.",
}


# ---------------------------------------------------------------------------- niveles
def nivel(pct, cortes):
    """Convierte un porcentaje (0–100) en nivel de desempeño según los 3 cortes."""
    if pct is None or (isinstance(pct, float) and np.isnan(pct)):
        return "Pendiente"
    c1, c2, c3 = cortes
    if pct < c1:
        return "Insuficiente"
    if pct < c2:
        return "Básico"
    if pct < c3:
        return "Satisfactorio"
    return "Avanzado"


def rangos_texto(cortes):
    c1, c2, c3 = cortes
    return {
        "Insuficiente": f"0 – {c1 - 1}",
        "Básico": f"{c1} – {c2 - 1}",
        "Satisfactorio": f"{c2} – {c3 - 1}",
        "Avanzado": f"{c3} – 100",
    }


def tabla_baremo(cortes):
    r = rangos_texto(cortes)
    return pd.DataFrame(
        {"Rango (%)": [r[n] for n in NIVELES], "Nivel": NIVELES,
         "Descriptor": [DESCRIPTORES[n] for n in NIVELES]}
    )


# ---------------------------------------------------------------------------- puntuación
def puntuar_item(p, opcion):
    """1.0 mejor opción · 0.5 opción parcial · 0.0 en otro caso (o sin responder)."""
    if opcion is None:
        return 0.0
    if opcion == p["correcta"]:
        return 1.0
    if opcion in p["parciales"]:
        return 0.5
    return 0.0


def resultado_area(area, respuestas):
    """Resultado de un área a partir de {qid: opción_original}."""
    qs = preguntas_de_area(area)
    subs = {s: {"puntos": 0.0, "max": 0, "respondidas": 0} for s in AREAS[area]["subs"]}
    for p in qs:
        op = respuestas.get(p["id"])
        subs[p["sub"]]["puntos"] += puntuar_item(p, op)
        subs[p["sub"]]["max"] += 1
        subs[p["sub"]]["respondidas"] += op is not None
    for s in subs.values():
        s["pct"] = 100.0 * s["puntos"] / s["max"]
    puntos = sum(s["puntos"] for s in subs.values())
    maximo = sum(s["max"] for s in subs.values())
    return {
        "puntos": puntos,
        "max": maximo,
        "pct": 100.0 * puntos / maximo,
        "respondidas": sum(s["respondidas"] for s in subs.values()),
        "subs": subs,
    }


def nota_global(pcts_por_area, pesos):
    """Promedio ponderado de los porcentajes por área. Devuelve None si falta alguna."""
    if any(pcts_por_area.get(a) is None or pd.isna(pcts_por_area.get(a)) for a in ORDEN_AREAS):
        return None
    total_peso = sum(pesos[a] for a in ORDEN_AREAS)
    return sum(pesos[a] * pcts_por_area[a] for a in ORDEN_AREAS) / total_peso


def revision_item(area, respuestas):
    """Filas para la revisión de respuestas (correcta / elegida / explicación)."""
    filas = []
    for i, p in enumerate(preguntas_de_area(area), start=1):
        op = respuestas.get(p["id"])
        filas.append({
            "N.º": i,
            "Subcompetencia": AREAS[area]["subs"][p["sub"]],
            "Pregunta": p["enunciado"],
            "Tu respuesta": p["opciones"][op] if op is not None else "(sin responder)",
            "Respuesta esperada": p["opciones"][p["correcta"]],
            "Puntos": puntuar_item(p, op),
            "Explicación": p["explicacion"],
        })
    return filas


# ---------------------------------------------------------------------------- retroalimentación
RETRO_AREA = {
    "A1": {
        "Insuficiente": "Tu resultado sugiere dificultades importantes para extraer ideas de textos académicos, redactar con corrección o seguir indicaciones de varios pasos. Prioriza la lectura guiada, la paráfrasis de cada párrafo y la verificación de cada condición antes de responder.",
        "Básico": "Identificas ideas explícitas, pero aún necesitas fortalecer la inferencia, la revisión de tus escritos o la atención a todas las condiciones de una indicación.",
        "Satisfactorio": "Comprendes y comunicas adecuadamente en la mayoría de las situaciones. Para llegar al nivel avanzado, practica la lectura crítica de argumentos y la revisión final de tus textos.",
        "Avanzado": "Demuestras una lectura sólida, una escritura cuidada y un seguimiento riguroso de las indicaciones. Puedes ser modelo de comunicación académica para tus estudiantes.",
    },
    "A2": {
        "Insuficiente": "En situaciones profesionales reales tiendes a elegir respuestas que no equilibran los criterios, las personas y las consecuencias. Conviene trabajar el análisis de casos, la comunicación asertiva y la planificación personal.",
        "Básico": "Muestras criterio en varias situaciones, pero a veces eliges respuestas parciales (por ejemplo, resolver el plazo sin atender la causa). Fortalece el diagnóstico antes de actuar.",
        "Satisfactorio": "Tomas decisiones razonadas y respetuosas en la mayoría de las situaciones. Afina los casos más complejos de ética digital y de gestión de la carga.",
        "Avanzado": "Demuestras un criterio sólido y consistente: contrastas evidencia, comunicas con asertividad, gestionas tu tiempo y actúas con ética digital.",
    },
    "A3": {
        "Insuficiente": "Es necesario reforzar los fundamentos de la informática educativa (modelos, diseño y evaluación de recursos, integración curricular). Un repaso guiado con ejemplos de tu práctica te ayudará a consolidarlos.",
        "Básico": "Dominas parte de los conceptos y modelos, pero aún confundes algunos criterios de diseño, evaluación o integración. Revisa los temas señalados abajo.",
        "Satisfactorio": "Muestras un dominio adecuado de la informática educativa. Profundiza en las tecnologías emergentes y en los criterios de alineación y evaluación para alcanzar el nivel avanzado.",
        "Avanzado": "Demuestras un dominio sólido y fundamentado de la informática educativa, con criterio para elegir, diseñar y evaluar recursos y entornos digitales.",
    },
    "A4": {
        "Insuficiente": "Se recomienda reforzar el manejo de Moodle y los fundamentos de la educación en línea. Practica en un curso de prueba la configuración de roles, actividades, calificador y restricciones.",
        "Básico": "Manejas las funciones básicas de Moodle y de la educación en línea, pero necesitas más práctica en configuración avanzada, diseño instruccional o evaluación en línea.",
        "Satisfactorio": "Muestras un buen desarrollo de las competencias de la especialización. Afina los aspectos señalados para llegar a un manejo experto.",
        "Avanzado": "Demuestras un dominio sólido de Moodle, del diseño y la facilitación de cursos en línea y de la evaluación e integridad académica.",
    },
}

RETRO_SUB = {
    "lectura_literal": "Practica la lectura activa: subraya la idea principal de cada párrafo y parafraséala antes de responder.",
    "lectura_inferencial": "Ejercita la inferencia: pregúntate qué afirma el autor, qué da por supuesto y qué evidencia presenta.",
    "escritura": "Revisa ortografía, puntuación y conectores con una lista de cotejo antes de enviar cualquier texto.",
    "indicaciones": "Antes de responder, enumera cada condición de la indicación y verifica una a una que tu entrega las cumple.",
    "pensamiento_critico": "Antes de aceptar una afirmación, contrasta la fuente, los datos y las explicaciones alternativas.",
    "comunicacion": "Usa la fórmula asertiva: hecho concreto + efecto + petición clara + apertura al diálogo.",
    "autogestion": "Planifica la semana con la matriz urgente/importante y reserva bloques de estudio y de descanso.",
    "etica_digital": "Repasa licencias abiertas, protección de datos de estudiantes y buenas prácticas de uso de IA.",
    "fundamentos": "Repasa TPACK, SAMR, ADDIE y las teorías del aprendizaje con ejemplos de tus propias clases.",
    "diseno_evaluacion": "Revisa Bloom, DUA, accesibilidad (WCAG), licencias Creative Commons y tipos de rúbricas.",
    "tecnologias": "Explora gamificación, analítica del aprendizaje, REA, estándares (SCORM/xAPI) y los riesgos de la IA generativa.",
    "integracion": "Fortalece la alineación constructiva, los tipos de evaluación y la protección de datos al integrar TIC.",
    "moodle_gestion": "Practica en un curso de prueba: roles, matriculación, grupos, restricciones de acceso y copias de seguridad.",
    "moodle_actividades": "Repasa foros, tareas, cuestionarios, talleres y el calificador (categorías y agregación).",
    "diseno_linea": "Revisa los modelos CoI y de Salmon, la carga cognitiva y las estrategias de tutoría en línea.",
    "evaluacion_linea": "Practica rúbricas, retroalimentación formativa y estrategias de integridad académica en línea.",
}

RETRO_GLOBAL = {
    "Insuficiente": "Hay brechas importantes en varias competencias. Se recomienda un plan de refuerzo guiado, comenzando por las áreas con menor puntaje.",
    "Básico": "Con un refuerzo dirigido a las áreas más bajas puedes alcanzar el nivel satisfactorio.",
    "Satisfactorio": "Enfoca tu práctica en las subcompetencias señaladas para alcanzar el nivel avanzado.",
    "Avanzado": "Puedes compartir tu experiencia apoyando a otras personas en las áreas donde necesiten refuerzo.",
}

AVISO = ("Resultado diagnóstico de la prueba piloto. Orienta el refuerzo y la mejora del curso; "
         "no constituye una calificación oficial.")


def retro_subs(area, res_area, cortes):
    """(fortalezas, por_mejorar) a partir de los resultados por subcompetencia."""
    fuertes, mejorar = [], []
    for sub, r in res_area["subs"].items():
        nom = AREAS[area]["subs"][sub]
        if r["pct"] >= cortes[1]:
            fuertes.append((nom, r["pct"]))
        else:
            mejorar.append((nom, r["pct"], RETRO_SUB[sub]))
    return fuertes, mejorar


# ---------------------------------------------------------------------------- tablas masivas
def calcular_todo(df_est, df_int, df_resp, cfg):
    """Devuelve (resumen_por_estudiante, subcompetencias_en_formato_largo)."""
    cortes, pesos = cfg["cortes"], cfg["pesos"]
    resp_por_intento = {
        iid: dict(zip(g["qid"], g["opcion"])) for iid, g in df_resp.groupby("intento_id")
    } if len(df_resp) else {}
    cerrados = df_int[df_int["estado"] != "en_curso"] if len(df_int) else df_int
    filas, largo = [], []
    for e in df_est.itertuples():
        fila = {"id": e.id, "nombre": e.nombre, "email": e.email, "grupo": e.grupo}
        pcts = {}
        ints = cerrados[cerrados["estudiante_id"] == e.id] if len(cerrados) else cerrados
        en_curso = df_int[(df_int["estudiante_id"] == e.id) & (df_int["estado"] == "en_curso")] \
            if len(df_int) else df_int
        for a in ORDEN_AREAS:
            fila_a = ints[ints["area"] == a] if len(ints) else ints
            if len(fila_a):
                it = fila_a.iloc[0]
                r = resultado_area(a, resp_por_intento.get(it["id"], {}))
                pcts[a] = r["pct"]
                fila[a] = round(r["pct"], 1)
                fila[f"{a}_nivel"] = nivel(r["pct"], cortes)
                fila[f"{a}_min"] = round((it["fin"] - it["inicio"]) / 60.0, 1)
                fila[f"{a}_estado"] = it["estado"]
                for s, rs in r["subs"].items():
                    largo.append({"id": e.id, "area": a, "sub": s,
                                  "subcompetencia": AREAS[a]["subs"][s], "pct": rs["pct"]})
            else:
                pcts[a] = None
                fila[a] = np.nan
                fila[f"{a}_nivel"] = "Pendiente"
                fila[f"{a}_min"] = np.nan
                fila[f"{a}_estado"] = "en_curso" if (len(en_curso) and (en_curso["area"] == a).any()) else "pendiente"
        g = nota_global(pcts, pesos)
        fila["completadas"] = sum(1 for a in ORDEN_AREAS if pcts[a] is not None)
        fila["global"] = round(g, 1) if g is not None else np.nan
        fila["nivel_global"] = nivel(g, cortes) if g is not None else "Pendiente"
        filas.append(fila)
    return pd.DataFrame(filas), pd.DataFrame(largo)
