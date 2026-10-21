"""Análisis estadístico del piloto: análisis de ítems, confiabilidad, perfiles (scikit-learn) y percentiles."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from banco import AREAS, ORDEN_AREAS, preguntas_de_area
from baremo import puntuar_item

LETRAS = "ABCD"


def matrices_area(df_int, df_resp, area):
    """(opciones elegidas, puntajes) por intento cerrado. NaN en opciones = sin responder."""
    if len(df_int) == 0:
        return None, None
    cerrados = df_int[(df_int["area"] == area) & (df_int["estado"] != "en_curso")]
    if len(cerrados) == 0:
        return None, None
    qs = preguntas_de_area(area)
    ids = [q["id"] for q in qs]
    resp = df_resp[df_resp["intento_id"].isin(cerrados["id"])] if len(df_resp) else df_resp
    if len(resp):
        elegidas = resp.pivot(index="intento_id", columns="qid", values="opcion")
    else:
        elegidas = pd.DataFrame(index=cerrados["id"])
    elegidas = elegidas.reindex(index=cerrados["id"], columns=ids)
    puntos = elegidas.copy().astype(float)
    for q in qs:
        puntos[q["id"]] = elegidas[q["id"]].map(
            lambda v, q=q: puntuar_item(q, None if pd.isna(v) else int(v))
        )
    return elegidas, puntos


def alfa_cronbach(puntos):
    """Alfa de Cronbach (equivale a KR-20 con ítems 0/1). NaN si no es calculable."""
    if puntos is None or len(puntos) < 5:
        return np.nan
    k = puntos.shape[1]
    var_items = puntos.var(axis=0, ddof=1).sum()
    var_total = puntos.sum(axis=1).var(ddof=1)
    if not var_total or np.isnan(var_total) or var_total == 0:
        return np.nan
    return float(k / (k - 1) * (1 - var_items / var_total))


def analisis_items(df_int, df_resp, area):
    """Dificultad, discriminación y análisis de distractores de las 20 preguntas de un área."""
    elegidas, puntos = matrices_area(df_int, df_resp, area)
    if puntos is None:
        return pd.DataFrame(), np.nan, 0
    n = len(puntos)
    total = puntos.sum(axis=1)
    filas = []
    for q in preguntas_de_area(area):
        s = puntos[q["id"]]
        resto = total - s
        if n >= 5 and s.std(ddof=0) > 0 and resto.std(ddof=0) > 0:
            disc = float(np.corrcoef(s, resto)[0, 1])
        else:
            disc = np.nan
        dif = float(s.mean())
        sin = float(elegidas[q["id"]].isna().mean() * 100)
        dist = {}
        for i, letra in enumerate(LETRAS):
            dist[f"% opción {i + 1}"] = float((elegidas[q["id"]] == i).mean() * 100)
        # distractor más elegido (entre las opciones que no son la mejor)
        otros = {i: dist[f"% opción {i + 1}"] for i in range(4) if i != q["correcta"]}
        top_i = max(otros, key=otros.get)
        alertas = []
        if n >= 5:
            if dif < 0.20:
                alertas.append("Muy difícil")
            if dif > 0.90:
                alertas.append("Muy fácil")
            if not np.isnan(disc) and disc < 0:
                alertas.append("Discriminación negativa: revisar clave o enunciado")
            elif not np.isnan(disc) and disc < 0.15:
                alertas.append("Baja discriminación")
            if sin > 20:
                alertas.append("Muchas omisiones")
        filas.append({
            "ID": q["id"],
            "Subcompetencia": AREAS[area]["subs"][q["sub"]],
            "Pregunta": q["enunciado"],
            "Dificultad (0–1)": round(dif, 2),
            "Discriminación": round(disc, 2) if not np.isnan(disc) else np.nan,
            "% sin responder": round(sin, 1),
            "% eligió la mejor": round(dist[f"% opción {q['correcta'] + 1}"], 1),
            "Distractor más elegido": f"{q['opciones'][top_i][:70]} ({otros[top_i]:.0f} %)" if n else "",
            "Alerta": "; ".join(alertas),
        })
    return pd.DataFrame(filas), alfa_cronbach(puntos), n


def correlaciones(df_res):
    completos = df_res[df_res["completadas"] == 4]
    if len(completos) < 4:
        return None
    return completos[ORDEN_AREAS].astype(float).corr()


def perfiles_kmeans(df_res, k=3, semilla=42):
    """Agrupa a quienes completaron las 4 áreas por su perfil de desempeño.

    Devuelve (df_con_perfil, centroides_en_porcentaje, silueta) o None si no hay datos suficientes.
    """
    completos = df_res[df_res["completadas"] == 4].copy()
    n = len(completos)
    if n < max(6, k + 2):
        return None
    X = completos[ORDEN_AREAS].astype(float).to_numpy()
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, n_init=10, random_state=semilla).fit(Xs)
    completos["_c"] = km.labels_
    medias = completos.groupby("_c")[ORDEN_AREAS].mean()
    medias["_global"] = medias.mean(axis=1)
    orden = medias["_global"].sort_values(ascending=False).index.tolist()
    nombres = {}
    for rango, c in enumerate(orden, start=1):
        nombres[c] = f"Perfil {rango}"
    completos["perfil"] = completos["_c"].map(nombres)
    cent = medias.drop(columns="_global").rename(index=nombres).sort_index()
    cent["n"] = completos.groupby("perfil").size()
    sil = float(silhouette_score(Xs, km.labels_)) if 1 < len(set(km.labels_)) < n else np.nan
    return completos.drop(columns="_c"), cent, sil


def percentil(valor, serie, minimo=5):
    s = pd.Series(serie).dropna().astype(float)
    if len(s) < minimo or valor is None or pd.isna(valor):
        return None
    return float(100.0 * ((s < valor).sum() + 0.5 * (s == valor).sum()) / len(s))


def tabla_percentiles(df_res):
    cols = ORDEN_AREAS + ["global"]
    qs = [10, 25, 50, 75, 90]
    out = {}
    for c in cols:
        s = df_res[c].dropna().astype(float)
        out[c] = [float(np.percentile(s, q)) if len(s) else np.nan for q in qs]
    t = pd.DataFrame(out, index=[f"P{q}" for q in qs]).round(1)
    t.columns = [AREAS[c]["corto"] if c in AREAS else "Global" for c in cols]
    return t
