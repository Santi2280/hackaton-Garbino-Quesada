# M01 · ¿Roma acepta la batalla campal?

**Hackatón IIA · UADE · Introducción a la Inteligencia Artificial (3.4.257)**  
**Integrantes:** Santino Garbino · Agustin Quesada  
**IA declarada:** ChatGPT  
**Pista:** Reglas  
**Fecha:** 3 de noviembre de 2026  
**Publicación en LinkedIn:** pendiente de publicar por el grupo y agregar el enlace.  
**Evaluación del bot:** pendiente; no se declara una nota ni una validación inexistente.

> Simulación educativa con los 20 casos inventados de M01, no un predictor históricamente validado de batallas. El sistema, las mediciones y este documento fueron preparados con asistencia de ChatGPT; los integrantes deben revisar y defender su funcionamiento.

**Acceso rápido:** [cuaderno autónomo](sistema_M01.ipynb) · [abrir en Colab una vez subido](https://colab.research.google.com/github/Santi2280/hackaton-Garbino-Quesada/blob/main/sistema_M01.ipynb) · [demostrador HTML sin conexión](demo_M01.html) · [código Python](sistema_M01.py) · [guía de defensa](DEFENSA.md).

## 1. Formulación y PEAS

**La pregunta de la ficha:** «¿Roma acepta la batalla campal?». Para predecirla operacionalizamos: **¿se predice que Roma ganaría esta batalla si la acepta?** SÍ (clase positiva, 1) significa que gana si acepta; NO (0), que no la gana. No es una clasificación de a cuál Guerra Púnica pertenece un texto.

**Quién decide y cuándo:** el cónsul y su consejo, antes de aceptar una batalla ofrecida por Aníbal, en el escenario didáctico de la Segunda Guerra Púnica. Una salida SÍ recomienda aceptar; una salida NO recomienda rehuir. El sistema asesora; la decisión final corresponde al cónsul. `resultado_real` no indica si se aceptó históricamente: es la etiqueta sintética definida en la ficha.

| PEAS | Nuestro sistema |
|---|---|
| **P — Medida de rendimiento** | Costo didáctico medio `(5 FP + FN) / N`, acompañado por exactitud, precisión, sensibilidad y especificidad, por separado en entrenamiento y prueba. Se compara contra respuestas constantes. |
| **E — Entorno** | Una batalla ofrecida del escenario M01. Hay incertidumbre sobre el resultado; solo se observan los tres indicadores previos suministrados. Se trabaja con la partición fija de 14/6. No se usan otras fichas ni el dataset anterior de 250 filas. |
| **A — Actuadores** | Emitir SÍ/NO, recomendar aceptar/rehuir y mostrar qué condiciones se cumplieron. Ante una entrada inválida se solicita corregirla: un error de formato no se interpreta como NO. |
| **S — Sensores** | Lectura de relación de infantería romana/cartaginesa, porcentaje de caballería propia e índice de terreno favorable. No se recibe el resultado de la batalla al predecir. |

**Objetivo y métrica no son lo mismo.** El objetivo es apoyar decisiones que eviten derrotas costosas sin renunciar innecesariamente a victorias. La métrica es una aproximación cuantificable sobre los casos sintéticos, no un conteo real de soldados, años de guerra o aliados. La ficha describe el falso positivo como la pérdida de un ejército y el falso negativo como prolongación de la guerra, pero **no fija costos numéricos**. Adoptamos, como supuesto didáctico explícito de esta implementación, costo FP = 5 y costo FN = 1. No presentamos esa relación como un dato histórico ni de la cátedra. El costo siempre se acompaña de los cuatro conteos para permitir otras valoraciones.

## 2. El sistema

### Cómo decide: reglas transparentes

Se construyen tres hechos intermedios:

| Regla | Condición | Hecho intermedio |
|---|---|---|
| R1 | Relación de infantería **≥ 1,42** | `infanteria_favorable = 1`; en otro caso, 0. |
| R2 | Caballería propia **≥ 15 %** | `caballeria_favorable = 1`; en otro caso, 0. |
| R3 | Terreno favorable **≥ 6,5** | `terreno_favorable = 1`; en otro caso, 0. |
| R4 | Se cumplen **al menos dos** de R1, R2 y R3 | Predecir **SÍ** y recomendar aceptar. |
| R5 | Se cumplen menos de dos | Predecir **NO** y recomendar rehuir. |

Las condiciones son inclusivas: un valor igual al umbral cuenta. Si el terreno se expresa solo como entero, `≥ 6,5` equivale a `≥ 7`. Los indicadores no son probabilidades ni verdades generales de estrategia militar.

```python
def decidir(relacion, caballeria, terreno):
    # Para entradas válidas; el programa completo también valida rangos.
    senales = int(relacion >= 1.42) + int(caballeria >= 15) + int(terreno >= 6.5)
    return int(senales >= 2)
```

### Cómo se fijaron los umbrales

El procedimiento está detallado en [PROTOCOLO.md](evidencia/PROTOCOLO.md) y programado en `ajustar(entrenamiento)`. Se fijó una familia de reglas de corroboración de dos de tres señales. Se generaron los puntos medios entre valores distintos consecutivos de **los casos 1–14**, obteniendo **1.144 combinaciones** de umbrales. Se eligió la de menor `5 FP + FN` en entrenamiento. Los desempates son: menos FP, mayor margen mínimo de clasificación, umbrales más cercanos al centro de los rangos observados y orden lexicográfico.

El margen usa la mediana de las diferencias normalizadas entre los tres valores y sus umbrales, orientada por la etiqueta real. Mide separación en entrenamiento, **no confianza probabilística**. El programa guarda [el modelo](resultados/modelo_M01.json) y su SHA-256 antes de evaluar prueba. Los umbrales elegidos son 1,42; 15; 6,5. No se modificaron después de obtener las métricas de prueba.

**Transparencia metodológica:** las etiquetas de prueba están publicadas y aparecieron en el chat durante la lectura inicial de la ficha. Por ello **no afirmamos una evaluación ciega**. La función de selección acepta únicamente los 14 casos de entrenamiento, rechaza cualquier otro conjunto y no usa la puntuación de prueba para elegir parámetros. La prueba sigue siendo la partición oficial, sin reutilizarla para ajustes; esta limitación se declara en lugar de ocultarla. Tampoco se afirma un preregistro externo.

### Variables que usa y por qué

| Campo | ¿Se usa para decidir? | Justificación |
|---|---|---|
| Relación de fuerzas | Sí | Resume la ventaja relativa de infantería previa de la ficha. |
| Caballería propia (%) | Sí | Permite corroborar una decisión con una señal diferente de la infantería. |
| Terreno favorable (0–10) | Sí | Incorpora las condiciones de terreno suministradas antes de decidir. |
| `caso` | No | Es un identificador, no evidencia de victoria. |
| `conjunto` | No | Sirve para separar ajuste/evaluación, no para predecir. |
| `resultado_real` | No | Solo se utiliza para ajustar y evaluar; usarlo al decidir sería fuga de información. |

No hay acceso a Internet ni a un modelo generativo al resolver un caso. La función `predecir` solo admite los tres indicadores y los parámetros congelados. Las entradas deben ser finitas, con relación > 0, caballería entre 0 y 100 y terreno entre 0 y 10. Se admiten punto y coma decimal. Para valores válidos fuera del rango de entrenamiento se calcula la regla, pero aparece una advertencia de extrapolación.

### Cómo se corre en vivo

**Colab:** abrir el cuaderno enlazado, ejecutar todas las celdas y modificar los tres valores de la última celda «Caso nuevo». El cuaderno trae código y datos oficiales incorporados: no depende de descargar el CSV ni de una API. La sesión de Colab sí requiere conexión.

**Sin conexión:** descargar `demo_M01.html` y abrirlo en el navegador. Ingresar los tres indicadores y pulsar «Evaluar caso». No hay que instalar nada. El HTML usa las mismas reglas congeladas; las mediciones se reproducen con Python o el cuaderno.

**Python local:** `python sistema_M01.py --caso 1.60 25 8`. No se necesitan paquetes externos. Para comprobar la implementación: `python -m unittest -v test_M01.py`.

**A mano:** comparar con 1,42; 15; 6,5 y contar. Dos o tres condiciones verdaderas → SÍ; cero o una → NO.

### Dos casos inventados para demostrar el procedimiento

Estos ejemplos no se agregan a entrenamiento ni a prueba y **no tienen etiqueta real verificada**.

| Caso | Relación | Caballería (%) | Terreno | Señales | Salida |
|---|---:|---:|---:|---|---|
| A | 1,60 | 25 | 8 | 1 + 1 + 1 = 3 | SÍ: recomendar aceptar. |
| B | 1,10 | 10 | 4 | 0 + 0 + 0 = 0 | NO: recomendar rehuir. |

## 3. Medición

**Datos:** 20 casos sintéticos oficiales. Entrenamiento = 1–14: 6 positivos y 8 negativos. Prueba = 15–20: 3 positivos y 3 negativos. No se cambia la división.

**Orientación de las matrices:** filas = realidad; columnas = predicción. VP: predecir victoria y acertar; FP: predecir victoria y que la etiqueta sea derrota; FN: predecir derrota cuando la etiqueta es victoria; VN: predecir derrota y acertar.

### Entrenamiento (14 casos)

| | Predice SÍ | Predice NO | Total |
|---|---:|---:|---:|
| **Real SÍ** | VP = 6 | FN = 0 | 6 |
| **Real NO** | FP = 0 | VN = 8 | 8 |
| **Total** | 6 | 8 | **14** |

### Prueba (6 casos)

| | Predice SÍ | Predice NO | Total |
|---|---:|---:|---:|
| **Real SÍ** | VP = 1 | FN = 2 | 3 |
| **Real NO** | FP = 0 | VN = 3 | 3 |
| **Total** | 1 | 5 | **6** |

| Métrica y fórmula | Entrenamiento | Prueba |
|---|---|---|
| Exactitud = `(VP + VN) / N` | 14/14 = **100 %** | 4/6 ≈ **66,67 %** |
| Precisión = `VP / (VP + FP)` | 6/6 = **100 %** | 1/1 = **100 %** |
| Sensibilidad = `VP / (VP + FN)` | 6/6 = **100 %** | 1/3 ≈ **33,33 %** |
| Especificidad = `VN / (VN + FP)` | 8/8 = **100 %** | 3/3 = **100 %** |
| Costo total = `5 FP + FN` | **0** | **2** |
| Costo medio = `(5 FP + FN) / N` | **0** | 2/6 ≈ **0,3333** |

Las fracciones son exactas; los decimales indicados con ≈ están redondeados. Cuando una fórmula tiene denominador cero se informa «no definida», no se inventa un cero ni se omite la métrica.

### Predicciones auditables, caso por caso

Los decimales de esta tabla y del CSV se muestran con punto para facilitar la reproducción.

| Caso | Conjunto | Relación | Caballería | Terreno | Real | Señales | Predicción | Tipo |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Entr. | 1.33 | 14 | 3 | 0 | 0 | 0 | VN |
| 2 | Entr. | 1.24 | 23 | 0 | 0 | 1 | 0 | VN |
| 3 | Entr. | 1.05 | 33 | 7 | 1 | 2 | 1 | VP |
| 4 | Entr. | 0.99 | 14 | 6 | 0 | 0 | 0 | VN |
| 5 | Entr. | 1.02 | 9 | 6 | 0 | 0 | 0 | VN |
| 6 | Entr. | 0.62 | 16 | 4 | 0 | 1 | 0 | VN |
| 7 | Entr. | 1.77 | 13 | 2 | 0 | 1 | 0 | VN |
| 8 | Entr. | 1.63 | 35 | 9 | 1 | 3 | 1 | VP |
| 9 | Entr. | 1.51 | 32 | 10 | 1 | 3 | 1 | VP |
| 10 | Entr. | 0.87 | 35 | 7 | 1 | 2 | 1 | VP |
| 11 | Entr. | 0.79 | 17 | 8 | 1 | 2 | 1 | VP |
| 12 | Entr. | 1.19 | 30 | 0 | 0 | 1 | 0 | VN |
| 13 | Entr. | 0.88 | 22 | 2 | 0 | 1 | 0 | VN |
| 14 | Entr. | 1.92 | 28 | 9 | 1 | 3 | 1 | VP |
| 15 | Prueba | 1.36 | 18 | 6 | 1 | 1 | 0 | FN |
| 16 | Prueba | 0.82 | 27 | 4 | 0 | 1 | 0 | VN |
| 17 | Prueba | 1.33 | 24 | 5 | 0 | 1 | 0 | VN |
| 18 | Prueba | 1.81 | 30 | 2 | 1 | 2 | 1 | VP |
| 19 | Prueba | 0.81 | 10 | 3 | 0 | 0 | 0 | VN |
| 20 | Prueba | 0.99 | 28 | 6 | 1 | 1 | 0 | FN |

**Entrenamiento contra prueba.** Pasamos de 14/14 a 4/6 aciertos. La especificidad permanece en 3/3 en prueba, pero se detecta solo una de tres victorias. Esto evidencia una generalización limitada y posible sobreajuste: buscar 1.144 combinaciones con solo 14 ejemplos puede ajustar peculiaridades de la muestra. El 100 % de precisión se apoya en **una sola predicción positiva** en prueba; no demuestra fiabilidad general. Seis casos tampoco permiten asegurar desempeño futuro.

**Errores concretos:** casos 15 y 20, ambos FN. En los dos solo se activa la condición de caballería; su terreno vale 6, por debajo de 6,5, y su relación está por debajo de 1,42. No bajamos el umbral después de ver estos errores: hacerlo contaminaría la prueba. Una revisión futura exigiría nuevos casos de validación y una prueba reservada distinta; no afirmaríamos que esos datos ya existen.

Los números provienen de una ejecución real del código, no de una estimación del modelo de lenguaje. Se guardan [métricas](resultados/metricas.json), [predicciones](resultados/predicciones_M01.csv) y [resumen](resultados/resumen.txt).

## 4. El error más caro

Según M01, el **falso positivo** recomienda aceptar una batalla que se pierde y puede costar un ejército consular y aliados. El falso negativo evita una victoria posible y prolonga la guerra. Por eso se da mayor peso al FP, sin tratar al FN como gratuito.

**Cambio técnico comprobado:** se ejecutó una variante permisiva que responde SÍ con **una sola** condición favorable, con los mismos umbrales, y se comparó con la regla final que exige **dos**. En entrenamiento la variante produjo VP = 6, FN = 0, FP = 5 y VN = 3; la final produjo VP = 6, FN = 0, FP = 0 y VN = 8. El costo pasó de 25 a 0. Exigir corroboración evita que, por ejemplo, una ventaja de infantería aislada alcance para recomendar atacar. Este análisis fue realizado por la IA; no es una corrida del bot ni una decisión humana inventada.

En prueba el sistema final no produjo FP, pero incurrió en dos FN. Es una política conservadora, no infalible. Para cualquier ponderación positiva del FN, la comparación de costos observados con «siempre NO» es favorable aquí: 2 FN frente a 3 FN, ambos con 0 FP. Esto no permite atribuir al cociente 5:1 una optimalidad histórica.

## 5. ¿Comparado contra qué?

**Línea base principal:** responder siempre NO, fijada porque NO es la clase mayoritaria en entrenamiento (8/14), sin consultar la distribución de prueba. Se mantiene la misma respuesta en ambos conjuntos. Se incluye también siempre SÍ para mostrar el otro extremo.

| Sistema y conjunto | VP | FN | FP | VN | Exactitud | Precisión | Sensibilidad | Especificidad | Costo total |
|---|---:|---:|---:|---:|---|---|---|---|---:|
| Reglas · entrenamiento | 6 | 0 | 0 | 8 | 14/14 = 100 % | 6/6 = 100 % | 6/6 = 100 % | 8/8 = 100 % | 0 |
| Siempre NO · entrenamiento | 0 | 6 | 0 | 8 | 8/14 ≈ 57,14 % | No definida (0/0) | 0/6 = 0 % | 8/8 = 100 % | 6 |
| Siempre SÍ · entrenamiento | 6 | 0 | 8 | 0 | 6/14 ≈ 42,86 % | 6/14 ≈ 42,86 % | 6/6 = 100 % | 0/8 = 0 % | 40 |
| Reglas · prueba | 1 | 2 | 0 | 3 | 4/6 ≈ 66,67 % | 1/1 = 100 % | 1/3 ≈ 33,33 % | 3/3 = 100 % | 2 |
| Siempre NO · prueba | 0 | 3 | 0 | 3 | 3/6 = 50 % | No definida (0/0) | 0/3 = 0 % | 3/3 = 100 % | 3 |
| Siempre SÍ · prueba | 3 | 0 | 3 | 0 | 3/6 = 50 % | 3/6 = 50 % | 3/3 = 100 % | 0/3 = 0 % | 15 |

En prueba, las reglas superan la base principal por **un caso correcto** y un FN menos. El costo medio es 2/6 frente a 3/6. No confundimos esa mejora en seis ejemplos con evidencia de superioridad estadística general.

| Checklist de la Clase 6 | Respuesta |
|---|---|
| **¿Qué datos?** | Únicamente los 20 casos inventados de M01 publicados por la cátedra; 14 para ajuste y 6 para prueba. Copia oficial verificada mediante SHA de GitHub. |
| **¿Qué métrica?** | Costo medio didáctico 5FP+FN dividido por N, más las cuatro métricas y los conteos de cada matriz. Sin denominadores ocultos. |
| **¿Comparado contra qué?** | Siempre NO como clase mayoritaria de entrenamiento; siempre SÍ como control adicional. Misma partición y fórmulas. |
| **¿Quién lo midió?** | El programa reproducible fue ejecutado por ChatGPT en su entorno de cálculo para esta entrega. No es validación externa; la revisión humana y la corrida del evaluador todavía deben registrarse. |

## 6. Riesgo: datos → modelo → decisión → consecuencia

**Datos:** una medición de terreno excesivamente favorable puede ser errónea → **modelo:** se activan dos señales en lugar de una → **decisión:** se recomienda aceptar → **consecuencia:** si la etiqueta verdadera es derrota, se incurre en un FP, el error más costoso de M01. La validación de formato no detecta una medición plausible pero equivocada; se requiere juicio del cónsul.

Ejemplo de sensibilidad a la entrada, sin etiqueta real inventada: con relación 1,10 y caballería 20 %, un terreno de 6 produce NO; un terreno de 7 produce SÍ. Por ello las condiciones y los datos deben quedar visibles, y la recomendación no equivale a certeza.

Otros límites: muestra muy pequeña; casos sintéticos; umbrales discontinuos; datos que pueden omitir factores relevantes. No hay prueba de validez histórica ni de utilidad fuera de M01. Se advierte si relación o caballería están fuera de los rangos observados; no se interpreta la extrapolación como validada. El resultado posterior jamás debe entrar al predictor.

## 7. Bitácora

### Uso de la IA

Registro de interacciones reales y del trabajo técnico de esta entrega; no se inventan aprobaciones humanas.

| # | Qué le pedimos a la IA / actividad | Qué se aceptó o implementó | Qué se descartó y por qué |
|---|---|---|---|
| 1 | Analizar capturas, bases y repositorios antes de construir. | La IA propuso resolver una pregunta SÍ/NO y seguir las siete secciones del README. | Reutilizar sin adaptación el clasificador de tres guerras o el dataset anterior: no corresponde a la ficha. |
| 2 | El grupo confirmó «somos la ficha M01» y aceptó la recomendación de Reglas. | M01, pista Reglas y documentación reproducible. | No se eligieron Neurona ni Agente: se priorizó una regla fácil de ejecutar y explicar. |
| 3 | «Hace todo lo que puedas y si te deja editar mejor; en caso de que no, dámelo ya hecho». | Se verificó acceso de lectura al fork y se prepararon archivos para subir. | No se afirmó una edición remota: la conexión informa `push: false`. |
| 4 | Implementación técnica por la IA bajo el encargo anterior. | Regla de dos de tres señales, selección automática usando solo entrenamiento y supuesto didáctico 5:1 documentado. | Una sola señal como decisión final: dio cinco FP en entrenamiento. Estos detalles se entregan para revisión humana; no se atribuye al grupo una aprobación específica aún no registrada. |
| 5 | Ejecutar y comprobar resultados. | 14/14 aciertos de entrenamiento y 4/6 de prueba; matrices, baselines y errores 15/20 documentados. | Ocultar la baja sensibilidad, redondear hasta aparentar perfección o ajustar con prueba. |
| 6 | Preparar demostración y defensa. | Cuaderno autónomo, script, HTML local, pruebas técnicas y guía oral. | Dependencia de un servicio generativo para decidir en vivo y promesas de predicción histórica real. |

### Corridas contra el evaluador

| Corrida | Nota | Agujero que encontró | Qué cambiamos |
|---|---|---|---|
| Pendiente | No obtenida | Aún no se envió este README al bot desde esta conversación. | Registrar la devolución real antes de la defensa. |

**Estado de entrega:** sistema ejecutado y resultados locales comprobados; faltan publicación/commits del grupo, publicación en LinkedIn, corrida real del bot y defensa humana. El 8/10 es la nota del trabajo otorgada por el evaluador, no un 80 % de exactitud exigido al clasificador. No afirmamos haberlo alcanzado.

**Registro de evidencia técnica:** [protocolo](evidencia/PROTOCOLO.md), [fuente y hash](evidencia/FUENTE.json), [modelo congelado](resultados/modelo_M01.json), [pruebas automatizadas](test_M01.py). La bitácora y las devoluciones deben actualizarse sin modificar retrospectivamente las etiquetas, la partición o los resultados.

### Fuentes del trabajo

- [Ficha M01, cátedra](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/problematicas/manana.md#m01--roma-acepta-la-batalla-campal).
- [Datos M01 oficiales](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/datos/M01.csv), blob SHA-1 `32035148f71046d2ffca305ea8caef83def93eb1`.
- [Bases y rúbrica](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/BASES.md).
- [Guía de LinkedIn](https://github.com/dharioprodigio/hackaton-iia-uade-2026/blob/main/GUIA_LINKEDIN.md).

No se incorporaron fuentes históricas externas ni datos de otros grupos para construir el sistema.
