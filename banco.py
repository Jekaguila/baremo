"""Banco de preguntas del Baremo de Competencias (versión piloto).

Cuatro áreas x 20 preguntas = 80 ítems. Cada área tiene 4 subcompetencias de 5 ítems.
Convención: en este archivo la MEJOR opción se escribe siempre primero; la aplicación
baraja el orden de las opciones por estudiante, así que la posición no delata la clave.

Puntuación por ítem: 1.0 (mejor opción), 0.5 (opción parcialmente adecuada, solo en
ítems de juicio situacional) o 0.0.
"""

BANCO_VERSION = "piloto-1.0"

# --------------------------------------------------------------------------------------
# Áreas y subcompetencias
# --------------------------------------------------------------------------------------
AREAS = {
    "A1": {
        "nombre": "Lectura, comprensión lectora, escritura y seguimiento de indicaciones",
        "corto": "Lectura y comunicación",
        "icono": "📖",
        "descripcion": (
            "Lee textos académicos, interpreta ideas explícitas e implícitas, revisa y "
            "redacta con corrección y sigue indicaciones de varios pasos."
        ),
        "subs": {
            "lectura_literal": "Lectura y comprensión literal",
            "lectura_inferencial": "Comprensión inferencial y crítica",
            "escritura": "Escritura y revisión de textos",
            "indicaciones": "Seguimiento de indicaciones",
        },
    },
    "A2": {
        "nombre": "Habilidades para la vida",
        "corto": "Habilidades para la vida",
        "icono": "🧭",
        "descripcion": (
            "Decide y actúa en situaciones profesionales reales: pensamiento crítico, "
            "comunicación asertiva, autogestión y ética digital."
        ),
        "subs": {
            "pensamiento_critico": "Pensamiento crítico y resolución de problemas",
            "comunicacion": "Comunicación asertiva y trabajo colaborativo",
            "autogestion": "Autogestión: tiempo, emociones y aprendizaje autónomo",
            "etica_digital": "Toma de decisiones, ética y ciudadanía digital",
        },
    },
    "A3": {
        "nombre": "Dominio de la informática educativa",
        "corto": "Informática educativa",
        "icono": "💻",
        "descripcion": (
            "Conocimientos y criterios propios de tu licenciatura: modelos, diseño y "
            "evaluación de recursos digitales, tecnologías emergentes e integración curricular."
        ),
        "subs": {
            "fundamentos": "Fundamentos y modelos de integración de las TIC",
            "diseno_evaluacion": "Diseño y evaluación de recursos digitales",
            "tecnologias": "Tecnologías emergentes y recursos digitales",
            "integracion": "Integración curricular, ética y gestión",
        },
    },
    "A4": {
        "nombre": "Entornos virtuales de aprendizaje, Moodle y educación en línea",
        "corto": "EVA, Moodle y educación en línea",
        "icono": "🎓",
        "descripcion": (
            "Lo desarrollado en la especialización: gestión de Moodle, actividades y "
            "calificación, diseño y facilitación en línea, evaluación e integridad."
        ),
        "subs": {
            "moodle_gestion": "Gestión y configuración de Moodle",
            "moodle_actividades": "Actividades, recursos y calificación en Moodle",
            "diseno_linea": "Diseño y facilitación de cursos en línea",
            "evaluacion_linea": "Evaluación, retroalimentación e integridad en línea",
        },
    },
}

# --------------------------------------------------------------------------------------
# Textos de lectura
# --------------------------------------------------------------------------------------
TEXTOS = {
    "A1-T1": {
        "titulo": "Texto 1 · La retroalimentación formativa en línea",
        "texto": (
            "La retroalimentación formativa es la información que recibe una persona sobre "
            "su desempeño con el propósito de mejorar su aprendizaje mientras este todavía "
            "está en proceso. En los cursos en línea su valor aumenta, porque el estudiante "
            "no siempre cuenta con el docente para resolver dudas de inmediato. Por eso, una "
            "devolución eficaz debe llegar a tiempo, ser específica y orientar los siguientes "
            "pasos.\n\n"
            "Una calificación sin comentarios indica cuánto se logró, pero no explica por qué "
            "ni cómo avanzar. En cambio, un comentario como «tu tesis es clara, pero falta "
            "evidencia en el segundo párrafo; agrega al menos dos fuentes» señala un logro, "
            "un vacío y una acción concreta. Además, la retroalimentación puede provenir de "
            "varias fuentes: el docente, los compañeros mediante la evaluación entre pares, o "
            "el propio estudiante cuando se autoevalúa con una rúbrica.\n\n"
            "Sin embargo, los comentarios por sí solos no garantizan el aprendizaje. Si el "
            "estudiante no tiene oportunidad de aplicar las sugerencias en una nueva versión "
            "de su trabajo, la información pierde utilidad. Por ello, muchos docentes permiten "
            "entregas en borrador y reservan la calificación final para la versión corregida."
        ),
    },
    "A1-T2": {
        "titulo": "Texto 2 · La inteligencia artificial en las aulas: ¿prohibir o rediseñar?",
        "texto": (
            "Cuando las herramientas de inteligencia artificial generativa llegaron a las "
            "aulas, muchas instituciones reaccionaron prohibiéndolas. La intención era proteger "
            "la honestidad académica: si un programa redacta un ensayo en segundos, ¿cómo saber "
            "qué aprendió el estudiante? Sin embargo, la prohibición total plantea un problema "
            "práctico: no existe un método infalible para detectar el uso de estas herramientas, "
            "de modo que las normas terminan aplicándose de forma desigual.\n\n"
            "Otros docentes han optado por rediseñar las tareas. En lugar de pedir un texto "
            "genérico, solicitan que el estudiante explique su proceso, relacione el tema con su "
            "contexto o defienda oralmente sus decisiones. Estas estrategias no eliminan por "
            "completo el riesgo, pero hacen más visible el razonamiento propio.\n\n"
            "Quienes defienden la integración de la IA señalan que los futuros profesionales "
            "deberán usarla con criterio. Aun así, reconocen que usarla bien exige competencias "
            "previas —leer con espíritu crítico, verificar fuentes, redactar con claridad— que se "
            "desarrollan justamente practicándolas sin atajos. Por eso, el debate no consiste "
            "únicamente en permitir o prohibir, sino en decidir en qué momentos la herramienta "
            "apoya el aprendizaje y en cuáles lo reemplaza."
        ),
    },
}

# --------------------------------------------------------------------------------------
# Construcción de ítems
# --------------------------------------------------------------------------------------
PREGUNTAS = []
_contador = {}


def _q(area, sub, enunciado, mejor, otros, explicacion, parcial=None, texto=None):
    """Registra una pregunta. `mejor` va primero; `parcial` debe ser una de `otros`."""
    assert len(otros) == 3, f"{area}/{sub}: se esperan 4 opciones en total"
    _contador[area] = _contador.get(area, 0) + 1
    opciones = [mejor] + list(otros)
    parciales = [opciones.index(parcial)] if parcial else []
    PREGUNTAS.append(
        {
            "id": f"{area}-{_contador[area]:02d}",
            "area": area,
            "sub": sub,
            "texto": texto,
            "enunciado": enunciado,
            "opciones": opciones,
            "correcta": 0,
            "parciales": parciales,
            "explicacion": explicacion,
        }
    )


# ======================================================================================
# ÁREA 1 · Lectura, comprensión lectora, escritura y seguimiento de indicaciones
# ======================================================================================
# --- Lectura y comprensión literal (Texto 1) -----------------------------------------
_q("A1", "lectura_literal",
   "Según el texto, ¿cuál es el propósito principal de la retroalimentación formativa?",
   "Mejorar el aprendizaje mientras el proceso todavía está en curso.",
   ["Asignar una calificación definitiva al finalizar el curso.",
    "Comparar el desempeño de un estudiante con el de sus compañeros.",
    "Sustituir la intervención del docente en los cursos en línea."],
   "El primer párrafo la define como información para mejorar el aprendizaje «mientras este todavía está en proceso».",
   texto="A1-T1")
_q("A1", "lectura_literal",
   "De acuerdo con el texto, ¿por qué la retroalimentación cobra mayor valor en los cursos en línea?",
   "Porque el estudiante no siempre puede consultar al docente de inmediato.",
   ["Porque los estudiantes en línea suelen obtener calificaciones más bajas.",
    "Porque las plataformas virtuales impiden la evaluación entre pares.",
    "Porque en los cursos en línea no se pueden utilizar rúbricas."],
   "El texto lo explica con una razón explícita: el estudiante no siempre cuenta con el docente para resolver dudas de inmediato.",
   texto="A1-T1")
_q("A1", "lectura_literal",
   "¿Qué tres características debe tener, según el texto, una devolución eficaz?",
   "Llegar a tiempo, ser específica y orientar los siguientes pasos.",
   ["Ser breve, anónima y expresada en números.",
    "Ser extensa, general y entregarse después de la calificación final.",
    "Provenir solo del docente, ser pública y estar calificada."],
   "Las tres características aparecen literalmente al final del primer párrafo.",
   texto="A1-T1")
_q("A1", "lectura_literal",
   "El ejemplo «tu tesis es clara, pero falta evidencia en el segundo párrafo…» se incluye en el texto para ilustrar:",
   "Un comentario que señala un logro, un vacío y una acción concreta.",
   ["Una calificación entregada sin ningún comentario.",
    "Un caso de autoevaluación mediante una rúbrica.",
    "Una devolución que llega demasiado tarde para ser útil."],
   "El propio texto indica que el ejemplo «señala un logro, un vacío y una acción concreta».",
   texto="A1-T1")
_q("A1", "lectura_literal",
   "¿Qué práctica docente menciona el último párrafo para aprovechar mejor los comentarios?",
   "Permitir entregas en borrador y reservar la calificación final para la versión corregida.",
   ["Eliminar la calificación final de los trabajos.",
    "Pedir a los estudiantes que califiquen el desempeño de sus docentes.",
    "Entregar los comentarios únicamente al terminar el curso."],
   "El último párrafo propone entregas en borrador para que el estudiante aplique las sugerencias.",
   texto="A1-T1")

# --- Comprensión inferencial y crítica (Texto 2) -------------------------------------
_q("A1", "lectura_inferencial",
   "¿Cuál es la idea central del texto?",
   "El debate sobre la IA en la educación consiste en decidir cuándo apoya el aprendizaje y cuándo lo reemplaza, más que en permitir o prohibir.",
   ["La IA generativa debe prohibirse porque pone en riesgo la honestidad académica.",
    "Los docentes que rediseñan las tareas han eliminado por completo el uso indebido de la IA.",
    "Los futuros profesionales no necesitarán leer ni redactar gracias a la IA."],
   "El último párrafo sintetiza la tesis: el debate va más allá de «permitir o prohibir».",
   texto="A1-T2")
_q("A1", "lectura_inferencial",
   "Del texto se puede inferir que las normas de prohibición total «se aplican de forma desigual» porque:",
   "No existe una forma segura de detectar quién usó la herramienta.",
   ["Los estudiantes siempre aceptan las normas sin cuestionarlas.",
    "Los docentes desconocen el contenido de sus propios cursos.",
    "Las instituciones no tienen interés en la honestidad académica."],
   "El texto afirma que no hay un método infalible de detección; de ahí se infiere la aplicación desigual.",
   texto="A1-T2")
_q("A1", "lectura_inferencial",
   "En el último párrafo, la expresión «sin atajos» se refiere a:",
   "Practicar directamente las competencias, sin sustituirlas por la herramienta.",
   ["Evitar cualquier tecnología durante todo el proceso educativo.",
    "Terminar las tareas en el menor tiempo posible.",
    "Copiar el trabajo de compañeros con mejor desempeño."],
   "Las competencias previas «se desarrollan justamente practicándolas», es decir, sin delegarlas en la herramienta.",
   texto="A1-T2")
_q("A1", "lectura_inferencial",
   "¿Qué función cumple el segundo párrafo dentro del texto?",
   "Presentar una alternativa a la prohibición: rediseñar las tareas.",
   ["Refutar a quienes defienden la integración de la IA.",
    "Demostrar que la IA no puede redactar ensayos.",
    "Resumir los argumentos del primer párrafo."],
   "El segundo párrafo abre con «Otros docentes han optado por rediseñar las tareas».",
   texto="A1-T2")
_q("A1", "lectura_inferencial",
   "¿Cuál de las siguientes afirmaciones NO está respaldada por el texto?",
   "Pedir al estudiante que explique su proceso elimina por completo el riesgo de uso indebido de la IA.",
   ["No existe un método infalible para detectar el uso de herramientas de IA.",
    "Usar bien la IA exige competencias previas como verificar fuentes y redactar con claridad.",
    "Una misma herramienta puede apoyar el aprendizaje en un momento y reemplazarlo en otro."],
   "El texto dice que esas estrategias «no eliminan por completo el riesgo»; las otras tres afirmaciones sí aparecen.",
   texto="A1-T2")

# --- Escritura y revisión de textos --------------------------------------------------
_q("A1", "escritura",
   "Seleccione la oración correctamente escrita y puntuada:",
   "Los estudiantes que aprobaron el curso recibirán su constancia.",
   ["Los estudiantes, que aprobaron el curso recibirán su constancia.",
    "Los estudiantes que aprobaron, el curso recibirán su constancia.",
    "Los estudiantes que aprobaron el curso, recibirán su constancia."],
   "No se separa con coma el sujeto del verbo; además, la oración especificativa no lleva comas.")
_q("A1", "escritura",
   "Complete la oración: «Quiero saber ______ no has entregado la actividad».",
   "por qué",
   ["porque", "porqué", "por que"],
   "En una pregunta indirecta se usa «por qué» (dos palabras, con tilde).")
_q("A1", "escritura",
   "Elija el conector que completa mejor el sentido: «El curso es virtual; ______, los estudiantes deben organizar su tiempo de estudio de manera autónoma».",
   "por lo tanto",
   ["sin embargo", "en cambio", "aunque"],
   "La segunda idea es consecuencia de la primera; «por lo tanto» expresa consecuencia.")
_q("A1", "escritura",
   "¿Cuál redacción es la más adecuada para escribir a un docente en un foro o mensaje formal?",
   "Estimado profesor: le escribo para consultarle si es posible ampliar el plazo de entrega de la actividad 3. Quedo atento a su respuesta. Saludos cordiales.",
   ["Profe, ¿me da más tiempo pa la actividad 3? Gracias.",
    "Necesito más tiempo, la actividad 3 está difícil.",
    "ola profe puedo entregar después la actividad 3"],
   "Combina saludo, motivo claro, tono respetuoso, corrección ortográfica y cierre cortés (registro formal).")
_q("A1", "escritura",
   "Ordene las oraciones para formar un párrafo coherente: (1) Por ello, es recomendable establecer un horario fijo de estudio. (2) En los cursos en línea, el estudiante administra su propio tiempo. (3) Sin una rutina clara, las tareas tienden a acumularse. (4) Esa libertad exige un alto nivel de autorregulación.",
   "2 – 4 – 3 – 1",
   ["3 – 2 – 4 – 1", "1 – 2 – 4 – 3", "4 – 3 – 2 – 1"],
   "La secuencia presenta la situación (2), su exigencia (4), el problema que surge (3) y la recomendación (1).")

# --- Seguimiento de indicaciones -----------------------------------------------------
_q("A1", "indicaciones",
   "Siga estas indicaciones: 1) Escriba el número 8. 2) Multiplíquelo por 3. 3) Réstele 4. 4) Divida el resultado entre 5. ¿Cuál es el resultado final?",
   "4",
   ["5", "2", "20"],
   "8 × 3 = 24; 24 − 4 = 20; 20 ÷ 5 = 4.")
_q("A1", "indicaciones",
   "Indicación del foro: «Publique su respuesta en el hilo principal, incluya al menos una referencia en formato APA y responda a un compañero antes del viernes». ¿Cuál de las siguientes entregas cumple TODAS las indicaciones?",
   "Una publicación en el hilo principal con una referencia APA y una respuesta a un compañero enviada el jueves.",
   ["Una publicación con tres referencias APA, sin respuesta a ningún compañero, enviada el miércoles.",
    "Un enlace a un documento externo con la respuesta, una referencia APA y una respuesta a un compañero.",
    "Una publicación en el hilo principal con una referencia APA y una respuesta a un compañero enviada el sábado."],
   "Las demás opciones omiten una condición: responder a un compañero, publicar la respuesta en el hilo o entregar antes del viernes.")
_q("A1", "indicaciones",
   "Indicaciones: (a) todo archivo debe entregarse en PDF; (b) si pesa más de 10 MB, debe comprimirse antes de subirlo; (c) el nombre debe ser Apellido_Actividad. Su trabajo está en .docx, pesa 14 MB, usted se apellida Rivas y es la Actividad 2. ¿Qué secuencia es correcta?",
   "Convertirlo a PDF, comprimirlo si aún supera 10 MB, nombrarlo Rivas_Actividad2 y subirlo.",
   ["Subirlo en .docx con el nombre Rivas_Actividad2, porque el peso no importa.",
    "Convertirlo a PDF y subirlo con el nombre Actividad2_Rivas.",
    "Comprimirlo en .docx y subirlo con el nombre Rivas."],
   "Deben cumplirse las tres condiciones: formato PDF, compresión si excede 10 MB y nombre Apellido_Actividad.")
_q("A1", "indicaciones",
   "Lea: «La actividad se habilita el lunes a las 8:00 a. m., permanece abierta 72 horas y no admite entregas tardías». ¿Hasta qué momento puede entregarse?",
   "Hasta el jueves a las 8:00 a. m.",
   ["Hasta el miércoles a las 8:00 a. m.",
    "Hasta el jueves a las 11:59 p. m.",
    "Hasta el viernes a las 8:00 a. m."],
   "72 horas equivalen a 3 días: lunes 8:00 a. m. + 3 días = jueves 8:00 a. m.")
_q("A1", "indicaciones",
   "Se le pide: «Responda en una sola oración, en tercera persona, sin usar la palabra “muy” y con un máximo de 12 palabras. Pregunta: ¿qué es el aprendizaje autónomo?». ¿Cuál respuesta cumple TODAS las condiciones?",
   "El aprendizaje autónomo es la capacidad de dirigir el propio estudio.",
   ["Es muy importante porque el estudiante aprende por sí mismo.",
    "Es cuando yo organizo mi aprendizaje sin depender de otros.",
    "El aprendizaje autónomo es la capacidad de dirigir el propio proceso de estudio con disciplina."],
   "La correcta tiene 11 palabras, una sola oración y tercera persona. Las otras usan «muy», primera persona o superan las 12 palabras.")

# ======================================================================================
# ÁREA 2 · Habilidades para la vida (juicio situacional; hay opciones con crédito parcial)
# ======================================================================================
# --- Pensamiento crítico y resolución de problemas -----------------------------------
_q("A2", "pensamiento_critico",
   "Un colega comparte en el grupo de docentes el titular: «Estudio demuestra que el 90 % de los estudiantes aprende mejor con videojuegos». No cita la fuente. ¿Qué haces primero?",
   "Buscar el estudio original y revisar quién lo realizó, la muestra y la metodología antes de usarlo o compartirlo.",
   ["Preguntar al colega de dónde lo tomó y esperar su respuesta antes de decidir.",
    "Reenviarlo a otros grupos porque confirma lo que ya pensabas.",
    "Descartarlo de inmediato porque las cifras tan altas siempre son falsas."],
   "El pensamiento crítico exige contrastar con la fuente primaria; ni aceptar ni rechazar sin evidencia.",
   parcial="Preguntar al colega de dónde lo tomó y esperar su respuesta antes de decidir.")
_q("A2", "pensamiento_critico",
   "La participación en los foros de tu curso en Moodle bajó de 70 % a 30 % en tres semanas. ¿Cuál es la mejor primera acción?",
   "Recoger evidencia (informes de actividad y una consulta breve a los estudiantes) para identificar causas antes de cambiar algo.",
   ["Enviar un recordatorio general a todos sobre la importancia de participar.",
    "Hacer obligatoria la participación con descuento de puntos desde la próxima semana.",
    "Esperar, porque probablemente se recupere por sí sola."],
   "Resolver problemas empieza por diagnosticar causas con datos; actuar sin diagnóstico puede agravar la situación.",
   parcial="Enviar un recordatorio general a todos sobre la importancia de participar.")
_q("A2", "pensamiento_critico",
   "Debes elegir entre dos soluciones: la A es más rápida pero requiere un software de pago que tus estudiantes no tienen; la B tarda más pero usa herramientas gratuitas. ¿Qué criterio es más sólido para decidir?",
   "Valorar el impacto de cada opción en el logro del objetivo y en la accesibilidad para todos los estudiantes.",
   ["Consultar cuál opción prefiere la mayoría de tus colegas.",
    "Elegir la A porque el tiempo siempre es el factor más importante.",
    "Elegir la B por ser gratuita, sin considerar si cumple el objetivo."],
   "Se decide con criterios explícitos ligados al objetivo y a la equidad, no por costumbre, moda o un solo factor.",
   parcial="Consultar cuál opción prefiere la mayoría de tus colegas.")
_q("A2", "pensamiento_critico",
   "«Todos los estudiantes que entregaron el proyecto aprobaron el módulo. Marta aprobó el módulo.» ¿Qué conclusión es válida?",
   "Es posible que Marta haya entregado el proyecto, pero no puede afirmarse con certeza.",
   ["Marta entregó el proyecto.",
    "Marta no entregó el proyecto.",
    "Marta aprobó porque es una buena estudiante."],
   "Haber aprobado no implica haber entregado: otras personas pudieron aprobar sin entregarlo (falacia de afirmar el consecuente).")
_q("A2", "pensamiento_critico",
   "Se analiza por qué el 40 % de los estudiantes no completó un curso virtual. Un compañero afirma: «Seguro es porque los jóvenes ya no tienen disciplina». ¿Qué respuesta muestra pensamiento crítico?",
   "«Es una suposición; propongo revisar datos de acceso, horarios, conectividad y razones de abandono antes de concluir.»",
   ["«Puede ser, aunque podrían existir otras causas.»",
    "«Estoy de acuerdo; es una explicación que se escucha mucho.»",
    "«Esa idea es absurda y no merece discutirse.»"],
   "Distingue opinión de evidencia y propone cómo comprobar la hipótesis, sin descalificar a la persona.",
   parcial="«Puede ser, aunque podrían existir otras causas.»")

# --- Comunicación asertiva y trabajo colaborativo -------------------------------------
_q("A2", "comunicacion",
   "En un trabajo en equipo virtual, un integrante aún no entrega su parte y faltan dos días para la fecha límite. ¿Qué haces?",
   "Escribirle de forma directa y respetuosa, preguntarle si necesita apoyo y acordar una fecha concreta para su aporte.",
   ["Reasignar su parte a otro integrante para asegurar la entrega.",
    "Publicar en el chat grupal que no está cumpliendo para presionarlo.",
    "Hacer su parte en silencio y no decirle nada."],
   "La asertividad combina claridad, respeto y un acuerdo concreto; reasignar sin hablar resuelve el plazo pero no la causa.",
   parcial="Reasignar su parte a otro integrante para asegurar la entrega.")
_q("A2", "comunicacion",
   "Un estudiante te dice que tus comentarios en el foro son «fríos». ¿Cuál es la respuesta más asertiva?",
   "Agradecer la observación, pedir un ejemplo concreto y explicar cómo puedes ajustar el tono.",
   ["Agradecer, pero aclarar que tu intención nunca fue ser frío.",
    "Ignorarlo porque es solo una opinión.",
    "Responder públicamente defendiendo tu estilo."],
   "Recibir críticas con apertura y pedir precisión permite mejorar sin ponerse a la defensiva.",
   parcial="Agradecer, pero aclarar que tu intención nunca fue ser frío.")
_q("A2", "comunicacion",
   "Necesitas la parte del informe de un compañero que no responde tus mensajes. ¿Cuál mensaje es más asertivo?",
   "«Hola, Luis. Necesito tu parte del informe para el jueves. ¿Podrías enviármela el miércoles? Si tienes algún inconveniente, dímelo y lo resolvemos.»",
   ["«Hola, Luis. Te recuerdo que el informe se entrega el jueves, ¿cómo vas?»",
    "«Luis, siempre eres el último en responder. Esta vez no voy a esperarte.»",
    "«Hola, ¿viste mi mensaje?»"],
   "Incluye petición clara, plazo, apertura al diálogo y ningún reproche personal.",
   parcial="«Hola, Luis. Te recuerdo que el informe se entrega el jueves, ¿cómo vas?»")
_q("A2", "comunicacion",
   "En una videollamada, dos compañeros interrumpen constantemente a otra persona. Como moderador/a, ¿qué haces?",
   "Recordar los acuerdos de participación y ceder la palabra a la persona interrumpida para que termine su idea.",
   ["Esperar a que terminen y luego pedir en privado que no vuelva a ocurrir.",
    "Dejar que se resuelva solo para no generar conflicto.",
    "Pasar a otro tema para evitar tensión."],
   "Intervenir en el momento, con base en acuerdos previos, protege la participación equitativa.",
   parcial="Esperar a que terminen y luego pedir en privado que no vuelva a ocurrir.")
_q("A2", "comunicacion",
   "Tu equipo está dividido sobre qué herramienta usar en un proyecto. ¿Qué estrategia favorece mejor la colaboración?",
   "Definir criterios comunes (objetivo, costo, facilidad de uso), valorar cada opción con ellos y decidir con base en los resultados.",
   ["Votar y aceptar lo que decida la mayoría sin más discusión.",
    "Que decida la persona con más experiencia.",
    "Dividir al equipo en dos proyectos distintos."],
   "Los criterios compartidos convierten un desacuerdo de preferencias en una decisión argumentada.",
   parcial="Votar y aceptar lo que decida la mayoría sin más discusión.")

# --- Autogestión ----------------------------------------------------------------------
_q("A2", "autogestion",
   "Tienes cuatro pendientes: (A) examen mañana, 20 % de la nota; (B) tarea para la próxima semana, 10 %; (C) revisar el correo, sin urgencia; (D) un foro que cierra hoy, 5 %, requiere 15 minutos. ¿Cuál es el orden más razonable?",
   "Participar primero en el foro (cierra hoy y toma poco tiempo), luego estudiar para el examen, después avanzar la tarea y dejar el correo al final.",
   ["Estudiar para el examen y, si queda tiempo hoy, participar en el foro.",
    "Revisar primero el correo para no perder nada importante y luego decidir.",
    "Empezar por la tarea de la próxima semana porque requiere más preparación."],
   "Se combina urgencia (plazo) e importancia (peso): lo que vence hoy y es breve se resuelve primero.",
   parcial="Estudiar para el examen y, si queda tiempo hoy, participar en el foro.")
_q("A2", "autogestion",
   "Estás sobrecargado/a entre trabajo, estudios y familia, y llevas una semana durmiendo poco con menor rendimiento. ¿Qué estrategia es más adecuada?",
   "Revisar tus compromisos, priorizar, renegociar o delegar plazos cuando sea posible y proteger tus horas de descanso.",
   ["Mantener el ritmo, apoyándote en pausas breves de descanso durante el día.",
    "Eliminar las actividades de ocio porque no son productivas.",
    "Esperar a que pase la temporada de mayor carga sin cambiar nada."],
   "Gestionar la carga implica decisiones sobre prioridades y límites, no solo resistir.",
   parcial="Mantener el ritmo, apoyándote en pausas breves de descanso durante el día.")
_q("A2", "autogestion",
   "No aprobaste una evaluación importante de un curso en línea. ¿Qué actitud favorece más tu aprendizaje?",
   "Analizar qué falló (estrategia, tiempo, comprensión), pedir retroalimentación y plantear acciones para el siguiente intento.",
   ["Repasar todo el contenido de nuevo desde el principio.",
    "Concluir que el curso estaba mal diseñado.",
    "Pensar que no tienes capacidad para este tipo de contenido."],
   "El error se usa como información para ajustar la estrategia (mentalidad de crecimiento).",
   parcial="Repasar todo el contenido de nuevo desde el principio.")
_q("A2", "autogestion",
   "Debes dominar una herramienta nueva (por ejemplo, un complemento de Moodle) sin ayuda de un docente. ¿Qué estrategia es más efectiva?",
   "Definir un objetivo concreto, consultar documentación oficial y tutoriales confiables, practicar en un curso de prueba y registrar lo aprendido.",
   ["Ver un video tutorial completo y luego usarla directamente en tu curso real.",
    "Esperar a que alguien más te la explique.",
    "Probar opciones al azar hasta que funcione."],
   "El aprendizaje autónomo combina meta, fuentes confiables, práctica segura y registro.",
   parcial="Ver un video tutorial completo y luego usarla directamente en tu curso real.")
_q("A2", "autogestion",
   "Un estudiante te envía un mensaje agresivo por una calificación y sientes enojo. ¿Qué haces primero?",
   "Pausar, respirar y responder después con calma, centrándote en los criterios de evaluación.",
   ["Consultar con un colega o coordinador cómo responder antes de contestar.",
    "Responder en el mismo tono para establecer límites.",
    "Ignorar el mensaje y no responder."],
   "Regular la emoción antes de responder permite una comunicación profesional y basada en criterios.",
   parcial="Consultar con un colega o coordinador cómo responder antes de contestar.")

# --- Toma de decisiones, ética y ciudadanía digital -----------------------------------
_q("A2", "etica_digital",
   "Quieres usar en tu curso una imagen encontrada en un buscador, sin información de licencia. ¿Qué es lo más adecuado?",
   "Verificar la licencia; si no permite el uso, elegir otra con licencia abierta o pedir permiso al autor, y dar siempre el crédito.",
   ["Usarla citando la fuente, aunque no puedas verificar la licencia.",
    "Usarla porque es con fines educativos y todo contenido educativo es de uso libre.",
    "Descargarla y quitar la marca de agua si la tiene."],
   "Que un contenido sea accesible en internet no significa que sea de uso libre; hay que verificar licencia y atribuir.",
   parcial="Usarla citando la fuente, aunque no puedas verificar la licencia.")
_q("A2", "etica_digital",
   "Un estudiante te pide las calificaciones de sus compañeros para «comparar su avance». ¿Qué haces?",
   "Explicar que son confidenciales y ofrecer estadísticas generales anónimas (por ejemplo, el promedio del grupo).",
   ["Negarte sin ofrecer ninguna alternativa.",
    "Compartirlas porque forma parte del mismo grupo.",
    "Compartirlas solo con los estudiantes de mejor desempeño."],
   "Se protege la privacidad y, a la vez, se atiende la necesidad legítima de referencia.",
   parcial="Negarte sin ofrecer ninguna alternativa.")
_q("A2", "etica_digital",
   "Quieres usar una herramienta de IA para generar retroalimentación sobre los trabajos de tus estudiantes. ¿Cuál es la práctica más responsable?",
   "Evitar ingresar datos personales identificables, revisar y ajustar cada retroalimentación antes de enviarla e informar a los estudiantes que usas IA.",
   ["Usarla para borradores sin ingresar nombres y enviar lo generado si te parece correcto.",
    "Pegar los trabajos completos con nombre y número de carné para darle más contexto.",
    "Enviar la retroalimentación tal como la genera para ahorrar tiempo."],
   "Privacidad, supervisión humana y transparencia son los tres pilares del uso ético de IA en evaluación.",
   parcial="Usarla para borradores sin ingresar nombres y enviar lo generado si te parece correcto.")
_q("A2", "etica_digital",
   "Descubres que un estudiante entregó un trabajo con fragmentos copiados sin citar. ¿Cuál es la decisión más justa?",
   "Revisar la evidencia, conversar con el estudiante para conocer su versión y aplicar el procedimiento institucional establecido.",
   ["Anular la actividad y notificarlo de inmediato a la coordinación.",
    "Dejarlo pasar para evitar conflictos esta vez.",
    "Publicar la situación en el foro para que sirva de ejemplo al grupo."],
   "El debido proceso exige evidencia, escuchar a la persona y seguir la norma institucional; evitar la exposición pública.",
   parcial="Anular la actividad y notificarlo de inmediato a la coordinación.")
_q("A2", "etica_digital",
   "En un grupo profesional de redes sociales, alguien publica la foto y el nombre de un estudiante menor de edad para «felicitarlo». ¿Qué haces?",
   "Pedirle de forma privada que retire la publicación, explicándole los riesgos de privacidad y la necesidad de consentimiento.",
   ["Reportarlo al administrador del grupo sin hablar antes con la persona.",
    "No hacer nada; es una felicitación y no tiene mala intención.",
    "Criticar públicamente a la persona en los comentarios."],
   "Se corrige el riesgo con respeto y pedagogía, sin exponer a la persona ni dejar pasar la vulneración de privacidad.",
   parcial="Reportarlo al administrador del grupo sin hablar antes con la persona.")

# ======================================================================================
# ÁREA 3 · Dominio de la informática educativa
# ======================================================================================
# --- Fundamentos y modelos ------------------------------------------------------------
_q("A3", "fundamentos",
   "El modelo TPACK integra tres tipos de conocimiento docente. ¿Cuáles son?",
   "Tecnológico, pedagógico y de contenido.",
   ["Técnico, psicológico y curricular.",
    "Tecnológico, administrativo y evaluativo.",
    "Teórico, práctico y actitudinal."],
   "TPACK = Technological, Pedagogical and Content Knowledge (Mishra y Koehler).")
_q("A3", "fundamentos",
   "Según el modelo SAMR, usar un procesador de texto solo para escribir lo que antes se escribía a mano, sin ningún cambio funcional, corresponde al nivel de:",
   "Sustitución.",
   ["Aumento.", "Modificación.", "Redefinición."],
   "En la sustitución la tecnología reemplaza una herramienta sin cambios funcionales (Puentedura).")
_q("A3", "fundamentos",
   "En el modelo ADDIE, ¿qué fase corresponde a determinar el perfil de los estudiantes, las necesidades de aprendizaje y las restricciones del contexto?",
   "Análisis.",
   ["Diseño.", "Desarrollo.", "Implementación."],
   "ADDIE: Análisis, Diseño, Desarrollo, Implementación y Evaluación. La primera fase diagnostica necesidades y contexto.")
_q("A3", "fundamentos",
   "¿Qué teoría sostiene que el conocimiento se construye activamente a partir de la experiencia y la interacción social, con el docente como mediador?",
   "Constructivismo.",
   ["Conductismo.", "Conectivismo.", "Aprendizaje por memorización."],
   "Es la tesis central del constructivismo (Piaget, Vygotsky, Bruner).")
_q("A3", "fundamentos",
   "El pensamiento computacional comprende, entre otras, las siguientes habilidades:",
   "Descomposición, reconocimiento de patrones, abstracción y diseño de algoritmos.",
   ["Memorización, repetición, copia y transcripción.",
    "Uso de redes sociales, edición de video y diseño gráfico.",
    "Instalación de software, mantenimiento de equipos y redes."],
   "Son los cuatro pilares clásicos del pensamiento computacional.")

# --- Diseño y evaluación de recursos digitales ----------------------------------------
_q("A3", "diseno_evaluacion",
   "En la Taxonomía de Bloom revisada (Anderson y Krathwohl), ¿cuál de estos verbos corresponde al nivel más alto, «Crear»?",
   "Diseñar.",
   ["Listar.", "Explicar.", "Comparar."],
   "Listar = recordar; explicar = comprender; comparar = analizar; diseñar = crear.")
_q("A3", "diseno_evaluacion",
   "El Diseño Universal para el Aprendizaje (DUA) propone ofrecer:",
   "Múltiples formas de representación, de acción y expresión, y de implicación.",
   ["Un único formato estándar de contenido para todos.",
    "Adaptaciones únicamente para estudiantes con discapacidad diagnosticada.",
    "Evaluaciones idénticas para garantizar la igualdad."],
   "Los tres principios del DUA (CAST) buscan reducir barreras para todos los estudiantes.")
_q("A3", "diseno_evaluacion",
   "Para que una imagen informativa de un recurso digital sea accesible a una persona que usa lector de pantalla, se debe:",
   "Incluir un texto alternativo que describa su contenido o función.",
   ["Aumentar su resolución.", "Colocarla al final de la página.", "Convertirla a blanco y negro."],
   "El texto alternativo es lo que lee el lector de pantalla (pauta WCAG 1.1.1).")
_q("A3", "diseno_evaluacion",
   "Una licencia Creative Commons BY-NC-SA permite:",
   "Compartir y adaptar la obra dando atribución, sin fines comerciales y con la misma licencia.",
   ["Usarla comercialmente sin dar atribución.",
    "Solo compartirla sin modificarla ni usarla comercialmente.",
    "Usarla sin ninguna condición, como si fuera de dominio público."],
   "BY = atribución; NC = no comercial; SA = compartir igual.")
_q("A3", "diseno_evaluacion",
   "Una rúbrica analítica se distingue de una holística porque:",
   "Desglosa criterios con niveles de desempeño para cada uno y permite una retroalimentación detallada.",
   ["Asigna una sola calificación global sin criterios separados.",
    "Solo puede usarse con pruebas de opción múltiple.",
    "No requiere descriptores de desempeño."],
   "La analítica valora cada criterio por separado; la holística emite un juicio global.")

# --- Tecnologías emergentes y recursos digitales --------------------------------------
_q("A3", "tecnologias",
   "¿Cuál describe mejor la gamificación en educación?",
   "Usar elementos y mecánicas de juego (puntos, insignias, retos) en contextos no lúdicos para motivar el aprendizaje.",
   ["Usar videojuegos comerciales como único recurso de enseñanza.",
    "Sustituir la evaluación por juegos sin objetivos de aprendizaje.",
    "Enseñar a programar videojuegos como materia obligatoria."],
   "Gamificar es aplicar elementos de juego al diseño de la experiencia de aprendizaje, no jugar sin más.")
_q("A3", "tecnologias",
   "La analítica del aprendizaje (learning analytics) consiste en:",
   "Recopilar y analizar datos de la actividad de los estudiantes para comprender y mejorar el aprendizaje y su entorno.",
   ["Calificar automáticamente todas las tareas sin intervención docente.",
    "Medir únicamente el tiempo que el estudiante permanece conectado.",
    "Almacenar copias de seguridad de los cursos."],
   "Se trata de usar datos para tomar decisiones pedagógicas, no solo de recolectarlos.")
_q("A3", "tecnologias",
   "Los Recursos Educativos Abiertos (REA) se caracterizan por:",
   "Tener licencias abiertas que permiten su acceso, reutilización, adaptación y redistribución.",
   ["Ser siempre gratuitos aunque prohíban su modificación.",
    "Estar disponibles solo dentro de una institución.",
    "Ser exclusivamente videos educativos."],
   "La licencia abierta (permisos de las «5R») es lo que define a un REA, no solo la gratuidad.")
_q("A3", "tecnologias",
   "Un riesgo propio de los modelos de lenguaje al usarlos como fuente de información académica es que:",
   "Pueden generar contenido plausible pero inexacto o inventado, por lo que debe verificarse.",
   ["Solo funcionan con textos en inglés.",
    "No pueden reutilizar ningún texto previo.",
    "Siempre citan fuentes verificables."],
   "Las llamadas «alucinaciones» exigen contrastar la información con fuentes confiables.")
_q("A3", "tecnologias",
   "¿Qué es SCORM?",
   "Un conjunto de especificaciones para empaquetar contenidos de e-learning de modo que puedan ejecutarse y reportar resultados en distintos LMS.",
   ["Un lenguaje de programación para crear plataformas educativas.",
    "Un tipo de licencia para recursos abiertos.",
    "Un protocolo de videoconferencia."],
   "SCORM (Sharable Content Object Reference Model) estandariza la interoperabilidad de contenidos.")

# --- Integración curricular, ética y gestión ------------------------------------------
_q("A3", "integracion",
   "En la alineación constructiva (Biggs) se espera que:",
   "Los resultados de aprendizaje, las actividades y la evaluación sean coherentes entre sí.",
   ["La evaluación sea independiente de los objetivos.",
    "Las actividades se elijan según la tecnología disponible.",
    "Los objetivos se definan después de evaluar."],
   "La coherencia entre objetivos, actividades y evaluación es el núcleo del enfoque.")
_q("A3", "integracion",
   "Una evaluación diagnóstica en un curso virtual se aplica principalmente:",
   "Al inicio, para conocer saberes previos y ajustar la planificación.",
   ["Al final, para certificar el aprendizaje.",
    "Durante todo el curso, como única calificación.",
    "Solo cuando el estudiante reprueba."],
   "La función diagnóstica orienta decisiones de diseño antes de enseñar.")
_q("A3", "integracion",
   "Un docente que integra tecnología con sentido pedagógico parte de:",
   "Los objetivos de aprendizaje y las necesidades de los estudiantes, para luego elegir la herramienta adecuada.",
   ["Elegir la herramienta más novedosa y luego adaptarle un objetivo.",
    "Usar la misma herramienta en todas las clases.",
    "Evitar las tecnologías gratuitas."],
   "La pedagogía guía a la tecnología, no al revés.")
_q("A3", "integracion",
   "En el uso de plataformas digitales con estudiantes, una buena práctica de protección de datos personales es:",
   "Recopilar solo los datos necesarios, informar su finalidad y restringir el acceso a quienes lo requieran.",
   ["Recopilar la mayor cantidad posible de datos por si sirven en el futuro.",
    "Compartir listados con nombres y calificaciones en canales abiertos por transparencia.",
    "Usar una misma contraseña compartida para todo el equipo docente."],
   "Minimización de datos, finalidad informada y control de acceso.")
_q("A3", "integracion",
   "En el aula invertida (flipped classroom):",
   "Los estudiantes revisan los contenidos antes de la sesión y el tiempo de clase se dedica a aplicar, discutir y resolver problemas.",
   ["Los estudiantes dan la clase en lugar del docente.",
    "Se elimina la evaluación del proceso.",
    "Toda la clase es asincrónica y no hay interacción."],
   "Se «invierte» el uso del tiempo: la exposición se hace antes y la clase se usa para la práctica activa.")

# ======================================================================================
# ÁREA 4 · EVA, Moodle y educación en línea
# ======================================================================================
# --- Gestión y configuración de Moodle ------------------------------------------------
_q("A4", "moodle_gestion",
   "En Moodle, ¿qué rol permite ver y calificar las actividades de un curso sin poder modificar su estructura ni configuración?",
   "Profesor sin permiso de edición.",
   ["Estudiante.", "Gestor.", "Creador de curso."],
   "El profesor sin permiso de edición puede calificar y participar en el curso, pero no editar su contenido.")
_q("A4", "moodle_gestion",
   "¿Qué método de matriculación permite que los estudiantes se inscriban por sí mismos, con posibilidad de proteger el acceso con una clave?",
   "Automatriculación.",
   ["Matriculación manual.", "Sincronización de cohortes.", "Acceso de invitados."],
   "La automatriculación admite una «clave de matriculación» opcional.")
_q("A4", "moodle_gestion",
   "Para que los estudiantes de cada grupo solo vean las aportaciones de su propio grupo en una actividad, el modo de grupo debe ser:",
   "Grupos separados.",
   ["Sin grupos.", "Grupos visibles.", "Solo agrupamientos, sin modo de grupo."],
   "En grupos separados cada grupo ve únicamente su propio trabajo; en grupos visibles pueden ver los demás.")
_q("A4", "moodle_gestion",
   "Quieres que la Unidad 2 solo aparezca a quienes hayan completado una actividad de la Unidad 1. ¿Qué combinación de funciones usas?",
   "Finalización de actividad en la Unidad 1 y restricción de acceso en la Unidad 2 basada en esa finalización.",
   ["Grupos y agrupamientos.",
    "Calificador y escalas.",
    "Copias de seguridad y restauración."],
   "La finalización de actividad se combina con «Restringir acceso» para crear rutas condicionadas.")
_q("A4", "moodle_gestion",
   "Para reutilizar en otro semestre la estructura de un curso, conservando actividades y recursos, es adecuado:",
   "Usar la copia de seguridad y restauración, o la función de importar contenido de otro curso.",
   ["Exportar el libro de calificaciones a Excel.",
    "Crear una cohorte con los estudiantes anteriores.",
    "Configurar la finalización del curso."],
   "Ambas herramientas copian actividades, recursos y su configuración.")

# --- Actividades, recursos y calificación ---------------------------------------------
_q("A4", "moodle_actividades",
   "¿Qué tipo de foro de Moodle exige que el estudiante publique su propia respuesta antes de poder ver las de sus compañeros?",
   "Foro de preguntas y respuestas.",
   ["Foro para uso general.", "Foro de avisos.", "Un solo debate simple."],
   "En el foro de preguntas y respuestas cada estudiante debe publicar primero; después accede a las demás respuestas.")
_q("A4", "moodle_actividades",
   "¿Qué actividad de Moodle permite la evaluación entre pares: los estudiantes envían un trabajo y evalúan los de sus compañeros con criterios definidos por el docente?",
   "Taller.",
   ["Lección.", "Glosario.", "Elección."],
   "El Taller (Workshop) gestiona envío, asignación de evaluadores, evaluación y calificación por pares.")
_q("A4", "moodle_actividades",
   "Una pregunta de tipo Ensayo en un cuestionario de Moodle:",
   "Requiere calificación manual por parte del docente.",
   ["Se califica automáticamente comparando palabras clave.",
    "Solo admite respuestas numéricas.",
    "No puede incluir retroalimentación."],
   "Las preguntas de ensayo no se autocalifican: quedan pendientes de revisión.")
_q("A4", "moodle_actividades",
   "En el libro de calificaciones de Moodle, las categorías sirven para:",
   "Agrupar ítems de calificación y definir cómo se agregan (por ejemplo, promedio ponderado o suma) para obtener la nota total.",
   ["Clasificar a los estudiantes por nivel socioeconómico.",
    "Crear grupos de trabajo.",
    "Definir los roles de los usuarios."],
   "Cada categoría tiene su método de agregación y puede ponderarse dentro del total.")
_q("A4", "moodle_actividades",
   "En un cuestionario con varios intentos permitidos, ¿qué ajuste determina cómo se calcula la calificación final (la más alta, el promedio, el primer o el último intento)?",
   "Método de calificación.",
   ["Comportamiento de las preguntas.", "Modo de grupo.", "Barajar dentro de las preguntas."],
   "«Comportamiento de las preguntas» controla cómo y cuándo se muestra la retroalimentación, no la nota final.")

# --- Diseño y facilitación de cursos en línea -----------------------------------------
_q("A4", "diseno_linea",
   "El modelo de Comunidad de Indagación (Garrison, Anderson y Archer) describe la experiencia educativa en línea a partir de tres presencias:",
   "Docente, social y cognitiva.",
   ["Técnica, administrativa y académica.",
    "Sincrónica, asincrónica y mixta.",
    "Visual, auditiva y kinestésica."],
   "Las tres presencias del modelo CoI son la docente, la social y la cognitiva.")
_q("A4", "diseno_linea",
   "En el modelo de cinco etapas de Gilly Salmon para la e-moderación, la primera etapa se centra en:",
   "Acceso y motivación.",
   ["Construcción de conocimiento.", "Intercambio de información.", "Desarrollo."],
   "Etapas: 1) acceso y motivación, 2) socialización, 3) intercambio de información, 4) construcción de conocimiento, 5) desarrollo.")
_q("A4", "diseno_linea",
   "Para evitar la sobrecarga cognitiva en un módulo en línea, la práctica más adecuada es:",
   "Dividir los contenidos en unidades breves con objetivos claros y actividades de aplicación.",
   ["Incluir en una sola página todos los recursos disponibles sobre el tema.",
    "Añadir música y animaciones decorativas para mantener la atención.",
    "Eliminar las instrucciones para que los estudiantes exploren."],
   "Segmentar, enfocar y eliminar lo accesorio reduce la carga cognitiva extrínseca (Sweller, Mayer).")
_q("A4", "diseno_linea",
   "Un estudiante no ha ingresado al curso en 10 días. ¿Cuál es la acción de tutoría más adecuada?",
   "Contactarlo de forma personalizada, preguntar si necesita apoyo y ofrecer opciones para reincorporarse.",
   ["Esperar a que él se comunique.",
    "Publicar su nombre en el foro de avisos.",
    "Darlo de baja automáticamente."],
   "La intervención temprana, personalizada y respetuosa favorece la permanencia.")
_q("A4", "diseno_linea",
   "¿Cuál es una ventaja característica de las actividades asincrónicas en un curso con estudiantes que trabajan?",
   "Permiten participar en horarios flexibles y dan tiempo para reflexionar antes de responder.",
   ["Garantizan la respuesta inmediata del docente.",
    "Eliminan la necesidad de organizar el propio tiempo.",
    "Suprimen la interacción entre estudiantes."],
   "La flexibilidad temporal y la reflexión previa son las ventajas típicas de lo asincrónico.")

# --- Evaluación, retroalimentación e integridad en línea ------------------------------
_q("A4", "evaluacion_linea",
   "En Moodle, ¿qué método de calificación avanzada permite evaluar una Tarea con criterios y niveles de desempeño descritos?",
   "Rúbrica.",
   ["Banco de preguntas.", "Glosario.", "Escala de insignias."],
   "La rúbrica define criterios con niveles y puntajes; se configura en el método de calificación de la Tarea.")
_q("A4", "evaluacion_linea",
   "¿Cuál de los siguientes comentarios es la retroalimentación formativa más útil?",
   "«Tu argumento central es claro; para mejorarlo, incorpora dos fuentes que lo respalden y revisa la conclusión.»",
   ["«Bien.»", "«7/10.»", "«Revisa todo el trabajo, hay varios errores.»"],
   "Es específica, reconoce un logro y orienta la acción siguiente.")
_q("A4", "evaluacion_linea",
   "¿Qué medida favorece la integridad académica en evaluaciones en línea sin depender solo de la vigilancia?",
   "Diseñar evaluaciones auténticas (casos, proyectos, explicación del proceso) y usar bancos de preguntas con variación aleatoria.",
   ["Prohibir la entrega de trabajos escritos.",
    "Reducir al mínimo el tiempo disponible para todos los estudiantes.",
    "Confiar en que nadie hará trampa."],
   "El diseño de la evaluación es la primera línea de defensa de la integridad académica.")
_q("A4", "evaluacion_linea",
   "Cuando los estudiantes valoran el trabajo de un compañero usando criterios definidos, se trata de:",
   "Coevaluación.",
   ["Heteroevaluación.", "Autoevaluación.", "Evaluación diagnóstica."],
   "Coevaluación: evaluación entre iguales; heteroevaluación: la hace el docente; autoevaluación: la persona evalúa su propio trabajo.")
_q("A4", "evaluacion_linea",
   "¿Qué información de Moodle es más útil para identificar a estudiantes con posible riesgo de abandono?",
   "Los informes de actividad y finalización: accesos, participación y entregas pendientes.",
   ["El número total de recursos del curso.",
    "La fecha de creación del curso.",
    "La cantidad de grupos configurados."],
   "Los indicadores de comportamiento del estudiante permiten intervenir a tiempo.")


# --------------------------------------------------------------------------------------
# Utilidades de consulta
# --------------------------------------------------------------------------------------
PREGUNTAS_POR_ID = {p["id"]: p for p in PREGUNTAS}
ORDEN_AREAS = ["A1", "A2", "A3", "A4"]


def preguntas_de_area(area):
    return [p for p in PREGUNTAS if p["area"] == area]


def paginas_de_area(area):
    """Una página por subcompetencia (5 ítems cada una), en el orden definido."""
    qs = preguntas_de_area(area)
    paginas = []
    for sub in AREAS[area]["subs"]:
        paginas.append((sub, [p for p in qs if p["sub"] == sub]))
    return paginas


def _verificar_banco():
    assert len(PREGUNTAS) == 80, len(PREGUNTAS)
    for a in AREAS:
        qs = preguntas_de_area(a)
        assert len(qs) == 20, (a, len(qs))
        for sub in AREAS[a]["subs"]:
            n = len([p for p in qs if p["sub"] == sub])
            assert n == 5, (a, sub, n)
    for p in PREGUNTAS:
        assert len(set(p["opciones"])) == 4, p["id"]
        if p["texto"]:
            assert p["texto"] in TEXTOS, p["id"]


_verificar_banco()
