"""Integración del punto de entrada tradicional, sin abrir ventanas."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import simulador_equipo2 as motor
from test_memoria_visual import ARCHIVOS_LOTES, REFERENCIA


class PruebasConsola(unittest.TestCase):
    def ejecutar(self, entrada):
        raiz = Path(__file__).resolve().parents[1]
        resultado = subprocess.run([sys.executable, "-B", str(raiz / "simulador_equipo2.py")],
                                   input=entrada, text=True, encoding="utf-8", capture_output=True,
                                   cwd=raiz, timeout=10,
                                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, "")
        return resultado.stdout

    def test_seis_lotes_desde_menu(self):
        for indice, archivo in enumerate(ARCHIVOS_LOTES):
            with self.subTest(lote=indice + 1):
                salida = self.ejecutar(f"2\n1\n{archivo.resolve()}\n")
                self.assertIn(f"Tiempo de Espera Promedio: {REFERENCIA[indice][1]:.1f}", salida)
                self.assertRegex(salida, r"Tiempo de Retorno Promedio:\s+" + re.escape(f"{REFERENCIA[indice][2]:.1f}"))
                filas = re.findall(r"^P\d+\s+\|\s+terminado", salida, re.MULTILINE)
                self.assertEqual(len(filas), [5, 5, 8, 10, 2, 10][indice])

    def test_salir_informacion_y_opcion_invalida(self):
        self.ejecutar("0\n")
        self.assertIn("Best Fit", self.ejecutar("1\n\n0\n"))
        self.assertIn("no es válida", self.ejecutar("9\n0\n"))
        self.assertIn("no es válida", self.ejecutar("abc\n0\n"))

    def test_ingreso_manual_desde_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "manual.txt"
            salida = self.ejecutar(f"2\n2\n{archivo}\nP1 0 1 1\n\n")
            self.assertEqual(archivo.read_text(), "P1 0 1 1\n")
            self.assertIn("Tiempo de Espera Promedio: 0.0", salida)

    def test_archivo_mixto_informa_rechazos_y_ejecuta_validos(self):
        archivo = Path(__file__).parent / "lotes" / "validos_invalidos.txt"
        salida = self.ejecutar(f"2\n1\n{archivo.resolve()}\n")
        self.assertIn("Procesos cargados: 5. Registros rechazados: 13.", salida)
        self.assertIn("Línea 3 (ID: P2)", salida)
        self.assertEqual(len(re.findall(r"^P\d+\s+\|\s+terminado", salida, re.MULTILINE)), 5)

    def test_exportacion_consola_utf8_con_acentos(self):
        ids = ["Peña", "Bárbara", "José", "Güemes"]
        texto = "\n".join(f"{id_} 0 1 10" for id_ in ids)
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "manual.txt"
            salida = self.ejecutar(f"2\n2\n{archivo}\n{texto}\n\n")
            self.assertEqual(archivo.read_bytes().decode("utf-8").splitlines(), texto.splitlines())
            carga = motor.cargarProcesosArchivo(archivo)
            self.assertEqual([p["id"] for p in carga["procesos"]], ids)
            self.assertFalse(carga["errores"])
            for id_ in ids:
                self.assertIn(id_, salida)


if __name__ == "__main__":
    unittest.main()
