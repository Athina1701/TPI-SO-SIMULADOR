"""Historial de ejecución y dibujo incremental del diagrama de Gantt."""

from math import ceil


def agregarIntervalos(historial, eventos, inicio, fin):
    """Añade ejecución real; la ausencia de consumo en un paso indica CPU libre."""
    def agregar(desde, hasta, proceso):
        if hasta <= desde:
            return
        if historial and historial[-1]["fin"] == desde and historial[-1]["proceso"] == proceso:
            historial[-1]["fin"] = hasta
        else:
            historial.append({"inicio": desde, "fin": hasta, "proceso": proceso})

    cursor = inicio
    for evento in eventos:
        if evento["tipo"] == "ejecucion_cpu":
            agregar(cursor, evento["inicio"], None)
            agregar(evento["inicio"], evento["fin"], evento["proceso"])
            cursor = evento["fin"]
    agregar(cursor, fin, None)


class GanttDinamico:
    """Conserva todo el historial y reutiliza los bloques ya dibujados."""

    def __init__(self, canvas, color_proceso, al_seleccionar):
        self.canvas = canvas
        self.color_proceso = color_proceso
        self.al_seleccionar = al_seleccionar
        self.intervalos = []
        self.items = []
        self._firma_ejes = None

    def reiniciar(self):
        self.canvas.delete("all")
        self.intervalos.clear()
        self.items.clear()
        self._firma_ejes = None
        self.canvas.xview_moveto(0)
        self.dibujar()

    def actualizar(self, eventos, inicio, fin):
        agregarIntervalos(self.intervalos, eventos, inicio, fin)
        self.dibujar()

    def _dibujarBloque(self, indice):
        intervalo = self.intervalos[indice]
        fin = intervalo["fin"]
        x0, x1 = 12 + intervalo["inicio"] * 28, 12 + fin * 28
        bloque, texto = self.items[indice]
        proceso = intervalo["proceso"]
        etiqueta = str(proceso) if proceso is not None else "Libre"
        color = self.color_proceso(proceso) if proceso is not None else "#25364D"
        self.canvas.coords(bloque, x0, 12, x1, 52)
        self.canvas.itemconfigure(bloque, fill=color)
        self.canvas.coords(texto, (x0 + x1) / 2, 32)
        self.canvas.itemconfigure(texto, text=etiqueta if x1 - x0 > 24 else "")

    def dibujar(self):
        canvas = self.canvas
        for indice in range(len(self.items), len(self.intervalos)):
            etiqueta = f"intervalo_{indice}"
            bloque = canvas.create_rectangle(0, 12, 0, 52, outline="#0B1120", width=2, tags=etiqueta)
            texto = canvas.create_text(0, 32, fill="#F1F5F9", font=("Segoe UI", 10), tags=etiqueta)
            self.items.append((bloque, texto))
            canvas.tag_bind(etiqueta, "<Enter>", lambda evento, i=indice: self._describir(i))
        for indice in range(len(self.items)):
            self._dibujarBloque(indice)
        fin = self.intervalos[-1]["fin"] if self.intervalos else 0
        firma = (fin, canvas.winfo_width())
        if firma != self._firma_ejes:
            seguir = canvas.xview()[1] >= .98
            canvas.delete("ejes")
            salto = max(1, ceil(fin / 80))
            for tiempo in sorted(set(range(0, fin + 1, salto)) | {fin}):
                canvas.create_text(12 + tiempo * 28, 67, text=str(tiempo), fill="#94A3B8",
                                   font=("Segoe UI", 9), tags="ejes")
            canvas.configure(scrollregion=(0, 0, max(canvas.winfo_width(), 32 + fin * 28), 80))
            if seguir:
                canvas.xview_moveto(1)
            self._firma_ejes = firma

    def _describir(self, indice):
        intervalo = self.intervalos[indice]
        nombre = intervalo["proceso"] if intervalo["proceso"] is not None else "CPU libre"
        self.al_seleccionar(f"{nombre} · [{intervalo['inicio']}, {intervalo['fin']}) · "
                            f"{intervalo['fin'] - intervalo['inicio']} unidades de tiempo")
