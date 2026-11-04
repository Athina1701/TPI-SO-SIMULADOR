
#ARCHIVO PRINCIPAL: SIMULADOR 
#Esta muy cargaado de anotaciones, al terminarlo, habria que "limpiarlo"

"""
TA: tiempo de arribo
TI: tiempo de irrupcion
TR: tiempo de retorno
TE: tiempo de espera
estados: "nuevo", "listo", "suspendido", "ejecutando" , "terminado"
"""
from operator import attrgetter

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

def EliminarDeCola(cola, fProceso): #recibe la cola y el proceso a eliminar.
   # no creo que pueda hacer uno general para todas las colas
   cola.remove(fProceso) #elimina el proceso puntual de la cola que se le pase. 
   #NOTA: esta funcion "remove" permite eliminar por nombre del elemento, si quisisera eliminar por indice de la lista: "del cola".
  

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
particionInicial = { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None }
#id no me parece tan necesario, ademas hay que revisar en el cargarmemoria, porque se repiten los id.
memoria.append(particionInicial)
""" o lo que es lo mismo:
memoria = [ { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None } , ]
"""

disponibleEnMemoria = 450 #este debo ir disminuyendolo, y aumentarlo al liberar memoria.

#-----------------------------------

def CargarEnMemoria(proceso, disponibleEnMemoria):
  logitudMemoria = len(memoria) 
  if logitudMemoria > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    for i in range(logitudMemoria):  #itero sobre cada particion, para saber cual esta libre
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if proceso.tamano <= memoria[i].get("tamanio"):
            disponibleEnMemoria =  disponibleEnMemoria - proceso.tamano 
            if disponibleEnMemoria != 0: #o sea, que aun hay espacio en memoria para cargar un proximo proceso.
              particionNueva = { "id": (logitudMemoria+1), "comienzo": memoria[i].get("comienzo") + proceso.tamano, "tamanio": disponibleEnMemoria , "procesoAsignado": None }
              memoria.append(particionNueva)
              #revisar el "id": (logitudMemoria+1). Quiza sea mejor preguntar por el id de la particion anterior y sumarle 1

            # de memoria[i] (o sea, la particion que esta libre en la cual voy a poner el proceso actual) me quedo con el id y el comienzo, el resto de los datos actualizo:
            memoria[i]["tamanio"] = proceso.tamano
            memoria[i]["procesoAsignado"] = proceso.id

            return True, disponibleEnMemoria #manda un mensaje de que el proceso se cargo en memoria.
    return False, disponibleEnMemoria #no hubo espacio, por tanto no se cargó.

#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.

def LiberarMemoria(proceso, memoria, disponibleEnMemoria): #revisar
  for particion in memoria:
    if particion.get("procesoAsignado") == proceso.id :
    #if str(particion.get("procesoAsignado")) == str(proceso.id): deberia cambairle por esta linea, ya que podria pasar que no sean del mismo tipo
      particion["procesoAsignado"] = None
      #ojo que: no elimino el elemento de la lista "memoria", solo cambio el estado, ya está desocupado.
      disponibleEnMemoria += proceso.tamano
      return True
  return False #no se encontró el proceso en memoria.




def CargarListosYSuspendidos(fProceso, colaActual): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso) #este lo agrega al final de la cola, no se si seria mejor acomodar segun TI.
  EliminarDeCola(colaActual, fProceso)

def CargarListos(fProceso, colaActual):
       #se actualliza estado del proceso a listo
        #a tener en cuenta: cargar los procesos segun TI.
        # quiza deba hacer una funcion aparte para eso
  hayEspacio = CargarEnMemoria(fProceso) #retorna v o f.
  if hayEspacio:
    #cargar a listos
    fProceso.estado = "listo"
    mayorTI = True
    for proc in listos:
      if (fProceso.TI < proc.TI): #el proceso nuevo a cargar tiene menor timepo de irrupción
        indice = listos.index(proc) 
        listos.insert(indice, fProceso)
        mayorTI = False
        break
    if mayorTI: 
      listos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

    EliminarDeCola(colaActual, fProceso) #elimina de la cola de nuevos, porque ya se cargo a listos o suspendidos.
      #con "cola actual" me refiero a la cola de la que se elimina, puede ser cola de ejecucion, de nuevos, de suspendidos.
  #no hay espacio: 
  elif (fProceso.estado != "suspendido"): #si es igual a suspendido es pq ya estaba en la lista de suspendidos. no hace falta volvcer a ponerlo.
    #cargar en suspendidos, solo si es que NO estaba en suspendidos
    CargarListosYSuspendidos(fProceso, colaActual)


#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

def EjecutarProceso(): #hacer
  #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.
  if ejecucion["enUso"] == False: #no hay proecsos ejecutandose.
    pass


def suspenderEjecucion(fProceso): #hacer
  pass #se usaria para sacarlo de la cola, actualizar estado.

def TerminarProceso(fProceso): #hacer
  pass #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria






