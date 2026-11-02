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
listSuspendidos = []
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
#sorted(student_objects, key=attrgetter('grade', 'age'))
    nuevos = sorted(nuevos, key = attrgetter('TA', 'TI') ) #revisar #probe y funciona. 


def mostrarCola(cola): #voy a tratar de hacer una sola funcion que reciba cualquiera de las colas, en vez de hacer una por cada cola.

  
  
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

def calcularEspacioDisponible(fProceso): #sinceramente no se como hacer.
  #si el proceso cabe en la memoria, el tema es que la memoria quiza no tenga espacios disponibles continuos.
  # yo tendria que tomar cada fin de proceso y el comienzo del proximo, para que ver si es que realmente hay espacio.

  pass


def CargarListos():
  pass #se actualliza estado del proceso a listo
        #a tener en cuenta: cargar los procesos segun TI.
        # quiza deba hacer una funcion aparte para eso


def cargarListosYSuspendidos():
  pass

#def seleccionarProcesoSRTF(): # no hace falta porque ya esta ordenada la cola, o eso deberia. El orden se debe hacer en la cola de listos.

def EjecutarProceso():
  pass #cambia estado a "ejecucion". Se llama a la funcion para cargar en cola de listos si es que hay otro proc en ejecucion.








