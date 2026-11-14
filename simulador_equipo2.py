
#ARCHIVO PRINCIPAL: simulador_equipo7.py 
#Version Limpia. Dejé el archivo anterior por si tienen dudas con alguna funcion o cualquier otra cosa. Puede ver los comentarios 

from operator import attrgetter, itemgetter

class Proceso:
  def __init__(self, id, TA, TI, tamano, estado):
    self.id = id
    self.TA = TA
    self.TI = TI
    self.resguardoTI = TI
    self.tamano = tamano
    self.estado = estado
    self.TR = 0. # TR = T_fin – TA
    self.TE = 0. # TE = TR – TI, donde TI es la duración de la ráfaga de CPU requerida).
#HACER: al tomar los procesos del archivo, debo validar los tiposde datos. tamaño debe ser numerico, en el archivo me lo entrega como string, o al menoS eso entiendo, lo tengo que pasar

#
nuevos = []
listos = []
listosSuspendidos = []
terminados = []
#cola de ejecucion, lo aplico como un diccionario:
ejecucion = { "enUso": False, "procEjecutandose": None }


def existeArchivo(nombreArchivo):
  try:
    with open(nombreArchivo, 'r') as archi:
      primerLinea = archi.readline()
      if primerLinea == "":
        print("-El archivo esta vacio.")
        return False
      return True
  except FileNotFoundError:
    print("-El archivo no fue encontrado.")
    return False
  except OSError as error:
    print(f"-No se pudo abrir el archivo: {error}")
    return False
#para ingresar los procesos por pantalla
def crearArchivoProcesos():
  print("Se ingresa un proceso por línea: id, TA, TI, tamaño. Separado por espacios")
  print("Presione Enter en una línea vacía para terminar.")
  while True:
    nombreArchivo = input("-Primero ingrese el nombre del archivo nuevo, en el formato [procesosIngresados.txt]: ").strip()
    if not nombreArchivo:
      nombreArchivo = "procesosIngresados.txt"
    if not nombreArchivo.lower().endswith(".txt"):
      nombreArchivo += ".txt"
    try:
      archi = open(nombreArchivo, "x", encoding="utf-8")
      break
    except FileExistsError:
      print("Ese archivo ya existe. Elija otro nombre para no sobrescribirlo.")
    except OSError as error:
      print(f"No se pudo crear el archivo: {error}")
      return None

  with archi:
    while True:
      linea = input("Proceso (Enter para terminar): ").strip()
      if not linea:
        break
      archi.write(linea + "\n")

  print(f"Procesos guardados en: {nombreArchivo}")
  return nombreArchivo

def cargarNuevos(nombreArchivo, colaNuevos):
    global cantProcesos
    with open(nombreArchivo, 'r') as archi:
    #Cargar procesos
      for linea in archi:
        linea = linea.strip() 
        #-------------------Control de Errores--------------------
        if linea: 
          if "," in linea:
            linea = linea.strip().split(",")
          else:
            linea = linea.strip().split()
          if len(linea) != 4:
            print(f"\n>> Formato incorrecto: {linea!r}. Se descarta este proceso!")
            continue
          try:
            ta = int(linea[1])
            ti = int(linea[2])
            tamano = int(linea[3])
          except ValueError:
            print(f"\n>> Error!Tiempo de Arribo, Tiempo de Irrupcion y tamaño deben ser números: {linea!r}. Se descarta este proceso!")
            continue
          if int(linea[3]) > 450:
            print(f"\n>> Este proceso: {linea!r}, supera el tamaño de la memoria. Será descartado!")
            continue
          #------------------------------------
          procesoNuevo = Proceso(linea[0], ta, ti , tamano, "nuevo")
          colaNuevos.append(procesoNuevo) 
          cantProcesos += 1  
          if cantProcesos >= 10:
            print("Se ha llegado al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
            break
        else: 
          continue #Para saltear renglones vacios.
    #Ordenar cola de procesos, segun tiempo de arribo.
    colaNuevos.sort(key=attrgetter("TA", "TI"))

def EliminarDeCola(cola, proceso): #recibe la cola y el proceso a eliminar.
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

def ControldeProcesos():

  pass


texto = "es para indicar el titulo. Ejemplo: 'Cola de nuevos', 'Cola de listos', etc."
def MostrarCola(cola, texto):
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 49)
    for p in cola:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")


def MostrarMemoria(fMemoria, fragmentacion):
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
    print(">Cantidad restante disponible en memoria: ", disponibleEnMemoria, "\n")


def PresentacionDeSalida(): #muestro todas las colas
  print("\n\n             -------- TIEMPO ACTUAL: ", tActual, " ---------\n")
  print(" >Cantidad de Procesos Faltantes a terminar: ", cantProcesos)
  print(" >Grado De Multiprogramación: ", GM, "\n")

  #Mostrar Memoria-----------------------------------------------------------------
  print("\n-----Tabla de PARTICIONES de MEMORIA-----")
  MostrarMemoria(memoria, fragmentacion)

  #-------------------------------------------------------------------------
  print("\n-----Cola de Procesos NUEVOS-----")
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 49)
  for p in nuevos:
    #if p.TA <= tActual:
    print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")
#---------------------------------------------------------------------------
  texto = "\n-----Cola de Procesos LISTOS-----"
  MostrarCola(listos, texto)
  texto = "\n-----Cola de Procesos LISTOS y SUSPENDIDOS-----"
  MostrarCola(listosSuspendidos, texto)
  #-------------------------------------------------------------------------
  if terminados: 
    texto = "\n-----Cola de Procesos TERMINADOS-----"
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 49)
    for p in terminados:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.resguardoTI:>4} | {p.tamano:>10} | {p.estado:<10} |")

  #Mostrar cola de Ejecucion------------------------------------------------
  print("\n-----Estado del PROCESADOR Actualmente-----\n")
  print(f"| {'Proceso Ejecutandose':^20} | {'Tiempo de Irrupción':^19} | ")
  print("-" * 46)
  if ejecucion["enUso"] == True:
    pEjecutandose = ejecucion["procEjecutandose"]
    print(f"| {pEjecutandose.id :^20} | {pEjecutandose.TI :^19} |\n")
  else: 
    print(f"| {'Ninguno':^20} | {'0':^19} |\n")
    print("\n>(Actualmente no hay procesos ejecutandose)--\n")
  print("-" * 100 , "\n")


#--------------------------MEMORIA-------------------------------------
# La memoria se maneja como una lista de diccionarios:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
contadorIDparticion = 2
disponibleEnMemoria = 450
#----------------------manejo de memoria-----------------------
def CargarEnMemoria(fproceso):
  global disponibleEnMemoria, contadorIDparticion
  fFragmentacion= [] #cada vez que se intente cargar un proceso: puede o no haber fragmentacion
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0:
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    
    for i in range(longitudMemoria):
      if memoria[i].get("procesoAsignado") is None:
        if fproceso.tamano <= memoria[i].get("tamanio"):
            sobraEspacio = memoria[i].get("tamanio") - fproceso.tamano # si hay fragmentacion interna al asignar el proceso, creo otra particion
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano 
            if sobraEspacio > 0:
              particionNueva = { "id": (contadorIDparticion), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": sobraEspacio , "procesoAsignado": None }
              memoria.append(particionNueva)
              contadorIDparticion += 1

            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id            
            return True, fFragmentacion #True: proceso cargado.
        else: #no ingresó porque la particion era pequeña:
          fFragmentacion.append(memoria[i]) 
        
    return False, fFragmentacion 

def MostrarFragmentacion(fFragmentacion):
  fragTotal = 0
  print("> Hubo FRAGMENTACIÓN en las particiones: ")
  for part in fFragmentacion:
    print(f"   -Particion: {part["id"]} ; Tamaño: {part["tamanio"]}")
    fragTotal += part["tamanio"]
  print("-Fragmentacion Externa total en la memoria: ", fragTotal, ", en el Tiempo = ", tActual, "\n")

def JuntarParticiones(fmemoria):
  #ACLARACION: esta funcion NO COMPACTA espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
  #Por cada proceso que se guarda en memoria se crea un nuevo diccionario, cuando el proceso se desasigna, el diccionario queda LIBRE, y se junta SOLO si el siguiente diccionario LIBRE es sucesivo en memoria al anterior (o sea: PART 1: Comienzo: 50, tamaño:50 → Si PART 2: comienzo: 100, y esta libre; se unen.) Asi un proceso mas grande, que la particion antes de juntarse, puede usar el espacio disponible """
  memoriaCopy = [] 
  longitudMemoria = len(fmemoria) 
  if longitudMemoria > 1: 
    fmemoria.sort(key=itemgetter("comienzo"))  #Ordeno segun direccion de inicio de cada particion, para facilitar.
    i = 0
    while i < longitudMemoria:  
      particionNueva = fmemoria[i].copy()
      if fmemoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre?→ Si → Entonces me fijo las siguientes.
        while ( i+1 < longitudMemoria) and (fmemoria[i+1].get("procesoAsignado") is None):
          particionNueva["tamanio"] += fmemoria[i +1].get("tamanio")
          i += 1
      memoriaCopy.append(particionNueva) 
      i += 1
  else:
    memoriaCopy= fmemoria
  return memoriaCopy      

def LiberarMemoria(fproceso, memoria):
  global disponibleEnMemoria, fragmentacion
  for particion in memoria: #Busco particion donde esta el proceso a quitar.
    if str(particion.get("procesoAsignado")) == str(fproceso.id) :
      particion["procesoAsignado"] = None #cambio estado de la particion a LIBRE
      disponibleEnMemoria += fproceso.tamano
      memoria = JuntarParticiones(memoria)
      return True, memoria
    fragmentacion = [] #reinicio las fragmentaciones que pudieron haber ocurrido.
  return False, memoria

#------------------------------------fin MEMORIA---------------------------------------


def CargarListosYSuspendidos(fProceso, colaActual): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso) #este lo agrega al final de la cola, no se si seria mejor acomodar segun TI.
  listosSuspendidos.sort(key= attrgetter("TI")) 
  EliminarDeCola(colaActual, fProceso)

def AgregarAListos(fProceso, colaListos): #SRTF
  fProceso.estado = "listo"
  mayorTI = True
  #Cargar segun TI
  listosCopy = list(colaListos)
  for proc in listosCopy: 
    if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor tiempo de irrupción
        indice = colaListos.index(proc) 
        colaListos.insert(indice, fProceso)
        mayorTI = False
        break
  if mayorTI: 
    colaListos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

def CargarListos(fProceso, colaListos, colaActual):
  hayEspacio, fFragmentacion = CargarEnMemoria(fProceso) 
  if hayEspacio:
    AgregarAListos(fProceso, colaListos)
    EliminarDeCola(colaActual, fProceso) #ColaActual: cola de la cual se elimina el proceso (puede ser nuevos, suspendidos) 
  #No hay espacio: 
  elif (fProceso.estado != "suspendido"):  #Cargar en suspendidos, solo si es que NO estaba en suspendidos.
    CargarListosYSuspendidos(fProceso, colaActual)
  return fFragmentacion
  
def EjecutarProceso(procActual, colaEjecucion, colaListos): 
  if colaEjecucion["enUso"] == True:
    procesoEjecutandose = colaEjecucion["procEjecutandose"]
    
    if procActual.TI < procesoEjecutandose.TI: #Expropio
      AgregarAListos(procesoEjecutandose, colaListos) #Ya esta asignado a memoria, no hace falta pregunta por espacio dispo.
      print(f"> Se expropió el proceso {procesoEjecutandose.id}, por el proceso: {procActual.id}, TI: {procActual.TI} (tiempo = {tActual}). \n")
    else: #print("\n> Un proceso intentó ejecutarse: La CPU está ocupada por un proceso con menor TI")
      return
  else:
    colaEjecucion["enUso"] = True
  EliminarDeCola(colaListos, procActual)
  procActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procActual
  
def TerminarProceso(proceso, fMemoria): 
  global cantProcesos, GM
  liberadoCorrectamente, fMemoria = LiberarMemoria(proceso, fMemoria)
  if liberadoCorrectamente:
    cantProcesos -=1
    GM -= 1
    proceso.estado = "terminado"
    proceso.TR = tActual - proceso.TA #Calculo su tiempo de retorno
    terminados.append(proceso)
    ejecucion["enUso"] = False
    ejecucion["procEjecutandose"] = None
  else: 
      print("Hubo un error al finalizar el proceso.")
  return fMemoria, disponibleEnMemoria

def DisminuirTI(colaEjecucion, fMemoria, disponibleEnMemoria ):
  fProceso  = colaEjecucion["procEjecutandose"]
  fProceso.TI -=1
  if fProceso.TI == 0: 
    print(f"\n>Terminó el proceso: {fProceso.id} (Tiempo = {tActual}) ")
    fMemoria, disponibleEnMemoria = TerminarProceso( fProceso, fMemoria )
    return True, fMemoria, disponibleEnMemoria
  return False, fMemoria, disponibleEnMemoria


def CalcularPromediosTEyTR():
  #tiempos promedios:
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
  totalProcTerm= len(colaTerminados)
  rendimiento = totalProcTerm / (tActual)
  return rendimiento
  #total de trabajos terminados / periodo de tiempo (o sea: cantidad en colaTerminados divido tActual)

def AumentarTiempo(colaListos, colaSuspendidos): 
  global tActual
  tActual +=1
  #Aumentar tiempos de espera de cada proceso:
  for proc in colaListos:
    proc.TE += 1
  for proc in colaSuspendidos:
    proc.TE += 1

def informacion():
  print("""--------------------------------------- Informacion ---------------------------------------
Este es un Trabajo Practico de la asignatura de Sistemas Operativos. 
En este simuulador se implementa la gestion de memoria de particiones variables. Donde la memoria esta dispuesta de la siguiente manera: 
  >100K destinados al Sistema Operativo
  >450K para trabajos de usuarios.
Se permite un maximo de 10 procesos. Se pueden cargar manualmente por teclado, o por medio de un archivo:
  > Si el archivo a ingresar no se encuentra en la misma carpeta del codigo, se deberá ingresar la ruta de acceso completa. 
  > Pudiendo ingresarse la ruta de acceso relativa si se copiase dicho archivo, dentro de la carpeta
La planificacion de procesos es a corto plazo → Incluye 5 estados: "nuevo", "listo", "suspendido", "ejecutando" , "terminado"

>> Las abreviaciones usadas en el programa son:
  TA: tiempo de arribo
  TI: tiempo de irrupcion
  TR: tiempo de retorno
  TE: tiempo de espera
  tActual: representa el tiempo que trascurre en el programa
  GM: grado de multiprogramacion. Refiere a la cantidad de proceso en las colas de: listos, suspendidos y ejecucion. Siendo el limite de 5 en total.

Respecto al formato de los procesos que admite este programa 
  → Deben tener la forma: " ID_Proceso TA TI Tamaño ", separado por espacios (P1 0 20 180) o por comas (P1,0,20,180).

  Al finalizar, se presentan los informes de promedios de tiempo de espera, tiempos de retorno y el rendimiento del sistema.
>> Nuestro archivo de prueba es: procesos.txt
El programa puede ejecutarlo en un terminal dedicado (en VSCode) o abriendo el terminal externo (ctrl+shift+c), una vez abierto→ escribir: python simulador_equipo7.py (copiar la ruta relativa)
""")
  salir = input("Para volver al menu presione 'Enter':")
  if salir == "":
    return True
  return False


##MAIN: ------------------------------------------------------------------------------------------------------------------
#declaracion de variables:
cantProcesos = 0
tActual = 0
GM = 0 # Grado de Multiprogramacion, maximo 5
fragmentacion = []
procesoActual = None

#--------------------------------------------MENU:------------------------------------ 
print("¡Bienvenido al SIMULADOR Del Equipo N° 2 de Sistemas Operativos!") 
print("""Este programa simula la gestion de asignacion de memoria (de particiones variables) y planificacion de procesos con el algoritmo SRTF.

> Equipo N° 7 - Comision: k2.1 - Integrantes:
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

  opcion = int(input("Seleccione una opción: "))
  if opcion != 1 and opcion != 2 and opcion != 0:
    print("\n>> Ha escrito una opcion invalida... \n")

  if opcion == 0:
    break
  elif opcion == 1:
    volverAMenu = informacion() 
    if volverAMenu:
      continue

#-------------------------------------------------------------------------------------------------------------
  elif opcion == 2:
    print("""\n           > COMENZANDO EL SIMULADOR...
-Elija un formato de carga de los procesos:
  1. Cargar un archivo existente
  2. Ingresar procesos y guardarlos en un archivo nuevo""")
    modoCarga = input("Seleccione una opción: ").strip()
    existe = False
    if modoCarga == "1":
      while not existe:
        print("-Cargue la ruta (o ingrese '0' para volver al menú). Puede usar nuestro archivo de prueba copiando la ruta: procesos.txt")
        archivo = input("-Cargue aquí: ").strip()
        if archivo == "0":
          break
        existe = existeArchivo(archivo)
    elif modoCarga == "2":
      archivo = crearArchivoProcesos()
      existe = archivo is not None
    else:
      print("- Opción de carga inválida.")
    
    if existe:
      #Cargo los procesos en el archivo, a la cola de nuevos.
      cargarNuevos(archivo, nuevos)
      if not nuevos:
        print("- No se encontraron procesos válidos para simular.")
        continue

      print("\n>>> Archivo Procesado Correctamente <<<\n")

      print(">" * 100)
      #Muestro los procesos cargados:
      texto = "\n---- Procesos En El Archivo Cargados Al Simulador: ----\n"
      MostrarCola(nuevos, texto)
      print(">" * 100)
      
      while cantProcesos > 0:
        llegoProcNuevo = False 
        if GM < 5:
          if nuevos:
            for proceso in list(nuevos): 
              if proceso.TA <= tActual:
                fragmentacion = CargarListos(proceso, listos, nuevos) 
                GM += 1
                llegoProcNuevo = True 
                if proceso.TA == tActual:
                  print(f"\n > Llegó un NUEVO proceso: {proceso.id} (Tiempo Actual = {tActual})")
                else: 
                  print(f"\n > Se admitió un proceso de Cola de Nuevos: {proceso.id}. (Tiempo Actual = {tActual} )")
                if GM >= 5:
                  break

        if listos:
          procesoActual = listos[0] #la lista ya esta ordenada por TI, entonces solo tomo el pimrer elemento
          if procesoActual.TA <= tActual: 
            EjecutarProceso(procesoActual, ejecucion, listos)

        if llegoProcNuevo:
          PresentacionDeSalida()

        AumentarTiempo(listos, listosSuspendidos)
#--------------------Una vez aumentado el tiempo: Control de ejecucion:-------------------------------------------------
        #finalizó la ejecucion del proceso?
        procFinalizado, memoria, disponibleEnMemoria = DisminuirTI(ejecucion, memoria, disponibleEnMemoria) 
        if procFinalizado:
          if listos:
            procesoActual= listos[0] #Siguiente proceso a ejecutar
            if procesoActual.TA <= tActual:
              EjecutarProceso(procesoActual, ejecucion, listos)

  #-----------------------Termina control de ejecucion---------------

          for p in list(listosSuspendidos): #hay un proceso suspendido en espera de ser cargado.
            fragmentacion = CargarListos(p, listos, listosSuspendidos)

          if cantProcesos == 0:
            print("\n\n               >>> Estado Final del Simulador <<<")
            
          PresentacionDeSalida()

        
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

  
  






    


