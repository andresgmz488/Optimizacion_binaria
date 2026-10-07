"""
Plan de medios con presupuesto — Optimización binaria (problema de la mochila 0/1) con PuLP.
Ejecutar localmente:  streamlit run app.py
"""
import pandas as pd
import pulp
import streamlit as st

st.set_page_config(page_title="Plan de medios óptimo", page_icon="📺", layout="wide")

CANALES_INICIALES = pd.DataFrame(
    {
        "Canal": ["TV", "Radio", "Redes sociales", "Prensa"],
        "Costo": [8.0, 3.0, 4.0, 2.0],
        "Impacto": [14.0, 5.0, 7.0, 3.0],
    }
)


def resolver_plan(df: pd.DataFrame, presupuesto: float):
    """Resuelve el modelo binario y devuelve (estado, impacto_total, costo_total, df_resultado)."""
    canales = df["Canal"].tolist()
    costo = dict(zip(canales, df["Costo"]))
    impacto = dict(zip(canales, df["Impacto"]))

    modelo = pulp.LpProblem("Plan_de_medios", pulp.LpMaximize)

    # Variables de decisión: x_i = 1 si se usa el canal i, 0 si no
    x = {c: pulp.LpVariable(f"x_{i}", cat=pulp.LpBinary) for i, c in enumerate(canales)}

    # Función objetivo: maximizar el impacto total
    modelo += pulp.lpSum(impacto[c] * x[c] for c in canales), "Impacto_total"

    # Restricción: no exceder el presupuesto
    modelo += pulp.lpSum(costo[c] * x[c] for c in canales) <= presupuesto, "Presupuesto"

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    estado = pulp.LpStatus[modelo.status]
    resultado = df.copy()
    resultado["Seleccionado"] = [int(round(x[c].value() or 0)) for c in canales]
    impacto_total = float((resultado["Impacto"] * resultado["Seleccionado"]).sum())
    costo_total = float((resultado["Costo"] * resultado["Seleccionado"]).sum())
    return estado, impacto_total, costo_total, resultado, modelo


# ---------------------------------------------------------------- Interfaz
st.title("📺 Plan de medios con presupuesto")
st.markdown(
    "Elige qué canales publicitarios usar este mes para **maximizar el impacto** "
    "sin exceder el presupuesto. Cada canal se usa o no se usa (variable **binaria**)."
)

with st.expander("Modelo matemático"):
    st.latex(r"\max \; Z = \sum_{i} \text{impacto}_i \, x_i")
    st.latex(r"\text{s.a.} \quad \sum_{i} \text{costo}_i \, x_i \le \text{Presupuesto}")
    st.latex(r"x_i \in \{0, 1\}")

col_datos, col_res = st.columns([1, 1], gap="large")

with col_datos:
    st.subheader("1. Datos")
    presupuesto = st.number_input("Presupuesto disponible", min_value=0.0, value=9.0, step=1.0)

    if "canales" not in st.session_state:
        st.session_state.canales = CANALES_INICIALES.copy()

    st.caption("Edita costos e impactos, o agrega/elimina canales en la tabla.")
    datos = st.data_editor(
        st.session_state.canales,
        num_rows="dynamic",
        width="stretch",
        key="editor",
        column_config={
            "Canal": st.column_config.TextColumn("Canal", required=True),
            "Costo": st.column_config.NumberColumn("Costo", min_value=0.0, step=1.0, required=True),
            "Impacto": st.column_config.NumberColumn("Impacto", min_value=0.0, step=1.0, required=True),
        },
    )

    if st.button("↺ Restablecer datos del ejercicio"):
        st.session_state.canales = CANALES_INICIALES.copy()
        st.session_state.pop("editor", None)
        st.rerun()

with col_res:
    st.subheader("2. Solución óptima")

    datos = datos.dropna(subset=["Canal", "Costo", "Impacto"])
    datos = datos[datos["Canal"].astype(str).str.strip() != ""]

    if datos.empty:
        st.warning("Agrega al menos un canal para resolver el problema.")
    elif datos["Canal"].duplicated().any():
        st.error("Hay canales con nombre repetido. Usa nombres únicos.")
    else:
        estado, impacto_total, costo_total, resultado, modelo = resolver_plan(datos, presupuesto)

        if estado != "Optimal":
            st.error(f"El solver terminó con estado: {estado}")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Impacto máximo", f"{impacto_total:g}")
            m2.metric("Costo usado", f"{costo_total:g}")
            m3.metric("Presupuesto sobrante", f"{presupuesto - costo_total:g}")

            elegidos = resultado.loc[resultado["Seleccionado"] == 1, "Canal"].tolist()
            if elegidos:
                st.success("Canales seleccionados: **" + ", ".join(elegidos) + "**")
            else:
                st.info("Con este presupuesto no es posible contratar ningún canal.")

            tabla = resultado.assign(
                Decisión=resultado["Seleccionado"].map({1: "✅ Usar", 0: "—"}),
                **{"Impacto/Costo": (resultado["Impacto"] / resultado["Costo"].replace(0, pd.NA)).round(2)},
            )[["Canal", "Costo", "Impacto", "Impacto/Costo", "Decisión"]]
            st.dataframe(tabla, hide_index=True, width="stretch")

            uso = pd.DataFrame(
                {"Costo": [costo_total, max(presupuesto - costo_total, 0)]},
                index=["Usado", "Disponible"],
            )
            st.caption("Uso del presupuesto")
            st.bar_chart(uso.T, horizontal=True, height=140)

        with st.expander("Ver modelo generado por PuLP"):
            st.code(str(modelo), language="text")

st.divider()
st.caption("Optimización binaria con PuLP (solver CBC) · Desplegado con Streamlit Community Cloud")
