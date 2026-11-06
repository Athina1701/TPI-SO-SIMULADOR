
from operator import attrgetter, itemgetter

#ESTE ARCHIVO ES PARA IR COLOCANDO LOS BLOQUES DE CODIGO QUE NO NECESITO EN EL ARCHIVO PRINCIPAL. 
#ES DE CODIGOS BORRADORES, Y ANOTACIONES VARIAS PARA NO SOBRECARGAR EL PPAL. NO EJECUTAR PORQUE ESTA LLLENO DE PROBLEMAS. PARA ESO, EL ARCHIVO "PRUEBAS"

"""

El simulador deberá presentar como salida la siguiente información:
 El estado del procesador (proceso que se encuentra corriendo en ese instante)
 La tabla de particiones de memoria, la cual deberá contener (Id de partición, dirección de comienzo de
partición, tamaño de la partición, id de proceso asignado a la partición, fragmentación)
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


#declaracion de variables------------------------------:

#en mi opinion, delcarar los procesos como diccionarios es lo ideal, ya que estos ya estan creados en el arch, no es que los voy a tener q armar yo
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


# f"{...}" permite meter variables dentro del text.

print(f"{p.id:<5}")
"""p.id va a entrar en el texto
:<5 = ocupa al menos 5 caracteres
si el valor tiene menos de 5, lo rellena con espacios a la derecha"""


#---------------- OTRA FORMA DE HACER LA MEMORIA: LISTA DE DICCIONARIOS:
memoria = []
particionInicial = { "id": 1, "comienzo": 0, "tamanio": 450, "procesoAsignado": None }
memoria.append(particionInicial)
#pero me parece que es mas facil de manejar si es una clase. A ver:

# t= 1, p1 = 100 k →
# ahora es 0 el indice, pero la idea es ir iterando sobre memoria hasta encontrar espacio.
# Nota: usar get para toma valores del diccionario: apellido = usuario.get("apellido") # Devuelve None

if memoria[0].get("procesoAsignado") is None: #no hay proceso asignado a la particion
  if proceso.memoria < memoria[0].get("tamanio"):

    #deberia ponerle otro nombre a particionAnterior, pq me refiero a a la particion la cual se agrega un procso, no es exactamente la anterior, aumque si tiene datos de la vieja, como el id y el cmoienzo.
    particionAnterior = memoria[0] #me quedo con el id y el comienzo, el resto de los datos actualizo:
    particionAnterior["tamanio"] = proceso.memoria
    particionAnterior["procesoAsignado"] = proceso
    particionNueva = { "id": 2, "comienzo": memoria[0].get("comienzo") + proceso.memoria, "tamanio": memoria[0].get("tamanio") - proceso.memoria, "procesoAsignado": None }

# ahora con iteracion:

def CargarEnMemoria(proceso):
  if len(memoria) > 0: #por las dudas no sea una lista vacia. pero capaz no sea necesario
    for i in range(len(memoria)):
      if memoria[i].get("procesoAsignado") is None: #no hay proceso asignado a la particion
        if proceso.memoria <= memoria[i].get("tamanio"):
          # de memoria[i] me quedo con el id y el comienzo, el resto de los datos actualizo:
          memoria[i]["tamanio"] = proceso.memoria
          memoria[i]["procesoAsignado"] = proceso.id
          particionNueva = { "id": (i+1), "comienzo": memoria[i].get("comienzo") + proceso.memoria, "tamanio": memoria[i].get("tamanio") - proceso.memoria, "procesoAsignado": None }
          memoria.append(particionNueva)

          return True #manda un mensaje de que el proceso se cargo en memoria.
    return False #no hubo espacio, por tanto no se cargó.


"""
#borrador anterior: no me parece necesario árticionAnterior
  
  #deberia ponerle otro nombre a particionAnterior, pq me refiero a a la particion la cual se agrega un procso, no es exactamente la anterior, aumque si tiene datos de la vieja, como el id y el cmoienzo.
  particionAnterior = memoria[i] #me quedo con el id y el comienzo, el resto de los datos actualizo:
          particionAnterior["tamanio"] = proceso.memoria
          particionAnterior["procesoAsignado"] = proceso.id
          particionNueva = { "id": 2, "comienzo": memoria[i].get("comienzo") + proceso.memoria, "tamanio": memoria[i].get("tamanio") - proceso.memoria, "procesoAsignado": None }
          memoria.append(particionNueva)"""


"""
---------------------esto lo saqué el archivo ppal. No es necesario. despues lo borro

cantDisponible = 450 
memoria = [cantDisponible, ]
#100k para el SO, 450k para procesos.
# la idea es que quede una lista de elementos que marque: proceso que ocupa el espacio, donde comienza, cuanta memoria lleva.
# por lo tanto, deberia haber una funcion que calcule el espacio disponible.


ACTUALIZADO
#  por el momento, la estructura de la memoria es esta. respondiendo a la pregunta de def calcularEsapcio.
class espacioMemoria:
  def __init__(self, id, comienzo, tamaño, procesoAsignado):
    self.id = id
    self.comienzo = comienzo
    self.tamaño = tamaño
    self.procesoAsignado = procesoAsignado # si no hay proceso asignado, es None. Entonces pregunto por none. Asi no creo un campo extra de libre/ocupado.

espacioInicial = espacioMemoria(1, 0, 450, None) # al principio no hay proceso asignado, entonces es None.
memoria = [espacioInicial]

def CargarEnMemoria(fProceso): #sinceramente no se como hacer.
  #si el proceso cabe en la memoria, el tema es que la memoria quiza no tenga espacios disponibles continuos.
  # yo tendria que tomar cada fin de proceso y el comienzo del proximo, para que ver si es que realmente hay espacio.

  pass  #hacer
#CargarEnMemoria mas o menos estaria hecho. pero hay que hacer otra funcion que sea liberar memoria. y en el caso que se liberen dos particiones contiguas. unirlas en una sola particion. para poder ingresar un proceso mas grande.
      #  OJO: contiguas: si habia una libre de direccion 50 a 100, y justo se liber aun proceso qu eocupaba de 100 a 130, unir esos espacios: de 50 a 130.
"""
#en: def LiberarMemoria, cual deberia usar?:
  #disponibleEnMemoria += proceso.tamano
  #o....   disponibleEnMemoria += particion.get("tamanio"). para ser mas precisos, evitar errores
#segun la IA, es mejor proceso.tamano, porque es lo que verdaderamente se esta liberando
""" si quisiera estar segura de que proc.tamao y aprticion.tamaño son iguales:

assert particion.get("tamanio") == proceso.tamano
disponibleEnMemoria += proceso.tamano

o....
if particion.get("tamanio") != proceso.tamano:
    raise ValueError("La partición no coincide con el tamaño del proceso")
disponibleEnMemoria += proceso.tamano
"""


"""---esta version de la funcion causa probleas por estar eliminado elementos mientras itero sobre la misma lista. Asi que, voy a trabajar con una copia o con una nueva lista

def JuntarParticiones():
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una paarticion
    for i in range(1, longitudMemoria): #comienzo a partir del 2do elemento, por eso el 1.
      if memoria[i-1].get("procesoAsignado") == None and (memoria[i].get("procesoAsignado") == None):
        #pregunto si la particion anterior no tiene procesos asignados, al igual que la particion actual.
        #si es que SI estan desocupadas, debo: combinar tamaño, manteniendose el id y el comienzo del anterior.
        memoria[i-1]["tamanio"] += memoria[i]["tamanio"]
        #elimino la particion actual
        del memoria[i]
      #esto se itera hasta terminar la lista. si se unieron las particiones ...  esta raro
"""
#version nueva:

#está mal. tengo que preguntar por el comienzo de cada particion. No si el siguiente es none
"""ACTUALIZACION: le agregué lo de ordenar la memoria"""

def JuntarParticiones(memoria): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  """#OJO: esta funcion NO compacta espacios libres. Esta por una cuestion tecnica de como se maneja lamemoria en nuestro codigo: 
    porque: como memoria es una lista con elementos (las particiones), cuando se libera un proceso, y luego se libera otro que estaba ocuapndo un espacio junto al anterior, de seguido, 
    cuando llegue otro proceso mas gande, y quiera ocupar  ese espacio entre medio no va a poder, porque en nuestro codigo queda como 2 particiones separadas, entonces detectaria como que no es suficiente espacio para el proceso
  """
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una paarticion
    memoria = sorted(memoria, key = itemgetter("comienzo") ) #primero ordeno memoria segun el comienzo de c/particion. 
    memoriaCopy = []
    i = 0
    while i < longitudMemoria : # -1 para no pasarme del rango al iterar con i+1
      particionNueva = memoria[i] #me quedo con id, comienzo y el procsoAsignado = none.
      if memoria[i].get("procesoAsignado") is None and (i < (longitudMemoria -1)): #particion actual libre: Si. entonces me fijo las siguientes
        
        while memoria[i+1].get("procesoAsignado") is None: #si da True, es pq puedo unirlas
          #particionNueva = {"id": memoria[i].get("id"), "comienzo" memoria[i].get("comienzo") , memoria[i+1].get("tamanio") }
          particionNueva["tamanio"] += memoria[i +1].get("tamanio")
          i += 1

      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
    print("\n dentro dela funcion: ",memoriaCopy)
  return memoriaCopy #si o si debo retornar las variables que fueron reasignadas en la funcion
                   



#ACTUALIZADO: Version: iteracion por busqueda de comienzos de particiones
# O sea, si la particion 1, comeinza en 50 y su tamaño es 50, yesta desocupada. Busco la siguiente particion que cominece en 100 (comienzo + tamaño de la particion anterior), y las junto si esta tambien esta desocupada.
  #hacer
def JuntarParticiones(): #revisar, se lo puede mejorar (el indice i+1 me hace ruido)
  longitudMemoria = len(memoria) 
  if longitudMemoria > 1: #seria al pedo ejecutar si solo hay una particion
    memoriaCopy = []
    i = 0
    while i < longitudMemoria:
      particionNueva = memoria[i] #me quedo con id, cmomienzo y el procsoAsignado = none.
      if memoria[i].get("procesoAsignado") == None: #particion actual libre: Si. entonces me fijo las siguientes
        while (memoria[i+1].get("procesoAsignado") == None): #si da True, es pq puedo unirlas
          particionNueva["tamanio"] += memoria[i +1].get("tamanio")
          i += 1

      memoriaCopy.append(particionNueva) #ya sea una particion ocupada o no, la copio a la nueva lista de memoria.
      i += 1
    memoria = memoriaCopy

"""Borrador del archivo ppal, lo cambié por las otras opciones"""
def EliminarDeCola(cola, fProceso): #recibe la cola y el proceso a eliminar.
   cola.remove(fProceso) #elimina el proceso puntual de la cola que se le pase. 
   #NOTA: esta funcion "remove" permite eliminar por nombre del elemento, si quisisera eliminar por indice de la lista: "del cola[indice]".
#la funcion asi tal cual, elimina SOLO SI ES IDENTICO al que esta en cola. asi q, cuidado
""" otra forma de implementarlo: 

def EliminarDeCola(cola, id_a_eliminar): y en vez de id a eliminar, paso el proceso directamente
    for i, elem in enumerate(cola):
        if elem.get("id") == id_a_eliminar:
            del cola[i]
            return True
    return False

    o sea:
def EliminarDeCola(cola, proceso):
    for i, elem in enumerate(cola):
        if elem.get("id") == proceso.id:
            del cola[i]
            return True
    return False
"""
  
"""Lo cambie por una solcuion que mantiene el orden de las columnas"""   
def MostrarCola(cola, texto): #voy a tratar de hacer una sola funcion que reciba cualquiera de las colas, en vez de hacer una por cada cola.
  print(texto, "\n")
  print("IDProcess | TA | TI | memoria | estado \n") #por el momento, le dejo 'estado', para ver si hay errores.
  for proc in cola:
    print(proc.id, " | ", proc.TA, " | ", proc.TI, " | ", proc.memoria, " | ", proc.estado)  
  #hay que hacerlo de forma tableada.
  """------------- la solucion de la IA para la tabla:
def MostrarCola(cola, texto):
    print(texto, "\n")
    print(f"{'ID':<5} | {'TA':>4} | {'TI':>4} | {'Tamaño':>8} | {'Estado':<10}")
    print("-" * 50)

    for p in cola:
        print(f"{p.id:<5} | {p.TA:>4} | {p.TI:>4} | {p.memoria:>8} | {p.estado:<10}")

  #lo que hace el ''TA':>4' es rellenar con espacios vacios a la izq, si el texto tiene menos de 4 caracteres.
  #print("-" * 50) lo que hace es imprimir 50 guiones, para separar el titulo del  contenido
  """