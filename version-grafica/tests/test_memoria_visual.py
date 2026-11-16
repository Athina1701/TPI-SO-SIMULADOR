from copy import deepcopy
from pathlib import Path
import unittest

from memoria_visual import MemoriaVisual
import simulador_equipo2 as motor


ARCHIVOS_LOTES = [Path(__file__).parent / "lotes" / f"lote{i}.txt" for i in range(1, 7)]
LOTES = [";".join(" ".join(linea.split()[1:]) for linea in archivo.read_text().splitlines())
         for archivo in ARCHIVOS_LOTES]
REFERENCIA = [(22, .4, 2.6), (56, 14, 25.2), (55, 12.125, 19.375),
              (56, 9.5, 15.9), (9, 1.5, 6), (45, 11.3, 19.3)]


class CanvasPrueba:
    def __init__(self):
        self.items = {}
        self.creados = 0

    def winfo_width(self):
        return 1104

    def delete(self, ident):
        self.items.pop(ident, None)

    def create_rectangle(self, *coords, **opciones):
        return self._crear("rectangle", coords, opciones)

    def create_text(self, *args, **kwargs):
        return self._crear("text", args, kwargs)

    def _crear(self, tipo, coords, opciones):
        self.creados += 1
        self.items[self.creados] = (tipo, coords, opciones)
        return self.creados

    def coords(self, ident, *coords):
        tipo, _, opciones = self.items[ident]
        self.items[ident] = (tipo, coords, opciones)

    def itemconfigure(self, ident, **cambios):
        self.items[ident][2].update(cambios)

class PruebasMemoria(unittest.TestCase):
    def setUp(self):
        motor.reiniciarSimulacion()
        self.addCleanup(motor.reiniciarSimulacion)
        self.canvas = CanvasPrueba()
        self.vista = MemoriaVisual(self.canvas, lambda _: "#2563EB", self.registrar)
        self.vista.sincronizar(motor.obtenerEstado()["memoria"])

    def registrar(self, partes):
        self.assertEqual(sum(p["tamanio"] for p in partes), 450)
        self.assertEqual(partes[0]["comienzo"], 0)
        for a, b in zip(partes, partes[1:]):
            self.assertEqual(a["comienzo"] + a["tamanio"], b["comienzo"])

    def test_seis_lotes_actualizacion_inmediata(self):
        for indice, archivo in enumerate(ARCHIVOS_LOTES):
            with self.subTest(lote=indice + 1):
                motor.iniciarSimulacion(motor.cargarProcesosArchivo(archivo)["procesos"])
                self.vista.sincronizar(motor.obtenerEstado()["memoria"])
                while motor.cantProcesos > 0:
                    motor.ejecutarIteracion(mostrarConsola=False)
                    estado, eventos = motor.obtenerEstado(), motor.obtenerEventos()
                    self.vista.sincronizar(estado["memoria"])
                    self.assertEqual(self.vista.particiones, sorted(estado["memoria"], key=lambda p: p["comienzo"]))
                    self.assertEqual(motor.obtenerEstado(), estado)
                    self.assertEqual(motor.obtenerEventos(), eventos)
                    self.assertFalse(any(opciones.get("tags") == "resaltado"
                                         for _, _, opciones in self.canvas.items.values()))
                self.assertEqual((motor.tActual, *motor.CalcularPromediosTEyTR()), REFERENCIA[indice])

    def test_sincronizacion_independiente_y_reinicio(self):
        motor.iniciarSimulacion([{"id": "P1", "TA": 0, "TI": 2, "tamano": 80}])
        motor.ejecutarIteracion(mostrarConsola=False)
        estado = motor.obtenerEstado()
        self.vista.sincronizar(estado["memoria"])
        anterior = deepcopy(self.vista.particiones)
        copia = deepcopy(estado["memoria"])
        self.vista.sincronizar(copia)
        copia[0]["tamanio"] = -1
        self.assertEqual(self.vista.particiones, anterior)
        libre = [{"id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None}]
        self.vista.sincronizar(libre)
        self.assertEqual(self.vista.particiones, libre)
        self.assertEqual(motor.obtenerEstado(), estado)
        self.assertFalse(hasattr(self.canvas, "after"))

    def test_particiones_y_sistema_operativo_proporcionales(self):
        self.vista.sincronizar([
            {"id": 1, "comienzo": 0, "tamanio": 80, "procesoAsignado": "P1"},
            {"id": 2, "comienzo": 80, "tamanio": 370, "procesoAsignado": None},
        ])
        anchos = [coords[2] - coords[0] for tipo, coords, _ in self.canvas.items.values() if tipo == "rectangle"]
        self.assertEqual(sorted(anchos), [160, 200, 740])

    def test_redibujar_no_crea_elementos(self):
        creados = self.canvas.creados
        for _ in range(100):
            self.vista.dibujar()
        self.assertEqual(self.canvas.creados, creados)


if __name__ == "__main__":
    unittest.main()
