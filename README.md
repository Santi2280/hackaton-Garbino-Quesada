# M01 · ¿Roma acepta la batalla campal?

**Materia:** Introducción a la Inteligencia Artificial · UADE  
**Integrantes:** Santino Garbino y Agustin Quesada  
**IA utilizada:** ChatGPT  
**Pista elegida:** Reglas  
**Fecha:** 3 de noviembre de 2026  
**LinkedIn:** agregar el enlace de la publicación del grupo.  
**Evaluador de Telegram:** corrida 1, **9,5/10**, sin topes y **habilitado para la mesa**, según la devolución compartida por el grupo. Esta revisión documental todavía no tiene una nueva nota. El 8/10 es el mínimo de habilitación, no la nota obtenida.

## Resumen del proyecto

Construimos un sistema que recomienda aceptar o rehuir una batalla en un escenario de la Segunda Guerra Púnica. Recibe tres datos, comprueba tres condiciones y responde SÍ cuando se cumplen al menos dos.

**Es una simulación educativa:** usamos los 20 casos inventados de la ficha M01. No demostramos que el sistema pueda predecir batallas históricas reales.

## 1. Formulación y PEAS

### ¿Qué pregunta responde?

La ficha se titula **«¿Roma acepta la batalla campal?»**. Para responderla, el sistema predice:

> **Si Roma acepta esta batalla, ¿la gana?**

**SÍ = 1:** predice una victoria y recomienda aceptar.  
**NO = 0:** predice que no gana y recomienda rehuir.

La decisión se toma antes de la batalla. El sistema asesora al cónsul y a su consejo; no reemplaza su decisión. La columna `resultado_real` es la respuesta correcta del ejercicio, no un registro de si Roma aceptó históricamente la batalla.

### Nuestro PEAS

| Elemento | Aplicación al sistema |
|---|---|
| **P — Medida de rendimiento** | Medimos los errores, dando mayor costo a recomendar una batalla que se pierde. También calculamos exactitud, precisión, sensibilidad y especificidad. |
| **E — Entorno** | Una batalla ofrecida por Aníbal en el escenario de M01. Tenemos tres indicadores previos, pero desconocemos el resultado al decidir. |
| **A — Actuadores** | Mostrar SÍ/NO, recomendar aceptar/rehuir y explicar cuáles condiciones se cumplieron. Ante datos inválidos, solicitar su corrección. |
| **S — Sensores** | Recibir la relación de infantería romana/cartaginesa, el porcentaje de caballería propia y el índice de terreno favorable. |

### Objetivo y métrica: no son lo mismo

**Objetivo:** ayudar a evitar derrotas costosas sin dejar pasar innecesariamente oportunidades de victoria.

**Métrica principal:** costo medio de los errores:

**Costo medio = (5 × falsos positivos + falsos negativos) / cantidad de casos.**

Un falso positivo cuesta 5 unidades y un falso negativo, 1. **Estos valores son un supuesto didáctico de nuestra implementación:** la ficha explica las consecuencias, pero no establece una proporción numérica de 5 a 1. No son pérdidas históricas medidas.

Cuanto menor es el costo, mejor es el resultado bajo ese supuesto. Lo acompañamos con las cuatro métricas y los conteos de errores para no esconder limitaciones.

## 2. El sistema

### Los tres datos que recibe

| Dato | Qué significa | Condición favorable |
|---|---|---|
| **Relación de infantería** | Infantería romana dividida por la cartaginesa. Por ejemplo, 1,42 representa 142 soldados romanos por cada 100 cartagineses. | **Mayor o igual a 1,42.** |
| **Caballería propia** | Porcentaje del ejército romano compuesto por caballería. No es una comparación con la caballería enemiga. | **Mayor o igual al 15 %.** |
| **Terreno favorable** | Índice de 0 a 10 de la ficha. | **Mayor o igual a 6,5.** |

### Las reglas

| Regla | Qué hace |
|---|---|
| **R1** | Si la relación de infantería es ≥ 1,42, marca esa condición como cumplida. |
| **R2** | Si la caballería propia es ≥ 15 %, marca esa condición como cumplida. |
| **R3** | Si el terreno es ≥ 6,5, marca esa condición como cumplida. |
| **R4** | Si se cumplen dos o tres condiciones, responde **SÍ**. |
| **R5** | Si se cumplen cero o una, responde **NO**. |

**Idea central: una sola ventaja no alcanza; pedimos al menos dos.** Los valores iguales al límite cuentan. Si el terreno se ingresa como entero, debe ser 7 o más. Las condiciones no son probabilidades de victoria.

### Dos ejemplos para explicarlo

| Ejemplo | Relación | Caballería | Terreno | Condiciones cumplidas | Respuesta |
|---|---:|---:|---:|---:|---|
| A | 1,60 | 25 % | 8 | 3 | **SÍ: aceptar.** |
| B | 1,10 | 10 % | 4 | 0 | **NO: rehuir.** |

Son ejemplos inventados para mostrar el procedimiento, sin resultado real verificado. No se agregan a los datos de entrenamiento ni de prueba.

### ¿De dónde salieron los límites?

El programa buscó límites usando **solamente los casos 1 a 14**, los de entrenamiento. Probó **1.144 combinaciones** de puntos medios entre valores observados, manteniendo la regla de exigir dos condiciones.

Eligió la combinación con menor costo `5 × FP + FN`. Si había empate, priorizó menos falsos positivos, mayor separación entre casos y límites, cercanía al centro de los rangos y, finalmente, un orden fijo. El procedimiento completo está en [el protocolo](evidencia/PROTOCOLO.md) y en el código.

Así quedaron fijados **1,42; 15; 6,5**. El modelo se guardó antes de calcular los resultados de prueba y no se modificó para corregir sus errores.

**Límite metodológico:** las respuestas de prueba ya habían aparecido en el chat al leer la ficha, antes de cerrar el diseño. El procedimiento de ajuste recibe únicamente entrenamiento y no utiliza la puntuación de prueba para elegir los límites, pero esto **no borra la exposición previa ni garantiza que el diseño haya sido independiente de la prueba**. No afirmamos una evaluación ciega, un preregistro externo ni una estimación independiente de generalización. Documentamos los 4/6 como resultado descriptivo en la partición oficial. Una validación más sólida necesitaría casos nuevos, no vistos, después de fijar las reglas.

### ¿Qué información no usa al decidir?

No usa el número del caso, el nombre del conjunto ni `resultado_real`. Este último solo sirve para ajustar y evaluar; entregárselo al predictor sería darle la respuesta antes de decidir.

Tampoco usa el dataset anterior de 250 filas, datos de otras fichas, Internet ni ChatGPT para resolver un caso nuevo.

### Cómo ejecutarlo

**Opción más sencilla:** descargar [demo_M01.html](demo_M01.html), abrirlo en el navegador, ingresar los tres valores y presionar **«Evaluar caso»**. Funciona sin conexión.

**En Colab:** abrir [el cuaderno](https://colab.research.google.com/github/Santi2280/hackaton-Garbino-Quesada/blob/main/sistema_M01.ipynb), ejecutar las celdas y modificar los valores de la última celda, «Caso nuevo». El cuaderno contiene el código y los datos; Colab requiere conexión.

**En Python:** ejecutar `python sistema_M01.py --caso 1.60 25 8`. No requiere paquetes externos. Las pruebas técnicas se ejecutan con `python -m unittest -v test_M01.py`.

**A mano:** comparar los tres datos con sus límites y contar las condiciones cumplidas.

La relación debe ser positiva, la caballería debe estar entre 0 y 100 y el terreno entre 0 y 10. Se admiten punto o coma decimal. Un dato inválido genera un aviso, no una predicción NO. Los valores válidos fuera del rango observado generan una advertencia: poder calcular una respuesta no significa que esté validada.

## 3. Medición

### Qué datos usamos

Los **20 casos sintéticos oficiales de M01**, sin modificar la división:

- **Entrenamiento, casos 1–14:** 6 victorias y 8 derrotas. Se usan para ajustar.
- **Prueba, casos 15–20:** 3 victorias y 3 derrotas. Se usan para medir, no para reajustar.

### Qué significa cada resultado

| Nombre | Significado |
|---|---|
| **VP: verdadero positivo** | Predice victoria y la respuesta correcta es victoria. |
| **FP: falso positivo** | Predice victoria, pero la respuesta correcta es derrota. |
| **FN: falso negativo** | Predice derrota, pero la respuesta correcta es victoria. |
| **VN: verdadero negativo** | Predice derrota y la respuesta correcta es derrota. |

### Matriz de entrenamiento

Las filas indican la realidad del ejercicio y las columnas, la predicción.

| Resultado real | Predice SÍ | Predice NO | Total |
|---|---:|---:|---:|
| **SÍ: victoria** | VP = 6 | FN = 0 | 6 |
| **NO: derrota** | FP = 0 | VN = 8 | 8 |
| **Total** | 6 | 8 | **14** |

### Matriz de prueba

| Resultado real | Predice SÍ | Predice NO | Total |
|---|---:|---:|---:|
| **SÍ: victoria** | VP = 1 | FN = 2 | 3 |
| **NO: derrota** | FP = 0 | VN = 3 | 3 |
| **Total** | 1 | 5 | **6** |

### Las cuatro métricas

| Métrica | Qué responde y cómo se calcula | Entrenamiento | Prueba |
|---|---|---|---|
| **Exactitud** | ¿Cuántos casos acertó en total? `(VP + VN) / N`. | 14/14 = **100 %** | 4/6 ≈ **66,67 %** |
| **Precisión** | De las victorias que predijo, ¿cuántas eran correctas? `VP / (VP + FP)`. | 6/6 = **100 %** | 1/1 = **100 %** |
| **Sensibilidad** | De las victorias reales, ¿cuántas detectó? `VP / (VP + FN)`. | 6/6 = **100 %** | 1/3 ≈ **33,33 %** |
| **Especificidad** | De las derrotas reales, ¿cuántas detectó? `VN / (VN + FP)`. | 8/8 = **100 %** | 3/3 = **100 %** |

`N` es la cantidad de casos. Las fracciones son exactas; los decimales con ≈ están redondeados. Si un denominador es cero, la métrica se informa como **no definida**.

**Costo total:** 0 en entrenamiento y 2 en prueba.  
**Costo medio:** 0/14 = 0 en entrenamiento y 2/6 ≈ 0,3333 en prueba.

### Qué pasó en los seis casos de prueba

| Caso | Relación | Caballería | Terreno | Real | Predicción | Resultado |
|---|---:|---:|---:|---|---|---|
| 15 | 1,36 | 18 % | 6 | SÍ | NO | FN |
| 16 | 0,82 | 27 % | 4 | NO | NO | VN |
| 17 | 1,33 | 24 % | 5 | NO | NO | VN |
| 18 | 1,81 | 30 % | 2 | SÍ | SÍ | VP |
| 19 | 0,81 | 10 % | 3 | NO | NO | VN |
| 20 | 0,99 | 28 % | 6 | SÍ | NO | FN |

Nos equivocamos en **15 y 20**: solo cumplen la condición de caballería. El sistema recomienda rehuir, aunque las etiquetas indican victoria.

### Cómo interpretamos los resultados

Acertar 14/14 en entrenamiento **no garantiza** funcionar igual con casos nuevos: en prueba acertó 4/6. Buscar 1.144 combinaciones sobre solo 14 ejemplos permite ajustar particularidades de la muestra. La caída es compatible con sobreajuste, pero seis casos no permiten determinar con certeza su causa ni el rendimiento futuro. Además, la exposición previa de las etiquetas impide presentar la prueba como independiente: **4/6 es el rendimiento observado en esos seis casos, no una garantía de generalización**.

El **100 % de precisión en prueba se apoya en una sola predicción SÍ**. No significa acertar todo: dejamos pasar dos de las tres victorias. No bajamos los límites después de conocer esos errores, porque eso usaría la prueba para ajustar.

Las mediciones provienen de la ejecución del programa. Se conservan las [20 predicciones](resultados/predicciones_M01.csv), las [métricas](resultados/metricas.json) y el [resumen](resultados/resumen.txt). Harían falta otros casos reservados para evaluar una versión futura.

## 4. El error más caro

El **falso positivo** es el más costoso según las consecuencias descritas en M01: recomendar aceptar una batalla que se pierde puede costar un ejército consular y aliados. Un falso negativo también perjudica: deja pasar una victoria y prolonga la guerra.

Por eso exigimos corroborar la recomendación con **dos condiciones**, no una sola.

La IA ejecutó una comparación técnica con los mismos límites:

| Regla comparada en entrenamiento | VP | FN | FP | VN | Costo total |
|---|---:|---:|---:|---:|---:|
| Aceptar con una condición favorable | 6 | 0 | 5 | 3 | 25 |
| Aceptar con dos condiciones favorables | 6 | 0 | 0 | 8 | 0 |

Exigir dos condiciones eliminó esos cinco falsos positivos en entrenamiento. En prueba mantuvo cero falsos positivos, pero produjo dos falsos negativos. **Es una regla conservadora, no infalible.** Esta comparación técnica no es una corrida del bot de Telegram ni demuestra que el costo 5:1 sea históricamente correcto.

### Respuesta a la corrida 1: ¿por qué 5:1 y qué pasa con 2:1 o 1:1?

**Lo que justifica la ficha:** un falso positivo puede significar perder un ejército y aliados; un falso negativo deja pasar una victoria y prolonga la guerra. Eso motiva dar mayor importancia al falso positivo, pero **no permite deducir que cueste exactamente cinco veces más**. El 5:1 fue un supuesto didáctico propuesto en la implementación asistida por IA, no una relación histórica medida ni una exigencia del profesor. Un 2:1 también expresa esa prioridad; 1:1 sirve como comparación con ambos errores igualmente ponderados. No sostenemos que 5:1 sea el único cociente correcto.

**Comprobación realizada después de recibir la evaluación:** se volvió a ejecutar el mismo ajuste con los 14 casos de entrenamiento, las mismas 1.144 combinaciones y los mismos desempates, cambiando únicamente el costo del falso positivo a 5, 2 y 1. No se eligió la ponderación por su resultado en prueba ni se reemplazó el modelo original.

| Costo FP:FN | Umbrales obtenidos: relación / caballería / terreno | Costo en entrenamiento | Costo en prueba: nuestras reglas | Costo en prueba: siempre NO | Costo en prueba: siempre SÍ |
|---|---|---:|---:|---:|---:|
| 5:1 | 1,42 / 15 % / 6,5 | 0 | 2 | 3 | 15 |
| 2:1 | 1,42 / 15 % / 6,5 | 0 | 2 | 3 | 6 |
| 1:1 | 1,42 / 15 % / 6,5 | 0 | 2 | 3 | 3 |

La tabla muestra **costos totales**, no porcentajes. El costo medio de prueba se obtiene dividiendo por 6. **No cambia ninguna predicción ni la recomendación del sistema:** las tres ejecuciones seleccionan exactamente los mismos umbrales y la misma regla de dos condiciones.

**Por qué ocurre:** hay reglas candidatas sin errores en entrenamiento. Su costo es cero con cualquiera de esos cocientes positivos, y los desempates, que no cambiaron, eligen la misma. En prueba nuestras reglas tienen cero FP y dos FN, por lo que el costo es siempre `costo_FP × 0 + 1 × 2 = 2`.

Esta estabilidad se refiere a nuestra familia de reglas y a estos datos. **No demuestra que los costos sean irrelevantes en general ni que 5:1 sea óptimo.** Si distintos candidatos intercambian FP por FN, el cociente puede cambiar cuál conviene. En una aplicación real habría que justificar los costos con quien decide y validar con datos nuevos.

La comprobación es reproducible con `python evidencia/verificar_costos.py`. Se conservan [los resultados](evidencia/SENSIBILIDAD_COSTOS.json). Es un análisis posterior de sensibilidad de la ponderación, no una nueva corrida del bot ni una modificación para mejorar los seis casos de prueba.

## 5. ¿Comparado contra qué?

### Línea base: responder siempre NO

Una línea base es un sistema muy sencillo con el que comparar. Elegimos **«siempre NO»** porque NO es la clase más frecuente en entrenamiento: 8 de 14 casos. Mantenemos esa respuesta también en prueba. Añadimos «siempre SÍ» como comparación adicional.

| Sistema | Aciertos en entrenamiento | Aciertos en prueba | Costo total en entrenamiento | Costo total en prueba |
|---|---|---|---:|---:|
| **Nuestras reglas** | 14/14 = 100 % | 4/6 ≈ 66,67 % | 0 | 2 |
| **Siempre NO** | 8/14 ≈ 57,14 % | 3/6 = 50 % | 6 | 3 |
| **Siempre SÍ** | 6/14 ≈ 42,86 % | 3/6 = 50 % | 40 | 15 |

En prueba, nuestras reglas consiguen **un acierto más que siempre NO** y un falso negativo menos. El costo medio baja de 3/6 = 0,5 a 2/6 ≈ 0,3333. Es una mejora observada en seis casos, no una garantía de superioridad general.

Para completar la comparación:

| Línea base y conjunto | VP | FN | FP | VN | Precisión | Sensibilidad | Especificidad |
|---|---:|---:|---:|---:|---|---|---|
| Siempre NO · entrenamiento | 0 | 6 | 0 | 8 | No definida: 0/0 | 0/6 = 0 % | 8/8 = 100 % |
| Siempre NO · prueba | 0 | 3 | 0 | 3 | No definida: 0/0 | 0/3 = 0 % | 3/3 = 100 % |
| Siempre SÍ · entrenamiento | 6 | 0 | 8 | 0 | 6/14 ≈ 42,86 % | 6/6 = 100 % | 0/8 = 0 % |
| Siempre SÍ · prueba | 3 | 0 | 3 | 0 | 3/6 = 50 % | 3/3 = 100 % | 0/3 = 0 % |

### Checklist crítico

| Pregunta | Respuesta |
|---|---|
| **¿Qué datos?** | Los 20 casos inventados oficiales de M01: 14 para ajustar y 6 para prueba. |
| **¿Qué métrica?** | Costo medio de errores, exactitud, precisión, sensibilidad y especificidad. |
| **¿Comparado contra qué?** | Principalmente, siempre NO. También se muestra siempre SÍ. |
| **¿Quién lo midió?** | ChatGPT ejecutó el código durante la preparación y entregó los archivos reproducibles. El grupo compartió la devolución del bot: corrida 1, 9,5/10; el bot informó haber recalculado las métricas y confirmado su coincidencia. La nota del bot evalúa el trabajo; no es una validación histórica independiente del predictor. |

## 6. Riesgo: datos → modelo → decisión → consecuencia

**Ejemplo:** se informa un terreno más favorable de lo que realmente es → se activan dos condiciones → el sistema recomienda aceptar → si la batalla se pierde, cometemos el error más costoso.

La sensibilidad al dato se puede mostrar: con relación **1,10** y caballería **20 %**, terreno **6** produce NO, pero terreno **7** produce SÍ. Esto muestra un cambio de recomendación, no un resultado real verificado.

Por eso mostramos los datos y las condiciones junto a la salida. El sistema detecta valores fuera del formato permitido, pero no puede saber si una medición plausible está equivocada. La decisión final requiere revisión humana.

Además, hay pocos casos, todos son ficticios y solo incluyen tres variables. No corresponde usar estos resultados para afirmar que el sistema predice guerras reales. Tampoco debe incorporarse el resultado posterior de una batalla como dato de entrada.

## 7. Bitácora

### Uso de la IA

Este registro distingue las decisiones comunicadas por el grupo de los detalles implementados por la IA.

| Paso | Qué se pidió o hizo | Qué se aceptó o implementó | Qué se descartó y por qué |
|---|---|---|---|
| 1 | El grupo pidió analizar la consigna y los repositorios. | Se propuso una pregunta SÍ/NO y seguir las siete secciones del README. | Reutilizar sin cambios el clasificador de tres guerras y el dataset de 250 filas: no eran la tarea M01. |
| 2 | El grupo confirmó M01 y aceptó la pista Reglas. | Una solución reproducible que pueda explicarse y ejecutarse en vivo. | Neurona y Agente como pistas: se priorizó la sencillez de Reglas. |
| 3 | El grupo pidió construir el trabajo y editar el repositorio si había permisos. | La IA preparó los archivos para subir. | No se afirmó haberlos subido: la conexión no tenía permiso de escritura. |
| 4 | La IA implementó y evaluó el sistema. | Dos de tres condiciones, ajuste con entrenamiento, costo didáctico 5:1 y resultados documentados. | La variante de una condición produjo cinco falsos positivos en entrenamiento. No se ajustó con prueba ni se ocultaron los errores. |
| 5 | Se preparó la ejecución en vivo y el material de estudio. | Python, cuaderno Colab, HTML sin conexión y pruebas técnicas. | Depender de ChatGPT para predecir cada caso o prometer exactitud histórica real. |
| 6 | El grupo pidió orientación para subir los archivos. | Luego confirmó que los subió y que aprobó en Telegram. En ese momento todavía no había compartido la devolución. | No se inventó entonces una nota ni un número de corrida. La devolución recibida después se registra abajo. |
| 7 | El grupo pidió un README más comprensible. | Se reescribieron las explicaciones manteniendo reglas y resultados. | No se alteran las métricas ni se presenta la reescritura como una nueva evaluación. |
| 8 | El grupo compartió la evaluación M01, corrida 1, 9,5/10. | Se registró la devolución y la IA ejecutó la comprobación 5:1, 2:1 y 1:1. En esta revisión se aclararon los límites de generalización y la diferencia entre nota y umbral. | Se descartó inventar otra corrida, afirmar que 5:1 es una proporción histórica o ajustar las reglas con las etiquetas de prueba. La incorporación de esta revisión a GitHub queda a cargo del grupo. |

### Corridas contra el evaluador

**Fuente del registro:** devolución del bot de Telegram pegada por el grupo en este chat. No se accedió directamente a la cuenta de Telegram. La transcripción completa está en [CORRIDA_1_TELEGRAM.txt](evidencia/CORRIDA_1_TELEGRAM.txt).

| Corrida | Nota | Observación del evaluador | Qué cambió después de esa corrida |
|---|---|---|---|
| **1** | **9,5/10** | A–F con puntaje máximo; G = 0,5/1 por registro de corridas incompleto e inconsistencia sobre el 8/10. Preguntó por los costos 5:1, 2:1 y 1:1 y por la generalización con prueba previamente vista. Sin topes. Habilitado para la mesa. | En esta revisión se incorpora la devolución, se aclara que 8/10 es el mínimo y 9,5/10 la nota obtenida, se documenta la comprobación de costos y se explicita la limitación de la evaluación. No cambiaron reglas, datos ni predicciones. |

| Criterio | Puntaje de la corrida 1 |
|---|---:|
| A. Formulación y PEAS | 2/2 |
| B. Sistema | 1,5/1,5 |
| C. Medición | 3/3 |
| D. Error más caro | 1/1 |
| E. Comparado contra qué | 1/1 |
| F. Riesgo | 0,5/0,5 |
| G. Bitácora | 0,5/1 |
| **Total** | **9,5/10** |

**Aclaración sobre las notas:** 8/10 es el umbral para habilitar la mesa; la nota respaldada por esta corrida es **9,5/10**. Ninguna de esas cifras equivale a la exactitud del clasificador, que en prueba es 4/6 ≈ 66,67 %. No se declara un 10/10 ni una segunda evaluación que no ocurrió.

**Estado:** el grupo confirmó que subió los archivos y compartió la aprobación. Esta revisión local aún debe incorporarse al repositorio y, si se vuelve a enviar al evaluador, registrarse como otra corrida. La publicación en LinkedIn no fue confirmada y falta su enlace; la defensa presencial aún no fue informada como realizada. Se conserva la corrida 1 sin cambiar retrospectivamente su nota ni sus observaciones.

### Archivos de respaldo y fuentes

- [Sistema Python](sistema_M01.py), [cuaderno](sistema_M01.ipynb) y [demo HTML](demo_M01.html).
- [Protocolo de construcción](evidencia/PROTOCOLO.md), [registro de la fuente](evidencia/FUENTE.json) y [modelo guardado](resultados/modelo_M01.json).
- [Pruebas técnicas](test_M01.py), [predicciones](resultados/predicciones_M01.csv) y [métricas](resultados/metricas.json).
- [Ficha M01 de la cátedra](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/problematicas/manana.md#m01--roma-acepta-la-batalla-campal).
- [Datos oficiales M01](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/datos/M01.csv).
- [Bases y rúbrica](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/BASES.md).
- [Guía de LinkedIn](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/GUIA_LINKEDIN.md).

No se usaron fuentes históricas externas ni datos de otros grupos para construir el sistema.
