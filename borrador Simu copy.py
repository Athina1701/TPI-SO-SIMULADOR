"""
El simulador deberá presentar como salida la siguiente información:
 El estado del procesador (proceso que se encuentra corriendo en ese instante)
 La tabla de particiones de memoria, la cual deberá contener (Id de partición, dirección de comienzo de
partición, tamaño de la partición, id de proceso asignado a la partición, fragmentación interna)
 El estado de la cola de procesos listos y listos/suspendidos.
 Al finalizar la simulación se deberá presentar un informe estadístico con, tiempo de retorno y espera para cada
proceso y los respectivos tiempos promedios. También deberá calcular el rendimiento del sistema para la
simulación (cantidad de trabajos terminados por unidad de tiempo)



para hace el simulador: 
main: el menu de opciones e info.
// si se quiere: una funcion para inicializar colas.
funcion 1: existencia del archivo
funcion 2: carga procesos a la cola de nuevos y ordenar
funcion 3: carga a la cola de listos / cargar en memoria
funcion 11: calcualr espacio disponible en memoria.
f4: carga de la cola de listos y suspendidos.
f5: seleccionar proceso en cola de listo, segun srtf
f6: poner proceso en ejecucion 
f7: quitar proceso en ejecucion ( e internamente se llama a las f3 y 4.
f8: contar tiempo y restra Ti
f9: liberar memoria
f10: cargar cola de terminados.

Estrcturas a usar:
*arreglos para las colas: nuevo, listo, LyS, terminados.
contadores: cant procesos, tiempo, GM
registros/clases/ diccionario: para el proceso,
lista: memoria  (a  ver, pq es variable)
bandera: cola de ejecucion.
acumuladores: promedios de tiempo, rendimiento sistema (cant trabajos terminados por u de timepo).
"""


#declaracion de variables:

#en mi opinion, delcarar los procesos como diccionarios es lo ideal, ya que estos ya estan creados, no es que los voy a tener q armar yo
proceso1 = { "TA": 3, "TI": 5, "memoria": 20, "estado": "nuevo"}

#asi tal cual estarian cargados en el archivo. Sino, uso clases:
class Proceso:

  def __init__(self, nombre, TA, TI, memoria, estado):
    self.nombre = nombre
    self.TA = TA
    self.TI = TI
    self.memoria = memoria
    self.estado = estado

p1 = Proceso("P1", 3, 5, 20, "nuevo")
# entonces en el arcivo solo estan cargados como columnas: P1 3 5 20 , el "nuevo" agregaria yo. 
#creo que no hace falta el campo "nombre".

nuevo = []
listo = []
lisSuspendidos = []
terminados = []


def calcularEspacioDisponible(fProceso): #sinceramente no se como hacer.
  #if fProceso.memoria <= memoria[0]: #si el proceso cabe en la memoria, el tema es que la memoria quiza no tenga espacios disponibles continuos.
  # yo tendria que tomar cada fin de proceso y el comienzo del proximo, para que ver si es que realmente hay espacio.
  pass

"""MUY CONFUSO. NO LO APLICO
memoria = [450, ]
p1.memoria < 

  memoria: 
    libre = [450]
    ocupado = []  # o tambien lo hago como un diccionario, en vez de clase.
  entonces:
  t=0 libre = 450.
  t = 1, p1= 100, p1 < 450, si: memoria.libre[1] (o sea, = 450) - p1.memoria = 350
  entonces a: memoria.libre = [350] y a memoria.ocupado = [ [p1, 150, 100] ] (o sea, p1 ocupa desde 150, 100 lugares)
  ahora: t=2, p1 = 300
"""


#OTRA FORMA:
"""
memoria = []

class espacioMemoria:
  def __init__(self, id, comienzo, tamaño, procesoAsignado, fragmentacionInterna):
    self.id = id
    self.comienzo = comienzo
    self.tamaño = tamaño
    self.procesoAsignado = procesoAsignado # si no hay proceso asignado, es None. Entonces pregunto por none.
    self.fragmentacionInterna = fragmentacionInterna
"""


class particionMemoria:
  def __init__(self, id, comienzo, tamaño, procesoAsignado):
    self.id = id #no creo que haga falta id
    self.comienzo = comienzo
    self.tamaño = tamaño
    self.procesoAsignado = procesoAsignado # si no hay proceso asignado, es None. Entonces pregunto por none. Asi no creo un campo extra de libre/ocupado.

espacioInicial = particionMemoria(1, 0, 450, None) # al principio no hay proceso asignado, entonces es None.
memoria = [espacioInicial]

#el flujo seria:
""" t= 1, p1 = 100 k → 
if memoria[0].procesoAsignado is None: #no hay proceso asignado.
  if p1.memoria < memoria[0].tamaño:   #el espacio es adecuado.
    espAnterior = particionMemoria(esp1, memoria[0].comienzo, p1.memoria, p1.id) 
      #creo un nuevo espacio de memoria para el proceso.
    espNuevo = particionMemoria(esp2, memoria[0].comienzo + p1.memoria, memoria[0].tamaño - p1.memoria, None) #creo un nuevo espacio de memoria para el proceso.
      # creo una nueva instancia de espacio de memoria libre.
    memoria = [espAnterior, espNuevo] #actualizo la lista de memoria.

    return True #manda un mensaje de que el proceso se cargo en memoria.
                #se debe actualizar el estado del proceso a listo, en def cargarListos
    else: 
      return False #manda un mensaje de que no hay espacio para el proceso.

      #el proceso lo pongo en la cola de listos/suspendidos. #podria hacer en otra parte esto.
    

"""


#ordena procesos. ordeno la cola de nuevos por TA, si hay dos con TA iguales, ordeno por id.
#sorted(student_objects, key=attrgetter('grade', 'age'))
nuevos = sorted(nuevos, key = attrgetter('TA', 'TI') ) #revisar #probe y funciona.