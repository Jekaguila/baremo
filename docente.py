"""Panel docente: resumen, estudiantes, análisis de ítems, perfiles (scikit-learn), baremo, banco y datos."""
import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import analitica
import baremo as bm
import db
import graficos as gr
import informes
from banco import AREAS, ORDEN_AREAS, PREGUNTAS, TEXTOS, preguntas_de_area

ss = st.session_state


def _cargar(cfg):
    df_est, df_int, df_resp = db.df_estudiantes(), db.df_intentos(), db.df_respuestas()
    df_res, df_subs = bm.calcular_todo(df_est, df_int, df_resp, cfg) if len(df_est) else (pd.DataFrame(), pd.DataFrame())
    return df_est, df_int, df_resp, df_res, df_subs


def _estilo_nivel(df, columnas):
    def color(v):
        c = bm.COLORES.get(v)
        return f"background-color:{c};color:white;font-weight:600" if c else ""
    return df.style.map(color, subset=columnas)


# =============================================================================== pestañas
def tab_resumen(cfg, df_res, df_subs, df_int):
    cortes = cfg["cortes"]
    completos = df_res[df_res["completadas"] == 4]
    iniciaron = df_res[df_res["completadas"] > 0]
    c = st.columns(5)
    c[0].metric("Registrados", len(df_res))
    c[1].metric("Con alguna evaluación", len(iniciaron))
    c[2].metric("Completaron las 4", len(completos))
    c[3].metric("Promedio global", f"{completos['global'].mean():.1f} %" if len(completos) else "—")
    mins = df_res[[f"{a}_min" for a in ORDEN_AREAS]].stack()
    c[4].metric("Tiempo medio por evaluación", f"{mins.mean():.0f} min" if len(mins) else "—")

    if len(iniciaron) == 0:
        st.info("Aún no hay evaluaciones completadas.")
        return
    st.markdown("#### Distribución por niveles")
    st.plotly_chart(gr.distribucion_niveles(df_res, cortes), width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        if len(completos):
            st.plotly_chart(gr.histograma(completos["global"], cortes), width="stretch")
        else:
            st.caption("El histograma global aparece cuando alguien completa las 4 áreas.")
    with col2:
        prom = pd.DataFrame({
            "Área": [AREAS[a]["corto"] for a in ORDEN_AREAS],
            "Promedio (%)": [df_res[a].mean() for a in ORDEN_AREAS],
            "Evaluados": [int(df_res[a].notna().sum()) for a in ORDEN_AREAS],
        })
        prom["Nivel del promedio"] = prom["Promedio (%)"].map(lambda v: bm.nivel(v, cortes))
        prom["Promedio (%)"] = prom["Promedio (%)"].round(1)
        st.markdown("**Promedio por área**")
        st.dataframe(_estilo_nivel(prom, ["Nivel del promedio"]), hide_index=True, width="stretch")

    st.markdown("#### Criterios (subcompetencias) con mayor dificultad")
    fig = gr.mapa_calor(df_subs)
    if fig:
        st.plotly_chart(fig, width="stretch")
        st.caption("Ordenadas de menor a mayor promedio dentro de cada área: las primeras son las que más requieren refuerzo.")

    if len(iniciaron) >= 5:
        st.markdown("#### Percentiles del grupo (referencia normativa)")
        st.dataframe(analitica.tabla_percentiles(df_res), width="stretch")
        st.caption("El documento de baremos distingue entre baremo por criterio (cortes fijos, el que se usa aquí) y "
                   "baremo normativo (percentiles de una población de referencia). Esta tabla sirve para contrastar ambos.")


def tab_estudiantes(cfg, df_est, df_res):
    cortes = cfg["cortes"]
    if len(df_res) == 0:
        st.info("Todavía no hay estudiantes registrados.")
        return
    def _p(v):
        return "—" if pd.isna(v) else f"{v:.0f}"

    vista = pd.DataFrame({"Nombre": df_res["nombre"], "Grupo": df_res["grupo"]})
    for a in ORDEN_AREAS:
        vista[AREAS[a]["corto"]] = df_res[a].map(_p)
    vista["Global"] = df_res["global"].map(_p)
    vista["Nivel global"] = df_res["nivel_global"]
    vista["Áreas"] = df_res["completadas"]
    st.dataframe(_estilo_nivel(vista, ["Nivel global"]), hide_index=True, width="stretch")

    st.markdown("#### Ficha individual")
    opciones = {f"{r.nombre} · {r.email}": r.id for r in df_res.itertuples()}
    elegido = st.selectbox("Estudiante", list(opciones))
    est_id = opciones[elegido]
    est = db.get_estudiante(est_id)
    ints = db.intentos_de(est_id)
    res = {}
    for a in ORDEN_AREAS:
        it = ints.get(a)
        if it and it["estado"] != "en_curso":
            res[a] = bm.resultado_area(a, db.cargar_respuestas(it["id"]))
    g = bm.nota_global({a: (res[a]["pct"] if a in res else None) for a in ORDEN_AREAS}, cfg["pesos"])
    if res:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(gr.radar({a: r["pct"] for a, r in res.items()}, None, cortes), width="stretch")
        with c2:
            if g is not None:
                st.metric("Puntaje global", f"{g:.1f} %", bm.nivel(g, cortes), delta_color="off")
            for a, r in res.items():
                st.markdown(f"**{AREAS[a]['corto']}** · {r['pct']:.0f} % &nbsp;{gr.badge(bm.nivel(r['pct'], cortes))}",
                            unsafe_allow_html=True)
            st.download_button("⬇️ Informe PDF de este estudiante", informes.pdf_individual(est, res, g, cfg),
                               file_name=f"informe_{est['email'].split('@')[0]}.pdf", mime="application/pdf")
    else:
        st.caption("Este estudiante aún no completa ninguna evaluación.")

    with st.expander("Acciones sobre este estudiante"):
        st.caption("Útil en el piloto: reabrir un área (por ejemplo, tras un problema técnico) o eliminar cuentas de prueba.")
        for a in ORDEN_AREAS:
            if a in ints:
                if st.button(f"Reabrir «{AREAS[a]['corto']}» (borra su intento y respuestas)", key=f"reabrir_{est_id}_{a}"):
                    db.borrar_intento(est_id, a)
                    st.rerun()
        confirmar = st.checkbox("Confirmo que quiero eliminar a este estudiante y todos sus datos", key=f"del_chk_{est_id}")
        if st.button("Eliminar estudiante", disabled=not confirmar, key=f"del_{est_id}"):
            db.borrar_estudiante(est_id)
            st.rerun()


def tab_items(df_int, df_resp):
    st.markdown("Esta vista convierte la prueba piloto en una **calibración del instrumento**: te dice qué preguntas "
                "están funcionando y cuáles conviene revisar antes de la aplicación definitiva.")
    area = st.selectbox("Área", ORDEN_AREAS, format_func=lambda a: f"{AREAS[a]['icono']} {AREAS[a]['corto']}", key="items_area")
    tabla, alfa, n = analitica.analisis_items(df_int, df_resp, area)
    if n == 0:
        st.info("Aún no hay evaluaciones cerradas en esta área.")
        return
    c = st.columns(3)
    c[0].metric("Evaluaciones analizadas", n)
    c[1].metric("Confiabilidad (alfa de Cronbach)", f"{alfa:.2f}" if not np.isnan(alfa) else "—",
                help="Referencia habitual: ≥ 0,70 aceptable; ≥ 0,80 buena. Requiere al menos 5 evaluaciones y es poco estable con muestras pequeñas.")
    c[2].metric("Ítems con alerta", int((tabla["Alerta"] != "").sum()))
    if n < 30:
        st.warning(f"Con n = {n}, los índices son solo orientativos (se recomienda n ≥ 30 para decidir sobre cada ítem).")
    st.dataframe(tabla, hide_index=True, width="stretch",
                 column_config={
                     "Pregunta": st.column_config.TextColumn(width="large"),
                     "Dificultad (0–1)": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f",
                                                                          help="Proporción del puntaje obtenido: cerca de 1 = fácil."),
                     "Discriminación": st.column_config.NumberColumn(format="%.2f",
                                                                      help="Correlación del ítem con el resto de la prueba. ≥ 0,20 es deseable."),
                 })


def tab_perfiles(df_res):
    st.markdown("Agrupa con **K-Means (scikit-learn)** a quienes completaron las cuatro áreas según su perfil de desempeño, "
                "para planificar apoyos diferenciados.")
    completos = df_res[df_res["completadas"] == 4]
    corr = analitica.correlaciones(df_res)
    if corr is not None:
        st.markdown("**Correlación entre áreas**")
        etiquetas = [AREAS[a]["corto"] for a in ORDEN_AREAS]
        fig = go.Figure(go.Heatmap(z=corr.values, x=etiquetas, y=etiquetas, zmin=-1, zmax=1, colorscale="RdBu",
                                   text=np.round(corr.values, 2), texttemplate="%{text}"))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), font=dict(size=14))
        st.plotly_chart(fig, width="stretch")
        st.caption("Con pocos estudiantes las correlaciones son inestables; interpreta con cautela.")
    if len(completos) < 6:
        st.info(f"Se necesitan al menos 6 estudiantes con las 4 áreas completas para formar perfiles (hay {len(completos)}).")
        return
    kmax = min(4, len(completos) - 2)
    k = st.slider("Número de perfiles", 2, max(2, kmax), min(3, kmax))
    out = analitica.perfiles_kmeans(df_res, k=k)
    if out is None:
        st.info("No hay datos suficientes todavía.")
        return
    perfiles, cent, sil = out
    c1, c2 = st.columns([1.2, 1])
    with c1:
        fig = go.Figure()
        etiquetas = [AREAS[a]["corto"] for a in ORDEN_AREAS]
        for nombre, fila in cent.iterrows():
            v = [fila[a] for a in ORDEN_AREAS]
            fig.add_trace(go.Scatterpolar(r=v + v[:1], theta=etiquetas + etiquetas[:1], name=f"{nombre} (n={int(fila['n'])})"))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=420, font=dict(size=14),
                          legend=dict(orientation="h", y=-0.12), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width="stretch")
    with c2:
        t = cent.copy()
        t.columns = [AREAS[a]["corto"] for a in ORDEN_AREAS] + ["Estudiantes"]
        st.dataframe(t.round(1), width="stretch")
        st.caption(f"Coeficiente de silueta: {sil:.2f}" if not np.isnan(sil) else "")
    st.markdown("**Integrantes de cada perfil**")
    st.dataframe(perfiles[["nombre", "perfil", "global", "nivel_global"]].sort_values(["perfil", "global"], ascending=[True, False])
                 .rename(columns={"nombre": "Nombre", "perfil": "Perfil", "global": "Global", "nivel_global": "Nivel"}),
                 hide_index=True, width="stretch")
    st.caption("El Perfil 1 es el de mayor puntaje promedio. Los grupos describen patrones de la muestra, no categorías de las personas.")


def tab_baremo(cfg):
    st.markdown("#### Constructor de baremo")
    st.caption("Los puntajes se recalculan con el baremo vigente: al cambiar los cortes o las ponderaciones se actualizan "
               "los resultados de todos los estudiantes, incluidos los ya evaluados.")
    c = cfg["cortes"]
    with st.form("form_baremo"):
        st.markdown("**Cortes de los niveles (% mínimo para alcanzar cada nivel)**")
        a, b, d = st.columns(3)
        c1 = a.number_input("Básico desde", 1, 98, int(c[0]))
        c2 = b.number_input("Satisfactorio desde", 2, 99, int(c[1]))
        c3 = d.number_input("Avanzado desde", 3, 100, int(c[2]))
        st.markdown("**Ponderación de cada área en el puntaje global (%)**")
        pcols = st.columns(4)
        pesos = {ar: pcols[i].number_input(AREAS[ar]["corto"], 0, 100, int(cfg["pesos"][ar]), key=f"peso_{ar}")
                 for i, ar in enumerate(ORDEN_AREAS)}
        st.markdown("**Tiempo**")
        t1, t2 = st.columns(2)
        minutos = t1.number_input("Minutos", 5, 240, int(cfg["minutos"]))
        modo = t2.radio("El tiempo corre…", ["por_area", "total"], index=0 if cfg["modo_tiempo"] == "por_area" else 1,
                        format_func=lambda m: "por cada evaluación" if m == "por_area" else "en total para las cuatro",
                        horizontal=True)
        rev = st.checkbox("Mostrar al estudiante la revisión de sus respuestas (respuesta esperada y explicación)",
                          value=cfg["mostrar_revision"],
                          help="Recomendado desactivado mientras otros compañeros aún rinden la prueba.")
        guardar = st.form_submit_button("Guardar configuración", type="primary")
    if guardar:
        if not (c1 < c2 < c3):
            st.error("Los cortes deben ser crecientes: Básico < Satisfactorio < Avanzado.")
        elif sum(pesos.values()) <= 0:
            st.error("La suma de las ponderaciones debe ser mayor que 0.")
        else:
            db.set_config(cortes=[int(c1), int(c2), int(c3)], pesos=pesos, minutos=int(minutos),
                          modo_tiempo=modo, mostrar_revision=bool(rev))
            st.success("Configuración guardada." + ("" if sum(pesos.values()) == 100 else
                       f" (Las ponderaciones suman {sum(pesos.values())}; se normalizan automáticamente a 100 %.)"))
            st.rerun()
    st.markdown("**Baremo vigente**")
    st.dataframe(bm.tabla_baremo(cfg["cortes"]), hide_index=True, width="stretch")

    st.markdown("#### Simulador")
    st.caption("Mueve los puntajes por área y observa el resultado global, como en el ejemplo del documento de baremos.")
    sc = st.columns(4)
    sim = {a: sc[i].slider(AREAS[a]["corto"], 0, 100, 75, key=f"sim_{a}") for i, a in enumerate(ORDEN_AREAS)}
    g = bm.nota_global(sim, cfg["pesos"])
    tot = sum(cfg["pesos"].values())
    formula = " + ".join(f"{cfg['pesos'][a] / tot:.2f}\\,C_{i + 1}" for i, a in enumerate(ORDEN_AREAS))
    st.latex(f"N = {formula}")
    st.markdown(f"### {g:.1f} / 100 &nbsp; {gr.badge(bm.nivel(g, cfg['cortes']))}", unsafe_allow_html=True)


def tab_banco():
    st.caption("Banco de preguntas con la clave de respuestas. En la prueba, el orden de las opciones se baraja por estudiante.")
    area = st.selectbox("Área", ORDEN_AREAS, format_func=lambda a: f"{AREAS[a]['icono']} {AREAS[a]['nombre']}", key="banco_area")
    textos_mostrados = set()
    for i, p in enumerate(preguntas_de_area(area), start=1):
        if p["texto"] and p["texto"] not in textos_mostrados:
            textos_mostrados.add(p["texto"])
            with st.expander(TEXTOS[p["texto"]]["titulo"]):
                st.write(TEXTOS[p["texto"]]["texto"])
        with st.container(border=True):
            st.markdown(f"**{i}. {p['enunciado']}**  \n<span style='color:#6B7785'>{AREAS[area]['subs'][p['sub']]} · {p['id']}</span>",
                        unsafe_allow_html=True)
            for j, op in enumerate(p["opciones"]):
                marca = "✅" if j == p["correcta"] else ("◐" if j in p["parciales"] else "▫️")
                extra = " *(1 punto)*" if j == p["correcta"] else (" *(0,5 puntos)*" if j in p["parciales"] else "")
                st.markdown(f"{marca} {op}{extra}")
            st.caption(f"Explicación: {p['explicacion']}")

    filas = []
    for p in PREGUNTAS:
        filas.append({"ID": p["id"], "Área": AREAS[p["area"]]["corto"], "Subcompetencia": AREAS[p["area"]]["subs"][p["sub"]],
                      "Pregunta": p["enunciado"], "Respuesta correcta": p["opciones"][p["correcta"]],
                      "Opción de crédito parcial (0,5)": "; ".join(p["opciones"][j] for j in p["parciales"]),
                      "Distractores": " | ".join(o for j, o in enumerate(p["opciones"]) if j != p["correcta"] and j not in p["parciales"]),
                      "Explicación": p["explicacion"]})
    buf = io.BytesIO()
    pd.DataFrame(filas).to_excel(buf, index=False, sheet_name="Banco y clave")
    st.download_button("⬇️ Descargar banco y clave (Excel)", buf.getvalue(), file_name="banco_de_preguntas_clave.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def tab_datos(cfg, df_est, df_int, df_resp, df_res, df_subs):
    st.markdown("#### Respaldo y exportación")
    st.warning("**Descarga un respaldo al terminar la sesión del piloto.** En Streamlit Community Cloud el almacenamiento "
               "de la aplicación puede reiniciarse cuando la app se reinicia o se duerme.")
    if len(df_res):
        items = {a: analitica.analisis_items(df_int, df_resp, a)[0] for a in ORDEN_AREAS}
        xls = informes.excel_resultados(df_res, df_subs, df_int, df_resp, df_est, cfg, items)
        st.download_button("⬇️ Informe completo (Excel)", xls, file_name="baremo_resultados.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
        st.download_button("⬇️ Resumen por estudiante (CSV)", df_res.to_csv(index=False).encode("utf-8-sig"),
                           file_name="baremo_resumen.csv", mime="text/csv")
    if db.DB_PATH.exists():
        st.download_button("⬇️ Copia de la base de datos (.db)", db.DB_PATH.read_bytes(), file_name="baremos_respaldo.db")
    st.markdown("#### Zona de riesgo")
    with st.expander("Borrar todos los datos del piloto"):
        txt = st.text_input("Escribe BORRAR para confirmar")
        if st.button("Borrar todo", disabled=(txt != "BORRAR")):
            db.borrar_todo()
            st.success("Datos eliminados.")
            st.rerun()


# =============================================================================== entrada
def render():
    cfg = db.get_config()
    st.title("👩‍🏫 Panel docente")
    st.caption("Resultados del piloto · Baremo de competencias")
    if st.button("🔄 Actualizar datos"):
        st.rerun()
    df_est, df_int, df_resp, df_res, df_subs = _cargar(cfg)
    tabs = st.tabs(["📊 Resumen", "👥 Estudiantes", "🧪 Análisis de ítems", "🤖 Perfiles", "⚙️ Baremo", "📚 Banco de preguntas", "💾 Datos"])
    with tabs[0]:
        if len(df_res):
            tab_resumen(cfg, df_res, df_subs, df_int)
        else:
            st.info("Aún no hay estudiantes registrados. Comparte el enlace de la aplicación para iniciar el piloto.")
    with tabs[1]:
        tab_estudiantes(cfg, df_est, df_res)
    with tabs[2]:
        tab_items(df_int, df_resp)
    with tabs[3]:
        if len(df_res):
            tab_perfiles(df_res)
        else:
            st.info("Aún no hay datos.")
    with tabs[4]:
        tab_baremo(cfg)
    with tabs[5]:
        tab_banco()
    with tabs[6]:
        tab_datos(cfg, df_est, df_int, df_resp, df_res, df_subs)
