"""Gráficos Plotly y pequeños componentes HTML compartidos por la vista del estudiante y la del docente."""
import plotly.graph_objects as go

import baremo as bm
from banco import AREAS, ORDEN_AREAS

ETIQ_RADAR = {
    "A1": "Lectura y<br>comunicación",
    "A2": "Habilidades<br>para la vida",
    "A3": "Informática<br>educativa",
    "A4": "EVA, Moodle y<br>educación en línea",
}
AZUL = "#2B5FA5"
GRIS = "#6B7785"
TEXTO = "#1F2933"


def _base(fig, alto=380):
    fig.update_layout(
        height=alto,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=15, color=TEXTO),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    return fig


def badge(nivel_txt):
    color = bm.COLORES.get(nivel_txt, "#9AA5B1")
    return (f"<span style='background:{color};color:#fff;padding:3px 12px;border-radius:14px;"
            f"font-weight:600;font-size:0.9em;white-space:nowrap'>{nivel_txt}</span>")


def barra_html(pct, cortes, ancho_etiqueta=""):
    niv = bm.nivel(pct, cortes)
    color = bm.COLORES[niv]
    return (
        f"<div style='display:flex;align-items:center;gap:10px;margin:4px 0'>"
        f"<div style='flex:1;background:#E8EDF2;border-radius:6px;height:16px;position:relative'>"
        f"<div style='width:{max(pct, 1):.0f}%;background:{color};height:16px;border-radius:6px'></div></div>"
        f"<div style='width:52px;text-align:right;font-weight:600'>{pct:.0f} %</div></div>"
    )


def radar(pcts, comparativo=None, cortes=(60, 75, 90), nombre="Tu resultado", nombre_comp="Promedio del grupo"):
    etiquetas = [ETIQ_RADAR[a] for a in ORDEN_AREAS]
    valores = [pcts.get(a) or 0 for a in ORDEN_AREAS]
    fig = go.Figure()
    if comparativo:
        vc = [comparativo.get(a) or 0 for a in ORDEN_AREAS]
        fig.add_trace(go.Scatterpolar(
            r=vc + vc[:1], theta=etiquetas + etiquetas[:1], name=nombre_comp,
            line=dict(color=GRIS, dash="dash", width=2), fill=None, hovertemplate="%{theta}: %{r:.0f} %<extra></extra>"))
    fig.add_trace(go.Scatterpolar(
        r=valores + valores[:1], theta=etiquetas + etiquetas[:1], name=nombre,
        fill="toself", fillcolor="rgba(43,95,165,0.22)", line=dict(color=AZUL, width=3),
        marker=dict(size=7), hovertemplate="%{theta}: %{r:.0f} %<extra></extra>"))
    _base(fig, 430)
    fig.update_layout(polar=dict(
        radialaxis=dict(range=[0, 100], tickvals=list(cortes), ticksuffix=" %", tickfont=dict(size=12),
                        gridcolor="#C9D2DC"),
        angularaxis=dict(tickfont=dict(size=14))),
        margin=dict(l=95, r=95, t=40, b=70), legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5))
    return fig


def barras_areas(pcts, cortes, titulo=""):
    areas = [a for a in ORDEN_AREAS if pcts.get(a) is not None]
    fig = go.Figure(go.Bar(
        y=[AREAS[a]["corto"] for a in areas][::-1],
        x=[pcts[a] for a in areas][::-1], orientation="h",
        marker_color=[bm.COLORES[bm.nivel(pcts[a], cortes)] for a in areas][::-1],
        text=[f"{pcts[a]:.0f} %  ·  {bm.nivel(pcts[a], cortes)}" for a in areas][::-1],
        textposition="inside", insidetextanchor="start", textfont=dict(color="white", size=14),
        hovertemplate="%{y}: %{x:.0f} %<extra></extra>"))
    for c in cortes:
        fig.add_vline(x=c, line_dash="dot", line_color="#6B7785", line_width=1.2)
    fig.update_xaxes(range=[0, 100], ticksuffix=" %", tickvals=[0, *cortes, 100], gridcolor="#E3E8EE")
    fig.update_layout(title=dict(text=titulo, font=dict(size=16)) if titulo else None, showlegend=False)
    return _base(fig, 120 + 52 * len(areas))


def distribucion_niveles(df_res, cortes):
    """Barras apiladas: cantidad de estudiantes por nivel en cada área y en el global."""
    cols = [(a, AREAS[a]["corto"]) for a in ORDEN_AREAS] + [("global", "Global")]
    fig = go.Figure()
    for nv in bm.NIVELES:
        valores = []
        for c, _ in cols:
            colnivel = "nivel_global" if c == "global" else f"{c}_nivel"
            valores.append(int((df_res[colnivel] == nv).sum()))
        fig.add_trace(go.Bar(name=nv, x=[e for _, e in cols], y=valores, marker_color=bm.COLORES[nv],
                             hovertemplate="%{x} · " + nv + ": %{y}<extra></extra>"))
    fig.update_layout(barmode="stack", yaxis_title="Estudiantes")
    return _base(fig, 380)


def histograma(serie, cortes, titulo="Distribución del puntaje global"):
    fig = go.Figure(go.Histogram(x=serie.dropna(), xbins=dict(start=0, end=100, size=5),
                                 marker_color=AZUL, hovertemplate="%{x} %: %{y} estudiantes<extra></extra>"))
    for c in cortes:
        fig.add_vline(x=c, line_dash="dot", line_color="#6B7785")
    fig.update_xaxes(range=[0, 100], title="Puntaje (%)")
    fig.update_yaxes(title="Estudiantes")
    fig.update_layout(title=dict(text=titulo, font=dict(size=16)), bargap=0.05, showlegend=False)
    return _base(fig, 340)


def mapa_calor(df_subs):
    """Promedio por subcompetencia (criterios con mayor dificultad)."""
    if len(df_subs) == 0:
        return None
    m = df_subs.groupby(["area", "subcompetencia"], sort=False)["pct"].mean().reset_index()
    m["orden"] = m["area"].map({a: i for i, a in enumerate(ORDEN_AREAS)})
    m = m.sort_values(["orden", "pct"], ascending=[False, True])
    fig = go.Figure(go.Bar(
        y=m["subcompetencia"], x=m["pct"], orientation="h",
        marker_color=[bm.COLORES[bm.nivel(v, [60, 75, 90])] for v in m["pct"]],
        text=[f"{v:.0f} %" for v in m["pct"]], textposition="outside",
        hovertemplate="%{y}: %{x:.1f} %<extra></extra>"))
    fig.update_xaxes(range=[0, 110], ticksuffix=" %")
    fig.update_layout(showlegend=False)
    return _base(fig, 150 + 34 * len(m))


def gauge(valor, cortes, titulo="Puntaje global"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=valor, number=dict(suffix=" / 100", font=dict(size=44)),
        title=dict(text=titulo, font=dict(size=18)),
        gauge=dict(
            axis=dict(range=[0, 100], tickvals=[0, *cortes, 100]),
            bar=dict(color="#1F3A5F", thickness=0.28),
            steps=[
                dict(range=[0, cortes[0]], color="#E9C4BF"),
                dict(range=[cortes[0], cortes[1]], color="#F2DFB4"),
                dict(range=[cortes[1], cortes[2]], color="#BFDDD6"),
                dict(range=[cortes[2], 100], color="#BCCDE6"),
            ])))
    _base(fig, 290)
    fig.update_layout(margin=dict(l=35, r=45, t=60, b=10))
    return fig
