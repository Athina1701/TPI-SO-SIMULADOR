from collections import deque
from copy import deepcopy
from pathlib import Path
from time import monotonic
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

import simulador_equipo2 as motor
from memoria_visual import MemoriaVisual
from visualizaciones import GanttDinamico


FONDO = "#0B1120"
PANEL = "#172339"
AZUL = "#2563EB"
HOVER = "#3B82F6"
CELESTE = "#38BDF8"
TEXTO = "#F1F5F9"
SECUNDARIO = "#94A3B8"
BORDE = "#263954"
LIBRE = "#25364D"
COLORES_PROCESOS = ("#2563EB", "#0891B2", "#4F46E5", "#0369A1", "#0E7490",
                    "#4338CA", "#1D4ED8", "#155E75", "#3730A3", "#075985")


class AplicacionSimulador(ctk.CTk):
    """Ventana de una simulación: controles, consultas y reproducción visual."""
    def __init__(self):
        ctk.set_appearance_mode("dark")
        super().__init__()
        self.title("Simulador SO · SRTF / Best Fit")
        self.geometry("1380x900")
        self.minsize(1000, 700)
        self.configure(fg_color=FONDO)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.procesos_cargados = []
        self.ruta_archivo = None
        self.carga_manual = False
        self.ventana_manual = None
        self.borrador_manual = []
        self.indice_edicion = None
        self.ventana_informe = None
        self.texto_informe = None
        self.estado_reproduccion = "Sin archivo"
        self.tarea = None
        self._proximo_paso = None
        self.velocidad = 1.0
        self.lineas_eventos = deque(maxlen=600)
        self.colores = {}
        self._firmas_colas = {}
        self._firma_memoria = None
        self._ultimo_texto_eventos = None
        self._widgets_colas = {}
        motor.reiniciarSimulacion()
        self.estado = motor.obtenerEstado()
        self._construir()
        self.actualizar()

    def _etiqueta(self, padre, texto, size=13, color=TEXTO, bold=False, **kwargs):
        return ctk.CTkLabel(padre, text=texto, text_color=color,
                            font=ctk.CTkFont(family="Segoe UI", size=size,
                                             weight="bold" if bold else "normal"), **kwargs)

    def _panel(self, padre, titulo, subtitulo=None):
        panel = ctk.CTkFrame(padre, fg_color=PANEL, corner_radius=16,
                             border_width=1, border_color=BORDE)
        panel.grid_columnconfigure(0, weight=1)
        self._etiqueta(panel, titulo, 16, bold=True, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=20, pady=(16, 2))
        if subtitulo:
            self._etiqueta(panel, subtitulo, 12, SECUNDARIO, anchor="w").grid(
                row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        return panel

    def _texto(self, padre, altura):
        return ctk.CTkTextbox(padre, height=altura, fg_color=FONDO, text_color=TEXTO,
                              corner_radius=10, font=("Consolas", 12), wrap="none")

    def _tabla(self, padre, columnas, altura):
        marco = ctk.CTkFrame(padre, fg_color=FONDO, corner_radius=10)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(0, weight=1)
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                            height=altura, style="Simulador.Treeview", selectmode="browse")
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, minwidth=60, anchor="center")
        tabla.grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 0))
        vertical = ctk.CTkScrollbar(marco, command=tabla.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ctk.CTkScrollbar(marco, orientation="horizontal", command=tabla.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        return marco, tabla

    @staticmethod
    def _actualizarTabla(tabla, filas):
        """Actualiza las filas existentes y conserva la posición de desplazamiento."""
        for indice, fila in enumerate(filas):
            ident = str(indice)
            valores = tuple(str(valor) for valor in fila)
            if tabla.exists(ident):
                if tuple(tabla.item(ident, "values")) != valores:
                    tabla.item(ident, values=valores)
            else:
                tabla.insert("", "end", iid=ident, values=valores)
        sobrantes = tabla.get_children()[len(filas):]
        if sobrantes:
            tabla.delete(*sobrantes)

    def _construir(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.layout("Simulador.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        estilo.configure("Simulador.Treeview", background=FONDO, foreground=TEXTO,
                         fieldbackground=FONDO, borderwidth=0, rowheight=28, font=("Segoe UI", 11))
        estilo.configure("Simulador.Treeview.Heading", background=PANEL, foreground=CELESTE,
                         borderwidth=0, font=("Segoe UI", 11, "bold"))
        estilo.map("Simulador.Treeview", background=[("selected", AZUL)])
        estilo.map("Simulador.Treeview.Heading", background=[("active", AZUL)])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._construirEncabezado()

        self._construirControles()

        self._construirDashboard()

    def _construirEncabezado(self):
        encabezado = ctk.CTkFrame(self, fg_color=FONDO, corner_radius=0)
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 14))
        encabezado.grid_columnconfigure(0, weight=1)
        self._etiqueta(encabezado, "SIMULADOR / SISTEMAS OPERATIVOS", 23, bold=True).grid(
            row=0, column=0, sticky="w")
        self._etiqueta(encabezado, "SRTF  /  Best Fit    ·    Particiones variables", 13, CELESTE).grid(
            row=1, column=0, sticky="w", pady=(4, 0))
        self.reloj = self._etiqueta(encabezado, "t = 0", 26, CELESTE, True)
        self.reloj.grid(row=0, column=1, rowspan=2, padx=(20, 0))

    def _construirControles(self):
        lateral = ctk.CTkScrollableFrame(self, width=230, fg_color=PANEL, corner_radius=16)
        lateral.grid(row=1, column=0, sticky="nsew", padx=(24, 12), pady=(0, 24))
        lateral.grid_columnconfigure(0, weight=1)
        self._etiqueta(lateral, "CONTROL DE SIMULACIÓN", 13, CELESTE, True).grid(
            row=0, column=0, sticky="w", padx=12, pady=(18, 12))
        self.estado_label = self._etiqueta(lateral, "", 16, bold=True)
        self.estado_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))
        acciones = [("cargar", "Cargar archivo", self.cargarArchivo),
                    ("manual", "Cargar procesos manualmente", self.abrirCargaManual),
                    ("iniciar", "Iniciar simulación", self.iniciar),
                    ("pausar", "Pausar", self.pausar),
                    ("continuar", "Continuar", self.continuar),
                    ("paso", "Avanzar 1 unidad", self.avanzar),
                    ("reiniciar", "Reiniciar", self.reiniciar)]
        self.botones = {}
        for fila, (clave, texto, accion) in enumerate(acciones, 2):
            boton = ctk.CTkButton(lateral, text=texto, command=accion, height=40,
                                  corner_radius=10, fg_color=AZUL, hover_color=HOVER,
                                  text_color=TEXTO, text_color_disabled=SECUNDARIO,
                                  font=("Segoe UI", 13))
            boton.grid(row=fila, column=0, sticky="ew", padx=12, pady=5)
            self.botones[clave] = boton
        self.velocidad_label = self._etiqueta(lateral, "Reproducción · 1.00×", 13)
        fila_velocidad = 2 + len(acciones)
        self.velocidad_label.grid(row=fila_velocidad, column=0, sticky="w", padx=12, pady=(24, 8))
        self.slider = ctk.CTkSlider(lateral, from_=0.25, to=4, number_of_steps=15,
                                    command=self.cambiarVelocidad, progress_color=AZUL,
                                    button_color=CELESTE, button_hover_color=HOVER)
        self.slider.set(1)
        self.slider.grid(row=fila_velocidad + 1, column=0, sticky="ew", padx=12)
        self._etiqueta(lateral, "La velocidad cambia la reproducción;\ncada paso conserva una unidad\nde tiempo simulado.", 12,
                       SECUNDARIO, justify="left").grid(row=fila_velocidad + 2, column=0, sticky="w", padx=12, pady=14)
        self.archivo_label = self._etiqueta(lateral, "Ningún archivo seleccionado", 12,
                                            SECUNDARIO, wraplength=200, justify="left")
        self.archivo_label.grid(row=fila_velocidad + 3, column=0, sticky="w", padx=12, pady=12)
        self.resumen = self._etiqueta(lateral, "", 13, CELESTE, justify="left")
        self.resumen.grid(row=fila_velocidad + 4, column=0, sticky="w", padx=12, pady=12)

    def _construirDashboard(self):
        dashboard = ctk.CTkScrollableFrame(self, fg_color=FONDO, corner_radius=0)
        dashboard.grid(row=1, column=1, sticky="nsew", padx=(0, 16), pady=(0, 24))
        dashboard.grid_columnconfigure(0, weight=1)
        superior = ctk.CTkFrame(dashboard, fg_color="transparent")
        superior.grid(row=0, column=0, sticky="ew")
        superior.grid_columnconfigure(0, weight=1, uniform="superior")
        superior.grid_columnconfigure(1, weight=2, uniform="superior")
        self._construirProcesador(superior)

        self._construirMemoria(superior)

        self._construirColas(dashboard)

        self._construirGantt(dashboard)

        self._construirDetalle(dashboard)

    def _construirProcesador(self, superior):
        cpu = self._panel(superior, "Procesador", "Planificación SRTF")
        cpu.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.cpu_proceso = self._etiqueta(cpu, "—", 34, CELESTE, True)
        self.cpu_proceso.grid(row=2, column=0, padx=20, pady=(14, 4))
        self.cpu_estado = self._etiqueta(cpu, "CPU libre", 13, SECUNDARIO)
        self.cpu_estado.grid(row=3, column=0, padx=20)
        self.cpu_ti = self._etiqueta(cpu, "0 unidades restantes", 14)
        self.cpu_ti.grid(row=4, column=0, padx=20, pady=12)
        self.cpu_barra = ctk.CTkProgressBar(cpu, progress_color=CELESTE, fg_color=LIBRE)
        self.cpu_barra.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 22))
        self.cpu_cambios = self._etiqueta(cpu, "", 12, CELESTE, wraplength=220)
        self.cpu_cambios.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))

    def _construirMemoria(self, superior):
        ram = self._panel(superior, "Memoria RAM", "550 KB totales · 450 KB de usuario + 100 KB de SO")
        ram.grid(row=0, column=1, sticky="nsew")
        self.canvas_ram = tk.Canvas(ram, height=88, bg=PANEL, highlightthickness=0)
        self.canvas_ram.grid(row=2, column=0, sticky="ew", padx=20)
        self.memoria_label = self._etiqueta(ram, "", 12, CELESTE, anchor="w")
        self.memoria_label.grid(row=3, column=0, sticky="ew", padx=20, pady=4)
        tabla_ram, self.tabla_memoria = self._tabla(ram, [
            ("particion", "Partición", 80), ("inicio", "Inicio (KB)", 90),
            ("tamano", "Tamaño (KB)", 100), ("proceso", "Proceso", 140)], 3)
        tabla_ram.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.accion_memoria = self._etiqueta(ram, "Estado actual de la memoria", 11, CELESTE, anchor="w", wraplength=480)
        self.accion_memoria.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.memoria_visual = MemoriaVisual(
            self.canvas_ram, lambda proceso: self.colores.get(proceso, AZUL),
            self._actualizarDetalleMemoria)
        self.memoria_visual.sincronizar(self.estado["memoria"])
        self.canvas_ram.bind("<Configure>", lambda event: self.dibujarMemoria())

    def _construirColas(self, dashboard):
        colas = ctk.CTkFrame(dashboard, fg_color="transparent")
        colas.grid(row=1, column=0, sticky="ew", pady=14)
        self.paneles_colas = {}
        self.titulos_colas = {}
        for columna, (clave, titulo) in enumerate([
            ("nuevos", "Nuevos"), ("listos", "Listos"),
            ("listosSuspendidos", "Suspendidos"), ("terminados", "Terminados")
        ]):
            colas.grid_columnconfigure(columna, weight=1, uniform="colas")
            panel = self._panel(colas, titulo)
            panel.grid(row=0, column=columna, sticky="nsew", padx=(0, 8 if columna < 3 else 0))
            self.titulos_colas[clave] = panel.grid_slaves(row=0, column=0)[0]
            lista = ctk.CTkScrollableFrame(panel, height=150, fg_color=PANEL, corner_radius=0)
            lista.grid(row=2, column=0, sticky="ew", padx=8, pady=(8, 12))
            lista.grid_columnconfigure(0, weight=1)
            self.paneles_colas[clave] = lista

    def _construirGantt(self, dashboard):
        panel_gantt = self._panel(dashboard, "Línea de tiempo · CPU", "Solo intervalos efectivos de ejecución")
        panel_gantt.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        self.canvas_gantt = tk.Canvas(panel_gantt, height=82, bg=FONDO, highlightthickness=0)
        self.canvas_gantt.grid(row=2, column=0, sticky="ew", padx=16)
        scroll_gantt = ctk.CTkScrollbar(panel_gantt, orientation="horizontal", command=self.canvas_gantt.xview)
        scroll_gantt.grid(row=3, column=0, sticky="ew", padx=16)
        self.canvas_gantt.configure(xscrollcommand=scroll_gantt.set)
        self.detalle_gantt = self._etiqueta(panel_gantt,
            "Desplazá la barra para consultar el historial; señalá un bloque para ver su intervalo.",
            12, SECUNDARIO, wraplength=650, anchor="w")
        self.detalle_gantt.grid(row=4, column=0, sticky="ew", padx=16, pady=(4, 12))
        self.gantt = GanttDinamico(self.canvas_gantt, lambda p: self.colores.get(p, AZUL),
                                  lambda texto: self.detalle_gantt.configure(text=texto))
        self.canvas_gantt.bind("<Configure>", lambda evento: self.gantt.dibujar())

    def _construirDetalle(self, dashboard):
        detalle = self._panel(dashboard, "Detalle de la simulación")
        detalle.grid(row=3, column=0, sticky="ew")
        tabs = ctk.CTkTabview(detalle, fg_color=PANEL, segmented_button_selected_color=AZUL,
                              segmented_button_selected_hover_color=HOVER)
        tabs.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        eventos = tabs.add("Eventos")
        estadisticas = tabs.add("Estadísticas")
        for tab in (eventos, estadisticas):
            tab.grid_columnconfigure(0, weight=1)
        self._etiqueta(eventos, "Orden real del motor · últimos 600 eventos y avisos", 12,
                       SECUNDARIO).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.texto_eventos = self._texto(eventos, 200)
        self.texto_eventos.grid(row=1, column=0, sticky="ew")
        self.metricas_label = self._etiqueta(estadisticas, "", 14, CELESTE,
                                             justify="left", anchor="w")
        self.metricas_label.grid(row=0, column=0, sticky="ew", pady=8)
        tarjetas = ctk.CTkFrame(estadisticas, fg_color="transparent")
        tarjetas.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.metricas = {}
        for columna, (clave, titulo) in enumerate([
            ("TE", "Espera promedio"), ("TR", "Retorno promedio"), ("rendimiento", "Procesos / unidad")
        ]):
            tarjetas.grid_columnconfigure(columna, weight=1, uniform="metricas")
            tarjeta = ctk.CTkFrame(tarjetas, fg_color=FONDO, corner_radius=10)
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=4)
            self._etiqueta(tarjeta, titulo, 12, SECUNDARIO).pack(padx=8, pady=(10, 0))
            valor = self._etiqueta(tarjeta, "—", 22, CELESTE, True)
            valor.pack(padx=8, pady=(0, 10))
            self.metricas[clave] = valor
        tabla_stats, self.tabla_estadisticas = self._tabla(estadisticas, [
            ("proceso", "Proceso", 110), ("TA", "Arribo", 90), ("TI", "TI original", 100),
            ("TE", "Espera", 90), ("TR", "Retorno", 90), ("fin", "Finalización", 100)], 5)
        tabla_stats.grid(row=2, column=0, sticky="ew")
        self._etiqueta(estadisticas, "TE conserva el cálculo del motor: espera en listos y suspendidos.",
                       12, SECUNDARIO).grid(row=3, column=0, sticky="w", pady=8)

    def cargarArchivo(self, ruta=None):
        if self.estado_reproduccion == "Ejecutando":
            return False
        if ruta is None:
            ruta = filedialog.askopenfilename(parent=self, title="Cargar procesos",
                                              filetypes=[("Archivos de texto", "*.txt"),
                                                         ("Todos los archivos", "*.*")])
        if not ruta:
            return False
        try:
            carga = motor.cargarProcesosArchivo(ruta)
        except (OSError, UnicodeError) as error:
            if isinstance(error, FileNotFoundError):
                mensaje = "No se encontró el archivo seleccionado. Compruebe su ubicación."
            elif isinstance(error, PermissionError):
                mensaje = "No hay permiso para leer el archivo seleccionado."
            elif isinstance(error, UnicodeError):
                mensaje = "No se pudo interpretar el texto del archivo. Revise su codificación."
            else:
                mensaje = "No se pudo leer el archivo. Compruebe que sea un archivo de texto accesible."
            messagebox.showerror("No se pudo cargar el archivo", mensaje, parent=self)
            return False
        self._cerrarInformeCarga()
        self._cerrarCargaManual()
        self._cancelarTarea()
        self.procesos_cargados = deepcopy(carga["procesos"])
        self.ruta_archivo = str(ruta)
        self.carga_manual = False
        self.colores = {p["id"]: COLORES_PROCESOS[i % len(COLORES_PROCESOS)]
                        for i, p in enumerate(self.procesos_cargados)}
        if self.procesos_cargados:
            self._preparar()
        else:
            self.reiniciar()
            self.estado_reproduccion = "Sin procesos válidos"
        self.lineas_eventos.append(f"Archivo: {Path(ruta).name} · {len(self.procesos_cargados)} procesos cargados")
        self.lineas_eventos.extend(carga["mensajes"].strip().splitlines())
        self.actualizar()
        if carga["errores"] or carga["noProcesados"] or not carga["procesos"]:
            self._mostrarInformeCarga(carga)
        return bool(carga["procesos"])

    def abrirCargaManual(self):
        if self.estado_reproduccion == "Ejecutando":
            return False
        if self.ventana_manual is not None:
            self.ventana_manual.lift()
            return True
        ventana = ctk.CTkToplevel(self)
        self.ventana_manual = ventana
        self.indice_edicion = None
        ventana.title("Carga manual de procesos")
        ventana.geometry("800x650")
        ventana.minsize(680, 540)
        ventana.configure(fg_color=FONDO)
        ventana.transient(self)
        ventana.protocol("WM_DELETE_WINDOW", self._cerrarCargaManual)
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(3, weight=1)
        self._etiqueta(ventana, "Carga manual de procesos", 21, CELESTE, True).grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 12))
        formulario = ctk.CTkFrame(ventana, fg_color=PANEL, corner_radius=12)
        formulario.grid(row=1, column=0, sticky="ew", padx=24)
        self.campos_manual = {}
        for columna, (clave, titulo) in enumerate([
            ("id", "ID del proceso"), ("TA", "Arribo (TA)"),
            ("TI", "Irrupción (TI)"), ("tamano", "Tamaño (KB)")
        ]):
            formulario.grid_columnconfigure(columna, weight=1, uniform="entrada")
            self._etiqueta(formulario, titulo, 13).grid(row=0, column=columna, padx=10, pady=(12, 4))
            entrada = ctk.CTkEntry(formulario, fg_color=FONDO, border_color=BORDE,
                                   text_color=TEXTO, corner_radius=8)
            entrada.grid(row=1, column=columna, sticky="ew", padx=10, pady=(0, 12))
            self.campos_manual[clave] = entrada
        self.boton_agregar_manual = ctk.CTkButton(formulario, text="Agregar proceso",
            fg_color=AZUL, hover_color=HOVER, command=self._agregarManual)
        self.boton_agregar_manual.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 12))
        self.boton_cancelar_edicion = ctk.CTkButton(formulario, text="Cancelar edición",
            fg_color=AZUL, hover_color=HOVER, state="disabled", command=self._cancelarEdicionManual)
        self.boton_cancelar_edicion.grid(row=2, column=2, columnspan=2, sticky="ew", padx=10, pady=(0, 12))
        self.mensaje_manual = self._etiqueta(ventana,
            "Agregue cada proceso a la lista antes de utilizarla. Seleccione una fila para editar o eliminar.",
            13, CELESTE, wraplength=700, anchor="w", justify="left")
        self.mensaje_manual.grid(row=2, column=0, sticky="ew", padx=24, pady=12)
        marco, self.tabla_manual = self._tabla(ventana, [
            ("id", "ID", 150), ("TA", "TA", 120), ("TI", "TI", 120), ("tamano", "Tamaño (KB)", 160)], 7)
        marco.grid(row=3, column=0, sticky="nsew", padx=24)
        self.tabla_manual.bind("<Double-1>", lambda evento: self._editarManual())
        acciones = ctk.CTkFrame(ventana, fg_color="transparent")
        acciones.grid(row=4, column=0, sticky="ew", padx=24, pady=12)
        for columna, (titulo, accion) in enumerate([
            ("Editar seleccionado", self._editarManual),
            ("Eliminar seleccionado", self._eliminarManual), ("Limpiar lista", self._limpiarManual)
        ]):
            acciones.grid_columnconfigure(columna, weight=1)
            ctk.CTkButton(acciones, text=titulo, fg_color=AZUL, hover_color=HOVER,
                          command=accion).grid(row=0, column=columna, sticky="ew", padx=4)
        pie = ctk.CTkFrame(ventana, fg_color="transparent")
        pie.grid(row=5, column=0, sticky="ew", padx=24, pady=(0, 20))
        pie.grid_columnconfigure(0, weight=1)
        self.contador_manual = self._etiqueta(pie, "", 15, CELESTE, True)
        self.contador_manual.grid(row=0, column=0, sticky="w")
        ctk.CTkButton(pie, text="Guardar como TXT", fg_color=AZUL, hover_color=HOVER,
                      command=self._guardarManual).grid(row=0, column=1, padx=6)
        ctk.CTkButton(pie, text="Usar estos procesos", fg_color=AZUL, hover_color=HOVER,
                      command=self._usarManual).grid(row=0, column=2, padx=(6, 0))
        self._actualizarListaManual()
        return True

    def _actualizarListaManual(self):
        filas = [(p["id"], p["TA"], p["TI"], p["tamano"]) for p in self.borrador_manual]
        self._actualizarTabla(self.tabla_manual, filas)
        self.contador_manual.configure(text=f"{len(filas)}/10 procesos")

    def _agregarManual(self):
        if self.indice_edicion is None and len(self.borrador_manual) >= 10:
            self.mensaje_manual.configure(text="Se alcanzó el máximo de diez procesos. Puede editar o eliminar una fila.")
            return False
        ids = {p["id"] for i, p in enumerate(self.borrador_manual) if i != self.indice_edicion}
        datos, motivos = motor.validarRegistro(
            [self.campos_manual[k].get() for k in ("id", "TA", "TI", "tamano")], ids)
        if motivos:
            self.mensaje_manual.configure(text="; ".join(m.rstrip(".") for m in motivos) + ".")
            return False
        if self.indice_edicion is None:
            self.borrador_manual.append(datos)
        else:
            self.borrador_manual[self.indice_edicion] = datos
        self._cancelarEdicionManual()
        self._actualizarListaManual()
        self.mensaje_manual.configure(text=f"Proceso {datos['id']} guardado en la lista.")
        return True

    def _seleccionManual(self):
        seleccion = self.tabla_manual.selection()
        if not seleccion:
            self.mensaje_manual.configure(text="Seleccione un proceso de la tabla.")
            return None
        return int(seleccion[0])

    def _editarManual(self):
        indice = self._seleccionManual()
        if indice is None:
            return False
        self.indice_edicion = indice
        for clave, entrada in self.campos_manual.items():
            entrada.delete(0, "end")
            entrada.insert(0, str(self.borrador_manual[indice][clave]))
        self.boton_agregar_manual.configure(text="Guardar cambios")
        self.boton_cancelar_edicion.configure(state="normal")
        self.mensaje_manual.configure(text="Edite los campos y guarde los cambios. Se conservará la posición de la fila.")
        return True

    def _cancelarEdicionManual(self):
        self.indice_edicion = None
        for entrada in self.campos_manual.values():
            entrada.delete(0, "end")
        self.boton_agregar_manual.configure(text="Agregar proceso")
        self.boton_cancelar_edicion.configure(state="disabled")
        self.mensaje_manual.configure(text="Ingrese los datos de un proceso para agregarlo a la lista.")

    def _eliminarManual(self):
        indice = self._seleccionManual()
        if indice is None:
            return False
        del self.borrador_manual[indice]
        self._cancelarEdicionManual()
        self._actualizarListaManual()
        self.mensaje_manual.configure(text="Proceso eliminado de la lista.")
        return True

    def _limpiarManual(self):
        if not self.borrador_manual:
            self.mensaje_manual.configure(text="La lista ya está vacía.")
            return False
        if not messagebox.askyesno("Limpiar lista", "¿Desea eliminar todos los procesos de la lista manual?",
                                   parent=self.ventana_manual):
            return False
        self.borrador_manual.clear()
        self._cancelarEdicionManual()
        self._actualizarListaManual()
        self.mensaje_manual.configure(text="Lista de procesos vacía.")
        return True

    def _usarManual(self):
        if self.estado_reproduccion == "Ejecutando":
            self.mensaje_manual.configure(text="Pause la simulación actual antes de utilizar otra lista de procesos.")
            return False
        if not self.borrador_manual:
            self.mensaje_manual.configure(text="Agregue al menos un proceso válido a la lista.")
            return False
        if self.indice_edicion is not None:
            self.mensaje_manual.configure(text="Guarde o cancele la edición antes de utilizar la lista.")
            return False
        self._cancelarTarea()
        self._cerrarInformeCarga()
        self.procesos_cargados = deepcopy(self.borrador_manual)
        self.ruta_archivo = None
        self.carga_manual = True
        self.colores = {p["id"]: COLORES_PROCESOS[i % len(COLORES_PROCESOS)]
                        for i, p in enumerate(self.procesos_cargados)}
        self._preparar()
        self.lineas_eventos.append(f"Carga manual: {len(self.procesos_cargados)} procesos preparados.")
        self._cerrarCargaManual()
        self.actualizar()
        return True

    def _guardarManual(self, ruta=None):
        if not self.borrador_manual:
            self.mensaje_manual.configure(text="Agregue al menos un proceso antes de guardar.")
            return False
        if self.indice_edicion is not None:
            self.mensaje_manual.configure(text="Guarde o cancele la edición antes de exportar la lista.")
            return False
        if any(c.isspace() or c == "," for p in self.borrador_manual for c in p["id"]):
            self.mensaje_manual.configure(text="Para guardar como TXT, los ID no pueden contener espacios ni comas. Edite esos ID; la lista puede utilizarse para simular.")
            return False
        texto = "".join(f"{p['id']} {p['TA']} {p['TI']} {p['tamano']}\n" for p in self.borrador_manual)
        try:
            contenido = texto.encode("utf-8")
        except UnicodeError:
            self.mensaje_manual.configure(text="Algún ID contiene caracteres que no pueden guardarse como texto UTF-8. Revise los identificadores.")
            return False
        if ruta is None:
            ruta = filedialog.asksaveasfilename(parent=self.ventana_manual, title="Guardar procesos",
                defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")], confirmoverwrite=False)
        if not ruta:
            return False
        try:
            try:
                archivo = open(ruta, "xb")
            except FileExistsError:
                if not messagebox.askyesno("Sobrescribir archivo", "El archivo ya existe. ¿Desea reemplazarlo?",
                                           parent=self.ventana_manual):
                    return False
                archivo = open(ruta, "wb")
            with archivo:
                archivo.write(contenido)
        except OSError:
            self.mensaje_manual.configure(text="No se pudo guardar el archivo. Compruebe la ubicación y los permisos.")
            return False
        self.mensaje_manual.configure(text=f"Procesos guardados en {Path(ruta).name}.")
        return True

    def _cerrarCargaManual(self):
        if self.ventana_manual is not None:
            self.ventana_manual.destroy()
            self.ventana_manual = None
            self.indice_edicion = None

    def _mostrarInformeCarga(self, carga):
        """Informe desplazable y no modal: permite usar los procesos aceptados."""
        self._cerrarInformeCarga()
        ventana = ctk.CTkToplevel(self)
        self.ventana_informe = ventana
        ventana.title("Informe de carga de procesos")
        ventana.geometry("780x540")
        ventana.minsize(560, 360)
        ventana.configure(fg_color=FONDO)
        ventana.transient(self)
        ventana.protocol("WM_DELETE_WINDOW", self._cerrarInformeCarga)
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(2, weight=1)
        self._etiqueta(ventana, "Revisión del archivo de procesos", 20, CELESTE, True).grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 8))
        resumen = carga["resumen"]
        self._etiqueta(ventana,
            f"Cargados: {resumen['aceptados']}   ·   Rechazados: {resumen['rechazados']}   ·   "
            f"Sin procesar por límite: {resumen['noProcesados']}",
            13, TEXTO, wraplength=700, anchor="w").grid(
                row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.texto_informe = ctk.CTkTextbox(ventana, fg_color=PANEL, text_color=TEXTO,
                                          font=("Segoe UI", 13), corner_radius=12, wrap="word")
        self.texto_informe.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self._escribir(self.texto_informe, carga["mensajes"])
        ctk.CTkButton(ventana, text="Cerrar informe", fg_color=AZUL, hover_color=HOVER,
                      corner_radius=10, command=self._cerrarInformeCarga).grid(
                          row=3, column=0, sticky="e", padx=24, pady=(0, 20))

    def _cerrarInformeCarga(self):
        if self.ventana_informe is not None:
            self.ventana_informe.destroy()
            self.ventana_informe = None
            self.texto_informe = None

    def _preparar(self):
        self._proximo_paso = None
        self.gantt.reiniciar()
        self.cpu_cambios.configure(text="")
        self._firmas_colas.clear()
        self.detalle_gantt.configure(text="Señalá un bloque para consultar proceso, inicio y fin. Historial completo con desplazamiento horizontal.")
        motor.iniciarSimulacion(self.procesos_cargados)
        self.estado_reproduccion = "Preparado"
        self.lineas_eventos.clear()

    def iniciar(self):
        if self.estado_reproduccion == "Preparado":
            self._reproducir()

    def continuar(self):
        if self.estado_reproduccion == "Pausado":
            self._reproducir()

    def _reproducir(self):
        if motor.obtenerEstado()["cantProcesos"] > 0:
            self.estado_reproduccion = "Ejecutando"
            self._proximo_paso = monotonic() + 1 / self.velocidad
            self.actualizar()
            self._programar()

    def pausar(self):
        if self.estado_reproduccion == "Ejecutando":
            self._cancelarTarea()
            self.estado_reproduccion = "Pausado"
            self.actualizar()

    def avanzar(self):
        if self.estado_reproduccion in ("Preparado", "Pausado"):
            self.estado_reproduccion = "Pausado"
            self._ejecutarPaso()

    def _ejecutarPaso(self):
        if motor.obtenerEstado()["cantProcesos"] <= 0:
            return
        inicio = motor.obtenerEstado()["tActual"]
        try:
            motor.ejecutarIteracion(mostrarConsola=False)
        except Exception:
            self._cancelarTarea()
            self.estado_reproduccion = "Error"
            self.actualizar()
            messagebox.showerror("Error de simulación",
                "No se pudo completar la iteración. Reinicie la simulación antes de volver a intentarlo.",
                parent=self)
            return
        eventos = motor.obtenerEventos()
        self.gantt.actualizar(eventos, inicio, motor.obtenerEstado()["tActual"])
        self.lineas_eventos.extend(self._describirEvento(e) for e in eventos)
        if motor.obtenerEstado()["cantProcesos"] == 0:
            self.estado_reproduccion = "Finalizado"
            self._cancelarTarea()
        self.actualizar()
        self._actualizarCambiosCPU(eventos)

    def _tick(self):
        self.tarea = None
        if self.estado_reproduccion == "Ejecutando":
            self._proximo_paso = monotonic() + 1 / self.velocidad
            self._ejecutarPaso()
            if self.estado_reproduccion == "Ejecutando":
                self._programar()

    def _programar(self):
        self._cancelarTarea()
        if self._proximo_paso is None:
            self._proximo_paso = monotonic() + 1 / self.velocidad
        demora = max(1, round((self._proximo_paso - monotonic()) * 1000))
        self.tarea = self.after(demora, self._tick)

    def _cancelarTarea(self):
        if self.tarea is not None:
            self.after_cancel(self.tarea)
            self.tarea = None

    def cambiarVelocidad(self, valor):
        self.velocidad = float(valor)
        self.slider.set(self.velocidad)
        self._proximo_paso = monotonic() + 1 / self.velocidad
        self.velocidad_label.configure(text=f"Reproducción · {self.velocidad:.2f}×")
        if self.estado_reproduccion == "Ejecutando":
            self._programar()

    def reiniciar(self):
        self._cerrarInformeCarga()
        self._cancelarTarea()
        self._proximo_paso = None
        motor.reiniciarSimulacion()
        self.lineas_eventos.clear()
        if self.procesos_cargados:
            self._preparar()
        else:
            self.estado_reproduccion = "Sin archivo"
        self.actualizar()

    def cerrar(self):
        self._cerrarCargaManual()
        self._cerrarInformeCarga()
        self._cancelarTarea()
        self.destroy()

    @staticmethod
    def _escribir(widget, texto):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)
        widget.configure(state="disabled")

    @staticmethod
    def _describirEvento(evento):
        tipo = evento["tipo"]
        p = evento.get("proceso", "")
        prefijo = f"#{evento['secuencia']:04d}  t={evento['tiempo']:<4}  "
        if tipo == "finalizacion":
            return prefijo + f"Finalizó {p} · TE {evento['TE']:g} · TR {evento['TR']:g}"
        detalle = {
            "arribo": f"Arribo de {p}",
            "admision": f"Admisión de {p}",
            "cambio_estado": f"{p}: {evento.get('estadoAnterior')} → {evento.get('estadoNuevo')}",
            "seleccion_cpu": f"CPU selecciona {p} · TI {evento.get('TI')}",
            "expropiacion_cpu": f"{p} expropiado por {evento.get('reemplazante')}",
            "asignacion_memoria": f"Best Fit asigna memoria a {p} · {evento.get('particion', {}).get('tamanio')} KB",
            "division_particion": f"División de partición para {p}",
            "liberacion_memoria": f"Memoria liberada por {p}",
            "fusion_particiones": "Fusión de particiones libres",
            "ejecucion_cpu": f"{p} ejecutó [{evento.get('inicio')}, {evento.get('fin')}) · TI restante {evento.get('TI')}",
        }.get(tipo, tipo)
        return prefijo + detalle

    def actualizar(self):
        self.estado = motor.obtenerEstado()
        estado = self.estado
        self.reloj.configure(text=f"t = {estado['tActual']}")
        self.estado_label.configure(text=self.estado_reproduccion)
        origen = (f"Carga manual · {len(self.procesos_cargados)} procesos" if self.carga_manual
                  else Path(self.ruta_archivo).name if self.ruta_archivo else "Ningún archivo seleccionado")
        self.archivo_label.configure(text=origen)
        self.resumen.configure(text=f"Pendientes  {estado['cantProcesos']}\nMultiprogramación  {estado['GM']} / 5")
        permisos = {
            "cargar": self.estado_reproduccion != "Ejecutando",
            "manual": self.estado_reproduccion != "Ejecutando",
            "iniciar": self.estado_reproduccion == "Preparado",
            "pausar": self.estado_reproduccion == "Ejecutando",
            "continuar": self.estado_reproduccion == "Pausado",
            "paso": self.estado_reproduccion in ("Preparado", "Pausado"),
            "reiniciar": bool(self.procesos_cargados),
        }
        for clave, boton in self.botones.items():
            boton.configure(state="normal" if permisos[clave] else "disabled")
        proceso = estado["ejecucion"]["procEjecutandose"]
        self.cpu_proceso.configure(text=proceso["id"] if proceso else "—", text_color=CELESTE)
        self.cpu_estado.configure(text=("● CPU ocupada" if self.estado_reproduccion == "Ejecutando"
                                       else "● Proceso seleccionado") if proceso else "○ CPU libre",
                                  text_color=CELESTE if proceso else SECUNDARIO)
        self.cpu_ti.configure(text=f"{proceso['TI'] if proceso else 0} unidades restantes")
        self.cpu_barra.set(proceso["TI"] / proceso["resguardoTI"]
                           if proceso and proceso["resguardoTI"] > 0 else 0)
        self.memoria_visual.sincronizar(estado["memoria"])
        self._actualizarColas(estado)
        texto_eventos = "\n".join(self.lineas_eventos) or "Cargá un archivo para comenzar."
        if texto_eventos != self._ultimo_texto_eventos:
            posicion, extremo = self.texto_eventos.yview()
            self._escribir(self.texto_eventos, texto_eventos)
            if extremo >= .98:
                self.texto_eventos.see("end")
            else:
                self.texto_eventos.yview_moveto(posicion)
            self._ultimo_texto_eventos = texto_eventos
        self._actualizarEstadisticas(estado)

    def _actualizarColas(self, estado):
        for clave, panel in self.paneles_colas.items():
            procesos = estado["colas"][clave]
            firma = tuple((p["id"], p["TA"], p["TI"], p["tamano"], p["TE"], p["TR"])
                          if clave == "terminados" else (p["id"], p["TA"], p["TI"], p["tamano"])
                          for p in procesos)
            if self._firmas_colas.get(clave) == firma:
                continue
            self._firmas_colas[clave] = firma
            titulo = {"nuevos": "Nuevos", "listos": "Listos", "listosSuspendidos": "Suspendidos",
                      "terminados": "Terminados"}[clave]
            self.titulos_colas[clave].configure(text=f"{titulo} · {len(procesos)}")
            if clave not in self._widgets_colas:
                vacio = self._etiqueta(panel, "Sin procesos", 12, SECUNDARIO)
                self._widgets_colas[clave] = {"vacio": vacio, "tarjetas": []}
            widgets = self._widgets_colas[clave]
            if procesos:
                widgets["vacio"].grid_remove()
            else:
                widgets["vacio"].grid(row=0, column=0, pady=16)
            while len(widgets["tarjetas"]) > len(procesos):
                tarjeta, _, _ = widgets["tarjetas"].pop()
                tarjeta.destroy()
            for i, p in enumerate(procesos):
                if i == len(widgets["tarjetas"]):
                    tarjeta = ctk.CTkFrame(panel, fg_color=FONDO, corner_radius=9, border_width=1)
                    tarjeta.grid(row=i, column=0, sticky="ew", padx=2, pady=4)
                    nombre = self._etiqueta(tarjeta, "", 15, CELESTE, True)
                    nombre.pack(anchor="w", padx=10, pady=(7, 0))
                    detalle = self._etiqueta(tarjeta, "", 12, SECUNDARIO, justify="left")
                    detalle.pack(anchor="w", padx=10, pady=(0, 7))
                    widgets["tarjetas"].append((tarjeta, nombre, detalle))
                tarjeta, nombre, detalle = widgets["tarjetas"][i]
                tarjeta.configure(border_color=self.colores.get(p["id"], AZUL))
                nombre.configure(text=p["id"])
                ti = p["resguardoTI"] if clave == "terminados" else p["TI"]
                segunda = f"TE {p['TE']:g} · TR {p['TR']:g}" if clave == "terminados" else f"TA {p['TA']}"
                detalle.configure(text=f"TI {ti} · {p['tamano']} KB\n{segunda}")

    def _actualizarEstadisticas(self, estado):
        terminados = estado["colas"]["terminados"]
        if terminados:
            te, tr = motor.CalcularPromediosTEyTR()
            rendimiento = motor.CalcularRendimientoSistema(motor.terminados, estado["tActual"])
            alcance = "Resultados finales" if estado["cantProcesos"] == 0 else "Resultados parciales"
            resumen = f"{alcance} · {len(terminados)} procesos terminados"
            for clave, valor in (("TE", te), ("TR", tr), ("rendimiento", rendimiento)):
                self.metricas[clave].configure(text=f"{valor:.6f}" if clave == "rendimiento" else f"{valor:.3f}")
        else:
            resumen = "Sin procesos terminados · las métricas aparecerán durante la simulación."
            for widget in self.metricas.values():
                widget.configure(text="—")
        self.metricas_label.configure(text=resumen, wraplength=650)
        filas = [(p["id"], p["TA"], p["resguardoTI"], f"{p['TE']:g}", f"{p['TR']:g}", p["TA"] + p["TR"])
                 for p in sorted(terminados, key=lambda p: p["TA"])]
        self._actualizarTabla(self.tabla_estadisticas, filas)

    def dibujarMemoria(self):
        self.memoria_visual.dibujar()

    def _actualizarCambiosCPU(self, eventos):
        """Informa selecciones y expropiaciones sin efectos temporales."""
        selecciones = [e["proceso"] for e in eventos if e["tipo"] == "seleccion_cpu"]
        expropiaciones = [f"{e['proceso']} → {e['reemplazante']}" for e in eventos
                          if e["tipo"] == "expropiacion_cpu"]
        mensajes = []
        if selecciones:
            mensajes.append("Selección: " + " → ".join(selecciones))
        if expropiaciones:
            mensajes.append("Expropiación SRTF: " + "; ".join(expropiaciones))
        if eventos:
            self.cpu_cambios.configure(text="\n".join(mensajes))

    def _actualizarDetalleMemoria(self, particiones):
        disponible = sum(p["tamanio"] for p in particiones if p["procesoAsignado"] is None)
        self.memoria_label.configure(text=f"Usuario: {450 - disponible} / 450 KB ocupados · Libre: {disponible} KB")
        firma = tuple(tuple(p.items()) for p in particiones)
        if firma == self._firma_memoria:
            return
        self._firma_memoria = firma
        filas = [(p["id"], p["comienzo"], p["tamanio"],
                  p["procesoAsignado"] if p["procesoAsignado"] is not None else "Libre") for p in particiones]
        filas.append(("SO", 450, 100, "Sistema operativo"))
        self._actualizarTabla(self.tabla_memoria, filas)
