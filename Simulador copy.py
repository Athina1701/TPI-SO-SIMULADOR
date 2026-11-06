
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
    #si es false, se le da otra chance para cargar, o que se cree desde 0. Hacer

def cargarNuevos (nombreArchivo):
    global cantProcesos
    with open(nombreArchivo, 'r') as archivo:
    #cargar procesos
      for linea in archivo: 
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

          nuevos.append(procesoNuevo) # proc cargado a la lista.

          cantProcesos += 1  
          if cantProcesos > 10: #vigila que no se pase de 10 proc.
            print("Se ha llegado al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
            break

        else: 
          continue #esto por si hay un renglon vacio.

  #ordena procesos. ordeno la cola de nuevos por TA, si hay dos con TA iguales, ordeno por id.
    nuevos = sorted(nuevos, key = attrgetter('TA', 'TI') ) #revisar #probe y funciona. 

def EliminarDeCola(cola, proceso): #recibe la cola y el proceso a eliminar.
  for i, proc in enumerate(cola):
      if proc.get("id") == proceso.id:
          del cola[i]
          return True
  return False


texto = "es para indicar el titulo. Ejemplo: 'Cola de nuevos', 'Cola de listos', etc."

def MostrarCola(cola, texto):
    print(texto, "\n")
    print(f"{'ID_P':<5} | {'TA':^4} | {'TI':^4} | {'Tamaño KB':^10} | {'Estado':<10}")
    print("-" * 50)
    for p in cola:
        print(f"{p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.memoria:>8} | {p.estado:<10}")

  #lo que hace el ''TA':>4' es rellenar con espacios vacios a la izq, si el texto tiene menos de 4 caracteres.
  #print("-" * 50) lo que hace es imprimir 50 guiones, para separar el titulo del  contenido

def MostrarMemoria():
  print(f"{'ID_Particion':<12} | {'Comienzo':^4} | {'Tamaño KB':^10} | {'Proceso Asignado':^16} | {'Fragmentacion':<13}")
  print("-" * 50)
  for part in memoria:
    pAsignado = part["procesoAsignado"]
    if pAsignado is None:
      pAsignado = "Libre"
    print(f"{part["id"]:<12} | {part["comienzo"]:^4} | {part["tamanio"]:^10} | {pAsignado:^16} | {0:^13}")


"""El simulador deberá presentar como salida la siguiente información:
 El estado del procesador (proceso que se encuentra corriendo en ese instante)
 La tabla de particiones de memoria, la cual deberá contener (Id de partición, dirección de comienzo de
partición, tamaño de la partición, id de proceso asignado a la partición, fragmentación)
 El estado de la cola de procesos listos y listos/suspendidos."""

def PresentacionDeSalida(): #muestro todas las colas
  print("Tiempo Actual: ", tActual)
  #Mostrar cola de Ejecucion
  print("\n-----Estado del Procesador actualmente-----\n")
  print(f"{'Proceso Ejecutandose':^20} | {'Tiempo de Irrupción':^19} ")
  print("-" * 50)
  if ejecucion["enUso"] == False:
    pEjecutandose = ejecucion["procEjecutandose"]
    print(f"{pEjecutandose.id :^20} | {pEjecutandose.TI :^19}")
  else: 
    print(f"{'Ninguno':^20} | {'0':^19} ")
    print("Actualmente no hay procesos ejecutandose")

  #Mostrar Memoria
  print("\n-----Tabla de Particiones de Memoria-----\n")
  #mostrar: id part, dir de comienzo, tamaño, id proceso asignado, fragmentacion?????
  #mostrar tabla
  MostrarMemoria()

  texto = "-----Cola de Procesos Listos-----"
  MostrarCola(listos, texto)
  texto = "-----Cola de Procesos Listos y Suspendidos-----"
  MostrarCola(listosSuspendidos, texto)
  texto = "-----Cola de Procesos Terminados-----"
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
def CargarEnMemoria(proceso): #REVISAR
  global disponibleEnMemoria
  longitudMemoria = len(memoria) 
  if longitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    memoria.sort(key=itemgetter("tamanio")) #ordeno la lista para hacer ASIGNACION BEST FIT
    for i in range(longitudMemoria):  #itero sobre cada particion, para saber cual esta libre
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if proceso.tamano <= memoria[i].get("tamanio"):
            disponibleEnMemoria =  disponibleEnMemoria - proceso.tamano 
            if disponibleEnMemoria != 0: #o sea, que aun hay espacio en memoria para cargar un proximo proceso.
              particionNueva = { "id": (longitudMemoria+1), "comienzo": memoria[i].get("comienzo") + proceso.tamano, "tamanio": disponibleEnMemoria , "procesoAsignado": None }
              memoria.append(particionNueva)
              #revisar el "id": (logitudMemoria+1). Quiza sea mejor preguntar por el id de la particion anterior y sumarle 1

            # de memoria[i] (o sea, la particion que esta libre en la cual voy a poner el proceso actual) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = proceso.tamano
            memoria[i]["procesoAsignado"] = proceso.id
            return True #manda un mensaje de que el proceso se cargo en memoria.
        #no ingresó pq la particion era pequeña:
        #else: 
        #  fragmentacion += memoria[i]["tamanio"] #siquiera hace falta, en mi opinion
    return False  #no hubo espacio, por tanto no se cargó.

#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
#Solucion: Version 1: uso un ordenador de lista
def JuntarParticiones(memoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja la memoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio junto al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una particion
    memoria = sorted(memoria, key = itemgetter("comienzo") ) #primero ordeno memoria segun el comienzo de c/particion. 
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
         

def LiberarMemoria(proceso, memoria, disponibleEnMemoria): #revisar #este se usaria al teminar un proceso
  for particion in memoria: #me fijo en que lugar esta el proceso a quitar
    if str(particion.get("procesoAsignado")) == str(proceso.id) :
    #El str es para pasar ambos a tipo string para que no de error de tipos. Solo por las dudas. 
      particion["procesoAsignado"] = None
      #ojo que: no elimino el elemento de la lista "memoria", solo cambio el estado, ya está desocupado.
      disponibleEnMemoria += proceso.tamano
      memoria = JuntarParticiones(memoria)
      return True, memoria, disponibleEnMemoria
  #si terminó de iterar es pq no encontró el proceso, por eso retorna False, deberia poner tmb un texto que idga que no se encontró
  return False, memoria, disponibleEnMemoria #no se encontró el proceso en memoria.


#----------------------------------------------------------------------------fin Memoria

def CargarListosYSuspendidos(fProceso, colaActual): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso) #este lo agrega al final de la cola, no se si seria mejor acomodar segun TI.
  EliminarDeCola(colaActual, fProceso)

def AgregarAListos(fProceso, listos):
  fProceso.estado = "listo"
  mayorTI = True
  #cargar segun TI
  for proc in listos: 
    if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor tiempo de irrupción
        indice = listos.index(proc) 
        listos.insert(indice, fProceso)
        mayorTI = False
        break
  if mayorTI: 
    listos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

#antes de cargar a listos, pregunto pot el tiempo actual
def CargarListos(fProceso, colaActual, colaListos):
      #se actualliza estado del proceso a listo
      #a tener en cuenta: cargar los procesos segun TI.
      # quiza deba hacer una funcion aparte para eso
  hayEspacio = CargarEnMemoria(fProceso) #retorna v o f.
  if hayEspacio:
    #cargar a listos
    AgregarAListos(fProceso, colaListos)
    #elimina de la cola anterior, porque ya se cargo a listos o suspendidos.
    EliminarDeCola(colaActual, fProceso) 
      #con "cola actual" me refiero a la cola de la que se elimina, puede ser cola de ejecucion, de nuevos, de suspendidos.
  
  #no hay espacio: 
  elif (fProceso.estado != "suspendido"): #si es igual a suspendido es pq ya estaba en la lista de suspendidos. no hace falta volvcer a ponerlo.
    #cargar en suspendidos, solo si es que NO estaba en suspendidos
    CargarListosYSuspendidos(fProceso, colaActual)
  #si es == suspendido, no hago nada.



#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

#ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }
def EjecutarProceso(procesoActual, colaEjecucion, colaListos): #hacer
  #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.
  #Nota: sí, tengo que agregarlo a la cola de lsitos, pero no tengo que preguntar si hay espacio en memoria, porque el proceso ya esta asignado en memoria
  #overhead:
  if colaEjecucion["enUso"] == True: #HAY proc EJecutandose: preguntar por TI y sacar proceso
    
    procesoEjecutandose = colaEjecucion["procEjecutandose"]
    #procesoEjecutandose.TI = colaEjecucion["tiempoEjecucion"] #creo qu eesta linea no hace falta. Es para ctualizar TI, pero spone que igual se va ir restando directamente del proceso actualemnte enejecucuion
    
    if procesoActual.TI < procesoEjecutandose.TI: #lo saco al anterior de la cola ejecutandose
      #llamo a la funcion de agragar a listos, sin preguntar por memoria.
      AgregarAListos(procesoEjecutandose, colaListos) #aca adentro ya se actualiza su estado
      #si no entra en el if es pq el procesoActual es igual al del ejecutandose.
    else: 
      print("La CPU está ocupada por un proceso con menor TI")
  #Si en este if, no entra, es pq no hay procesos ejecutandose: colaEjecucion["enUso"] == False:
  else:
    colaEjecucion["enUso"] = True
  #no pongo en else, pq en ambos casos debo asignar el proceso actual en la cola de listos
  EliminarDeCola(colaListos, procesoActual)
  procesoActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procesoActual
  #colaEjecucion["tiempoEjecucion"] = procesoActual.TI #no hace falta este, creo
  #NOTA: aca se deberia hacer un print general de el estado de todos los procesos y la cola de ejecucion 


#  TR = T_fin – TA. El tiempo de fin seria el TActual en que termina
def TerminarProceso(proceso): #hacer
  global cantProcesos, GM
  liberadoCorrectamente, memoria, disponibleEnMemoria = LiberarMemoria(proceso, memoria, disponibleEnMemoria)
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

  return memoria, disponibleEnMemoria
 #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria

def FinalizoEjecucion(colaEjecucion):
    colaEjecucion["procEjecutandose"].TI -=1
    if colaEjecucion["procEjecutandose"].TI == 0: #en esta funcion se "aumenta" el TR del proceso
      memoria, disponibleEnMemoria = TerminarProceso( ejecucion["procEjecutandose"] ) 
      return True, memoria, disponibleEnMemoria
    return False



""" Al finalizar la simulación se deberá presentar un informe estadístico con, tiempo de retorno y espera para cada
proceso y los respectivos tiempos promedios. También deberá calcular el rendimiento del sistema para la
simulación (cantidad de trabajos terminados por unidad de tiempo)"""


def CalcularPromediosTEyTR ():
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



def AumentarTiempo(): #hacer
  global tActual
  #aumenta tiempo actual
  #en esta funcion, deberia tambien aumentar lso tiempos de espera, o de retorno, no se, de cada proceso
  tActual +=1
  #Aumentar tiempos de espera de cada proceso:
  for proc in listos:
    proc.TE += 1
  for proc in listosSuspendidos:
    proc.TE += 1

    



#----------------------------------------------------------------------------------
#MAIN:

#declaracion de variables:

cantProcesos = 0
tActual = 0
GM = 0 # Grado de Multiprogramacion, maximo 5


#menu: #mejorar la salida de texto
print("""Bienvenido al Simulador...! Opciones Disponibles:
  "0. Salir: ingrese '0' para salir
  "1. Informacion (recomendable)
  "2. Comenzar Simulador
  -----------------------------------------------------------------------""")
opcion = 8
while opcion != 1 and opcion != 2 and opcion != 0: #para controlar la entrada
  opcion = int(input("Seleccione una opción: "))
  if opcion == 0:
    break
  elif opcion == 1:
      pass
  elif opcion == 2:
    print("""Comenzando el Simulador...
    Por favor, cargue la ruta del archivo con los procesos, en el formato: ... """)
    existe = False
    while not existe:
      archivo = input("Cargue aquí: ")
      existe = existeArchivo(archivo)
      if existe == False:
        archivo = input("""Intente ingresarlo otra vez o intente con otro archivo: 
        o ingrese '0' para volver a menu """)
        if archivo == 0:
          break #REVISAR ESTO

    #Sigo con el programa:
    #una vez abierto el archivo:
    cargarNuevos (archivo)

    i = 1
    while cantProcesos > 0:
      if GM < 5:
        if len(nuevos) != 0:
          for proceso in nuevos:
            if proceso.TA <= tActual:
              CargarListos(proceso, listos, nuevos) #aca se carga en listos, a memoria, o a listos y suspendidos, y se saca de la cola de nuevos
              GM += 1
              if GM >= 5:
                break
          #  else:
          #    break
        else:
          print("---Cola de Nuevos Vacia---")

      if len(listos) != 0:
        procesoActual = listos[i]
        if procesoActual.TA <= tActual: 
          EjecutarProceso(procesoActual, ejecucion)

      AumentarTiempo()

      if ejecucion["enUso"] == True:
      #finalizó la ejecucion del proceso?
        if procesoActual == ejecucion["procEjecutandose"]: #es el que recien se ejecutó
          i += 1
          procesoActual = listos[i] #quiza deba usar pop, para ello debo modifica lo de eliminar de cola
        #si no es, es pq sigue esperando a ser ejecutado
        procFinalizado, memoria, disponibleEnMemoria = FinalizoEjecucion() 
        if procFinalizado: #Si terminó, asigno otro proceso
          #cantProcesos, memoria, disponibleEnMemoria = TerminarProceso( ejecucion["procEjecutandose"] ) 
          
          if procesoActual.TA <= tActual:
            EjecutarProceso()

        if len(listosSuspendidos) > 0: #hay un proceso en espera de ser cargado.
          for i, p in enumerate(listosSuspendidos):
            if p.TA <= tActual:
              CargarListos(p, listos, listosSuspendidos)
          
        PresentacionDeSalida()







"""    tope = 0
    while GM <= 5 or tope < len(nuevos):
      CargarListos()
      GM += 1.
    """
    #...
  






    


