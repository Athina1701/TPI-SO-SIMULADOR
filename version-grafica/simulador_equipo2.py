# Simulador de Sistemas Operativos: motor y presentación por consola.
from operator import attrgetter, itemgetter
from copy import deepcopy 
from contextlib import redirect_stdout
from io import StringIO

class Proceso:
  def __init__(self, id, TA, TI, tamano, estado):
    self.id = id
    self.TA = TA
    self.TI = TI  #Representa una ráfaga: TI disminuye y resguardoTI conserva su valor original.
    self.resguardoTI = TI  
    self.tamano = tamano
    self.estado = estado
    self.TR = 0.
    self.TE = 0.
    """ NOTA: El TR se calcula restando el tiempo de arribo original del proceso y exactamente el tiempo en que termina; 
  Es decir, que tambien incluye el tiempo que pasa esperando ANTES de ingresar a LISTOS (o listos y suspendidos) por el limite impuesto del GM = 5, el cual no deja que ingrese un proceso por mas que ya haya arribado. 
  En cambio, el TE, se calcula tomando en cuenta solo el tiempo que pasa esperando en la cola listos y la de suspendidos. Tal como dice en la teoria de la catedra."""

# Colas y CPU compartidas por las funciones del simulador.
nuevos = []
listos = []
listosSuspendidos = []
terminados = []

ejecucion = { "enUso": False, "procEjecutandose": None }


def _leerTextoProcesos(nombreArchivo):
  # Lee UTF-8 con BOM opcional; admite Windows-1252 para archivos anteriores.
  try:
    with open(nombreArchivo, "r", encoding="utf-8-sig") as archivo:
      return archivo.read()
  except UnicodeDecodeError:
    with open(nombreArchivo, "r", encoding="cp1252") as archivo:
      return archivo.read()


def existeArchivo(nombreArchivo):
  # Comprueba la existencia del archivo .txt que contiene los procesos.
  try:
    if not _leerTextoProcesos(nombreArchivo):
      print("\nEl archivo está vacío. Ingrese otra ruta:")
      return False
    return True
  except FileNotFoundError:
    print("\nNo se encontró el archivo. Ingrese otra ruta:")
    return False
  except (OSError, UnicodeError):
    print("\nNo se pudo leer el archivo. Compruebe la ruta, los permisos y la codificación.")
    return False


def crearArchivoProcesos():
  #Funcion para ingresar por teclado los procesos.
  print("\nIngreso de procesos por teclado\nIngrese ID, TA, TI y tamaño, separados por espacios.")
  print("(Puede copiar varios procesos y pegar)\nPresione Enter en una línea vacía para terminar.")
  while True:
    nombreArchivo = input("Nombre del archivo nuevo [procesosIngresados.txt]: ").strip()
    if not nombreArchivo:
      nombreArchivo = "procesosIngresados.txt"
    if not nombreArchivo.lower().endswith(".txt"):
      nombreArchivo += ".txt"
    try:
      archi = open(nombreArchivo, "x", encoding="utf-8")
      break
    except FileExistsError:
      print(">> Ese archivo ya existe. Elija otro nombre para no sobrescribirlo.")
    except OSError:
      print(">> No se pudo crear el archivo. Compruebe la ubicación y los permisos.")
      return None

  try:
    with archi:
      while True:
        linea = input("Proceso (Enter para terminar): ").strip()
        if not linea:
          break
        archi.write(linea + "\n")
  except (OSError, UnicodeError):
    print(">> No se pudo completar el guardado. El archivo puede haber quedado incompleto. Revise la ubicación, el espacio disponible y los datos.")
    return None

  print(f"Procesos guardados en: {nombreArchivo} \n")
  return nombreArchivo

def validarRegistro(campos, identificadores=()):
  #Valida los campos de cada proceso: ID, TA, TI y tamaño; devuelve datos normalizados y todos los motivos.
  if len(campos) != 4:
    return None, ["se requieren exactamente cuatro campos: ID TA TI tamaño."]
  identificador = campos[0].strip() if isinstance(campos[0], str) else ""
  motivos = []
  if not isinstance(campos[0], str):
    motivos.append("el identificador del proceso debe ser un texto.")
  elif not identificador:
    motivos.append("el identificador del proceso no puede estar vacío.")
  elif identificador in identificadores:
    motivos.append("el identificador del proceso ya existe entre los procesos aceptados.")
  valores = {}
  for clave, nombre, valor in (("TA", "tiempo de arribo", campos[1]),
                               ("TI", "tiempo de irrupción", campos[2]),
                               ("tamano", "tamaño", campos[3])):
    try:
      if isinstance(valor, bool) or not isinstance(valor, (str, int)):
        raise ValueError
      valores[clave] = int(valor)
    except ValueError:
      motivos.append(f"el {nombre} debe ser un número entero.")
  if "TA" in valores and valores["TA"] < 0:
    motivos.append("el tiempo de arribo debe ser mayor o igual que cero.")
  if "TI" in valores and valores["TI"] <= 0:
    motivos.append("el tiempo de irrupción debe ser mayor que cero.")
  if "tamano" in valores:
    if valores["tamano"] <= 0:
      motivos.append("el tamaño del proceso debe ser mayor que cero.")
    elif valores["tamano"] > 450:
      motivos.append("el tamaño del proceso no puede superar los 450 KB.")
  if motivos:
    return None, motivos
  return {"id": identificador, **valores}, []


def formatearInformeCarga(carga):
  #Presentación de diagnósticos: procesos aceptados, rechazados; cada línea cuenta como un registro, aunque tenga varios errores. 
  resumen = carga["resumen"]
  lineas = ["Formato: ID TA TI tamaño (KB).",
            f"Procesos cargados: {resumen['aceptados']}. Registros rechazados: {resumen['rechazados']}. "
            f"No procesados por límite: {resumen['noProcesados']}."]
  if carga["procesos"]:
    lineas.append("Aceptados: " + ", ".join(p["id"] for p in carga["procesos"]) + ".")
  else:
    lineas.append("No hay procesos válidos para iniciar la simulación.")
  for error in carga["errores"]:
    ident = f" (ID: {error['id']})" if error["id"] else ""
    lineas.append(f"Línea {error['linea']}{ident}: " +
                  "; ".join(motivo.rstrip(".") for motivo in error["motivos"]) + ".")
  for omitido in carga["noProcesados"]:
    ident = f" (ID: {omitido['id']})" if omitido["id"] else ""
    lineas.append(f"Línea {omitido['linea']}{ident}: no se procesó porque ya se alcanzó "
                  "el máximo de procesos válidos; no se validó este registro.")
  return "\n".join(lineas)


def cargarNuevos(nombreArchivo, colaNuevos):
  # Una vez procesado el archivo, carga los procesos a la cola de nuevos.
  # Carga por consola con la misma validación utilizada por la interfaz gráfica.
  global cantProcesos
  try:
    carga = cargarProcesosArchivo(nombreArchivo, limite=max(0, 10 - cantProcesos),
                                 identificadores={p.id for p in colaNuevos})
  except (OSError, UnicodeError):
    print("No se pudo leer el archivo. Compruebe la ruta, los permisos y la codificación.")
    return
  print(carga["mensajes"])
  for datos in carga["procesos"]:
    colaNuevos.append(Proceso(datos["id"], datos["TA"], datos["TI"], datos["tamano"], "nuevo"))
    cantProcesos += 1
  colaNuevos.sort(key=attrgetter("TA", "TI"))


def EliminarDeCola(cola, proceso):
  seEncontroProc = False
  indice = 0
  while indice < len(cola):
    proc = cola[indice]
    if proc.id == proceso.id:
      resguardoIndice = indice
      seEncontroProc = True
      break
    indice += 1
  if seEncontroProc:
    del cola[resguardoIndice]

def MostrarCola(cola, texto):
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 49)
    for p in cola:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")


def MostrarMemoria(fMemoria, fragmentacion):
  """Muestra y ordena la memoria original por dirección. Este efecto puede influir en empates de Best Fit y se conserva también en modo silencioso."""
  print(f"| {'ID_Particion':<12} | {'Comienzo':^4} | {'Tamaño KB':^8} | {'Proceso Asignado':^16} |")
  print("-" * 60)
  print(f"| {'Par_0':<12} | {'450':^8} | {'100':^9} | {' SIST. OPERATIVO':^16} |")
  fMemoria.sort(key=itemgetter("comienzo"))
  for part in fMemoria:
    pAsignado = part["procesoAsignado"]
    if pAsignado is None:
      pAsignado = "Libre"
    print(f"| Par_{part["id"]:<8} | {part["comienzo"]:^8} | {part["tamanio"]:^9} | {pAsignado:^16} |")
  if fragmentacion:
    MostrarFragmentacion(fragmentacion)
  else:
    print(">Memoria de usuario disponible (KB): ", disponibleEnMemoria, "\n")


def PresentacionDeSalida():
  print("\n\n             -------- TIEMPO ACTUAL: ", tActual, " ---------\n")
  print(" >Cantidad de Procesos Faltantes a terminar: ", cantProcesos)
  print(" >Grado De Multiprogramación: ", GM, "\n")


  print("\n-----Tabla de PARTICIONES de MEMORIA-----")
  MostrarMemoria(memoria, fragmentacion)


  print("\n-----Cola de Procesos NUEVOS-----")
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 49)
  for p in nuevos:

    print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")

  texto = "\n-----Cola de Procesos LISTOS-----"
  MostrarCola(listos, texto)
  texto = "\n-----Cola de Procesos LISTOS y SUSPENDIDOS-----"
  MostrarCola(listosSuspendidos, texto)

  if terminados:
    texto = "\n-----Cola de Procesos TERMINADOS-----"
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 49)
    for p in terminados:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.resguardoTI:>4} | {p.tamano:>10} | {p.estado:<10} |")


  print("\n-----Estado de la CPU Actualmente-----\n")
  print(f"| {'Proceso en ejecución':^20} | {'Tiempo de Irrupción':^19} | ")
  print("-" * 46)
  if ejecucion["enUso"] == True:
    pEjecutandose = ejecucion["procEjecutandose"]
    print(f"| {pEjecutandose.id :^20} | {pEjecutandose.TI :^19} |\n")
  else:
    print(f"| {'Ninguno':^20} | {'0':^19} |\n")
    print(">(Actualmente no hay procesos ejecutándose)\n")
  print("-" * 100 , "\n")


memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]

contadorIDparticion = 2
disponibleEnMemoria = 450

def CargarEnMemoria(fproceso):
  """Aplica Best Fit con orden estable por tamaño y divide el espacio sobrante en un hueco libre."""
  global disponibleEnMemoria, contadorIDparticion
  fFragmentacion= []
  longitudMemoria = len(memoria)
  if longitudMemoria > 0:
    memoria.sort(key=itemgetter("tamanio"))

    for i in range(longitudMemoria):
      if memoria[i].get("procesoAsignado") is None:
        if fproceso.tamano <= memoria[i].get("tamanio"):
            particionOriginal = memoria[i].copy()
            sobraEspacio = memoria[i].get("tamanio") - fproceso.tamano
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano
            if sobraEspacio > 0:
              particionNueva = { "id": (contadorIDparticion), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": sobraEspacio , "procesoAsignado": None }
              memoria.append(particionNueva)
              _registrarEvento("division_particion", proceso=fproceso.id,
                               particionOriginal=particionOriginal,
                               particionLibre=particionNueva, tamanoAsignado=fproceso.tamano)
              contadorIDparticion += 1

            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id
            _registrarEvento("asignacion_memoria", proceso=fproceso.id,
                             estrategia="Best Fit", particion=memoria[i],
                             disponibleEnMemoria=disponibleEnMemoria)
            return True, fFragmentacion
        else:
          fFragmentacion.append(memoria[i])

    return False, fFragmentacion

def MostrarFragmentacion(fFragmentacion):
  fragTotal = 0
  print("> ¡Fragmentacion!: Huecos libres insuficientes en el intento de asignación: ")
  for part in fFragmentacion:
    print(f"   -Particion: {part["id"]} ; Tamaño: {part["tamanio"]}")
    fragTotal += part["tamanio"]
  print("-Fragmentación Externa Total (KB): ", fragTotal, "\n")

def JuntarParticiones(fmemoria):
  """Fusiona entradas libres consecutivas de la memoria ordenada; no desplaza procesos."""


  memoriaCopy = []
  longitudMemoria = len(fmemoria)
  if longitudMemoria > 1:
    fmemoria.sort(key=itemgetter("comienzo"))
    i = 0
    while i < longitudMemoria:
      particionNueva = fmemoria[i].copy()
      if fmemoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)):
        while ( i+1 < longitudMemoria) and (fmemoria[i+1].get("procesoAsignado") is None):
          particionAnterior = particionNueva.copy()
          particionNueva["tamanio"] += fmemoria[i +1].get("tamanio")
          _registrarEvento("fusion_particiones",
                           particiones=[particionAnterior, fmemoria[i +1]],
                           resultado=particionNueva)
          i += 1
      memoriaCopy.append(particionNueva)
      i += 1
  else:
    memoriaCopy= fmemoria
  return memoriaCopy

def LiberarMemoria(fproceso, memoria):
  global disponibleEnMemoria, fragmentacion
  fragmentacion = []

  for particion in memoria:
    if particion.get("procesoAsignado") is not None and particion["procesoAsignado"] == fproceso.id:
      particionAnterior = particion.copy()
      particion["procesoAsignado"] = None
      disponibleEnMemoria += fproceso.tamano
      _registrarEvento("liberacion_memoria", proceso=fproceso.id,
                       particionAnterior=particionAnterior, particion=particion,
                       disponibleEnMemoria=disponibleEnMemoria)
      memoria = JuntarParticiones(memoria)
      return True, memoria
  return False, memoria


def CargarListosYSuspendidos(fProceso, colaActual):
  estadoAnterior = fProceso.estado
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso)
  listosSuspendidos.sort(key= attrgetter("TI"))
  EliminarDeCola(colaActual, fProceso)
  _registrarCambioEstado(fProceso, estadoAnterior)

def AgregarAListos(fProceso, colaListos):
  #Inserta el proceso a cargar por TI creciente y conserva el orden en caso de empate.
  estadoAnterior = fProceso.estado
  fProceso.estado = "listo"
  mayorTI = True

  listosCopy = list(colaListos)
  for proc in listosCopy:
    if (fProceso.TI < proc.TI):
        indice = colaListos.index(proc)
        colaListos.insert(indice, fProceso)
        mayorTI = False
        break
  if mayorTI:
    colaListos.append(fProceso)
  _registrarCambioEstado(fProceso, estadoAnterior)

def CargarListos(fProceso, colaListos, colaActual):
  hayEspacio, fFragmentacion = CargarEnMemoria(fProceso)
  if hayEspacio:
    AgregarAListos(fProceso, colaListos)
    EliminarDeCola(colaActual, fProceso)

  elif (fProceso.estado != "suspendido"):
    CargarListosYSuspendidos(fProceso, colaActual)
  return fFragmentacion

def EjecutarProceso(procActual, colaEjecucion, colaListos):
  #Asigna un proceso a la CPU o expropia ante un TI estrictamente menor; conserva la memoria asignada.
  if colaEjecucion["enUso"] == True:
    procesoEjecutandose = colaEjecucion["procEjecutandose"]

    if procActual.TI < procesoEjecutandose.TI:
      _registrarEvento("expropiacion_cpu", proceso=procesoEjecutandose.id,
                       reemplazante=procActual.id,
                       TI=procesoEjecutandose.TI, TIReemplazante=procActual.TI)
      AgregarAListos(procesoEjecutandose, colaListos)

    else:
      return
  else:
    colaEjecucion["enUso"] = True
  EliminarDeCola(colaListos, procActual)
  estadoAnterior = procActual.estado
  procActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procActual
  _registrarCambioEstado(procActual, estadoAnterior)
  _registrarEvento("seleccion_cpu", proceso=procActual.id, TI=procActual.TI)

def TerminarProceso(proceso, fMemoria):
  #Al finalizar de ejecutarse (TI = 0), se cambia el estado del proceso a terminado, se lo agrega a la lista de terminados, se libera el espacio de memoria que utiliza y se calcual su TR.
  global cantProcesos, GM
  liberadoCorrectamente, fMemoria = LiberarMemoria(proceso, fMemoria)
  if liberadoCorrectamente:
    cantProcesos -=1
    GM -= 1
    estadoAnterior = proceso.estado
    proceso.estado = "terminado"
    proceso.TR = tActual - proceso.TA 
    terminados.append(proceso)
    ejecucion["enUso"] = False
    ejecucion["procEjecutandose"] = None
    _registrarCambioEstado(proceso, estadoAnterior)
    _registrarEvento("finalizacion", proceso=proceso.id, TE=proceso.TE, TR=proceso.TR)
  else:
      print("> Hubo un error al finalizar el proceso.")
  return fMemoria, disponibleEnMemoria

def DisminuirTI(colaEjecucion, fMemoria, disponibleEnMemoria ):
  #Luego de haber incrementado el tiempo actual, disminuyo el TI del proceso ejecutandose
  fProceso  = colaEjecucion["procEjecutandose"]
  fProceso.TI -=1
  _registrarEvento("ejecucion_cpu", proceso=fProceso.id, inicio=tActual - 1,
                   fin=tActual, TIAnterior=fProceso.TI + 1, TI=fProceso.TI)
  if fProceso.TI == 0:
    print(f"\n>Terminó el proceso: {fProceso.id} (Tiempo = {tActual}) ")
    fMemoria, disponibleEnMemoria = TerminarProceso( fProceso, fMemoria )
    return True, fMemoria, disponibleEnMemoria
  return False, fMemoria, disponibleEnMemoria


def CalcularPromediosTEyTR():
  #Promedia los tiempos TE y TR de los procesos terminados; requiere al menos uno.
  totalProcesos = len(terminados)
  TEpromedio = 0
  TRpromedio = 0
  for p in terminados:
    TEpromedio += p.TE
    TRpromedio += p.TR

  TEpromedio = TEpromedio / totalProcesos
  TRpromedio = TRpromedio / totalProcesos
  return TEpromedio, TRpromedio

def CalcularRendimientoSistema (colaTerminados, tActual):
  #Divide la cantidad de procesos terminados por tiempo total, incluida la inactividad.
  totalProcTerm= len(colaTerminados)
  rendimiento = totalProcTerm / (tActual)
  return rendimiento


def AumentarTiempo(colaListos, colaSuspendidos):
  #Avanza el reloj y acumula TE solo para listos y suspendidos, sin incluir nuevos.
  global tActual
  tActual +=1

  for proc in colaListos:
    proc.TE += 1
  for proc in colaSuspendidos:
    proc.TE += 1

def informacion():
  print("""   ---Información del simulador de Sistemas Operativos---

Memoria: 100 KB reservados al sistema operativo y 450 KB para procesos.
Se utilizan particiones variables con asignación Best Fit y fusión de entradas
libres consecutivas, sin compactación ni desplazamiento de procesos.
SRTF expropia únicamente si un listo tiene menor TI restante que la CPU.

Carga: hasta 10 procesos válidos desde un archivo o mediante ingreso manual.
Formato: ID TA TI tamaño, separado por espacios o comas. Ejemplo: P1 0 20 180.
Las rutas pueden ser absolutas o relativas a la carpeta de ejecución.
Archivo de ejemplo: procesos.txt.

Estados: nuevo, listo, suspendido, en ejecución y terminado.
TA: tiempo de arribo. 
TI: tiempo de CPU original o restante según la vista.
TR: tiempo de finalización - TA.
TE: espera acumulada en listos y suspendidos; no incluye permanencia en nuevos.
GM: grado de multiprogramación; procesos en listos, suspendidos y ejecución; máximo de 5.

Al finalizar se informan TE, TR y rendimiento por unidad de tiempo simulado.
Para ejecutar por: 
  Consola: python simulador_equipo2.py. 
  Interfaz gráfica: python main_gui.py.
""")
  salir = input("Presione Enter para volver al menú: ")
  if salir == "":
    return True
  return False


# Estado inicial; reiniciarSimulacion() restablece estos valores.
cantProcesos = 0
tActual = 0
GM = 0
fragmentacion = []
procesoActual = None
procFinalizado = False


_eventosIteracion = []
_secuenciaEvento = 0
_registrandoEventos = False
_procesosArribados = set()


def _registrarEvento(tipo, **datos):
  global _secuenciaEvento
  if not _registrandoEventos:
    return
  _secuenciaEvento += 1
  _eventosIteracion.append({
    "tipo": tipo,
    "tiempo": tActual,
    "secuencia": _secuenciaEvento,
    **deepcopy(datos),
  })


def _registrarCambioEstado(proceso, estadoAnterior):
  colas = {
    "nuevo": "nuevos",
    "listo": "listos",
    "suspendido": "listosSuspendidos",
    "ejecutandose": "ejecucion",
    "terminado": "terminados",
  }
  _registrarEvento("cambio_estado", proceso=proceso.id,
                   estadoAnterior=estadoAnterior, estadoNuevo=proceso.estado,
                   colaOrigen=colas.get(estadoAnterior),
                   colaDestino=colas.get(proceso.estado))


def obtenerEventos():
  #Devuelve copias de los eventos de la última iteración, sin consumirlos.
  return deepcopy(_eventosIteracion)


def reiniciarSimulacion():
  #Restablece reloj, CPU, colas, memoria, contadores y eventos.
  global cantProcesos, tActual, GM, contadorIDparticion, disponibleEnMemoria
  global procesoActual, procFinalizado, _secuenciaEvento, _registrandoEventos
  nuevos.clear()
  listos.clear()
  listosSuspendidos.clear()
  terminados.clear()
  ejecucion.clear()
  ejecucion.update({"enUso": False, "procEjecutandose": None})
  memoria[:] = [{"id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None}]
  fragmentacion.clear()
  cantProcesos = 0
  tActual = 0
  GM = 0
  contadorIDparticion = 2
  disponibleEnMemoria = 450
  procesoActual = None
  procFinalizado = False
  _eventosIteracion.clear()
  _procesosArribados.clear()
  _secuenciaEvento = 0
  _registrandoEventos = False


def cargarProcesosArchivo(nombreArchivo, limite=10, identificadores=()):
  # Valida los procesos del archivo .txt. Pasado el límite, las lineas restantes se anotan como "no procesadas".
  limite = max(0, min(10, limite))
  aceptados = []
  errores = []
  noProcesados = []
  ids = set(identificadores) # Guarda los IDs existentes y los aceptados para detectar duplicados.
  with StringIO(_leerTextoProcesos(nombreArchivo)) as archivo:
    for numero, linea in enumerate(archivo, 1):
      linea = linea.strip()
      if not linea:
        continue
      campos = linea.split(",") if "," in linea else linea.split()
      identificador = campos[0].strip() or None
      if len(aceptados) >= limite:
        noProcesados.append({"linea": numero, "id": identificador})
        continue
      datos, motivos = validarRegistro(campos, ids)
      if motivos:
        errores.append({"linea": numero, "id": identificador, "motivos": motivos})
        continue
      ids.add(datos["id"])
      aceptados.append(vars(Proceso(datos["id"], datos["TA"], datos["TI"], datos["tamano"], "nuevo")).copy())
  aceptados.sort(key=lambda p: (p["TA"], p["TI"]))
  carga = {
    "procesos": aceptados,
    "errores": errores,
    "noProcesados": noProcesados,
    "resumen": {"aceptados": len(aceptados), "rechazados": len(errores),
                "noProcesados": len(noProcesados)},
  }
  carga["mensajes"] = formatearInformeCarga(carga)
  return carga


def iniciarSimulacion(procesos):
  # Valida la lista de procesos y ordena hasta diez procesos, inicia la simulación y devuelve su estado inicial.
  global cantProcesos
  if len(procesos) > 10:
    raise ValueError("Solo se pueden iniciar hasta diez procesos válidos.")
  procesosNuevos = []
  ids = set() # para llevar registro de los identificadores aceptados.
  for indice, proceso in enumerate(procesos, 1):
    if not isinstance(proceso, dict):
      raise ValueError(f"Proceso {indice}: se requieren ID, TA, TI y tamaño.")
    datos, motivos = validarRegistro([proceso.get("id"), proceso.get("TA"),
                                      proceso.get("TI"), proceso.get("tamano")], ids)
    if motivos:
      raise ValueError(f"Proceso {indice}: " + " ".join(motivos))
    ids.add(datos["id"])
    procesosNuevos.append(Proceso(datos["id"], datos["TA"], datos["TI"], datos["tamano"], "nuevo"))
  procesosNuevos.sort(key=attrgetter("TA", "TI"))
  reiniciarSimulacion()
  nuevos.extend(procesosNuevos)
  cantProcesos = len(nuevos)
  return obtenerEstado()


def obtenerEstado():
  #Devuelve una instantánea independiente del estado y del orden de las colas.
  def copiarProceso(proceso):
    if proceso is None:
      return None
    return {
      "id": proceso.id,
      "TA": proceso.TA,
      "TI": proceso.TI,
      "resguardoTI": proceso.resguardoTI,
      "tamano": proceso.tamano,
      "estado": proceso.estado,
      "TR": proceso.TR,
      "TE": proceso.TE,
    }

  return {
    "tActual": tActual,
    "cantProcesos": cantProcesos,
    "GM": GM,
    "disponibleEnMemoria": disponibleEnMemoria,
    "ejecucion": {
      "enUso": ejecucion["enUso"],
      "procEjecutandose": copiarProceso(ejecucion["procEjecutandose"]),
    },
    "colas": {
      "nuevos": [copiarProceso(p) for p in nuevos],
      "listos": [copiarProceso(p) for p in listos],
      "listosSuspendidos": [copiarProceso(p) for p in listosSuspendidos],
      "terminados": [copiarProceso(p) for p in terminados],
    },
    "memoria": [particion.copy() for particion in memoria],
    "fragmentacion": [particion.copy() for particion in fragmentacion],
  }


def ejecutarIteracion(mostrarConsola=True):
  # Bucle Principal: Una vez cargado en nuevos, carga en Listos los procesos correspondientes, toma el primer proceso en listos y ejecuta, segun corresponda.
  # Avanza una unidad de tiempo; conserva el orden de operaciones y el cálculo actual de TE.
  global GM, fragmentacion, procesoActual, procFinalizado, memoria, disponibleEnMemoria
  global _registrandoEventos
  if not mostrarConsola:
    with redirect_stdout(StringIO()):
      return ejecutarIteracion()
  _eventosIteracion.clear()
  _registrandoEventos = True
  try:
    for procesoArribado in nuevos:
      if procesoArribado.TA <= tActual and procesoArribado not in _procesosArribados:
        _procesosArribados.add(procesoArribado)
        _registrarEvento("arribo", proceso=procesoArribado.id, TA=procesoArribado.TA,
                         estadoNuevo=procesoArribado.estado)
    llegoProcNuevo = False
    if GM < 5:
      if nuevos:
        for proceso in list(nuevos):
          if proceso.TA <= tActual:
            fragmentacion = CargarListos(proceso, listos, nuevos)
            GM += 1
            _registrarEvento("admision", proceso=proceso.id, TA=proceso.TA,
                             estadoNuevo=proceso.estado, GM=GM)
            llegoProcNuevo = True
            if proceso.TA == tActual:
              print(f"\n > Llegó un NUEVO proceso: {proceso.id} (Tiempo Actual = {tActual})")
            else:
              print(f"\n > Se admitió un proceso de Cola de Nuevos: {proceso.id}. (Tiempo Actual = {tActual})")
            if GM >= 5:
              break

    if listos:
      procesoActual = listos[0]
      if procesoActual.TA <= tActual:
        EjecutarProceso(procesoActual, ejecucion, listos)

    if llegoProcNuevo:
      PresentacionDeSalida()

    AumentarTiempo(listos, listosSuspendidos)


    if ejecucion["enUso"] == True:
      procFinalizado, memoria, disponibleEnMemoria = DisminuirTI(ejecucion, memoria, disponibleEnMemoria)
      if procFinalizado:
        if listos:
          procesoActual= listos[0]
          if procesoActual.TA <= tActual:
            EjecutarProceso(procesoActual, ejecucion, listos)


        for p in list(listosSuspendidos):
          fragmentacion = CargarListos(p, listos, listosSuspendidos)

        if cantProcesos == 0:
          print("\n\n               >>> Estado Final del Simulador <<<")

        PresentacionDeSalida()
  finally:
    _registrandoEventos = False


def ejecutarConsola():
  # Ejecuta el FLUJO PRINCIPAL por CONSOLA: el menú tradicional, carga de procesos, simulacion y los informes. 
  print("Bienvenido al simulador de Sistemas Operativos.")
  print("""Este programa simula la gestion de asignacion de memoria (de particiones variables) y planificacion de procesos con el algoritmo SRTF.

> Grupo Nro 2 - Comisión: K2.1 - Integrantes:
  > Alvarez Brivet, Camila
  > Arias, Alejandro Nicolas
  > Aristegui Gassmann, Valentina
  > Gutierrez Kolarik, Lucía Maylén
  > Maldonado Karlen, Alan
  > Ruiz Diaz, Mateo
  > Zaracho Simonetto, Athina """)

  while True:
    print("""\n------------------------------------------------------------------------
  Opciones Disponibles:
    0. Salir: Ingrese '0' para salir
    1. Informacion
    2. Comenzar Simulador
----------------------------------------------------------------------------------""")

    try:
      opcion = int(input("Seleccione una opción: "))
    except ValueError:
      print("\n>> La opción no es válida. Seleccione 0, 1 o 2. \n")
      continue
    if opcion != 1 and opcion != 2 and opcion != 0:
      print("\n>> La opción no es válida. Seleccione 0, 1 o 2. \n")

    if opcion == 0:
      break
    elif opcion == 1:
      volverAMenu = informacion()
      if volverAMenu:
        continue


    elif opcion == 2:
      print("""\n           > COMENZANDO EL SIMULADOR...
-Elija un formato de carga de los procesos:
  1. Cargar un archivo existente
  2. Ingresar procesos y guardarlos en un archivo nuevo
> Nota: Se cargan como máximo 10 procesos válidos.""")
      modoCarga = input("Seleccione una opción: ").strip()
      existe = False
      if modoCarga == "1":
        while not existe:
          print("-Cargue la ruta (o ingrese '0' para volver al menú). Puede usar nuestro archivo de prueba copiando la ruta: procesos.txt")
          archivo = input("-Ruta del archivo: ").strip()
          if archivo == "0":
            break
          existe = existeArchivo(archivo)
      elif modoCarga == "2":
        archivo = crearArchivoProcesos()
        existe = archivo is not None
      else:
        print("- Opción de carga inválida.")

      if existe:

        cargarNuevos(archivo, nuevos)
        if not nuevos:
          print("- No se encontraron procesos válidos para simular.")
          continue

        print("\n>>> Carga de procesos finalizada <<<\n")

        print(">" * 100)

        texto = "\n---- Procesos En El Archivo Cargados Al Simulador: ----\n"
        MostrarCola(nuevos, texto)
        print(">" * 100)

        while cantProcesos > 0:
          ejecutarIteracion()

        print("\n                        -----El Simulador Finalizó-----")

        print ("-"* 100)
        print("\n                        ------COMENZANDO INFORMES------\n")
        TEprom, TRprom = CalcularPromediosTEyTR()
        rendimientoSistema = CalcularRendimientoSistema(terminados, tActual)
        print("----Tiempos de ESPERA y RETORNO para Cada Proceso:-----\n")
        print(f"{'ID_P':<5} | {'Estado':<10} | {'T_Arribo':<9} | {'T_Espera':<9} | {'T_Retorno':<10} |")
        print ("-"* 50)
        terminados.sort(key=attrgetter("TA"))
        for p in terminados:
          print(f"{p.id:<5} | {p.estado:<10} | {p.TA:<9} | {round(p.TE):<9} | {round(p.TR):<10} |")

        print(f"""\n                --- Tiempos Promedios: ---

> Tiempo de Espera Promedio: {TEprom:.1f}

> Tiempo de Retorno Promedio:  {TRprom:.1f}""")

        print(f"""\n           ---- Rendimiento del Sistema: ----

> Rendimiento: {rendimientoSistema:.2f} trabajos terminados por unidad de tiempo
 (Total de Procesos Terminados respecto del Tiempo Transcurrido)
""")
        print("""\n                               -------Fin De INFORMES-------

¡Gracias por usar el Simulador!""")
        print("-" * 100)
        break


if __name__ == "__main__":
  ejecutarConsola()
