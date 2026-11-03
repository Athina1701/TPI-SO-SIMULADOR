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

#---------------------------------
#  por el momento, la estructura de la memoria es esta. respondiendo a la pregunta de def calcularEsapcio.
class espacioMemoria:
  def __init__(self, id, comienzo, tamaño, procesoAsignado):
    self.id = id
    self.comienzo = comienzo
    self.tamaño = tamaño
    self.procesoAsignado = procesoAsignado # si no hay proceso asignado, es None. Entonces pregunto por none. Asi no creo un campo extra de libre/ocupado.

espacioInicial = espacioMemoria(1, 0, 450, None) # al principio no hay proceso asignado, entonces es None.
memoria = [espacioInicial]
#-----------------------------------


def CargarEnMemoria(fProceso): #sinceramente no se como hacer.
  #si el proceso cabe en la memoria, el tema es que la memoria quiza no tenga espacios disponibles continuos.
  # yo tendria que tomar cada fin de proceso y el comienzo del proximo, para que ver si es que realmente hay espacio.

  pass  #hacer
#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
      #  OJO: contiguas: si habia una libre de direccion 50 a 100, y justo se liber aun proceso qu eocupaba de 100 a 130, unir esos espacios: de 50 a 130.

def LiberarMemoria():
  pass

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
  if ejecucion ["enUso"] == False: #no hay proecsos ejecutandose.
    pass


def suspenderEjecucion(fProceso): #hacer
  pass #se usaria para sacarlo de la cola, actualizar estado.

def TerminarProceso(fProceso): #hacer
  pass #pasarlo a cola de terminados y disminuir cant procesos. aca llamaria a la funcion LiberarMemoria






