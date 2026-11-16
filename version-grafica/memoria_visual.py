from copy import deepcopy


class MemoriaVisual:
    """Dibuja una copia del estado actual de RAM, sin efectos ni temporizadores."""
    PANEL = "#172339"
    TEXTO = "#F1F5F9"
    SECUNDARIO = "#94A3B8"
    LIBRE = "#25364D"

    def __init__(self, canvas, color_proceso, al_actualizar):
        self.canvas = canvas
        self.color_proceso = color_proceso
        self.al_actualizar = al_actualizar
        self.particiones = []
        self.elementos = {}
        self._vistos = set()

    def sincronizar(self, particiones):
        self.particiones = sorted(deepcopy(particiones), key=lambda p: p["comienzo"])
        self.dibujar()
        self.al_actualizar(deepcopy(self.particiones))

    def _color(self, particion):
        proceso = particion["procesoAsignado"]
        return self.color_proceso(proceso) if proceso is not None else self.LIBRE

    def _item(self, clave, tipo, coordenadas, **opciones):
        """Reutiliza los elementos de Canvas; solo envía los cambios a Tk."""
        self._vistos.add(clave)
        if clave not in self.elementos:
            crear = getattr(self.canvas, f"create_{tipo}")
            ident = crear(*coordenadas, **opciones)
            self.elementos[clave] = (ident, coordenadas, opciones)
            return
        ident, anteriores, estilo = self.elementos[clave]
        if anteriores != coordenadas:
            self.canvas.coords(ident, *coordenadas)
        cambios = {k: v for k, v in opciones.items() if estilo.get(k) != v}
        if cambios:
            self.canvas.itemconfigure(ident, **cambios)
        self.elementos[clave] = (ident, coordenadas, opciones)

    def dibujar(self):
        canvas = self.canvas
        self._vistos.clear()
        ancho = max(canvas.winfo_width() - 4, 100)
        for particion in self.particiones:
            x0 = 2 + ancho * particion["comienzo"] / 550
            x1 = 2 + ancho * (particion["comienzo"] + particion["tamanio"]) / 550
            color = self._color(particion)
            borde = self.PANEL
            etiqueta = particion["procesoAsignado"]
            self._item(("bloque", particion["id"]), "rectangle", (x0, 8, x1, 60),
                       fill=color, outline=borde, width=2,
                       tags=("particion", f"particion_{particion['id']}"))
            if x1 - x0 > 48:
                self._item(("etiqueta", particion["id"]), "text", ((x0 + x1) / 2, 34),
                                   text=str(etiqueta) if etiqueta is not None else "Libre",
                                   fill=self.TEXTO, font=("Segoe UI", 10))
        xso = 2 + ancho * 450 / 550
        self._item("so", "rectangle", (xso, 8, 2 + ancho, 60), fill="#334155", outline=self.PANEL,
                                width=2, tags="sistema_operativo")
        self._item("texto_so", "text", ((xso + 2 + ancho) / 2, 34), text="SO\n100 KB", fill=self.TEXTO,
                           font=("Segoe UI", 9))
        for x, texto, anchor in [(2, "0 KB", "w"), (xso, "450", "center"),
                                  (2 + ancho, "550 KB", "e")]:
            self._item(("marca", texto), "text", (x, 76), text=texto, fill=self.SECUNDARIO, anchor=anchor,
                               font=("Segoe UI", 9))
        for clave in self.elementos.keys() - self._vistos:
            ident, _, _ = self.elementos.pop(clave)
            canvas.delete(ident)
