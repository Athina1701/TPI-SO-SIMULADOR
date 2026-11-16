"""Pruebas de reglas y limitaciones, con tiempos esperados independientes."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

import simulador_equipo2 as motor
from test_memoria_visual import LOTES, REFERENCIA


SECUENCIAS = [
    [(3, 5, "P1"), (10, 11, "P3"), (11, 15, "P2"), (15, 17, "P4"), (20, 22, "P5")],
    [(0, 2, "P2"), (2, 11, "P5"), (11, 21, "P4"), (21, 36, "P3"), (36, 56, "P1")],
    [(0, 1, "P2"), (1, 3, "P4"), (3, 7, "P7"), (7, 13, "P6"), (13, 18, "P8"),
     (18, 28, "P1"), (28, 40, "P3"), (40, 55, "P5")],
    [(0, 2, "P1"), (2, 3, "P2"), (3, 4, "P3"), (4, 5, "P4"), (5, 8, "P3"),
     (8, 10, "P5"), (10, 13, "P7"), (13, 15, "P9"), (15, 20, "P8"),
     (20, 24, "P10"), (24, 30, "P6"), (30, 38, "P2"), (38, 56, "P1")],
    [(0, 5, "P1"), (5, 9, "P3")],
    [(0, 4, "P2"), (4, 6, "P5"), (6, 9, "P3"), (9, 14, "P1"), (14, 18, "P7"),
     (18, 21, "P9"), (21, 26, "P8"), (26, 32, "P4"), (32, 38, "P10"), (38, 45, "P6")],
]

ASIGNACIONES = [
    "P1:3:0:120;P2:10:40:130;P3:10:0:40;P4:14:170:60;P5:20:0:90",
    "P1:11:0:180;P2:0:0:120;P3:0:340:100;P4:0:200:140;P5:0:120:80",
    "P1:0:170:100;P2:0:0:80;P3:0:270:120;P4:0:80:90;P5:0:390:50;P6:3:70:85;P7:3:0:70;P8:13:0:140",
    "P1:0:0:80;P2:2:80:80;P3:3:160:70;P4:4:230:100;P5:6:230:90;P6:7:320:60;P7:10:160:120;P8:13:160:110;P9:13:380:70;P10:20:160:130",
    "P1:0:0:200;P3:2:200:30",
    "P1:0:60:50;P2:0:0:60;P3:1:110:70;P4:1:180:80;P5:2:260:90;P6:4:350:100;P7:14:0:110;P8:21:0:120;P9:18:0:130;P10:26:0:140",
]
METRICAS = [
    "P1:0:2;P2:1:5;P3:0:1;P4:1:3;P5:0:2",
    "P1:36:56;P2:0:2;P3:21:36;P4:11:21;P5:2:11",
    "P1:18:28;P2:0:1;P3:28:40;P4:1:3;P5:40:55;P6:4:10;P7:0:4;P8:6:14",
    "P1:36:56;P2:27:36;P3:1:5;P4:0:1;P5:2:4;P6:17:23;P7:2:5;P8:5:11;P9:0:5;P10:5:13",
    "P1:0:5;P3:3:7",
    "P1:9:14;P2:0:4;P3:5:8;P4:25:31;P5:2:4;P6:34:43;P7:8:15;P8:12:23;P9:4:17;P10:14:34",
]


def preparar(filas):
    motor.iniciarSimulacion([{"id": f"P{i}", "TA": ta, "TI": ti, "tamano": tam}
                            for i, (ta, ti, tam) in enumerate(filas, 1)])


class PruebasMotor(unittest.TestCase):
    def setUp(self):
        motor.reiniciarSimulacion()
        self.addCleanup(motor.reiniciarSimulacion)

    def cargar(self, texto):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "procesos.txt"
            archivo.write_text(texto, encoding="utf-8")
            return motor.cargarProcesosArchivo(archivo)

    def comprobar_invariantes(self):
        estado = motor.obtenerEstado()
        memoria = sorted(estado["memoria"], key=lambda p: p["comienzo"])
        self.assertEqual(sum(p["tamanio"] for p in memoria), 450)
        self.assertEqual(memoria[0]["comienzo"], 0)
        for a, b in zip(memoria, memoria[1:]):
            self.assertEqual(a["comienzo"] + a["tamanio"], b["comienzo"])
        self.assertEqual(sum(p["tamanio"] for p in memoria if p["procesoAsignado"] is None),
                         estado["disponibleEnMemoria"])
        cpu = estado["ejecucion"]["procEjecutandose"]
        colas = estado["colas"]
        self.assertEqual(estado["GM"], len(colas["listos"]) + len(colas["listosSuspendidos"]) + bool(cpu))
        self.assertLessEqual(estado["GM"], 5)
        ids = [p["id"] for cola in colas.values() for p in cola] + ([cpu["id"]] if cpu else [])
        self.assertEqual(len(ids), len(set(ids)))
        asignados = [p["procesoAsignado"] for p in memoria if p["procesoAsignado"] is not None]
        self.assertFalse(set(asignados) & {p["id"] for p in colas["terminados"]})
        self.assertEqual(set(asignados), {p["id"] for p in colas["listos"]} | ({cpu["id"]} if cpu else set()))

    def ejecutar(self, limite=1000):
        eventos = []
        for _ in range(limite):
            if not motor.cantProcesos:
                return eventos
            tiempo = motor.tActual
            motor.ejecutarIteracion(mostrarConsola=False)
            self.assertEqual(motor.tActual, tiempo + 1)
            self.comprobar_invariantes()
            eventos.extend(motor.obtenerEventos())
        self.fail("La entrada válida no finalizó dentro del límite de prueba")

    @staticmethod
    def secuencia(eventos):
        intervalos = []
        for e in eventos:
            if e["tipo"] != "ejecucion_cpu":
                continue
            if intervalos and intervalos[-1][1] == e["inicio"] and intervalos[-1][2] == e["proceso"]:
                intervalos[-1] = (intervalos[-1][0], e["fin"], e["proceso"])
            else:
                intervalos.append((e["inicio"], e["fin"], e["proceso"]))
        return intervalos

    def test_seis_lotes_secuencias_metricas_y_eventos(self):
        for i, lote in enumerate(LOTES):
            with self.subTest(lote=i + 1):
                carga = self.cargar("\n".join(f"P{j} {r}" for j, r in enumerate(lote.split(";"), 1)))
                motor.iniciarSimulacion(carga["procesos"])
                eventos = self.ejecutar()
                self.assertEqual(self.secuencia(eventos), SECUENCIAS[i])
                esperadas = sorted((campos[0], *map(int, campos[1:]))
                                   for campos in (fila.split(":") for fila in ASIGNACIONES[i].split(";")))
                reales = sorted((e["proceso"], e["tiempo"], e["particion"]["comienzo"], e["particion"]["tamanio"])
                                for e in eventos if e["tipo"] == "asignacion_memoria")
                self.assertEqual(reales, esperadas)
                esperadas_metricas = {p: (int(te), int(tr)) for p, te, tr in
                                      (fila.split(":") for fila in METRICAS[i].split(";"))}
                self.assertEqual({p.id: (p.TE, p.TR) for p in motor.terminados}, esperadas_metricas)
                self.assertEqual((motor.tActual, *motor.CalcularPromediosTEyTR()), REFERENCIA[i])
                self.assertEqual([e["secuencia"] for e in eventos], list(range(1, len(eventos) + 1)))
                self.assertEqual([e["tiempo"] for e in eventos], sorted(e["tiempo"] for e in eventos))
                self.assertEqual(len([e for e in eventos if e["tipo"] == "finalizacion"]), len(motor.terminados))
                for evento in eventos:
                    if evento["tipo"] == "expropiacion_cpu":
                        self.assertLess(evento["TIReemplazante"], evento["TI"])
                self.assertEqual(motor.disponibleEnMemoria, 450)

    def test_unico_proceso_y_cpu_inactiva(self):
        preparar([(3, 2, 1)])
        self.assertEqual(self.secuencia(self.ejecutar()), [(3, 5, "P1")])
        self.assertEqual((motor.terminados[0].TE, motor.terminados[0].TR), (0, 2))
        self.assertEqual(motor.CalcularRendimientoSistema(motor.terminados, 5), .2)

    def test_empate_no_expropia(self):
        preparar([(0, 4, 1), (1, 3, 1)])
        eventos = self.ejecutar()
        self.assertEqual(self.secuencia(eventos), [(0, 4, "P1"), (4, 7, "P2")])
        self.assertFalse(any(e["tipo"] == "expropiacion_cpu" for e in eventos))

    def test_arribos_simultaneos_desempate_estable(self):
        preparar([(0, 2, 1), (0, 2, 1), (0, 1, 1)])
        self.assertEqual(self.secuencia(self.ejecutar()), [(0, 1, "P3"), (1, 3, "P1"), (3, 5, "P2")])

    def test_expropiaciones_consecutivas(self):
        preparar([(0, 10, 1), (1, 4, 1), (2, 1, 1)])
        self.assertEqual(self.secuencia(self.ejecutar()),
                         [(0, 1, "P1"), (1, 2, "P2"), (2, 3, "P3"), (3, 6, "P2"), (6, 15, "P1")])

    def test_finalizacion_en_instante_de_arribo(self):
        preparar([(0, 2, 1), (2, 1, 1)])
        self.assertEqual(self.secuencia(self.ejecutar()), [(0, 2, "P1"), (2, 3, "P2")])

    def test_tiempos_muy_diferentes(self):
        preparar([(0, 100, 1), (1, 1, 1)])
        self.assertEqual(self.secuencia(self.ejecutar()), [(0, 1, "P1"), (1, 2, "P2"), (2, 101, "P1")])

    def test_asignacion_exacta_y_un_kb(self):
        for tamano in (1, 450):
            with self.subTest(tamano=tamano):
                motor.reiniciarSimulacion()
                proceso = motor.Proceso("P", 0, 1, tamano, "nuevo")
                self.assertTrue(motor.CargarEnMemoria(proceso)[0])
                self.assertEqual(motor.disponibleEnMemoria, 450 - tamano)
                self.assertEqual(len(motor.memoria), 1 if tamano == 450 else 2)
                liberado, motor.memoria = motor.LiberarMemoria(proceso, motor.memoria)
                self.assertTrue(liberado)
                self.assertEqual(motor.memoria[0]["tamanio"], 450)

    def test_best_fit_hueco_mas_pequeno(self):
        motor.memoria[:] = [
            {"id": 1, "comienzo": 0, "tamanio": 200, "procesoAsignado": None},
            {"id": 2, "comienzo": 200, "tamanio": 100, "procesoAsignado": "X"},
            {"id": 3, "comienzo": 300, "tamanio": 150, "procesoAsignado": None}]
        motor.disponibleEnMemoria = 350
        self.assertTrue(motor.CargarEnMemoria(motor.Proceso("P", 0, 1, 120, "nuevo"))[0])
        self.assertEqual(next(p["comienzo"] for p in motor.memoria if p["procesoAsignado"] == "P"), 300)

    def test_id_none_libera_solo_su_particion(self):
        carga = self.cargar("A 0 1 100\nNone 0 2 100\n")
        motor.iniciarSimulacion(carga["procesos"])
        eventos = self.ejecutar()
        liberaciones = [e for e in eventos if e["tipo"] == "liberacion_memoria"]
        self.assertEqual([e["proceso"] for e in liberaciones], ["A", "None"])
        self.assertEqual(liberaciones[-1]["particionAnterior"]["procesoAsignado"], "None")
        self.assertEqual(motor.disponibleEnMemoria, 450)
        self.assertEqual(motor.memoria, [
            {"id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None}])
        self.assertEqual(motor.cantProcesos, 0)
        self.assertEqual(motor.GM, 0)

    def test_empate_best_fit_y_efecto_de_presentacion(self):
        partes = [{"id": 9, "comienzo": 400, "tamanio": 50, "procesoAsignado": None},
                  {"id": 2, "comienzo": 50, "tamanio": 350, "procesoAsignado": "X"},
                  {"id": 4, "comienzo": 0, "tamanio": 50, "procesoAsignado": None}]
        for presentar, direccion in ((False, 400), (True, 0)):
            motor.memoria[:] = deepcopy(partes)
            motor.disponibleEnMemoria = 100
            if presentar:
                with redirect_stdout(io.StringIO()):
                    motor.MostrarMemoria(motor.memoria, [])
            motor.CargarEnMemoria(motor.Proceso("P", 0, 1, 50, "nuevo"))
            self.assertEqual(next(p["comienzo"] for p in motor.memoria if p["procesoAsignado"] == "P"), direccion)

    def test_fragmentacion_externa(self):
        motor.memoria[:] = [{"id": 1, "comienzo": 0, "tamanio": 100, "procesoAsignado": None},
                           {"id": 2, "comienzo": 100, "tamanio": 250, "procesoAsignado": "X"},
                           {"id": 3, "comienzo": 350, "tamanio": 100, "procesoAsignado": None}]
        motor.disponibleEnMemoria = 200
        self.assertFalse(motor.CargarEnMemoria(motor.Proceso("P", 0, 1, 150, "nuevo"))[0])
        self.assertEqual(motor.disponibleEnMemoria, 200)

    def test_fusion_tres_particiones(self):
        partes = [{"id": i, "comienzo": inicio, "tamanio": tam, "procesoAsignado": None}
                  for i, (inicio, tam) in enumerate(((0, 50), (50, 150), (200, 250)), 1)]
        self.assertEqual(motor.JuntarParticiones(partes),
                         [{"id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None}])

    def test_multiprogramacion_y_espera_en_nuevos_no_contabilizada(self):
        preparar([(0, 1, 1)] * 6)
        motor.ejecutarIteracion(mostrarConsola=False)
        self.assertEqual(len(motor.nuevos), 1)
        self.ejecutar()
        ultimo = next(p for p in motor.terminados if p.id == "P6")
        self.assertEqual((ultimo.TE, ultimo.TR, ultimo.resguardoTI), (4, 6, 1))
        self.assertNotEqual(ultimo.TE, ultimo.TR - ultimo.resguardoTI)

    def test_suspension_por_memoria_completa(self):
        preparar([(0, 2, 450), (0, 3, 1)])
        motor.ejecutarIteracion(mostrarConsola=False)
        self.assertEqual([p.id for p in motor.listosSuspendidos], ["P2"])
        self.assertEqual(motor.disponibleEnMemoria, 0)
        self.ejecutar()

    def test_carga_separadores_vacios_y_registros_invalidos(self):
        carga = self.cargar("\nP1,0,2,1\n\nP2 1 3 450\nmal\nP3 x 1 2\nP4 0 1 451\nP5\t2\t1\t1\n")
        self.assertEqual([p["id"] for p in carga["procesos"]], ["P1", "P2", "P5"])
        self.assertTrue(carga["mensajes"])
        self.assertEqual(motor.cantProcesos, 0)

    def test_limite_diez_antes_de_ordenar(self):
        for cantidad in (10, 12):
            carga = self.cargar("\n".join(f"P{i} {cantidad-i} 1 1" for i in range(cantidad)))
            self.assertEqual(len(carga["procesos"]), 10)
            self.assertEqual({p["id"] for p in carga["procesos"]}, {f"P{i}" for i in range(10)})

    def test_archivo_vacio_e_inexistente(self):
        self.assertEqual(self.cargar("")["procesos"], [])
        antes = motor.obtenerEstado()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                motor.cargarProcesosArchivo(Path(tmp) / "inexistente.txt")
        self.assertEqual(motor.obtenerEstado(), antes)

    def test_menu_no_numerico_permite_reintentar(self):
        ruta = Path(motor.__file__)
        resultado = subprocess.run([sys.executable, "-B", str(ruta)], input="abc\n\n0\n", text=True,
                                   capture_output=True, timeout=5)
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(resultado.stderr, "")
        self.assertEqual(resultado.stdout.count("Seleccione una opci"), 3)
        self.assertNotIn("ValueError", resultado.stdout)

    def test_importacion_no_abre_menu(self):
        raiz = Path(motor.__file__).parent
        resultado = subprocess.run([sys.executable, "-B", "-c", "import simulador_equipo2"],
                                   cwd=raiz, capture_output=True, text=True, timeout=5)
        self.assertEqual((resultado.returncode, resultado.stdout, resultado.stderr), (0, "", ""))

    def test_carga_preserva_simulacion_en_curso(self):
        preparar([(0, 3, 50), (0, 4, 100)])
        motor.ejecutarIteracion(mostrarConsola=False)
        estado, eventos = motor.obtenerEstado(), motor.obtenerEventos()
        carga = self.cargar("\n".join(f"X{i} 0 1 1" for i in range(12)))
        self.assertEqual(len(carga["procesos"]), 10)
        self.assertEqual(motor.obtenerEstado(), estado)
        self.assertEqual(motor.obtenerEventos(), eventos)

    def test_eventos_solo_ultima_iteracion(self):
        preparar([(0, 3, 1)])
        motor.ejecutarIteracion(mostrarConsola=False)
        primeros = motor.obtenerEventos()
        copia = deepcopy(primeros)
        motor.ejecutarIteracion(mostrarConsola=False)
        segundos = motor.obtenerEventos()
        self.assertFalse({e["secuencia"] for e in primeros} & {e["secuencia"] for e in segundos})
        self.assertEqual(primeros, copia)
        self.assertEqual([e["tipo"] for e in segundos], ["ejecucion_cpu"])

    def test_ingreso_manual_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as tmp:
            existente = Path(tmp) / "existente.txt"
            nuevo = Path(tmp) / "nuevo.txt"
            existente.write_text("contenido original")
            with patch("builtins.input", side_effect=[str(existente), str(nuevo), "P1 0 2 50", ""]):
                with redirect_stdout(io.StringIO()):
                    resultado = motor.crearArchivoProcesos()
            self.assertEqual(resultado, str(nuevo))
            self.assertEqual(existente.read_text(), "contenido original")
            self.assertEqual(nuevo.read_text(), "P1 0 2 50\n")

    def test_error_creacion_archivo_mensaje_claro(self):
        salida = io.StringIO()
        with patch("builtins.input", return_value="procesos.txt"), \
             patch("builtins.open", side_effect=PermissionError("detalle tecnico")), \
             redirect_stdout(salida):
            self.assertIsNone(motor.crearArchivoProcesos())
        self.assertIn("ubicación y los permisos", salida.getvalue())
        self.assertNotIn("detalle tecnico", salida.getvalue())

    def test_error_escritura_archivo_mensaje_claro(self):
        salida = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "manual.txt"
            with patch("builtins.input", side_effect=[str(ruta), "Peña 0 1 10", ""]), \
                 patch("builtins.open") as abrir, redirect_stdout(salida):
                archivo = abrir.return_value
                archivo.write.side_effect = OSError("detalle tecnico")
                self.assertIsNone(motor.crearArchivoProcesos())
                abrir.return_value.__exit__.assert_called_once()
        self.assertIn("puede haber quedado incompleto", salida.getvalue())
        self.assertNotIn("detalle tecnico", salida.getvalue())

    def test_entradas_invalidas_rechazadas_antes_de_simular(self):
        carga = self.cargar("P 0 0 0\nP -1 -2 -3\n")
        self.assertEqual(carga["procesos"], [])
        self.assertEqual(carga["resumen"]["rechazados"], 2)
        self.assertEqual([e["linea"] for e in carga["errores"]], [1, 2])

    def test_ti_no_positivo_no_ingresa_al_motor(self):
        for ti in (0, -1):
            with self.assertRaises(ValueError):
                preparar([(0, ti, 1)])
            self.assertEqual(motor.cantProcesos, 0)

    def test_tamano_negativo_no_ingresa_al_motor(self):
        with self.assertRaises(ValueError):
            preparar([(0, 1, -1)])
        self.assertEqual(motor.memoria[0]["comienzo"], 0)

    def test_id_duplicado_no_inicializa_simulacion(self):
        with self.assertRaises(ValueError):
            motor.iniciarSimulacion([{"id": "P", "TA": 0, "TI": 5, "tamano": 100},
                                     {"id": "P", "TA": 1, "TI": 1, "tamano": 50}])
        self.assertEqual(motor.disponibleEnMemoria, 450)

    def test_tamano_cero_y_arribo_negativo_se_rechazan(self):
        with self.assertRaises(ValueError):
            preparar([(-2, 1, 0)])
        self.assertEqual(motor.cantProcesos, 0)

    def test_consultas_independientes_y_reinicio(self):
        preparar([(0, 2, 20), (0, 3, 30)])
        inicial = motor.obtenerEstado()
        motor.ejecutarIteracion(mostrarConsola=False)
        antes, eventos = motor.obtenerEstado(), motor.obtenerEventos()
        copia = motor.obtenerEstado()
        copia["memoria"][0]["tamanio"] = -1
        copia["colas"]["listos"].clear()
        eventos_copia = motor.obtenerEventos()
        eventos_copia[0]["tipo"] = "modificado"
        self.assertEqual(motor.obtenerEstado(), antes)
        self.assertEqual(motor.obtenerEventos(), eventos)
        preparar([(0, 2, 20), (0, 3, 30)])
        self.assertEqual(motor.obtenerEstado(), inicial)
        self.assertEqual(motor.obtenerEventos(), [])
        self.assertEqual(motor.contadorIDparticion, 2)
        self.assertEqual(motor._secuenciaEvento, 0)


if __name__ == "__main__":
    unittest.main()
