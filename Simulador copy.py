
#ARCHIVO PRINCIPAL: SIMULADOR 
#Esta muy cargaado de anotaciones, al terminarlo, habria que "limpiarlo"

"""
TA: tiempo de arribo
TI: tiempo de irrupcion
TR: tiempo de retorno
TE: tiempo de espera
estados: "nuevo", "listo", "suspendido", "ejecutando" , "terminado"
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

cantProcesos = 0

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
  #if existeArchivo(nombreArchivo): #esto pienso preguntar en el main, no acá
    with open(nombreArchivo, 'r') as archivo:
  #carga procesos
      for linea in archivo: 
        if linea != "": 
          #cada linea es un proceso.
          # El proceso está cargado en archivo como: id,TA,TI,memoria.
          linea = linea.strip().split(",") #strip para sacar \n y split para separar por comas.
          procesoNuevo = Proceso(linea[0], int(linea[1]), int(linea[2]), int(linea[3]), "nuevo")
          # nombre = linea 0 , TA = linea 1, 
          #pNuevo = Proceso(p1,3, 5, 20, "nuevo")
          nuevos.append(procesoNuevo) # proc cargado a la lista.

          cantProcesos += 1  
          if cantProcesos > 10: #vigila que no se pase de 10 proc.
            print("Se ha lleago al limite de procesos a cargar. Cantidad actual: ", cantProcesos)
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

def MostrarCola(cola, texto): #voy a tratar de hacer una sola funcion que reciba cualquiera de las colas, en vez de hacer una por cada cola.
  print(texto, "\n")
  print("IDProcess | TA | TI | memoria | estado \n") #por el momento, le dejo 'estado', para ver si hay errores.
  for proc in cola:
    print(proc.id, " | ", proc.TA, " | ", proc.TI, " | ", proc.memoria, " | ", proc.estado)  
  #hay que hacerlo de forma tableada.
"""------------- la solucion de la IA para la tabla:
def MostrarCola(cola):
    print(f"{'ID':<5} | {'TA':>4} | {'TI':>4} | {'Memoria':>8} | {'Estado':<10}")
    print("-" * 50)

    for p in cola:
        print(f"{p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.memoria:>8} | {p.estado:<10}")

  #lo que hace el ''TA':>4' es rellenar con espacios vacios a la izq, si el texto tiene menos de 4 caracteres.
  #print("-" * 50) lo que hace es imprimir 50 guiones, para separar el titulo del  contenido
  """

#---------------------------------------------------------------
# Por el momento, la memoria se maneja d esta forma. Es lo que se me ocurrió
# Es una lista de diccionarios. Las particiones son los diccionarios

memoria = []
particionInicial = { "id": "1", "comienzo": 0, "tamanio": 450, "procesoAsignado": None }
#id no me parece tan necesario, ademas hay que revisar en el cargarmemoria, porque se repiten los id.
memoria.append(particionInicial)
""" o lo que es lo mismo:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
"""

disponibleEnMemoria = 450 #este debo ir disminuyendolo, y aumentarlo al liberar memoria.

#-----------------------------------
#actualizacion: saque a DisponibleEnMemoria como parametro, para usarla como global, y se actualice automaticamente
def CargarEnMemoria(proceso):
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
  for proc in listos: #pongo el nuevo proceso segun TI
    if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor timepo de irrupción
        indice = listos.index(proc) 
        listos.insert(indice, fProceso)
        mayorTI = False
        break
    if mayorTI: 
        listos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene



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


#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

#ejecucion = { "enUso": False, "procEjecutandose": None, "tiempoEjecucion": 0 }
def EjecutarProceso(procesoActual, colaEjecucion): #hacer
  #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.
  #Nota: sí, tengo que agregarlo a la cola de lsitos, pero no tengo que preguntar si hay espacio en memoria, porque el proceso ya esta asignado en memoria
  if colaEjecucion["enUso"] == True: #HAY proc EJecutandose: preguntar por TI y sacar proceso
    procesoEjecutandose = colaEjecucion["procEjecutandose"]
    procesoEjecutandose.TI = colaEjecucion["tiempoEjecucion"] #T ejecucion debe ir restandose al pasar el tiempo
    
    if procesoActual.TI < procesoEjecutandose.TI: #lo saco al anterior de la cola ejecutandose
      #llamo a la funcion cargar
      AgregarAListos(procesoEjecutandose, listos) #aca adentro ya se actualiza su estado
      #si no entra en el if es pq el procesoActual es igual al del ejecutandose.
  #Si en este if, no entra, es pq no hay procesos ejecutandose: colaEjecucion["enUso"] == False:
  #no pongo un else, pq en ambos casos debo asignar el proceso actual en la cola de listos
  EliminarDeCola(listos, procesoActual)
  procesoActual.estado = "ejecutandose"
  colaEjecucion["procEjecutandose"] = procesoActual
  colaEjecucion["tiempoEjecucion"] = procesoActual.TI #no hace falta este, creo
  #NOTA: aca se deberia hacer un print general de el estado de todos los procesos y la cola de ejecucion 

  



def suspenderEjecucion(fProceso): #hacer
  pass #se usaria para sacarlo de la cola, actualizar estado.

def TerminarProceso(proceso, cantProcesos): #hacer
  if proceso.TI == 0:
    liberadoCorrectamente, memoria, disponibleEnMemoria = LiberarMemoria(proceso, memoria, disponibleEnMemoria)
    if liberadoCorrectamente:
      ejecucion["enUso"] = False
      ejecucion["procEjecutandose"] = None
      ejecucion["tiempoEjecucion"] = 0

      cantProcesos -=1
      proceso.estado = "terminado"
      terminados.append(proceso)
    else: 
      print("Hubo un error al finalizar el proceso.")

  return cantProcesos, memoria, disponibleEnMemoria
 #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria

def AumentarTiempo(): #hacer
  #aumenta tiempo actual
  #en esta funcion, deberia tambien aumentar lso tiempos de espera, o de retorno, no se, de cada proceso
  pass


""" Al finalizar la simulación se deberá presentar un informe estadístico con, tiempo de retorno y espera para cada
proceso y los respectivos tiempos promedios. También deberá calcular el rendimiento del sistema para la
simulación (cantidad de trabajos terminados por unidad de tiempo)"""
def CalcularTEyTR ():
  pass

def CalcularRendimientoSistema ():
  pass




