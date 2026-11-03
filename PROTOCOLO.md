# Protocolo de selección M01

Fecha: 2026-11-03. Este protocolo se guarda antes de ejecutar el ajuste y la evaluación de esta implementación; no constituye un preregistro externo.

- Fuente exclusiva: datos/M01.csv de la cátedra; 14 casos de entrenamiento y 6 de prueba, sin redistribuirlos.
- Familia fijada: SÍ si al menos DOS de tres indicadores alcanzan sus respectivos umbrales (relación de infantería, porcentaje de caballería, terreno). NO en cualquier otro caso válido.
- Candidatos: puntos medios entre valores distintos consecutivos de cada variable, calculados SOLO con entrenamiento.
- Costo de selección: 5 FP + 1 FN. La ficha ordena cualitativamente los daños; el cociente 5:1 es una decisión didáctica propuesta por la IA, NO una cifra de la cátedra ni una estimación histórica.
- Desempate determinista: menor FP; mayor margen mínimo de clasificación en entrenamiento; menor distancia cuadrática normalizada de los umbrales al centro del rango de entrenamiento; finalmente orden lexicográfico de umbrales.
- Margen: mediana de las tres diferencias (valor - umbral) normalizadas por sus rangos de entrenamiento, con signo positivo para la etiqueta real. NO es una probabilidad.
- Se congelan umbrales antes de medir prueba. No se cambia familia, costo ni desempate para mejorar prueba.
- Comparadores: siempre NO (clase mayoritaria de entrenamiento) y siempre SÍ. Se muestra también una variante permisiva de una sola señal para analizar falsos positivos, sin elegirla por la prueba.
- Transparencia: las etiquetas de prueba son públicas y aparecieron en el chat al leer la ficha antes de programar. No se afirma una evaluación ciega. La selección computacional recibe exclusivamente entrenamiento; el caso nuevo del docente será una comprobación adicional.
- Ningún identificador, conjunto o resultado_real se usa como predictor. La etiqueta solo interviene en ajuste y evaluación.
