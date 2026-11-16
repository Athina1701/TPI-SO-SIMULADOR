"""Validación compartida y diagnósticos de carga por registro original."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
from pathlib import Path
import tempfile
import unittest

import simulador_equipo2 as motor


class PruebasValidaciones(unittest.TestCase):
    def setUp(self):
        motor.reiniciarSimulacion()
        self.addCleanup(motor.reiniciarSimulacion)

    def cargar(self, texto):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "procesos.txt"
            ruta.write_text(texto, encoding="utf-8")
            return motor.cargarProcesosArchivo(ruta)

    def comprobar_rechazo(self, registro, motivo):
        carga = self.cargar("\n" + registro + "\n")
        self.assertEqual(carga["procesos"], [])
        self.assertEqual(carga["resumen"], {"aceptados": 0, "rechazados": 1, "noProcesados": 0})
        self.assertEqual(carga["errores"][0]["linea"], 2)
        self.assertIn(motivo, " ".join(carga["errores"][0]["motivos"]))

    def test_cantidad_exacta_de_campos(self):
        for linea in ("P1 0 1", "P1 0 1 20 extra"):
            with self.subTest(linea=linea):
                self.comprobar_rechazo(linea, "exactamente cuatro campos")

    def test_id_vacio(self):
        self.comprobar_rechazo(",0,1,30", "identificador del proceso no puede estar vacío")

    def test_tipo_de_tamano(self):
        for tamano in ("grande", "1.5", "nan", "inf"):
            with self.subTest(tamano=tamano):
                self.comprobar_rechazo(f"P1 0 1 {tamano}", "tamaño debe ser un número entero")

    def test_tipo_de_arribo(self):
        self.comprobar_rechazo("P1 cero 1 30", "tiempo de arribo debe ser un número entero")

    def test_tipo_de_irrupcion(self):
        self.comprobar_rechazo("P1 0 uno 30", "tiempo de irrupción debe ser un número entero")

    def test_tamano_mayor_que_cero(self):
        for tamano in (0, -1):
            with self.subTest(tamano=tamano):
                self.comprobar_rechazo(f"P1 0 1 {tamano}", "tamaño del proceso debe ser mayor que cero")

    def test_tamano_maximo(self):
        self.comprobar_rechazo("P1 0 1 451", "no puede superar los 450 KB")

    def test_arribo_no_negativo(self):
        self.comprobar_rechazo("P1 -1 1 30", "tiempo de arribo debe ser mayor o igual que cero")

    def test_irrupcion_positiva(self):
        for ti in (0, -2):
            with self.subTest(ti=ti):
                self.comprobar_rechazo(f"P1 0 {ti} 30", "tiempo de irrupción debe ser mayor que cero")

    def test_id_duplicado_entre_aceptados(self):
        carga = self.cargar("P1 0 2 30\nP1 1 2 40\n")
        self.assertEqual(carga["resumen"]["aceptados"], 1)
        self.assertEqual(carga["errores"][0]["id"], "P1")
        self.assertIn("ya existe", carga["mensajes"])

    def test_id_rechazado_no_reserva_identificador(self):
        carga = self.cargar("P1 0 0 30\nP1 0 1 30\n")
        self.assertEqual(carga["resumen"]["aceptados"], 1)
        self.assertEqual(carga["resumen"]["rechazados"], 1)
        self.assertEqual(carga["procesos"][0]["TI"], 1)

    def test_todos_los_motivos_cuentan_como_un_registro_rechazado(self):
        carga = self.cargar("P1 -1 0 -30\n")
        self.assertEqual(len(carga["errores"][0]["motivos"]), 3)
        self.assertEqual(carga["resumen"]["rechazados"], 1)

    def test_separadores_y_lineas_vacias(self):
        carga = self.cargar("\n \nP1 0 1 1\nP2,0,1,450\n\nP3\t1\t2\t30\n")
        self.assertEqual(carga["resumen"], {"aceptados": 3, "rechazados": 0, "noProcesados": 0})

    def test_campos_vacios_con_comas(self):
        self.comprobar_rechazo("P1,,1,30", "tiempo de arribo debe ser un número entero")

    def test_limite_distingue_rechazados_y_no_procesados(self):
        texto = "MAL 0 0 5\n" + "\n".join(f"P{i} 0 1 1" for i in range(10))
        texto += "\n\nP10 0 1 1\nregistro incorrecto\n"
        carga = self.cargar(texto)
        self.assertEqual(carga["resumen"], {"aceptados": 10, "rechazados": 1, "noProcesados": 2})
        self.assertEqual([p["linea"] for p in carga["noProcesados"]], [13, 14])
        self.assertEqual(carga["errores"][0]["linea"], 1)
        self.assertIn("no se validó este registro", carga["mensajes"])

    def test_diez_validos_exactos_no_generan_omitidos(self):
        carga = self.cargar("\n".join(f"P{i} 0 1 1" for i in range(10)))
        self.assertEqual(carga["resumen"], {"aceptados": 10, "rechazados": 0, "noProcesados": 0})

    def test_archivo_vacio(self):
        carga = self.cargar("\n  \n")
        self.assertEqual(carga["resumen"], {"aceptados": 0, "rechazados": 0, "noProcesados": 0})

    def test_codificaciones_utf8_bom_y_windows1252(self):
        ids = ["Peña", "Bárbara", "José", "Güemes"]
        texto = "\n".join(f"{id_} 0 1 10" for id_ in ids)
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "acentos.txt"
            for codificacion in ("utf-8", "utf-8-sig", "cp1252"):
                with self.subTest(codificacion=codificacion):
                    ruta.write_bytes(texto.encode(codificacion))
                    with redirect_stdout(io.StringIO()):
                        self.assertTrue(motor.existeArchivo(ruta))
                    carga = motor.cargarProcesosArchivo(ruta)
                    self.assertFalse(carga["errores"])
                    self.assertEqual([p["id"] for p in carga["procesos"]], ids)

    def test_codificacion_incompatible_no_modifica_motor(self):
        motor.iniciarSimulacion([{"id": "A", "TA": 0, "TI": 2, "tamano": 10}])
        antes = motor.obtenerEstado()
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "ilegible.txt"
            ruta.write_bytes(b"\x81")
            with self.assertRaises(UnicodeError):
                motor.cargarProcesosArchivo(ruta)
            with redirect_stdout(io.StringIO()):
                self.assertFalse(motor.existeArchivo(ruta))
        self.assertEqual(motor.obtenerEstado(), antes)

    def test_archivo_mixto_y_ejecucion_de_validos(self):
        ruta = Path(__file__).parent / "lotes" / "validos_invalidos.txt"
        carga = motor.cargarProcesosArchivo(ruta)
        self.assertEqual(carga["resumen"], {"aceptados": 5, "rechazados": 13, "noProcesados": 0})
        self.assertEqual([e["linea"] for e in carga["errores"]], list(range(3, 16)))
        self.assertEqual({p["id"] for p in carga["procesos"]}, {"P1", "P2", "P3", "P4", "P5"})
        motor.iniciarSimulacion(carga["procesos"])
        for _ in range(100):
            if not motor.cantProcesos:
                break
            motor.ejecutarIteracion(mostrarConsola=False)
        self.assertEqual(motor.cantProcesos, 0)
        self.assertEqual(len(motor.terminados), 5)
        self.assertEqual(motor.disponibleEnMemoria, 450)

    def test_consola_y_api_usan_mismos_datos_y_diagnosticos(self):
        ruta = Path(__file__).parent / "lotes" / "validos_invalidos.txt"
        carga = motor.cargarProcesosArchivo(ruta)
        cola = []
        salida = io.StringIO()
        with redirect_stdout(salida):
            motor.cargarNuevos(ruta, cola)
        self.assertEqual([vars(p) for p in cola], carga["procesos"])
        self.assertEqual(salida.getvalue().strip(), carga["mensajes"])

    def test_carga_y_consulta_del_informe_no_modifican_motor(self):
        motor.iniciarSimulacion([{"id": "A", "TA": 0, "TI": 3, "tamano": 30}])
        motor.ejecutarIteracion(mostrarConsola=False)
        estado, eventos = motor.obtenerEstado(), motor.obtenerEventos()
        carga = self.cargar("P1 0 0 30\nP2 0 1 30\n")
        antes = deepcopy(carga)
        motor.formatearInformeCarga(carga)
        self.assertEqual(carga, antes)
        self.assertEqual(motor.obtenerEstado(), estado)
        self.assertEqual(motor.obtenerEventos(), eventos)

    def test_api_rechaza_tipos_inadecuados_sin_perder_simulacion(self):
        motor.iniciarSimulacion([{"id": "A", "TA": 0, "TI": 2, "tamano": 30}])
        estado = motor.obtenerEstado()
        for campo, valor in (("TA", 1.5), ("TI", True), ("tamano", None), ("id", 5)):
            registro = {"id": "P1", "TA": 0, "TI": 1, "tamano": 30}
            registro[campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                motor.iniciarSimulacion([registro])
            self.assertEqual(motor.obtenerEstado(), estado)

    def test_api_rechaza_mas_de_diez(self):
        procesos = [{"id": f"P{i}", "TA": 0, "TI": 1, "tamano": 1} for i in range(11)]
        with self.assertRaises(ValueError):
            motor.iniciarSimulacion(procesos)
        self.assertEqual(motor.cantProcesos, 0)

    def test_inicializacion_invalida_no_aplica_cambios_parciales(self):
        motor.iniciarSimulacion([{"id": "A", "TA": 0, "TI": 4, "tamano": 80}])
        motor.ejecutarIteracion(mostrarConsola=False)
        antes, eventos = motor.obtenerEstado(), motor.obtenerEventos()
        with self.assertRaises(ValueError):
            motor.iniciarSimulacion([{"id": "P1", "TA": 0, "TI": 1, "tamano": 30},
                                     {"id": "P2", "TA": 0, "TI": 0, "tamano": 30}])
        self.assertEqual(motor.obtenerEstado(), antes)
        self.assertEqual(motor.obtenerEventos(), eventos)


if __name__ == "__main__":
    unittest.main()
