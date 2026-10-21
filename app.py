"""Baremo de competencias · Informática Educativa (prueba piloto).

Aplicación Streamlit: el estudiante rinde 4 evaluaciones de 20 preguntas y obtiene un panel con su
nivel de desempeño según el baremo; el docente accede con contraseña al panel de análisis.

Ejecutar:  streamlit run app.py
"""
import os
import random
import re
import time

import streamlit as st
import streamlit.components.v1 as components

import baremo as bm
import db
import graficos as gr
import informes
from banco import AREAS, BANCO_VERSION, ORDEN_AREAS, TEXTOS, paginas_de_area, preguntas_de_area

st.set_page_config(
    page_title="Baremo de competencias · Informática Educativa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
  html, body, .stApp { font-size: 18px; }
  .block-container { padding-top: 2.2rem; max-width: 1100px; }
  h1 { font-size: 2.1rem !important; color: #1F3A5F; }
  h2, h3 { color: #1F3A5F; }
  div[role="radiogroup"] label p { font-size: 1.05rem; line-height: 1.5; }
  div[role="radiogroup"] { gap: 0.35rem; }
  .pregunta { font-size: 1.12rem; font-weight: 600; margin: 1.1rem 0 0.2rem 0; color: #1F2933; }
  .lectura { background: #F4F7FB; border-left: 5px solid #2B5FA5; padding: 1rem 1.3rem; border-radius: 6px;
             font-size: 1.05rem; line-height: 1.65; margin-bottom: 0.8rem; }
  .reloj { font-size: 1.9rem; font-weight: 700; text-align: center; padding: 0.35rem 0.6rem;
           border-radius: 10px; background: #E8EEF6; color: #1F3A5F; }
  .reloj.alerta { background: #F8E1DE; color: #9E2F22; }
  .area-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin: 0.8rem 0 1rem 0; }
  .area-card { border: 1px solid #D5DCE4; border-radius: 10px; padding: 12px 14px; background: #fff; }
  .area-card .ico { font-size: 1.6rem; line-height: 1.2; }
  .area-card .nom { font-weight: 700; color: #1F2933; margin-top: 2px; }
  .area-card .cnt { color: #6B7785; font-size: 0.9rem; }
  .tarjeta-meta { color: #4A5568; font-size: 0.95rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

db.init_db()
ss = st.session_state
ss.setdefault("est_id", None)
ss.setdefault("vista", "registro")
ss.setdefault("area_actual", None)
ss.setdefault("pagina", 0)
ss.setdefault("confirmar_inicio", None)
ss.setdefault("confirmar_envio", False)
ss.setdefault("es_docente", False)
ss.setdefault("aviso", None)
ss.setdefault("scroll_top", False)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LETRAS = "ABCD"


# =============================================================================== utilidades
def password_docente():
    try:
        v = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        v = None
    return v or os.environ.get("ADMIN_PASSWORD")


def limite_intento(intento, intentos_est, cfg):
    """Instante (epoch) en que vence el intento según el modo de tiempo configurado."""
    dur = cfg["minutos"] * 60
    if cfg["modo_tiempo"] == "total":
        return min(i["inicio"] for i in intentos_est.values()) + dur
    return intento["inicio"] + dur


def cerrar_vencidos(est_id, cfg):
    """Cierra automáticamente los intentos en curso cuyo tiempo ya venció."""
    ints = db.intentos_de(est_id)
    cerrados = []
    for a, it in ints.items():
        if it["estado"] == "en_curso" and time.time() >= limite_intento(it, ints, cfg):
            db.finalizar_intento(it["id"], "tiempo_agotado")
            cerrados.append(a)
    return cerrados


def tiempo_total_agotado(intentos_est, cfg):
    if cfg["modo_tiempo"] != "total" or not intentos_est:
        return False
    return time.time() >= min(i["inicio"] for i in intentos_est.values()) + cfg["minutos"] * 60


def mmss(segundos):
    segundos = max(0, int(segundos))
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


def ir(vista, **kw):
    ss.vista = vista
    ss.scroll_top = True
    for k, v in kw.items():
        ss[k] = v


def cambiar_pagina(n):
    ss.pagina = n
    ss.confirmar_envio = False
    ss.scroll_top = True


JS_SCROLL = """
function up(){try{const d=window.parent.document;
  const el=d.querySelector('[data-testid="stMain"]')||d.querySelector('section.main');
  if(el){el.scrollTop=0;} window.parent.scrollTo(0,0);}catch(e){}}
up(); [100,300,700].forEach(t=>setTimeout(up,t));
"""


def scroll_arriba():
    """Devuelve la vista al inicio tras un cambio de pantalla (Streamlit conserva el scroll)."""
    if ss.get("scroll_top"):
        ss.scroll_top = False
        ss.scroll_n = ss.get("scroll_n", 0) + 1   # contenido distinto => el iframe se vuelve a montar
        components.html("<script>/* " + str(ss.scroll_n) + " */" + JS_SCROLL + "</script>", height=0)


def cerrar_sesion():
    for k in ("est_id", "area_actual", "confirmar_inicio", "confirmar_envio", "aviso"):
        ss[k] = None if k != "confirmar_envio" else False
    ss.vista = "registro"
    ss.pagina = 0


def resultados_estudiante(est_id, cfg):
    """({area: resultado}, nota_global | None) solo con las áreas ya cerradas."""
    ints = db.intentos_de(est_id)
    res = {}
    for a in ORDEN_AREAS:
        it = ints.get(a)
        if it and it["estado"] != "en_curso":
            res[a] = bm.resultado_area(a, db.cargar_respuestas(it["id"]))
    g = bm.nota_global({a: (res[a]["pct"] if a in res else None) for a in ORDEN_AREAS}, cfg["pesos"])
    return res, g


# =============================================================================== registro
def form_docente(prefijo):
    clave = password_docente()
    if not clave:
        st.info("Define la variable ADMIN_PASSWORD (en los secretos de la app) para habilitar el panel docente.")
        return
    pw = st.text_input("Contraseña", type="password", key=f"pw_doc_{prefijo}")
    if st.button("Entrar", key=f"btn_doc_{prefijo}"):
        if pw == clave:
            ss.es_docente = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")


def vista_registro():
    cfg = db.get_config()
    st.title("🎓 Baremo de competencias")
    st.markdown("##### Egresados de la Licenciatura en Informática Educativa · Especialización en Entornos Virtuales de Aprendizaje")
    st.write(
        "Esta **prueba piloto** diagnostica tus competencias en cuatro áreas. "
        "Al terminar verás un panel con tu nivel de desempeño y recomendaciones para fortalecerte."
    )
    tarjetas = "".join(
        f"<div class='area-card'><div class='ico'>{AREAS[a]['icono']}</div>"
        f"<div class='nom'>{AREAS[a]['corto']}</div><div class='cnt'>20 preguntas</div></div>"
        for a in ORDEN_AREAS
    )
    st.markdown(f"<div class='area-grid'>{tarjetas}</div>", unsafe_allow_html=True)
    tiempo = (f"**{cfg['minutos']} minutos por evaluación** (el reloj comienza cuando inicias cada una)."
              if cfg["modo_tiempo"] == "por_area"
              else f"**{cfg['minutos']} minutos en total** para las cuatro evaluaciones (el reloj comienza al iniciar la primera).")
    st.info(
        f"⏱️ Tiempo: {tiempo}  \n"
        "✅ Puedes hacer las evaluaciones en el orden que prefieras. Tus respuestas se guardan automáticamente.  \n"
        "🔁 Si se cierra la página, vuelve a ingresar con el mismo correo: continuarás donde quedaste y el reloj **no se reinicia**."
    )
    with st.form("registro"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico", help="Es tu identificador; usa el mismo si necesitas volver a entrar.")
        grupo = st.text_input("Cohorte o grupo (opcional)")
        acepto = st.checkbox(
            "Entiendo que se trata de una prueba piloto con fines de diagnóstico y mejora del curso, "
            "y autorizo el uso de mis resultados para ese propósito."
        )
        ok = st.form_submit_button("Comenzar", type="primary", width="stretch")
    if ok:
        if len(nombre.strip().split()) < 2:
            st.error("Escribe tu nombre completo (nombre y apellido).")
        elif not EMAIL_RE.match(email.strip()):
            st.error("Escribe un correo electrónico válido.")
        elif not acepto:
            st.error("Debes aceptar la autorización para continuar.")
        else:
            ss.est_id = db.upsert_estudiante(nombre, email, grupo)
            ir("panel")
            st.rerun()
    st.write("")
    with st.expander("🔒 Acceso docente"):
        form_docente("reg")


# =============================================================================== panel del estudiante
def iniciar_area(area):
    est_id = ss.est_id
    db.crear_intento(est_id, area, random.randint(1, 2**31 - 1), BANCO_VERSION)
    ss.area_actual = area
    ss.pagina = 0
    ss.confirmar_inicio = None
    ss.confirmar_envio = False
    ir("prueba")


def continuar_area(area):
    ss.area_actual = area
    ss.pagina = 0
    ss.confirmar_envio = False
    ir("prueba")


def vista_panel():
    cfg = db.get_config()
    est = db.get_estudiante(ss.est_id)
    cerrados = cerrar_vencidos(ss.est_id, cfg)
    ints = db.intentos_de(ss.est_id)
    if cerrados:
        nombres = ", ".join(AREAS[a]["corto"] for a in cerrados)
        st.warning(f"⏰ Se agotó el tiempo en: {nombres}. Se enviaron las respuestas que habías guardado.")
    if ss.aviso:
        st.success(ss.aviso)
        ss.aviso = None

    st.title(f"Hola, {est['nombre'].split()[0]} 👋")
    txt = (f"Cada evaluación tiene {cfg['minutos']} minutos." if cfg["modo_tiempo"] == "por_area"
           else f"Tienes {cfg['minutos']} minutos en total para las cuatro evaluaciones.")
    st.write(f"Elige una evaluación. {txt} Una vez iniciada, el reloj no se detiene.")

    hechas = sum(1 for i in ints.values() if i["estado"] != "en_curso")
    st.progress(hechas / 4, text=f"Evaluaciones completadas: {hechas} de 4")

    agotado_total = tiempo_total_agotado(ints, cfg)
    filas = [ORDEN_AREAS[:2], ORDEN_AREAS[2:]]
    for fila in filas:
        cols = st.columns(2)
        for col, a in zip(cols, fila):
            it = ints.get(a)
            with col.container(border=True):
                st.markdown(f"### {AREAS[a]['icono']} {AREAS[a]['corto']}")
                st.markdown(f"<span class='tarjeta-meta'>{AREAS[a]['descripcion']}</span>", unsafe_allow_html=True)
                st.write("")
                if it and it["estado"] != "en_curso":
                    r = bm.resultado_area(a, db.cargar_respuestas(it["id"]))
                    n = bm.nivel(r["pct"], cfg["cortes"])
                    st.markdown(f"✅ **Completada** · {r['pct']:.0f} % &nbsp; {gr.badge(n)}", unsafe_allow_html=True)
                    if it["estado"] == "tiempo_agotado":
                        st.caption("Finalizada por tiempo agotado.")
                elif it:
                    resto = limite_intento(it, ints, cfg) - time.time()
                    st.markdown(f"⏳ **En curso** · quedan {mmss(resto)}")
                    st.button("Continuar", key=f"cont_{a}", type="primary", width="stretch",
                              on_click=continuar_area, args=(a,))
                elif agotado_total:
                    st.markdown("⛔ **Tiempo total agotado**")
                else:
                    st.markdown("⚪ **Pendiente** · 20 preguntas")
                    st.button("Iniciar", key=f"ini_{a}", width="stretch",
                              on_click=lambda x=a: ss.update(confirmar_inicio=x))

    if ss.confirmar_inicio:
        a = ss.confirmar_inicio
        with st.container(border=True):
            st.warning(
                f"Vas a iniciar **{AREAS[a]['corto']}**. El reloj de {cfg['minutos']} minutos comienza ahora y no se detiene, "
                "aunque cierres la página. ¿Deseas comenzar?"
            )
            c1, c2 = st.columns(2)
            c1.button("Sí, comenzar ahora", type="primary", width="stretch",
                      on_click=iniciar_area, args=(a,))
            c2.button("Cancelar", width="stretch", on_click=lambda: ss.update(confirmar_inicio=None))

    st.divider()
    c1, c2 = st.columns([3, 1])
    if hechas:
        c1.button("📊 Ver mi panel de resultados", type="primary", on_click=ir, args=("resultados",))
    c2.button("Cerrar sesión", on_click=cerrar_sesion, width="stretch")


# =============================================================================== prueba
def _guardar(intento_id, qid, key, limite):
    """Callback de cada pregunta: guarda al instante (si el tiempo no venció)."""
    sel = ss.get(key)
    if sel is not None and time.time() <= limite + 2:
        db.guardar_respuesta(intento_id, qid, sel)


def _orden_opciones(semilla, qid, n=4):
    idx = list(range(n))
    random.Random(f"{semilla}-{qid}").shuffle(idx)
    return idx


@st.fragment(run_every=1)
def reloj(limite):
    resto = limite - time.time()
    if resto <= 0:
        st.rerun()
    alerta = " alerta" if resto < 300 else ""
    st.markdown(f"<div class='reloj{alerta}'>⏱️ {mmss(resto)}</div>", unsafe_allow_html=True)


def finalizar(intento, estado="finalizado"):
    db.finalizar_intento(intento["id"], estado)
    ss.confirmar_envio = False
    ss.aviso = f"✅ Enviaste «{AREAS[intento['area']]['corto']}». ¡Buen trabajo!"
    ir("panel")


def vista_prueba():
    cfg = db.get_config()
    area = ss.area_actual
    intento = db.get_intento(ss.est_id, area) if area else None
    if not intento:
        ir("panel")
        st.rerun()
    ints = db.intentos_de(ss.est_id)
    limite = limite_intento(intento, ints, cfg)
    if intento["estado"] != "en_curso" or time.time() >= limite:
        if intento["estado"] == "en_curso":
            db.finalizar_intento(intento["id"], "tiempo_agotado")
            ss.aviso = f"⏰ Se agotó el tiempo en «{AREAS[area]['corto']}». Se enviaron tus respuestas guardadas."
        ir("panel")
        st.rerun()

    respuestas = db.cargar_respuestas(intento["id"])
    paginas = paginas_de_area(area)
    total_pag = len(paginas)
    pag = min(max(ss.pagina, 0), total_pag - 1)
    sub, preguntas = paginas[pag]

    top = st.columns([4, 1.3])
    with top[0]:
        st.markdown(f"## {AREAS[area]['icono']} {AREAS[area]['nombre']}")
    with top[1]:
        reloj(limite)
    n_resp = sum(1 for p in preguntas_de_area(area) if p["id"] in respuestas)
    st.progress(n_resp / 20, text=f"Respondidas: {n_resp} de 20 · Parte {pag + 1} de {total_pag}: {AREAS[area]['subs'][sub]}")

    texto_id = preguntas[0]["texto"]
    if texto_id:
        t = TEXTOS[texto_id]
        st.markdown(f"**{t['titulo']}**")
        parrafos = t["texto"].split("\n\n")
        st.markdown("<div class='lectura'>" + "<br><br>".join(parrafos) + "</div>", unsafe_allow_html=True)

    base_n = sum(len(paginas[i][1]) for i in range(pag))
    for k, p in enumerate(preguntas, start=1):
        orden = _orden_opciones(intento["semilla"], p["id"])
        st.markdown(f"<div class='pregunta'>{base_n + k}. {p['enunciado']}</div>", unsafe_allow_html=True)
        previo = respuestas.get(p["id"])
        key = f"r_{intento['id']}_{p['id']}"
        st.radio(
            f"Pregunta {base_n + k}", options=orden,
            format_func=lambda i, p=p, orden=orden: f"{LETRAS[orden.index(i)]}) {p['opciones'][i]}",
            index=orden.index(previo) if previo is not None else None,
            key=key, label_visibility="collapsed",
            on_change=_guardar, args=(intento["id"], p["id"], key, limite),
        )

    st.divider()
    nav = st.columns([1, 2, 1])
    if pag > 0:
        nav[0].button("← Anterior", width="stretch", on_click=cambiar_pagina, args=(pag - 1,))
    nav[1].markdown(f"<div style='text-align:center;padding-top:0.5rem'>Parte {pag + 1} de {total_pag}</div>", unsafe_allow_html=True)
    if pag < total_pag - 1:
        nav[2].button("Siguiente →", type="primary", width="stretch", on_click=cambiar_pagina, args=(pag + 1,))
    else:
        nav[2].button("Finalizar y enviar", type="primary", width="stretch",
                      on_click=lambda: ss.update(confirmar_envio=True))

    if ss.confirmar_envio:
        sin = [i for i, p in enumerate(preguntas_de_area(area), start=1) if p["id"] not in respuestas]
        with st.container(border=True):
            if sin:
                st.warning(f"Tienes **{len(sin)} pregunta(s) sin responder**: {', '.join(map(str, sin))}. "
                           "Las que queden en blanco valen 0 puntos.")
            else:
                st.success("Respondiste las 20 preguntas.")
            st.write("Al enviar no podrás modificar tus respuestas.")
            c1, c2 = st.columns(2)
            c1.button("Sí, enviar ahora", type="primary", width="stretch", on_click=finalizar, args=(intento,))
            c2.button("Seguir revisando", width="stretch", on_click=lambda: ss.update(confirmar_envio=False))

    st.button("↩ Volver al panel (el reloj sigue corriendo)", on_click=ir, args=("panel",))


# =============================================================================== resultados
def vista_resultados():
    import analitica

    cfg = db.get_config()
    cortes = cfg["cortes"]
    est = db.get_estudiante(ss.est_id)
    cerrar_vencidos(ss.est_id, cfg)
    res, g = resultados_estudiante(ss.est_id, cfg)

    st.button("← Volver al panel", on_click=ir, args=("panel",))
    st.title("📊 Tu panel de resultados")
    st.caption(f"{est['nombre']} · {est['email']}")
    if not res:
        st.info("Aún no has completado ninguna evaluación.")
        return

    # comparación con el grupo (solo si hay al menos 5 participantes con datos)
    df_res, df_subs = bm.calcular_todo(db.df_estudiantes(), db.df_intentos(), db.df_respuestas(), cfg)
    comp = None
    if len(df_res) >= 5:
        comp = {a: float(df_res[a].mean()) for a in ORDEN_AREAS if df_res[a].notna().sum() >= 5}
        comp = comp or None

    pcts = {a: r["pct"] for a, r in res.items()}
    c1, c2 = st.columns([1, 1.2])
    with c1:
        if g is not None:
            ng = bm.nivel(g, cortes)
            st.plotly_chart(gr.gauge(g, cortes), width="stretch")
            st.markdown(f"<div style='text-align:center'>{gr.badge(ng)}</div>", unsafe_allow_html=True)
            st.write("")
            st.markdown(f"**Nivel {ng}.** {bm.DESCRIPTORES[ng]}")
            st.write(bm.RETRO_GLOBAL[ng])
        else:
            falta = 4 - len(res)
            st.info(f"Tu puntaje global se calculará al completar las 4 evaluaciones (te faltan {falta}).")
    with c2:
        st.plotly_chart(gr.radar(pcts, comp, cortes), width="stretch")
        if comp:
            st.caption("La línea punteada es el promedio del grupo en el piloto.")

    st.plotly_chart(gr.barras_areas(pcts, cortes, "Resultado por área"), width="stretch")

    # Fortalezas y prioridades
    st.subheader("Detalle por área")
    for a in ORDEN_AREAS:
        if a not in res:
            continue
        r = res[a]
        n = bm.nivel(r["pct"], cortes)
        with st.expander(f"{AREAS[a]['icono']} {AREAS[a]['corto']} · {r['pct']:.0f} % · {n}", expanded=False):
            st.write(bm.RETRO_AREA[a][n])
            for s, rs in r["subs"].items():
                ns = bm.nivel(rs["pct"], cortes)
                st.markdown(f"**{AREAS[a]['subs'][s]}** &nbsp; {gr.badge(ns)}", unsafe_allow_html=True)
                st.markdown(gr.barra_html(rs["pct"], cortes), unsafe_allow_html=True)
            _, mejorar = bm.retro_subs(a, r, cortes)
            if mejorar:
                st.markdown("**Para fortalecer**")
                for nom, pct, rec in mejorar:
                    st.markdown(f"- **{nom}.** {rec}")
            if cfg["mostrar_revision"]:
                it = db.get_intento(ss.est_id, a)
                import pandas as pd
                filas = bm.revision_item(a, db.cargar_respuestas(it["id"]))
                st.markdown("**Revisión de respuestas**")
                st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")

    st.subheader("Cómo interpretar los niveles")
    st.dataframe(bm.tabla_baremo(cortes), hide_index=True, width="stretch")
    st.caption(bm.AVISO)

    pdf = informes.pdf_individual(est, res, g, cfg)
    st.download_button("⬇️ Descargar mi informe (PDF)", pdf, file_name="mi_informe_baremo.pdf",
                       mime="application/pdf", type="primary")


# =============================================================================== enrutamiento
def sidebar():
    with st.sidebar:
        st.markdown("### 🎓 Baremo de competencias")
        if ss.est_id and not ss.es_docente:
            est = db.get_estudiante(ss.est_id)
            if est:
                st.write(f"**{est['nombre']}**")
                st.button("Cerrar sesión", on_click=cerrar_sesion, key="logout_sb")
        st.divider()
        if ss.es_docente:
            st.success("Modo docente activo")
            if st.button("Salir del modo docente"):
                ss.es_docente = False
                st.rerun()
        else:
            with st.expander("🔒 Acceso docente"):
                form_docente("sb")

sidebar()
scroll_arriba()

if ss.es_docente:
    import docente
    docente.render()
elif ss.vista == "registro" or not ss.est_id:
    vista_registro()
elif ss.vista == "panel":
    vista_panel()
elif ss.vista == "prueba":
    vista_prueba()
elif ss.vista == "resultados":
    vista_resultados()
