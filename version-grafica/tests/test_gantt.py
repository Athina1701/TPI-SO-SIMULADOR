from copy import deepcopy
import unittest

from visualizaciones import agregarIntervalos, GanttDinamico
from unittest.mock import MagicMock


class PruebasGantt(unittest.TestCase):
    def test_bloque_actualizado_inmediatamente_sin_temporizador(self):
        canvas = MagicMock()
        canvas.winfo_width.return_value = 600
        canvas.xview.return_value = (0, 1)
        canvas.create_rectangle.return_value = 1
        canvas.create_text.return_value = 2
        vista = GanttDinamico(canvas, lambda _: "#2563EB", lambda _: None)
        vista.actualizar([{"tipo": "ejecucion_cpu", "proceso": "P1", "inicio": 0, "fin": 1}], 0, 1)
        canvas.coords.assert_any_call(1, 12, 12, 40, 52)
        canvas.after.assert_not_called()

    def test_seleccion_transitoria_no_consume_cpu(self):
        historial = []
        eventos = [{"tipo": "seleccion_cpu", "proceso": "P1"},
                   {"tipo": "expropiacion_cpu", "proceso": "P1", "reemplazante": "P2"},
                   {"tipo": "ejecucion_cpu", "proceso": "P2", "inicio": 0, "fin": 1}]
        antes = deepcopy(eventos)
        agregarIntervalos(historial, eventos, 0, 1)
        self.assertEqual(historial, [{"inicio": 0, "fin": 1, "proceso": "P2"}])
        self.assertEqual(eventos, antes)

    def test_libre_y_union_de_intervalos(self):
        historial = []
        agregarIntervalos(historial, [], 0, 1)
        agregarIntervalos(historial, [], 1, 2)
        for inicio in (2, 3):
            agregarIntervalos(historial, [{"tipo": "ejecucion_cpu", "proceso": "P1",
                                          "inicio": inicio, "fin": inicio + 1}], inicio, inicio + 1)
        agregarIntervalos(historial, [], 4, 5)
        self.assertEqual(historial, [{"inicio": 0, "fin": 2, "proceso": None},
                                     {"inicio": 2, "fin": 4, "proceso": "P1"},
                                     {"inicio": 4, "fin": 5, "proceso": None}])

    def test_historial_no_se_recorta(self):
        historial = []
        for inicio in range(1500):
            agregarIntervalos(historial, [{"tipo": "ejecucion_cpu", "proceso": str(inicio % 2),
                                          "inicio": inicio, "fin": inicio + 1}], inicio, inicio + 1)
        self.assertEqual(len(historial), 1500)
        self.assertEqual(historial[0]["inicio"], 0)
        self.assertEqual(historial[-1]["fin"], 1500)


if __name__ == "__main__":
    unittest.main()
