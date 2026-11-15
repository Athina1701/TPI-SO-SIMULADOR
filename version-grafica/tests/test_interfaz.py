"""Pruebas de ventana real, habilitadas con SIMULADOR_PRUEBAS_GUI=1."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import os
from pathlib import Path
import tempfile
from time import monotonic
import tkinter as tk
import unittest
from unittest.mock import patch

import simulador_equipo2 as motor
from test_memoria_visual import LOTES, REFERENCIA
from test_motor import SECUENCIAS


@unittest.skipUnless(os.environ.get("SIMULADOR_PRUEBAS_GUI") == "1", "Requiere una sesión gráfica habilitada")
class PruebasInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interfaz import AplicacionSimulador
        cls.app = AplicacionSimulador()
        cls.app.withdraw()
        cls.errores = []
        cls.app.report_callback_exception = lambda *args: cls.errores.append(args)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.archivos = []
        for indice, lote in enumerate(LOTES):
            archivo = Path(cls.tmp.name) / f"lote{indice + 1}.txt"
            archivo.write_text("\n".join(f"P{i} {r}" for i, r in enumerate(lote.split(";"), 1)))
            cls.archivos.append(archivo)

    @classmethod
    def tearDownClass(cls):
        cls.app.cerrar()
        assert cls.app.tarea is None
        assert not cls.errores, cls.errores
        cls.tmp.cleanup()

    def setUp(self):
        self.app.reiniciar()
        self.app.cambiarVelocidad(4)
        self.app._cerrarCargaManual()
        self.app.borrador_manual.clear()

    def ingresarManual(self, valores):
        for clave, valor in zip(("id", "TA", "TI", "tamano"), valores):
            entrada = self.app.campos_manual[clave]
            entrada.delete(0, "end")
            entrada.insert(0, str(valor))
        return self.app._agregarManual()

    def test_manual_agregar_y_orden(self):
        self.app.abrirCargaManual()
        with patch.object(motor, "validarRegistro", wraps=motor.validarRegistro) as validar:
            self.assertTrue(self.ingresarManual(("B", 2, 3, 450)))
            self.assertTrue(self.ingresarManual(("A", 0, 1, 1)))
        self.assertEqual(validar.call_count, 2)
        self.assertEqual([p["id"] for p in self.app.borrador_manual], ["B", "A"])
        self.assertEqual(self.app.contador_manual.cget("text"), "2/10 procesos")
        self.assertEqual(self.app.tabla_manual.item("0", "values"), ("B", "2", "3", "450"))

    def test_manual_invalidos_conservan_campos(self):
        self.app.abrirCargaManual()
        casos = [("", 0, 1, 10), ("P", -1, 1, 10), ("P", 0, 0, 10),
                 ("P", 0, -1, 10), ("P", 0, 1, 0), ("P", 0, 1, -1),
                 ("P", 0, 1, 451), ("P", "a", 1, 10), ("P", 0, "1.5", 10),
                 ("P", 0, 1, "abc")]
        for valores in casos:
            with self.subTest(valores=valores):
                self.assertFalse(self.ingresarManual(valores))
                self.assertEqual([e.get() for e in self.app.campos_manual.values()], list(map(str, valores)))
                self.assertTrue(self.app.mensaje_manual.cget("text"))
                self.assertFalse(self.app.borrador_manual)
                self.assertTrue(self.app.ventana_manual.winfo_exists())

    def test_manual_duplicados(self):
        self.app.abrirCargaManual()
        self.assertTrue(self.ingresarManual(("P", 0, 1, 10)))
        self.assertFalse(self.ingresarManual(("P", 2, 3, 20)))
        self.assertEqual(len(self.app.borrador_manual), 1)
        self.assertIn("existe", self.app.mensaje_manual.cget("text"))

    def test_manual_limite_y_edicion(self):
        self.app.abrirCargaManual()
        for i in range(10):
            self.assertTrue(self.ingresarManual((f"P{i}", 0, 1, 10)))
        self.assertFalse(self.ingresarManual(("P10", 0, 1, 10)))
        self.app.tabla_manual.selection_set("4")
        self.assertTrue(self.app._editarManual())
        self.assertFalse(self.ingresarManual(("P0", 0, 2, 20)))
        self.assertTrue(self.ingresarManual(("P4", 3, 2, 20)))
        self.assertEqual(self.app.borrador_manual[4], {"id": "P4", "TA": 3, "TI": 2, "tamano": 20})
        self.assertEqual(len(self.app.borrador_manual), 10)
        self.assertEqual(self.app.contador_manual.cget("text"), "10/10 procesos")

    def test_manual_eliminar(self):
        self.app.abrirCargaManual()
        self.assertFalse(self.app._eliminarManual())
        for id_ in ("A", "B", "C"):
            self.ingresarManual((id_, 0, 1, 10))
        self.app.tabla_manual.selection_set("1")
        self.assertTrue(self.app._eliminarManual())
        self.assertEqual([p["id"] for p in self.app.borrador_manual], ["A", "C"])
        self.assertEqual(len(self.app.tabla_manual.get_children()), 2)

    def test_manual_limpiar_con_confirmacion(self):
        self.app.abrirCargaManual()
        self.ingresarManual(("P", 0, 1, 10))
        with patch("interfaz.messagebox.askyesno", return_value=False):
            self.assertFalse(self.app._limpiarManual())
        self.assertEqual(len(self.app.borrador_manual), 1)
        with patch("interfaz.messagebox.askyesno", return_value=True) as confirmar:
            self.assertTrue(self.app._limpiarManual())
            confirmar.assert_called_once()
        self.assertFalse(self.app.borrador_manual)
        self.assertEqual(self.app.contador_manual.cget("text"), "0/10 procesos")

    def test_manual_preparar_y_reiniciar(self):
        self.app.abrirCargaManual()
        self.assertFalse(self.app._usarManual())
        self.ingresarManual(("B", 2, 3, 100))
        self.ingresarManual(("A", 0, 2, 100))
        self.assertTrue(self.app._usarManual())
        self.assertIsNone(self.app.ventana_manual)
        self.assertEqual(self.app.estado_reproduccion, "Preparado")
        self.assertTrue(self.app.carga_manual)
        inicial = motor.obtenerEstado()
        self.app.borrador_manual[0]["TI"] = 99
        self.app.avanzar()
        self.app.reiniciar()
        self.assertEqual(motor.obtenerEstado(), inicial)
        self.assertFalse(motor.obtenerEventos())
        self.assertFalse(self.app.gantt.intervalos)
        self.assertIsNone(self.app.tarea)

    def test_manual_borrador_no_modifica_motor(self):
        self.app.cargarArchivo(self.archivos[0])
        antes = motor.obtenerEstado()
        self.app.abrirCargaManual()
        self.ingresarManual(("P", 0, 1, 10))
        self.app._cerrarCargaManual()
        self.assertEqual(motor.obtenerEstado(), antes)
        self.app.abrirCargaManual()
        self.assertEqual(len(self.app.borrador_manual), 1)
        self.app.tabla_manual.selection_set("0")
        self.app._editarManual()
        self.assertFalse(self.app._usarManual())
        self.assertEqual(motor.obtenerEstado(), antes)
        self.app._cancelarEdicionManual()
        self.app.iniciar()
        self.assertFalse(self.app._usarManual())
        self.assertEqual(self.app.botones["manual"].cget("state"), "disabled")
        self.app.pausar()

    def test_manual_guardar_y_recargar(self):
        self.app.abrirCargaManual()
        self.ingresarManual(("B", 1, 2, 450))
        self.ingresarManual(("A", 0, 1, 1))
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "manual.txt"
            with patch("interfaz.filedialog.asksaveasfilename", return_value=str(ruta)):
                self.assertTrue(self.app._guardarManual())
            self.assertEqual(ruta.read_text(), "B 1 2 450\nA 0 1 1\n")
            carga = motor.cargarProcesosArchivo(ruta)
            self.assertFalse(carga["errores"])
            self.assertEqual(carga["resumen"]["aceptados"], 2)
            self.assertTrue(self.app.cargarArchivo(ruta))
            self.assertFalse(self.app.carga_manual)
            self.assertIsNone(self.app.ventana_manual)

    def test_manual_guardado_cancelacion_y_errores(self):
        self.app.abrirCargaManual()
        self.assertFalse(self.app._guardarManual())
        self.ingresarManual(("P", 0, 1, 10))
        with patch("interfaz.filedialog.asksaveasfilename", return_value=""):
            self.assertFalse(self.app._guardarManual())
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "manual.txt"
            ruta.write_text("original")
            with patch("interfaz.messagebox.askyesno", return_value=False):
                self.assertFalse(self.app._guardarManual(ruta))
            self.assertEqual(ruta.read_text(), "original")
            with patch("interfaz.messagebox.askyesno", return_value=True):
                self.assertTrue(self.app._guardarManual(ruta))
            self.assertEqual(ruta.read_text(), "P 0 1 10\n")
            self.assertFalse(self.app._guardarManual(Path(carpeta) / "no_existe" / "p.txt"))
        self.assertEqual(len(self.app.borrador_manual), 1)

    def test_manual_exportacion_utf8_con_acentos(self):
        self.app.abrirCargaManual()
        ids = ["Peña", "Bárbara", "José", "Güemes"]
        for id_ in ids:
            self.assertTrue(self.ingresarManual((id_, 0, 1, 10)))
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "acentos.txt"
            self.assertTrue(self.app._guardarManual(ruta))
            self.assertEqual(ruta.read_bytes().decode("utf-8"),
                             "".join(f"{id_} 0 1 10\n" for id_ in ids))
            self.assertTrue(self.app.cargarArchivo(ruta))
            self.assertEqual([p["id"] for p in self.app.procesos_cargados], ids)
            for _ in ids:
                self.app.avanzar()
            self.assertEqual([p.id for p in motor.terminados], ids)

    def test_manual_id_no_exportable(self):
        self.app.abrirCargaManual()
        self.assertTrue(self.ingresarManual(("Proceso A", 0, 1, 10)))
        with patch("interfaz.filedialog.asksaveasfilename") as dialogo:
            self.assertFalse(self.app._guardarManual())
            dialogo.assert_not_called()
        self.assertTrue(self.app._usarManual())

    def test_manual_y_archivo_seis_lotes_identicos(self):
        def ejecutar():
            pasos = [(motor.obtenerEstado(), motor.obtenerEventos())]
            for _ in range(1000):
                if not motor.cantProcesos:
                    break
                self.app.avanzar()
                pasos.append((motor.obtenerEstado(), motor.obtenerEventos()))
            self.assertFalse(motor.cantProcesos)
            return pasos, motor.CalcularPromediosTEyTR()

        for archivo in self.archivos:
            with self.subTest(archivo=archivo.name):
                self.app.cargarArchivo(archivo)
                aceptados = {p["id"] for p in self.app.procesos_cargados}
                referencia = ejecutar()
                self.app.abrirCargaManual()
                self.app.borrador_manual.clear()
                for linea in archivo.read_text().splitlines():
                    self.assertEqual(self.ingresarManual(linea.split()), linea.split()[0] in aceptados)
                self.app._usarManual()
                self.assertEqual(ejecutar(), referencia)

    def esperar(self, condicion, limite=3):
        listo = tk.BooleanVar(self.app, value=False)
        resultado = []
        hasta = monotonic() + limite
        def comprobar():
            if condicion():
                resultado.append(True)
                listo.set(True)
            elif monotonic() >= hasta or self.errores:
                listo.set(True)
            else:
                self.app.after(10, comprobar)
        self.app.after(1, comprobar)
        self.app.wait_variable(listo)
        self.assertFalse(self.errores, str(self.errores))
        self.assertTrue(resultado, "Se agotó el tiempo de espera")

    def test_seis_lotes_desde_ventana(self):
        for indice, archivo in enumerate(self.archivos):
            with self.subTest(lote=indice + 1):
                self.assertTrue(self.app.cargarArchivo(archivo))
                for _ in range(1000):
                    if not motor.cantProcesos:
                        break
                    antes = motor.tActual
                    salida = io.StringIO()
                    with redirect_stdout(salida):
                        self.app.avanzar()
                    self.assertEqual(salida.getvalue(), "")
                    self.assertEqual(motor.tActual, antes + 1)
                    self.assertEqual(self.app.estado, motor.obtenerEstado())
                    self.assertEqual(self.app.memoria_visual.particiones,
                                     sorted(motor.obtenerEstado()["memoria"], key=lambda p: p["comienzo"]))
                    self.assertEqual(self.app.gantt.intervalos[-1]["fin"], motor.tActual)
                    cpu = motor.obtenerEstado()["ejecucion"]["procEjecutandose"]
                    self.assertEqual(self.app.cpu_proceso.cget("text"), cpu["id"] if cpu else "—")
                self.assertEqual((motor.tActual, *motor.CalcularPromediosTEyTR()), REFERENCIA[indice])
                self.assertEqual(self.app.metricas["TE"].cget("text"), f"{REFERENCIA[indice][1]:.3f}")
                self.assertEqual(len(self.app.tabla_estadisticas.get_children()), len(motor.terminados))
                self.assertEqual(len(self.app.tabla_memoria.get_children()), 2)
                widgets = [id(w) for w in self.app.paneles_colas["terminados"].winfo_children()]
                self.app.actualizar()
                self.assertEqual(widgets, [id(w) for w in self.app.paneles_colas["terminados"].winfo_children()])
                intervalos = [(i["inicio"], i["fin"], i["proceso"]) for i in self.app.gantt.intervalos
                              if i["proceso"] is not None]
                self.assertEqual(intervalos, SECUENCIAS[indice])
                self.assertEqual(self.app.estado_reproduccion, "Finalizado")
                self.assertIsNone(self.app.tarea)
                self.app.reiniciar()
                self.assertEqual(motor.tActual, 0)
                self.assertFalse(self.app.gantt.intervalos)
                self.assertFalse(motor.obtenerEventos())

    def test_iniciar_pausar_continuar_y_velocidad(self):
        self.app.cargarArchivo(self.archivos[1])
        self.app.iniciar()
        self.esperar(lambda: motor.tActual >= 1)
        self.app.pausar()
        tiempo = motor.tActual
        self.assertIsNone(self.app.tarea)
        self.app.cambiarVelocidad(.25)
        self.assertEqual(motor.tActual, tiempo)
        self.assertEqual(self.app.slider.get(), .25)
        self.app.cambiarVelocidad(4)
        self.app.continuar()
        self.esperar(lambda: motor.tActual > tiempo)
        self.app.reiniciar()
        self.assertEqual(motor.tActual, 0)
        self.assertIsNone(self.app.tarea)

    def test_reinicio_y_carga_sin_esperas(self):
        self.app.cargarArchivo(self.archivos[1])
        self.app.avanzar()
        self.app.reiniciar()
        self.assertFalse(self.app.gantt.intervalos)
        self.app.avanzar()
        self.app.cargarArchivo(self.archivos[0])
        self.assertFalse(self.app.gantt.intervalos)
        self.assertEqual(motor.tActual, 0)

    def test_ventana_responde_y_consultas_no_mutan(self):
        self.app.cargarArchivo(self.archivos[1])
        self.app.cambiarVelocidad(.25)
        self.app.avanzar()
        antes = deepcopy(motor.obtenerEstado())
        latidos = []
        self.app.after(5, lambda: latidos.append(True))
        self.esperar(lambda: bool(latidos))
        self.assertEqual(motor.obtenerEstado(), antes)
        self.app.reiniciar()

    def test_error_de_archivo_no_pierde_estado(self):
        antes = motor.obtenerEstado()
        with patch("interfaz.messagebox.showerror") as mensaje:
            self.assertFalse(self.app.cargarArchivo(Path(self.tmp.name) / "no_existe.txt"))
            mensaje.assert_called_once()
            self.assertNotIn("Errno", mensaje.call_args.args[1])
        self.assertEqual(motor.obtenerEstado(), antes)

    def test_error_interno_mensaje_claro_y_reinicio(self):
        self.app.cargarArchivo(self.archivos[0])
        inicial = motor.obtenerEstado()
        self.app.iniciar()
        with patch("interfaz.motor.ejecutarIteracion", side_effect=RuntimeError("detalle tecnico")), \
             patch("interfaz.messagebox.showerror") as mensaje:
            self.app._ejecutarPaso()
        self.assertEqual(self.app.estado_reproduccion, "Error")
        self.assertIsNone(self.app.tarea)
        self.assertIn("Reinicie", mensaje.call_args.args[1])
        self.assertNotIn("detalle tecnico", mensaje.call_args.args[1])
        self.assertEqual(self.app.botones["continuar"].cget("state"), "disabled")
        self.app.reiniciar()
        self.assertEqual(motor.obtenerEstado(), inicial)
        self.app.avanzar()
        self.assertEqual(motor.tActual, 1)

    def test_informe_azul_y_ejecucion_de_validos(self):
        ruta = Path(__file__).parent / "lotes" / "validos_invalidos.txt"
        self.assertTrue(self.app.cargarArchivo(ruta))
        self.assertTrue(self.app.ventana_informe.winfo_exists())
        self.assertEqual(self.app.ventana_informe.cget("fg_color"), "#0B1120")
        self.assertIsNone(self.app.grab_current())
        texto = self.app.texto_informe.get("1.0", "end")
        self.assertIn("Procesos cargados: 5. Registros rechazados: 13.", texto)
        self.assertIn("Línea 3 (ID: P2)", texto)
        self.assertIn("Línea 15", texto)
        self.assertIn("Aceptados: P1, P2, P3, P5, P4", texto)
        self.app.iniciar()
        self.assertEqual(self.app.estado_reproduccion, "Ejecutando")
        self.app.pausar()
        for _ in range(100):
            if not motor.cantProcesos:
                break
            self.app.avanzar()
        self.assertEqual(motor.cantProcesos, 0)
        self.assertEqual(len(motor.terminados), 5)

    def test_archivo_sin_validos_impide_inicio_y_limpia_carga_anterior(self):
        self.app.cargarArchivo(self.archivos[1])
        self.app.avanzar()
        ruta = Path(self.tmp.name) / "invalidos.txt"
        ruta.write_text("P1 0 0 30\nP2 -1 1 30\n")
        self.assertFalse(self.app.cargarArchivo(ruta))
        self.assertEqual(motor.cantProcesos, 0)
        self.assertEqual(motor.tActual, 0)
        self.assertFalse(self.app.procesos_cargados)
        self.assertEqual(self.app.botones["iniciar"].cget("state"), "disabled")
        self.assertEqual(self.app.botones["paso"].cget("state"), "disabled")
        self.app.iniciar()
        self.assertNotEqual(self.app.estado_reproduccion, "Ejecutando")
        self.assertIn("Registros rechazados: 2", self.app.texto_informe.get("1.0", "end"))

    def test_archivo_vacio_muestra_informe(self):
        ruta = Path(self.tmp.name) / "vacio.txt"
        ruta.write_text("")
        self.assertFalse(self.app.cargarArchivo(ruta))
        self.assertIn("No hay procesos válidos", self.app.texto_informe.get("1.0", "end"))
        self.assertEqual(self.app.botones["iniciar"].cget("state"), "disabled")

    def test_informe_completo_no_se_recorta_como_el_panel_de_eventos(self):
        ruta = Path(self.tmp.name) / "muchos_errores.txt"
        ruta.write_text("\n".join(f"P{i} 0 0 1" for i in range(650)) + "\nOK 0 1 1\n")
        self.assertTrue(self.app.cargarArchivo(ruta))
        texto = self.app.texto_informe.get("1.0", "end")
        self.assertIn("Registros rechazados: 650", texto)
        self.assertIn("Línea 1 (ID: P0)", texto)
        self.assertIn("Línea 650 (ID: P649)", texto)
        self.assertIn("Aceptados: OK.", texto)
        self.app.texto_informe.insert("end", "modificación no permitida")
        self.assertEqual(self.app.texto_informe.get("1.0", "end"), texto)

    def test_informe_de_limite_no_confunde_omitidos_y_rechazados(self):
        self.assertTrue(self.app.cargarArchivo(self.archivos[5]))
        texto = self.app.texto_informe.get("1.0", "end")
        self.assertIn("Registros rechazados: 0. No procesados por límite: 2", texto)
        self.assertIn("Línea 11 (ID: P11): no se procesó", texto)
        self.assertIn("Línea 12 (ID: P12): no se procesó", texto)

    def test_error_de_codificacion_se_informa_sin_excepcion_tecnica(self):
        error = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")
        with patch("interfaz.motor.cargarProcesosArchivo", side_effect=error):
            with patch("interfaz.messagebox.showerror") as mensaje:
                self.assertFalse(self.app.cargarArchivo("archivo.txt"))
        self.assertIn("codificación", mensaje.call_args.args[1])
        self.assertNotIn("codec", mensaje.call_args.args[1])

    def test_pasos_inmediatos_no_programan_efectos(self):
        for velocidad in (.25, 1, 4):
            self.app.cargarArchivo(self.archivos[1])
            self.app.cambiarVelocidad(velocidad)
            with patch.object(self.app, "after", wraps=self.app.after) as temporizador:
                for tiempo in range(1, 4):
                    self.app.avanzar()
                    self.assertEqual(motor.tActual, tiempo)
                    self.assertEqual(self.app.memoria_visual.particiones,
                                     sorted(motor.obtenerEstado()["memoria"], key=lambda p: p["comienzo"]))
                    self.assertEqual(self.app.botones["paso"].cget("state"), "normal")
                temporizador.assert_not_called()
            self.assertIsNone(self.app.tarea)

    def test_redimensionado_y_proporciones(self):
        self.app.deiconify()
        for geometria in ("1000x700", "1380x900"):
            self.app.geometry(geometria)
            self.app.update_idletasks()
            self.assertGreater(self.app.canvas_ram.winfo_width(), 100)
            self.app.dibujarMemoria()
            canvas = self.app.canvas_ram
            partes = [canvas.coords(i) for i in canvas.find_withtag("particion")]
            so = canvas.coords(canvas.find_withtag("sistema_operativo")[0])
            self.assertAlmostEqual(sum(p[2] - p[0] for p in partes) / (so[2] - so[0]), 4.5)
        self.app.withdraw()


if __name__ == "__main__":
    unittest.main()
