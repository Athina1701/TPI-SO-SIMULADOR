"""
TA: tiempo de arribo
TI: tiempo de irrupcion
TR: tiempo de retorno
TE: tiempo de espera
estados: "nuevo", "listo", "suspendido", "terminado"
"""
from operator import attrgetter

class Proceso:
  def __init__(self, id, TA, TI, memoria, estado):
    self.id = id
    self.TA = TA
    self.TI = TI
    self.memoria = memoria
    self.estado = estado
    self.TR = 0. # TR = T_fin – TA
    self.TE = 0. # TE = TR – TI, donde TI es la duración de la ráfaga de CPU requerida).

cantDisponible = 450 
memoria = [cantDisponible, ]
#100k para el SO, 450k para procesos.
# la idea es que quede una lista de elementos que marque: proceso que ocupa el espacio, donde comienza, cuanta memoria lleva.
# por lo tanto, deberia haber una funcion que calcule el espacio disponible.

#En si, inicializar de esta forma no hace falta, lo hago para tener en cuenta las estrcturas a usar.
nuevos = []
listos = []
listosSuspendidos = []
terminados = []

cantProcesos = 0
finArch = False

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
   #NOta: esta funcion "remove" permite eliminar por nombre del elemento, si quisisera eliminar por indice de la lista: "del cola".

def MostrarCola(cola): #voy a tratar de hacer una sola funcion que reciba cualquiera de las colas, en vez de hacer una por cada cola.
#hacer
  
  
  pass #hay que hacerlo de forma tableada.


# por el momento, la estructura de la memoria es esta. respondiendo a la pregunta de def calcularEsapcio.
class espacioMemoria:
  def __init__(self, id, comienzo, tamaño, procesoAsignado):
    self.id = id
    self.comienzo = comienzo
    self.tamaño = tamaño
    self.procesoAsignado = procesoAsignado # si no hay proceso asignado, es None. Entonces pregunto por none. Asi no creo un campo extra de libre/ocupado.

espacioInicial = espacioMemoria(1, 0, 450, None) # al principio no hay proceso asignado, entonces es None.
memoria = [espacioInicial]

def CalcularEspacioDisponible(fProceso): #sinceramente no se como hacer.
  #si el proceso cabe en la memoria, el tema es que la memoria quiza no tenga espacios disponibles continuos.
  # yo tendria que tomar cada fin de proceso y el comienzo del proximo, para que ver si es que realmente hay espacio.

  pass  #hacer

def CargarListosYSuspendidos(fProceso, colaAnterior): #hacer
  fProceso.estado = "suspendido"
  listosSuspendidos.append(fProceso)
  EliminarDeCola(colaAnterior, fProceso)

def CargarListos(fProceso, colaActual):
       #se actualliza estado del proceso a listo
        #a tener en cuenta: cargar los procesos segun TI.
        # quiza deba hacer una funcion aparte para eso
  hayEspacio = CalcularEspacioDisponible() #retorna v o f.
  if hayEspacio:
    #cargar a listos
    fProceso.estado = "listo"
    esMayor = True
    for proc in listos:
      if (fProceso.TI < proc.TI): #el proceso a cargar tiene menor timepo de irrupción
        indice = listos.index(proc) 
        listos.insert(indice, fProceso)
        esMayor = False
        break
    if esMayor: 
      listos.append(fProceso) #lo agrego al final, pq es el que mayor TI tiene

    EliminarDeCola(colaActual, fProceso) #elimina de la cola de nuevos, porque ya se cargo a listos o suspendidos.
      #con "cola actual" me refiero a la cola de la que se elimina, puede ser cola de ejecucion, de nuevos, de suspendidos.
  #no hay espacio: 
  elif (fProceso.estado != "suspendido"): #si es igual a suspendido es pq ya estaba en la lista de suspendidos. no hace falta volvcer a ponerlo.
    #cargar en suspendidos, solo si es que NO estaba en suspendidos
    CargarListosYSuspendidos(fProceso, colaActual)


#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

def EjecutarProceso(): #hacer
  pass #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.








