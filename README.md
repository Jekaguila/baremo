# Baremo de competencias · Informática Educativa (prueba piloto)

Aplicación Streamlit para evaluar a egresados de la Licenciatura en Informática Educativa en **cuatro áreas**
(20 preguntas cada una, 80 en total) y devolverles un panel con su nivel de desempeño según un baremo.

| Área | Subcompetencias (5 preguntas c/u) |
|---|---|
| 📖 Lectura, comprensión lectora, escritura y seguimiento de indicaciones | Lectura literal · Comprensión inferencial y crítica · Escritura y revisión · Seguimiento de indicaciones |
| 🧭 Habilidades para la vida | Pensamiento crítico y resolución de problemas · Comunicación asertiva y trabajo colaborativo · Autogestión · Ética y ciudadanía digital |
| 💻 Dominio de la informática educativa | Fundamentos y modelos · Diseño y evaluación de recursos · Tecnologías emergentes · Integración curricular y gestión |
| 🎓 EVA, Moodle y educación en línea | Gestión de Moodle · Actividades y calificación · Diseño y facilitación en línea · Evaluación e integridad |

## Baremo (según BAREMOS.docx)

| Rango | Nivel | Descriptor |
|---|---|---|
| 0–59 | Insuficiente | Presenta dificultades importantes en el cumplimiento de los criterios. |
| 60–74 | Básico | Cumple parcialmente los requisitos y necesita mejoras. |
| 75–89 | Satisfactorio | Demuestra un desempeño adecuado en la mayoría de los criterios. |
| 90–100 | Avanzado | Demuestra un desempeño sólido, fundamentado y consistente. |

- Cada pregunta vale 1 punto (en *Habilidades para la vida* hay opciones de crédito parcial de 0,5).
- El nivel se calcula por **subcompetencia, por área y global**. El puntaje global es el promedio ponderado
  `N = Σ pesoᵢ · puntajeᵢ` (por defecto 25 % cada área). Cortes, ponderaciones y tiempo se editan en el panel docente (pestaña **Baremo**) y los resultados se recalculan.

## Ejecutar en tu computadora

```bash
pip install -r requirements.txt
export ADMIN_PASSWORD="tu-clave"        # Windows PowerShell:  $env:ADMIN_PASSWORD="tu-clave"
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (puede ser privado).
2. Entra a <https://share.streamlit.io> → **Create app** → elige el repositorio, la rama y el archivo principal `app.py`.
3. En **Advanced settings → Secrets** pega:
   ```toml
   ADMIN_PASSWORD = "elige-una-clave-segura"
   ```
4. **Deploy**. Comparte el enlace con los estudiantes. Tú entras con *🔒 Acceso docente* (al final de la pantalla de inicio o en la barra lateral).

## Durante el piloto

- **Tiempo:** 40 min por evaluación por defecto. En el panel docente puedes cambiarlo o hacer que sean 40 min *en total* para las cuatro.
  El reloj corre en el servidor: si el estudiante cierra la página y vuelve a entrar con el mismo correo, continúa donde quedó y el reloj no se reinicia. Al vencer el tiempo se envía lo respondido.
- **Revisión de respuestas** para el estudiante: desactivada por defecto (para que no circule la clave mientras otros siguen rindiendo). Se activa en *Baremo*.
- **Respaldo:** la app guarda en SQLite (`data/baremos.db`). En Streamlit Community Cloud ese almacenamiento **puede reiniciarse** si la app se reinicia o se duerme. Al terminar, descarga el **Excel completo** y la **copia .db** desde *Datos*.
- **Análisis del piloto:** *Análisis de ítems* (dificultad, discriminación, distractores, alfa de Cronbach) te dice qué preguntas ajustar; *Perfiles* usa K-Means de scikit-learn; *Resumen* incluye percentiles del grupo para contrastar con el baremo por criterio.

## Estructura

```
app.py          interfaz del estudiante y enrutamiento
docente.py      panel docente (resumen, estudiantes, ítems, perfiles, baremo, banco, datos)
banco.py        80 preguntas, textos de lectura, áreas y subcompetencias  ← edita aquí el contenido
baremo.py       puntuación, niveles, ponderación y retroalimentación
analitica.py    análisis de ítems, alfa, K-Means, percentiles (pandas / scikit-learn)
informes.py     Excel (openpyxl) y PDF individual (ReportLab)
graficos.py     gráficos Plotly
db.py           SQLite
tests/          verificar_baremo.py
```

## Límites conocidos

- La identificación es por correo (sin contraseña de estudiante): adecuada para un piloto supervisado, no para una evaluación con consecuencias formales.
- Los índices de ítems son orientativos con menos de ~30 estudiantes.
- Los resultados son diagnósticos; los cortes del baremo son los del documento y deben ajustarse al reglamento institucional.
