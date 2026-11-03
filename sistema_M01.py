"""M01: reglas de corroboración, ajuste SOLO con entrenamiento y evaluación reproducible.
Python 3.9+; biblioteca estándar; no requiere internet ni servicios de IA.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
import statistics
from pathlib import Path
from typing import Any

COSTO_FP = 5
COSTO_FN = 1
VARIABLES = ('relacion', 'caballeria', 'terreno')
COLUMNAS = (
    'Relación de fuerzas (infantería romana / cartaginesa)',
    'Caballería propia (% del ejército)',
    'Terreno favorable (índice 0 a 10; 10 = llano propio y conocido)',
)


def numero(valor: Any) -> float:
    """Admite coma decimal en ingreso manual; rechaza booleanos y no finitos."""
    if isinstance(valor, bool):
        raise ValueError('Ingrese un número, no un booleano.')
    try:
        x = float(str(valor).strip().replace(',', '.'))
    except (ValueError, TypeError) as exc:
        raise ValueError(f'Valor no numérico: {valor!r}') from exc
    if not math.isfinite(x):
        raise ValueError('No se admiten NaN ni infinitos.')
    return x


def validar_entrada(relacion: Any, caballeria: Any, terreno: Any) -> tuple[float, float, float]:
    r, c, t = map(numero, (relacion, caballeria, terreno))
    if r <= 0:
        raise ValueError('La relación de infantería debe ser mayor que cero.')
    if not 0 <= c <= 100:
        raise ValueError('La caballería debe expresarse como porcentaje entre 0 y 100.')
    if not 0 <= t <= 10:
        raise ValueError('El terreno debe estar entre 0 y 10.')
    return r, c, t


def cargar_datos(ruta: str | Path) -> list[dict]:
    with Path(ruta).open(encoding='utf-8-sig', newline='') as f:
        lector = csv.DictReader(f)
        esperadas = {'caso', 'conjunto', *COLUMNAS, 'resultado_real'}
        if set(lector.fieldnames or []) != esperadas:
            raise ValueError('El CSV no tiene las columnas oficiales de M01.')
        filas = []
        for fila in lector:
            valores = validar_entrada(*(fila[c] for c in COLUMNAS))
            y = int(fila['resultado_real'])
            if y not in (0, 1):
                raise ValueError('La etiqueta real debe ser 0 o 1.')
            filas.append(dict(caso=int(fila['caso']), conjunto=fila['conjunto'],
                              **dict(zip(VARIABLES, valores)), resultado_real=y))
    if len(filas) != 20 or {f['caso'] for f in filas} != set(range(1, 21)):
        raise ValueError('Se requieren exactamente los 20 casos oficiales, sin duplicados.')
    for f in filas:
        esperado = 'entrenamiento' if f['caso'] <= 14 else 'prueba'
        if f['conjunto'] != esperado:
            raise ValueError('No se permite cambiar la división 1–14 / 15–20.')
    return sorted(filas, key=lambda f: f['caso'])


def puntos_medios(valores: list[float]) -> list[float]:
    xs = sorted(set(valores))
    if len(xs) < 2:
        raise ValueError('Una variable constante no admite este ajuste.')
    return [round((a + b) / 2, 10) for a, b in zip(xs, xs[1:])]


def matriz(reales: list[int], predichos: list[int]) -> dict:
    if not reales or len(reales) != len(predichos):
        raise ValueError('Listas vacías o de distinta longitud.')
    if any(y not in (0, 1) for y in [*reales, *predichos]):
        raise ValueError('Las etiquetas deben ser binarias.')
    return {
        'VP': sum(y == 1 and p == 1 for y, p in zip(reales, predichos)),
        'FN': sum(y == 1 and p == 0 for y, p in zip(reales, predichos)),
        'FP': sum(y == 0 and p == 1 for y, p in zip(reales, predichos)),
        'VN': sum(y == 0 and p == 0 for y, p in zip(reales, predichos)),
    }


def metricas(reales: list[int], predichos: list[int]) -> dict:
    m = matriz(reales, predichos)
    vp, fn, fp, vn = (m[k] for k in ('VP', 'FN', 'FP', 'VN'))
    dividir = lambda a, b: a / b if b else None
    n = len(reales)
    return {**m, 'N': n,
            'exactitud': (vp + vn) / n,
            'precision': dividir(vp, vp + fp),
            'sensibilidad': dividir(vp, vp + fn),
            'especificidad': dividir(vn, vn + fp),
            'costo_total': COSTO_FP * fp + COSTO_FN * fn,
            'costo_medio': (COSTO_FP * fp + COSTO_FN * fn) / n}


def ajustar(entrenamiento: list[dict]) -> dict:
    """Busca umbrales sin recibir prueba. No se altera la familia por su resultado."""
    if len(entrenamiento) != 14 or {f['caso'] for f in entrenamiento} != set(range(1, 15)):
        raise ValueError('El ajuste exige SOLO los casos 1 a 14.')
    if any(f['conjunto'] != 'entrenamiento' for f in entrenamiento):
        raise ValueError('Está prohibido usar prueba en el ajuste.')
    X = [tuple(f[v] for v in VARIABLES) for f in entrenamiento]
    y = [f['resultado_real'] for f in entrenamiento]
    columnas = list(zip(*X))
    rangos = [max(xs) - min(xs) for xs in columnas]
    centros = [(max(xs) + min(xs)) / 2 for xs in columnas]
    candidatos = [puntos_medios(list(xs)) for xs in columnas]
    mejor, mejor_key, total = None, None, 0
    for umbrales in itertools.product(*candidatos):
        total += 1
        pred = [int(sum(a >= b for a, b in zip(x, umbrales)) >= 2) for x in X]
        m = metricas(y, pred)
        margenes = [(2 * real - 1) * statistics.median(
            (a - b) / rango for a, b, rango in zip(x, umbrales, rangos))
            for x, real in zip(X, y)]
        margen = min(margenes)
        distancia = sum(((u - centro) / rango) ** 2
                        for u, centro, rango in zip(umbrales, centros, rangos))
        # Redondeo SOLO para estabilidad del desempate numérico, no de las métricas.
        key = (m['costo_total'], m['FP'], -round(margen, 12), round(distancia, 12), umbrales)
        if mejor_key is None or key < mejor_key:
            mejor_key = key
            mejor = {'umbrales': dict(zip(VARIABLES, umbrales)),
                     'minimo_senales': 2, 'margen_minimo_entrenamiento': margen,
                     'metricas_entrenamiento': m}
    assert mejor is not None
    mejor.update(candidatos_evaluados=total, costo_fp=COSTO_FP, costo_fn=COSTO_FN,
                 rangos_entrenamiento={v: [min(xs), max(xs)] for v, xs in zip(VARIABLES, columnas)},
                 seleccion='Costo, FP, margen mínimo, centralidad, orden lexicográfico; solo casos 1–14.')
    return mejor


def predecir(relacion: Any, caballeria: Any, terreno: Any, modelo: dict) -> dict:
    """La función de inferencia NO recibe caso, conjunto ni resultado_real."""
    valores = validar_entrada(relacion, caballeria, terreno)
    senales = {v: x >= modelo['umbrales'][v] for v, x in zip(VARIABLES, valores)}
    cuenta = sum(senales.values())
    pred = int(cuenta >= modelo['minimo_senales'])
    fuera = [v for v, x in zip(VARIABLES, valores)
             if not modelo['rangos_entrenamiento'][v][0] <= x <= modelo['rangos_entrenamiento'][v][1]]
    return {'prediccion': pred, 'salida': 'SÍ' if pred else 'NO', 'senales': senales,
            'cantidad_senales': cuenta,
            'accion': 'Recomendar aceptar' if pred else 'Recomendar rehuir',
            'explicacion': f'{cuenta} de 3 condiciones favorables; se requieren {modelo["minimo_senales"]}.',
            'advertencias': (['Fuera del rango observado: ' + ', '.join(fuera) + '. Resultado no validado en esa zona.'] if fuera else [])}


def evaluar(filas: list[dict], modelo: dict) -> dict:
    reporte = {}
    for grupo in ('entrenamiento', 'prueba'):
        fs = [f for f in filas if f['conjunto'] == grupo]
        y = [f['resultado_real'] for f in fs]
        pred = [predecir(*(f[v] for v in VARIABLES), modelo)['prediccion'] for f in fs]
        permisivos = [int(any(f[v] >= modelo['umbrales'][v] for v in VARIABLES)) for f in fs]
        reporte[grupo] = {
            'sistema': metricas(y, pred),
            'siempre_no': metricas(y, [0] * len(fs)),
            'siempre_si': metricas(y, [1] * len(fs)),
            'variante_una_senal': metricas(y, permisivos),
            'errores': [f['caso'] for f, p in zip(fs, pred) if p != f['resultado_real']],
        }
    return reporte


def guardar_resultados(filas: list[dict], modelo: dict, reporte: dict, carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / 'metricas.json').write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding='utf-8')
    campos = ['caso', 'conjunto', *VARIABLES, 'resultado_real', 'senales', 'prediccion', 'tipo']
    with (carpeta / 'predicciones_M01.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader()
        for fila in filas:
            p = predecir(*(fila[v] for v in VARIABLES), modelo)
            tipo = {(1, 1): 'VP', (1, 0): 'FN', (0, 1): 'FP', (0, 0): 'VN'}[(fila['resultado_real'], p['prediccion'])]
            w.writerow({**fila, 'senales': p['cantidad_senales'], 'prediccion': p['prediccion'], 'tipo': tipo})


def resumen(reporte: dict) -> str:
    texto = []
    fmt = lambda x: 'No definida (denominador cero)' if x is None else f'{100 * x:.2f}%'
    for grupo, modelos in reporte.items():
        texto.append('\n' + grupo.upper())
        for nombre in ('sistema', 'siempre_no', 'siempre_si'):
            m = modelos[nombre]
            texto.append(f'{nombre}: VP={m["VP"]} FN={m["FN"]} FP={m["FP"]} VN={m["VN"]}; N={m["N"]}')
            texto.append('  ' + '; '.join(f'{k}={fmt(m[k])}' for k in ('exactitud', 'precision', 'sensibilidad', 'especificidad')))
            texto.append(f'  costo 5FP+FN={m["costo_total"]}; costo medio={m["costo_medio"]:.6f}')
        texto.append('Casos mal clasificados: ' + str(modelos['errores']))
    return '\n'.join(texto)


def ejecutar(ruta: str | Path, salida: str | Path) -> tuple[dict, dict]:
    filas = cargar_datos(ruta)
    entrenamiento = [f for f in filas if f['conjunto'] == 'entrenamiento']
    modelo = ajustar(entrenamiento)
    carpeta = Path(salida); carpeta.mkdir(parents=True, exist_ok=True)
    # Congelación antes de llamar a evaluar, que es quien usa las etiquetas de prueba.
    texto_modelo = json.dumps(modelo, ensure_ascii=False, indent=2)
    (carpeta / 'modelo_M01.json').write_text(texto_modelo, encoding='utf-8')
    (carpeta / 'modelo_M01.sha256').write_text(hashlib.sha256(texto_modelo.encode()).hexdigest() + '\n', encoding='utf-8')
    reporte = evaluar(filas, modelo)
    guardar_resultados(filas, modelo, reporte, carpeta)
    (carpeta / 'resumen.txt').write_text(resumen(reporte) + '\n', encoding='utf-8')
    return modelo, reporte


def main() -> None:
    base = Path(__file__).resolve().parent
    p = argparse.ArgumentParser(description='M01: simulación didáctica de decisión del cónsul romano.')
    p.add_argument('--datos', type=Path, default=base / 'datos' / 'M01.csv')
    p.add_argument('--salida', type=Path, default=base / 'resultados')
    p.add_argument('--caso', nargs=3, metavar=('RELACION', 'CABALLERIA', 'TERRENO'))
    args = p.parse_args()
    try:
        modelo, reporte = ejecutar(args.datos, args.salida)
        print('Umbrales congelados:', modelo['umbrales'])
        print(resumen(reporte))
        if args.caso:
            print('\nCASO NUEVO:')
            print(json.dumps(predecir(*args.caso, modelo), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        p.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
