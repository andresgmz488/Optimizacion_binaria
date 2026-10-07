# 📺 Plan de medios con presupuesto — Optimización binaria con PuLP

Elige qué canales publicitarios usar para **maximizar el impacto** sin exceder el presupuesto.
Es un problema de la mochila 0/1 resuelto con programación entera binaria (PuLP + solver CBC).

## Modelo

- **Variables:** `x_i ∈ {0,1}` (1 = se usa el canal *i*)
- **Objetivo:** `max Σ impacto_i · x_i`
- **Restricción:** `Σ costo_i · x_i ≤ Presupuesto`

Con los datos del ejercicio (presupuesto 9) la solución óptima es **Radio + Redes sociales + Prensa**, con **impacto = 15**.

## Archivos

| Archivo | Descripción |
|---|---|
| `plan_medios_pulp.ipynb` | Notebook con la formulación, solución con PuLP, verificación por fuerza bruta y sensibilidad al presupuesto |
| `app.py` | Aplicación Streamlit: modifica presupuesto, costos e impactos (y agrega/elimina canales) y resuelve el modelo |
| `requirements.txt` | Dependencias para Streamlit Community Cloud |

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

> Nota: se fija `pulp==3.3.2` porque PuLP 4.0 cambió la forma de crear variables y la sintaxis clásica
> `pulp.LpVariable(nombre, cat=pulp.LpBinary)` ya no funciona en esa versión.

## Despliegue en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio público de GitHub.
2. Entra a <https://share.streamlit.io> e inicia sesión con GitHub.
3. **Create app** → selecciona el repositorio, rama `main` y archivo principal `app.py`.
4. **Deploy**. La app queda en una URL `https://<nombre>.streamlit.app`.
