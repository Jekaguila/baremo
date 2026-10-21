"""Persistencia en SQLite (sin servidor). Guarda estudiantes, intentos, respuestas y configuración.

Se guardan las respuestas CRUDAS; los puntajes y niveles se calculan al consultar con el baremo
vigente, de modo que si la docente ajusta los cortes o las ponderaciones, todo se recalcula.
"""
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

DB_PATH = Path(os.environ.get("BAREMOS_DB", Path(__file__).parent / "data" / "baremos.db"))

CONFIG_DEFECTO = {
    "cortes": [60, 75, 90],                       # Básico desde 60, Satisfactorio desde 75, Avanzado desde 90
    "pesos": {"A1": 25, "A2": 25, "A3": 25, "A4": 25},
    "minutos": 40,
    "modo_tiempo": "por_area",                    # "por_area" | "total"
    "mostrar_revision": False,                    # ¿el estudiante ve las respuestas correctas al terminar?
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    grupo TEXT DEFAULT '',
    creado REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS intentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id) ON DELETE CASCADE,
    area TEXT NOT NULL,
    inicio REAL NOT NULL,
    fin REAL,
    estado TEXT NOT NULL DEFAULT 'en_curso',      -- en_curso | finalizado | tiempo_agotado
    semilla INTEGER NOT NULL,
    version TEXT NOT NULL,
    UNIQUE (estudiante_id, area)
);
CREATE TABLE IF NOT EXISTS respuestas (
    intento_id INTEGER NOT NULL REFERENCES intentos(id) ON DELETE CASCADE,
    qid TEXT NOT NULL,
    opcion INTEGER NOT NULL,                      -- índice ORIGINAL de la opción elegida
    ts REAL NOT NULL,
    PRIMARY KEY (intento_id, qid)
);
CREATE TABLE IF NOT EXISTS config (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
"""


@contextmanager
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db():
    with _conn() as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)


# ------------------------------------------------------------------ configuración
def get_config():
    cfg = json.loads(json.dumps(CONFIG_DEFECTO))
    with _conn() as c:
        for r in c.execute("SELECT clave, valor FROM config"):
            try:
                cfg[r["clave"]] = json.loads(r["valor"])
            except json.JSONDecodeError:
                pass
    return cfg


def set_config(**kwargs):
    with _conn() as c:
        for k, v in kwargs.items():
            c.execute(
                "INSERT INTO config(clave, valor) VALUES (?, ?) "
                "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
                (k, json.dumps(v)),
            )


# ------------------------------------------------------------------ estudiantes
def upsert_estudiante(nombre, email, grupo=""):
    email = email.strip().lower()
    with _conn() as c:
        row = c.execute("SELECT id FROM estudiantes WHERE email = ?", (email,)).fetchone()
        if row:
            c.execute(
                "UPDATE estudiantes SET nombre = ?, grupo = ? WHERE id = ?",
                (nombre.strip(), grupo.strip(), row["id"]),
            )
            return row["id"]
        cur = c.execute(
            "INSERT INTO estudiantes(email, nombre, grupo, creado) VALUES (?, ?, ?, ?)",
            (email, nombre.strip(), grupo.strip(), time.time()),
        )
        return cur.lastrowid


def get_estudiante(est_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM estudiantes WHERE id = ?", (est_id,)).fetchone()
        return dict(r) if r else None


def borrar_estudiante(est_id):
    with _conn() as c:
        c.execute("DELETE FROM estudiantes WHERE id = ?", (est_id,))


def borrar_todo():
    with _conn() as c:
        c.execute("DELETE FROM respuestas")
        c.execute("DELETE FROM intentos")
        c.execute("DELETE FROM estudiantes")


# ------------------------------------------------------------------ intentos y respuestas
def get_intento(est_id, area):
    with _conn() as c:
        r = c.execute(
            "SELECT * FROM intentos WHERE estudiante_id = ? AND area = ?", (est_id, area)
        ).fetchone()
        return dict(r) if r else None


def intentos_de(est_id):
    with _conn() as c:
        return {r["area"]: dict(r) for r in c.execute(
            "SELECT * FROM intentos WHERE estudiante_id = ?", (est_id,))}


def borrar_intento(est_id, area):
    """Elimina el intento (y sus respuestas) para permitir que el estudiante repita el área."""
    with _conn() as c:
        c.execute("DELETE FROM intentos WHERE estudiante_id = ? AND area = ?", (est_id, area))


def crear_intento(est_id, area, semilla, version):
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO intentos(estudiante_id, area, inicio, semilla, version) "
            "VALUES (?, ?, ?, ?, ?)",
            (est_id, area, time.time(), semilla, version),
        )
    return get_intento(est_id, area)


def finalizar_intento(intento_id, estado="finalizado"):
    with _conn() as c:
        c.execute(
            "UPDATE intentos SET estado = ?, fin = ? WHERE id = ? AND estado = 'en_curso'",
            (estado, time.time(), intento_id),
        )


def guardar_respuesta(intento_id, qid, opcion):
    """Guarda (o reemplaza) la respuesta solo si el intento sigue en curso."""
    with _conn() as c:
        c.execute(
            "INSERT INTO respuestas(intento_id, qid, opcion, ts) "
            "SELECT ?, ?, ?, ? WHERE EXISTS "
            "(SELECT 1 FROM intentos WHERE id = ? AND estado = 'en_curso') "
            "ON CONFLICT(intento_id, qid) DO UPDATE SET opcion = excluded.opcion, ts = excluded.ts",
            (intento_id, qid, int(opcion), time.time(), intento_id),
        )


def cargar_respuestas(intento_id):
    with _conn() as c:
        return {r["qid"]: r["opcion"] for r in c.execute(
            "SELECT qid, opcion FROM respuestas WHERE intento_id = ?", (intento_id,))}


# ------------------------------------------------------------------ lecturas masivas (pandas)
def df_estudiantes():
    with _conn() as c:
        return pd.read_sql_query("SELECT * FROM estudiantes ORDER BY nombre", c)


def df_intentos():
    with _conn() as c:
        return pd.read_sql_query("SELECT * FROM intentos", c)


def df_respuestas():
    with _conn() as c:
        return pd.read_sql_query("SELECT * FROM respuestas", c)
