"""Pruebas técnicas; no son nuevos ejemplos históricos etiquetados."""
import copy
import json
import math
from pathlib import Path
import unittest
import sistema_M01 as s

ROOT = Path(__file__).resolve().parent

class PruebasM01(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = s.cargar_datos(ROOT / 'datos/M01.csv')
        cls.ent = [f for f in cls.filas if f['conjunto'] == 'entrenamiento']
        cls.modelo = s.ajustar(cls.ent)
        cls.reporte = s.evaluar(cls.filas, cls.modelo)

    def test_umbrales_reproducibles(self):
        self.assertEqual(self.modelo['umbrales'], {'relacion':1.42,'caballeria':15.0,'terreno':6.5})
        self.assertEqual(self.modelo['candidatos_evaluados'], 1144)

    def test_todas_predicciones(self):
        esperado = [0,0,1,0,0,0,0,1,1,1,1,0,0,1,0,0,0,1,0,0]
        obtenido = [s.predecir(*(f[v] for v in s.VARIABLES), self.modelo)['prediccion'] for f in self.filas]
        self.assertEqual(obtenido, esperado)

    def test_matrices_cierran(self):
        for grupo,n in [('entrenamiento',14),('prueba',6)]:
            for nombre in ('sistema','siempre_no','siempre_si','variante_una_senal'):
                m=self.reporte[grupo][nombre]
                self.assertEqual(sum(m[k] for k in ('VP','FN','FP','VN')),n)
        self.assertEqual({k:self.reporte['prueba']['sistema'][k] for k in ('VP','FN','FP','VN')},
                         {'VP':1,'FN':2,'FP':0,'VN':3})

    def test_prediccion_solo_tres_entradas(self):
        import inspect
        self.assertEqual(list(inspect.signature(s.predecir).parameters),
                         ['relacion','caballeria','terreno','modelo'])

    def test_todas_combinaciones_logicas(self):
        import itertools
        for bits in itertools.product([0,1], repeat=3):
            valores=[umbral + (0.01 if bit else -0.01)
                     for bit,umbral in zip(bits,[1.42,15.0,6.5])]
            self.assertEqual(s.predecir(*valores,self.modelo)['prediccion'],int(sum(bits)>=2))

    def test_limites_inclusivos(self):
        self.assertEqual(s.predecir(1.42,15,0,self.modelo)['prediccion'],1)
        self.assertEqual(s.predecir(1.419999,15,0,self.modelo)['prediccion'],0)
        self.assertEqual(s.predecir(.9,15,6.5,self.modelo)['prediccion'],1)

    def test_coma_decimal(self):
        self.assertEqual(s.predecir('1,60','25','8',self.modelo)['prediccion'],1)

    def test_entradas_invalidas(self):
        for valores in [(0,20,5),(-1,20,5),(1,-1,5),(1,101,5),(1,20,-1),(1,20,11),
                        ('abc',20,5),('',20,5),(None,20,5),(float('nan'),20,5),(1,float('inf'),5),(True,20,5)]:
            with self.subTest(valores=valores):
                with self.assertRaises(ValueError):
                    s.predecir(*valores,self.modelo)

    def test_advertencia_extrapolacion(self):
        self.assertTrue(s.predecir(3,60,8,self.modelo)['advertencias'])
        self.assertFalse(s.predecir(1.6,25,8,self.modelo)['advertencias'])

    def test_denominadores_cero(self):
        self.assertIsNone(s.metricas([0,1],[0,0])['precision'])
        self.assertIsNone(s.metricas([0,0],[0,0])['sensibilidad'])
        self.assertIsNone(s.metricas([1,1],[1,1])['especificidad'])
        with self.assertRaises(ValueError): s.metricas([],[])
        with self.assertRaises(ValueError): s.metricas([1],[1,0])

    def test_rechaza_prueba_en_ajuste(self):
        with self.assertRaises(ValueError): s.ajustar(self.filas)
        alterado=copy.deepcopy(self.ent); alterado[0]['conjunto']='prueba'
        with self.assertRaises(ValueError): s.ajustar(alterado)

    def test_etiquetas_prueba_no_eligen_umbrales(self):
        # Alteración SOLO en memoria para test técnico; no modifica el CSV oficial.
        alternativo=copy.deepcopy(self.filas)
        for f in alternativo:
            if f['conjunto']=='prueba': f['resultado_real']=1-f['resultado_real']
        modelo=s.ajustar([f for f in alternativo if f['conjunto']=='entrenamiento'])
        self.assertEqual(modelo,self.modelo)

    def test_orden_entrenamiento_no_cambia_ajuste(self):
        self.assertEqual(s.ajustar(list(reversed(self.ent))),self.modelo)

    def test_modelo_y_metricas_guardadas(self):
        self.assertEqual(json.loads((ROOT/'resultados/modelo_M01.json').read_text()),self.modelo)
        self.assertEqual(json.loads((ROOT/'resultados/metricas.json').read_text()),self.reporte)

    def test_corroboracion_reduce_falsos_positivos_entrenamiento(self):
        self.assertEqual(self.reporte['entrenamiento']['variante_una_senal']['FP'],5)
        self.assertEqual(self.reporte['entrenamiento']['sistema']['FP'],0)

if __name__=='__main__': unittest.main(verbosity=2)
