
#ARCHIVO PRINCIPAL: SIMULADOR 
#Esta muy cargaado de anotaciones, al terminarlo, habria que "limpiarlo"

"""
TA: tiempo de arribo
TI: tiempo de irrupcion
TR: tiempo de retorno
TE: tiempo de espera
estados: "nuevo", "listo", "suspendido", "ejecutando" , "terminado"

Las presentaciones de salida deberán realizarse cada vez que llega un nuevo proceso
y se termina un proceso en ejecución.
"""
from operator import attrgetter, itemgetter

class Proceso:
  def __init__(self, id, TA, TI, tamano, estado):
    self.id = id
    self.TA = TA
    self.TI = TI
    self.tamano = tamano
    self.estado = estado
    self.TR = 0. # TR = T_fin – TA
    self.TE = 0. # TE = TR – TI, donde TI es la duración de la ráfaga de CPU requerida).
#HACER: al tomar los procesos del archivo, debo validar los tiposde datos. tamaño debe ser numerico, en el archivo me lo entrega como string, o al menoS eso entiendo, lo tengo que pasar


#En si, inicializar de esta forma no hace falta, lo hago para tener en cuenta las estrcturas a usar.
nuevos = []
listos = []
listosSuspendidos = []
terminados = []
#cola de ejecucion, lo aplico como un diccionario:
ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }


def existeArchivo(nombreArchivo):
  try:
    with open(nombreArchivo, 'r') as archi:
      primerLinea = archi.readline()
      if primerLinea == "":
        print("El archivo esta vacio.")
        return False
      return True
  except FileNotFoundError:
    print("El archivo no fue encontrado.")
    return False
    #si es false, se le da otra chance para cargar, o que se cree desde 0. #HACERRRR

def cargarNuevos (nombreArchivo, colaNuevos):
    global cantProcesos
    with open(nombreArchivo, 'r') as archi:
    #cargar procesos
      for linea in archi: 
        if linea != "": 
          #cada linea es un proceso.
          # El proceso está cargado en archivo como: id,TA,TI,memoria.
          linea = linea.strip().split(",") #strip para sacar \n y split para separar por comas.
          procesoNuevo = Proceso(linea[0], int(linea[1]), int(linea[2]), int(linea[3]), "nuevo")
          # nombre = linea 0 , TA = linea 1, 
          #pNuevo = Proceso(p1,3, 5, 20, "nuevo")

          #TE = TR – TI, tengo 2 opciones: ya resto el TI aca y al terminar el proceso le sumo el retorno (que se calcula cuando termina)
          #procesoNuevo.TE = - procesoNuevo.TI
          #o la segunda opcion: ir sumando TE +1 por cada vez que el timpo pasa

          colaNuevos.append(procesoNuevo) # proc cargado a la lista.

          cantProcesos += 1  
          if cantProcesos > 10: #vigila que no se pase de 10 proc.
            print("Se ha llegado al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
            break

        else: 
          continue #esto por si hay un renglon vacio.

  #ordena procesos. ordeno la cola de nuevos por TA, si hay dos con TA iguales, ordeno por id.
    colaNuevos.sort(key=attrgetter("TA", "TI"))
     #OTRA FORMA: colaNuevos = sorted(nuevos, key = attrgetter('TA', 'TI') ) #revisar #probe y funciona. 

def EliminarDeCola(cola, proceso): #recibe la cola y el proceso a eliminar.
  """colaCopy = list(cola)
  for i, proc in enumerate(colaCopy):
      if proc.get("id") == proceso.id:
          del cola[i]
          return True
  return False"""
  #otra froma de: la anterior no parece eliminar correctamente
  seEncontroProc = False
  indice = 0
  while i < len(cola):
    proc = cola[indice]
    if proc.id == proceso.id:
      resguardoIndice = indice
      seEncontroProc = True
      break
    indice += 1
  if seEncontroProc:
    del cola[resguardoIndice]



texto = "es para indicar el titulo. Ejemplo: 'Cola de nuevos', 'Cola de listos', etc."

def MostrarCola(cola, texto):
    print(texto)
    print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
    print("-" * 50)
    for p in cola:
        print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")

  #lo que hace el ''TA':>4' es rellenar con espacios vacios a la izq, si el texto tiene menos de 4 caracteres.
  #print("-" * 50) lo que hace es imprimir 50 guiones, para separar el titulo del  contenido

def MostrarMemoria(fMemoria):
  print(f"{'ID_Particion':<12} | {'Comienzo':^4} | {'Tamaño KB':^8} | {'Proceso Asignado':^16} | {'Fragmentacion':<13}")
  print("-" * 70)
  print(f"{'Par_0':<12} | {'450':^8} | {'100':^9} | {'SIST. OPERATIVO':^16} | {' ':<13}")
  fMemoria.sort(key=itemgetter("comienzo")) 
  for part in fMemoria:
    pAsignado = part["procesoAsignado"]
    if pAsignado is None:
      pAsignado = "Libre"
    print(f"Par_{part["id"]:<8} | {part["comienzo"]:^8} | {part["tamanio"]:^9} | {pAsignado:^16} | {0:^13}")


"""El simulador deberá presentar como salida la siguiente información:
 El estado del procesador (proceso que se encuentra corriendo en ese instante)
 La tabla de particiones de memoria, la cual deberá contener (Id de partición, dirección de comienzo de
partición, tamaño de la partición, id de proceso asignado a la partición, fragmentación)
 El estado de la cola de procesos listos y listos/suspendidos."""

def PresentacionDeSalida(): #muestro todas las colas
  print("\n             -------- Tiempo Actual: ", tActual, " ---------\n")
  #Mostrar cola de Ejecucion
  print("\n-----Estado del PROCESADOR Actualmente-----\n")
  print(f"| {'Proceso Ejecutandose':^20} | {'Tiempo de Irrupción':^19} | ")
  print("-" * 50)
  if ejecucion["enUso"] == True:
    pEjecutandose = ejecucion["procEjecutandose"]
    print(f"| {pEjecutandose.id :^20} | {pEjecutandose.TI :^19} |")
  else: 
    print(f"| {'Ninguno':^20} | {'0':^19} |")
    print("\n--(Actualmente no hay procesos ejecutandose)--")

  #Mostrar Memoria-----------------------------------------------------------------
  print("\n-----Tabla de PARTICIONES de MEMORIA-----")
  #mostrar: id part, dir de comienzo, tamaño, id proceso asignado, fragmentacion?????
  #mostrar tabla
  MostrarMemoria(memoria)
  print(" Cantidad de Procesos Actualmente: ", cantProcesos)
  #-----------------------------------------------------------------------------------
  print("\n-----Cola de Procesos NUEVOS-----")
  print(f"| {'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10} |")
  print("-" * 50)
  for p in nuevos:
    #if p.TA <= tActual:
    print(f"| {p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.tamano:>10} | {p.estado:<10} |")

#---------------------------------------------------------------------
  texto = "\n-----Cola de Procesos LISTOS-----"
  MostrarCola(listos, texto)
  texto = "\n-----Cola de Procesos LISTOS y SUSPENDIDOS-----"
  MostrarCola(listosSuspendidos, texto)
  texto = "\n-----Cola de Procesos TERMINADOS-----"
  MostrarCola(terminados, texto)


#---------------------------------------------------------------
# Por el momento, la memoria se maneja d esta forma. Es lo que se me ocurrió
# Es una lista de diccionarios. Las particiones son los diccionarios

memoria = []
particionInicial = { "id": "1", "comienzo": 0, "tamanio": 450, "procesoAsignado": None, "fragmentacion": 0 }
#en la consigna piden al fragmentacion. Pero no entiendo para qué, si es variable
#hay que revisar en el def cargarmemoria, los ID porque se repiten.
memoria.append(particionInicial)
""" o lo que es lo mismo:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
"""

disponibleEnMemoria = 450 #este debo ir disminuyendolo, y aumentarlo al liberar memoria.

#-----------------------------------
#actualizacion: saque a DisponibleEnMemoria como parametro, para usarla como global, y se actualice automaticamente
def CargarEnMemoria(fproceso): #REVISAR #por las, poner como parametro memoria
  global disponibleEnMemoria
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    for i in range(longitudMemoria):  #itero sobre cada particion, para saber cual esta libre
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if fproceso.tamano <= memoria[i].get("tamanio"):
            disponibleEnMemoria =  disponibleEnMemoria - fproceso.tamano 
            if disponibleEnMemoria > 0: #o sea, que aun hay espacio en memoria para cargar un proximo proceso.
              # def asignar id
              particionNueva = { "id": (longitudMemoria+1), "comienzo": memoria[i].get("comienzo") + fproceso.tamano, "tamanio": disponibleEnMemoria , "procesoAsignado": None }
              memoria.append(particionNueva)
              #revisar el "id": (logitudMemoria+1). Quiza sea mejor preguntar por el id de la particion anterior y sumarle 1

            # de memoria[i] (o sea, la particion que esta libre en la cual voy a poner el proceso actual) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = fproceso.tamano
            memoria[i]["procesoAsignado"] = fproceso.id
            return True #manda un mensaje de que el proceso se cargo en memoria.
        #no ingresó pq la particion era pequeña:
        #else: 
        #  fragmentacion += memoria[i]["tamanio"] #siquiera hace falta, en mi opinion
    return False  #no hubo espacio, por tanto no se cargó.

#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
#Solucion: Version 1: uso un ordenador de lista
def JuntarParticiones(memoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio sucesivo al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una particion
    memoria.sort(key=itemgetter("comienzo"))  #primero ordeno memoria segun el comienzo de c/particion.
    memoriaCopy = []
    i = 0
    while i < longitudMemoria :  
      particionNueva = memoria[i] #me quedo con id, comienzo y el procsoAsignado = none.
      if memoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre: Si. entonces me fijo las siguientes
        #-1 para no pasarme del rango al iterar con i+1
        while memoria[i+1].get("procesoAsignado") is None: #si da True, es pq puedo unirlas
          particionNueva["tamanio"] += memoria[i +1].get("tamanio")
          i += 1
      #en este caso, no hace falta eliminar la particion de la memoria, porque ya estoy colocando solo las nuevas particiones en otra lista de memoria.
      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
  return memoriaCopy #si o si debo retornar las variables que fueron reasignadas en la funcion
         

def LiberarMemoria(fproceso, memoria): #revisar #este se usaria al teminar un proceso
  global disponibleEnMemoria
  for particion in memoria: #me fijo en que lugar esta el proceso a quitar
    if str(particion.get("procesoAsignado")) == str(fproceso.id) :
    #El str es para pasar ambos a tipo string para que no de error de tipos. Solo por las dudas. 
      particion["procesoAsignado"] = None
      #ojo que: no elimino el elemento de la lista "memoria", solo cambio el estado, ya está desocupado.
      disponibleEnMemoria += fproceso.tamano
      memoria = JuntarParticiones(memoria)
      return True, memoria
  #si terminó de iterar es pq no encontró el proceso, por eso retorna False, deberia poner tmb un texto que idga que no se encontró
  return False, memoria #no se encontró el proceso en memoria.
#CAMBIAR A RETURN FALSE

#----------------------------------------------------------------------------fin Memoria

def CargarListosYSuspendidos(fProceso, colaActual): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso) #este lo agrega al final de la cola, no se si seria mejor acomodar segun TI.
  EliminarDeCola(colaActual, fProceso)

def AgregarAListos(fProceso, colaListos):
  fProceso.estado = "listo"
  mayorTI = True
  #cargar segun TI
  listosCopy = list(colaListos)
  for proc in listosCopy: 
    if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor tiempo de irrupción
        indice = colaListos.index(proc) 
        colaListos.insert(indice, fProceso)
        mayorTI = False
        break
  if mayorTI: 
    colaListos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

#antes de cargar a listos, pregunto pot el tiempo actual
def CargarListos(fProceso, colaListos, colaActual):
      #se actualliza estado del proceso a listo
      #a tener en cuenta: cargar los procesos segun TI.
      # quiza deba hacer una funcion aparte para eso
  hayEspacio = CargarEnMemoria(fProceso) #retorna v o f.
  if hayEspacio:
    #cargar a listos
    AgregarAListos(fProceso, colaListos)
    #elimina de la cola anterior, porque ya se cargo a listos o suspendidos.
    EliminarDeCola(colaActual, fProceso)  #POR EL MOMENTO DEJO INACTIVO, PARA SABER SI ES ESTE EL PROBLEMA, ELIMINO AFUERA
      #con "cola actual" me refiero a la cola de la que se elimina, puede ser cola de ejecucion, de nuevos, de suspendidos.
  
  #no hay espacio: 
  elif (fProceso.estado != "suspendido"): #si es igual a suspendido es pq ya estaba en la lista de suspendidos. no hace falta volvcer a ponerlo.
    #cargar en suspendidos, solo si es que NO estaba en suspendidos
    CargarListosYSuspendidos(fProceso, colaActual)
  #si es == suspendido, no hago nada.



#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

#ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }
def EjecutarProceso(procActual, colaEjecucion, colaListos): #hacer
  #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.
  #Nota: sí, tengo que agregarlo a la cola de lsitos, pero no tengo que preguntar si hay espacio en memoria, porque el proceso ya esta asignado en memoria
  #overhead:
  if colaEjecucion["enUso"] == True: #HAY proc EJecutandose: preguntar por TI y sacar proceso
    
    procesoEjecutandose = colaEjecucion["procEjecutandose"]
    #procesoEjecutandose.TI = colaEjecucion["tiempoEjecucion"] #creo qu eesta linea no hace falta. Es para ctualizar TI, pero spone que igual se va ir restando directamente del proceso actualemnte enejecucuion
    
    if procActual.TI < procesoEjecutandose.TI: #lo saco al anterior de la cola ejecutandose
      #llamo a la funcion de agragar a listos, sin preguntar por memoria.
      AgregarAListos(procesoEjecutandose, colaListos) #aca adentro ya se actualiza su estado
      #si no entra en el if es pq el proceso Actual es igual al del ejecutandose.
    else: 
      print("La CPU está ocupada por un proceso con menor TI")
  #Si en este if, no entra, es pq no hay procesos ejecutandose: colaEjecucion["enUso"] == False:
  else:
    colaEjecucion["enUso"] = True
  #no pongo en else, pq en ambos casos debo asignar el proceso actual en la cola de listos
  EliminarDeCola(colaListos, procActual)
  procActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procActual
  #colaEjecucion["tiempoEjecucion"] = procesoActual.TI #no hace falta este, creo
  #NOTA: aca se deberia hacer un print general de el estado de todos los procesos y la cola de ejecucion 


#  TR = T_fin – TA. El tiempo de fin seria el TActual en que termina
def TerminarProceso(proceso, fMemoria): #hacer
  global cantProcesos, GM
  liberadoCorrectamente, fMemoria = LiberarMemoria(proceso, fMemoria)
  if liberadoCorrectamente:
    cantProcesos -=1
    GM -= 1
    proceso.estado = "terminado"
    #calcular TR del proceso
    proceso.TR = tActual - proceso.TA
    terminados.append(proceso)

    ejecucion["enUso"] = False
    ejecucion["procEjecutandose"] = None
    #ejecucion["tiempoEjecucion"] = 0
  else: 
      print("Hubo un error al finalizar el proceso.")

  return fMemoria, disponibleEnMemoria
 #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria

def DisminuirTI(colaEjecucion, fMemoria, disponibleEnMemoria ):
    colaEjecucion["procEjecutandose"].TI -=1
    if colaEjecucion["procEjecutandose"].TI == 0: #en esta funcion se "aumenta" el TR del proceso
      fMemoria, disponibleEnMemoria = TerminarProceso( ejecucion["procEjecutandose"], fMemoria ) 
      return True, memoria, disponibleEnMemoria
    return False, memoria, disponibleEnMemoria



""" Al finalizar la simulación se deberá presentar un informe estadístico con, tiempo de retorno y espera para cada
proceso y los respectivos tiempos promedios. También deberá calcular el rendimiento del sistema para la
simulación (cantidad de trabajos terminados por unidad de tiempo)"""


def CalcularPromediosTEyTR():
  #tiempos promedios:
  #TE suma de todos los TE divido la cant de procesos
  totalProcesos = len(terminados)
  TEpromedio = 0
  TRpromedio = 0
  for p in terminados:
    TEpromedio += p.TE
    TRpromedio += p.TR

  TEpromedio = TEpromedio / totalProcesos
  TRpromedio = TRpromedio / totalProcesos
  return TEpromedio, TRpromedio


def CalcularRendimientoSistema ():
  pass



def AumentarTiempo(colaListos, colaSuspendidos): #hacer
  global tActual
  #aumenta tiempo actual
  #en esta funcion, deberia tambien aumentar lso tiempos de espera, o de retorno, no se, de cada proceso
  tActual +=1
  #Aumentar tiempos de espera de cada proceso:
  for proc in colaListos:
    proc.TE += 1
  for proc in colaSuspendidos:
    proc.TE += 1

def informacion():
  print("""Este es un proyecto de la materia de Sistemas Operativos, trata de un simulador.. bla bla.."

  El archivo a ingresar puede y debe tenr al forma: ....
  Al finalizar ... etc""")
  salir = input("Para volver al menu presione 'Enter':")
  if salir == "":
    return True
  return False




#----------------------------------------------------------------------------------
#MAIN:

#declaracion de variables:

cantProcesos = 0
tActual = 0
GM = 0 # Grado de Multiprogramacion, maximo 5


#menu: #mejorar la salida de texto
print("Bienvenido al Simulador... ETC...!")

while True:
  print("""Opciones Disponibles:
    "0. Salir: ingrese '0' para salir
    "1. Informacion (recomendable)
    "2. Comenzar Simulador
    -----------------------------------------------------------------------""")

  opcion = int(input("Seleccione una opción: "))
  if opcion != 1 and opcion != 2 and opcion != 0: #para controlar la entrada
    print("\n-----Ha escrito una opcion invalida----- \n")

  if opcion == 0:
    break
  elif opcion == 1:
    volverAMenu = informacion()
    if volverAMenu:
      continue

#-------------------------------------------------
  elif opcion == 2:
    print("""           > Comenzando el Simulador...
-Por favor, cargue la ruta del archivo con los procesos, en el formato: txt """)
    existe = False
    while not existe:
      archivo = input("-Cargue aquí: ")
      existe = existeArchivo(archivo)
      if not existe:
        archivo = input("""-ERROR!-Intente ingresarlo otra vez o intente con otro archivo (Ingrese '0' para volver al Menu) """)
        if archivo == "0":
          break         #REVISAR ESTO
     
    if existe:
    #Sigo con el programa, por:
    #una vez abierto el archivo:
      cargarNuevos (archivo, nuevos)
      """ for p in nuevos:
        print("proceso: ", p.id )
      esto era para probar si cargaba correcta,emte. Lo hacxe: el porblema no esta acá"""

      i = 0 #el indice de las listas comienza en 0
      while cantProcesos > 0:
            #creo q aca deberia comenzar a incrementar manualemnte, o usando pop en la lista de nuevos.
        if GM < 5:
          if len(nuevos) > 0:
            llegoProcNuevo: False
            """ otra forma:
                i = 0
                while GM <= 5 or i < len(nuevos):
                  CargarListos()
                  GM += 1.
                """
                #...
            # list() hace una copia de la lista nuevos, esto solo lo uso para iterar, sin embargo, modifico la lista original dentro del bucle y no la copia
            for proceso in list(nuevos): #mepa q lo ideal es usar pop
              if proceso.TA <= tActual:
                CargarListos(proceso, listos, nuevos) #aca se carga en listos, a memoria, o a listos y suspendidos, y se saca de la cola de nuevos
                GM += 1
                llegoProcNuevo = True #solo me interesa saber si llego un nuevo proceso, no si se cargó
                if GM >= 5:
                  break
            #  else:
            #    break
            if llegoProcNuevo: #una de las peticiones es mostrar la presentacion de salida cada vez que se admite un proceso
              PresentacionDeSalida()
          else:
            print("---Cola de Nuevos Vacia---")

        if listos: #pregunta si la lista no esta vacia
          if i < len(listos): #para no pasarme del tamaño
            procesoActual = listos[i]
            if procesoActual.TA <= tActual: 
              EjecutarProceso(procesoActual, ejecucion, listos)
        else:
          print("Por el momento, no hay procesos el cola de listos para ejecutar")

        AumentarTiempo(listos, listosSuspendidos)

      #Una vez aumentado el tiempo: Control de ejecucion:---------------------

        if ejecucion["enUso"] == True:
          if procesoActual == ejecucion["procEjecutandose"]: #pregunto si es el que recien se ejecutó, si es asi, entonces ejecuto el siguiente en listos
            
            """if listos: ultimo = listos[-1]
            listos debería ser una lista
            if listos: significa:
            si la lista no está vacía, entra
            si está vacía, no entra
            eso es válido para listas
            no es un bool en sí mismo, es una condición sobre la lista"""
            if listos: #pregunta si la lista no esta vacia
              #ultimo = listos[-1]
              i += 1
              #if i != ultimo:
              if i < (len(listos) -1) :
                procesoActual = listos[i] #quiza deba usar pop, para ello debo modificar lo de eliminar de cola
              #else:
              #  i = 0 #reinicio i, pq ya llegó al fin de la cola de listos
            else:
              print("\n -- Por el momento, no hay procesos en la cola de listos que puedan ejecutarse... \n")
            #else: es pq sigue esperando a ser ejecutado

          #finalizó la ejecucion del proceso?
          procFinalizado, memoria, disponibleEnMemoria = DisminuirTI(ejecucion, memoria, disponibleEnMemoria)  #aca dentro llamo a la funcion terminar
          if procFinalizado: #Si terminó, asigno otro proceso
            if procesoActual.TA <= tActual: #la lista ya esta ordenada por TI, por eso solo pregunto por TA
              EjecutarProceso(procesoActual, ejecucion, listos)

  #-------------termina control de ejecucion---------------

            if len(listosSuspendidos) > 0: #hay un proceso en espera de ser cargado.
              for j, p in enumerate(listosSuspendidos):
                if p.TA <= tActual:
                  CargarListos(p, listos, listosSuspendidos)

            PresentacionDeSalida() #mostrar cada vez que se termina un proceso
            #lo pongo a lo ultimo pq considero que en el mismo TActual se debe mover un proceso suspendido a listo

      #------finalizado el bucle, cantProcesos = 0. Hago los informes:
      print("-----El Simmulador Finalizó-----")
      print ("-"* 50)
      print("-----Comenzando Informes------")

      TEprom, TRprom = CalcularPromediosTEyTR()
      # rendimiento = CalcularRendimientoSistema ()

      print("----Tiempos de Espera y Retorno para cada Proceso:-----")
      print(f"{'ID_P':<5} | {'Estado':<10} | {'T_Espera':<9} | {'T_Retorno':<10} |")
      print ("-"* 50)
      for p in terminados:
        print(f"{p.id:<5} | {p.estado:<10} | {p.TE:<9} | {p.TR:<10} |")

      print(f""" ---Tiempos Promedios---
      
      --Tiempo de Espera Promedio: {TEprom}

      --Tiempo de Retorno Promedio:  {TRprom}""")
  

  #hay algo en la cola de nuevos, que hace que el resto se ejecute mal
        



        






  






    


